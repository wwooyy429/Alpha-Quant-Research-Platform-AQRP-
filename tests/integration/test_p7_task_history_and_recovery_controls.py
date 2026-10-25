"""Public Task history, cancellation fencing and real completion recovery controls."""

import hashlib
import json
import sqlite3
import uuid
from contextlib import closing, contextmanager
from functools import partial
from pathlib import Path

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import (
    advance_actor,
    complete_actor,
    install_execution_plan,
    open_protocol_driver,
)
from aqrp.services.task_requests import catalogue, initialize
from aqrp.services.task_state import TaskState
from aqrp.services.tasks import TaskService

DRAFT = {"factor_ids": ["momentum"], "start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}


def database_rows(state):
    with closing(sqlite3.connect(state.db)) as c:
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {
            name: list(c.execute('SELECT * FROM "' + name + '" ORDER BY rowid')) for name in tables
        }


def original_files(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and p.suffix in (".json", ".jsonl", ".html")
    }


def strip_declared_control_schema(state):
    """Simulate the approved same-bundle pre-control format; preserve old records."""
    with state.transaction() as c:
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for name in tables:
            if name.startswith(("admission_", "execution_plan")) or name in {
                "budget_domains",
                "admissions",
                "trial_claims",
                "legacy_execution_owners",
            }:
                c.execute('DROP TABLE "' + name + '"')
    state.budget.anchor.unlink()


def refused_without_changes(state, root, action, expected):
    rows, files = database_rows(state), original_files(root)
    with pytest.raises(ContractError) as raised:
        action()
    assert raised.value.code == expected
    assert database_rows(state) == rows
    assert original_files(root) == files


@pytest.mark.parametrize("attempt", ["frozen-request", "domain-transition", "research-receipt"])
def test_data_free_queue_cannot_become_a_research_execution_bypass(tmp_path, attempt):
    queue = TaskState(tmp_path)
    if attempt == "domain-transition":
        initialize(tmp_path, "a" * 40)
        action = partial(queue.submit, canonical({"original_generic_request": True}), "stale")
        expected = "ADMISSION_DOMAIN_CONFLICT"
    elif attempt == "frozen-request":
        action = partial(queue.submit, canonical({"schema": "task-request/1"}), "forged")
        expected = "ADMISSION_DOMAIN_CONFLICT"
    else:
        action = partial(queue.research_attempt, str(uuid.uuid4()))
        expected = "CAMPAIGN_ATTEMPT_REQUIRED"
    refused_without_changes(queue, tmp_path, action, expected)


@pytest.mark.parametrize("attempt", ["invalid-key", "replay-receipt", "stale-cancel"])
def test_managed_submission_and_cancellation_refusals_preserve_budget(tmp_path, attempt):
    initialize(tmp_path, "a" * 40)
    service = TaskService(tmp_path)
    frozen = service.freeze(DRAFT)
    task = service.submit(frozen, "original")["task_id"]
    if attempt == "invalid-key":
        action = partial(service.submit, frozen, "")
        expected = "INVALID_IDEMPOTENCY_KEY"
    elif attempt == "replay-receipt":
        replay = service.submit(
            service.freeze({"kind": "replay", "source_task": task}), "unstarted-replay"
        )["task_id"]
        action = partial(service.state.research_attempt, replay)
        expected = "CAMPAIGN_ATTEMPT_REQUIRED"
    else:
        action = partial(service.state.cancel, task, activation={"foreign_activation": True})
        expected = "EXECUTION_PLAN_ACTIVATION_STALE"
    refused_without_changes(service.state, tmp_path, action, expected)


def test_later_actor_cannot_cancel_or_relabel_an_earlier_owner(tmp_path):
    initialize(tmp_path, "a" * 40)
    request = TaskService(tmp_path).freeze(DRAFT)
    cat = catalogue(tmp_path)
    runner = Path(__file__).resolve()
    identity = {
        "runner_path": str(runner),
        "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }
    plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "CANCELLATION_OWNER_FENCING_REGRESSION_NOT_MAIN_E2E",
        "data_hash": cat["snapshot"]["manifest_hash"],
        "catalogue_hash": digest(cat),
        **identity,
        "slots": [
            {
                "slot_id": name,
                "service_kind": "TASK",
                "request_hash": request.config_hash,
                "output_root": str(tmp_path / "research-runs"),
                "requested_units": 1,
                "grant_capacity": 1,
                "max_admitted_owners": 1,
                "expected_status": "CANCELLED",
            }
            for name in ("first", "second")
        ],
    }
    fixed = install_execution_plan(tmp_path, plan, identity)
    driver = open_protocol_driver(tmp_path, fixed, identity)
    advance_actor(driver, -1)
    first = TaskService(tmp_path)
    task = first.submit(request, "first")["task_id"]
    assert first.cancel(task) == "CANCELLED"
    path = tmp_path / "tasks" / task / "request.json"
    complete_actor(
        driver,
        {
            "owner_id": task,
            "status": "CANCELLED",
            "evidence": [
                {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            ],
        },
    )
    advance_actor(driver, 0)
    refused_without_changes(
        first.state,
        tmp_path,
        lambda: first.state.cancel(task),
        "EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT",
    )


@pytest.mark.parametrize(
    "damage",
    [
        "noncanonical-request",
        "unreproducible-request",
        "claim-type",
        "claim-uppercase-uuid",
        "queued-with-slot",
        "missing-run-directory",
        "orphan-campaign",
        "orphan-run",
    ],
)
def test_complete_history_import_rejects_changed_identity_and_orphans(tmp_path, damage):
    root = tmp_path / "workspace"
    initialize(root, "a" * 40)
    service = TaskService(root)
    task = service.submit(service.freeze(DRAFT), "original")["task_id"]
    if damage in {
        "claim-type",
        "claim-uppercase-uuid",
        "queued-with-slot",
        "missing-run-directory",
    }:
        assert service.work(task)["status"] == "SUCCEEDED"
    strip_declared_control_schema(service.state)
    request_path = root / "tasks" / task / "request.json"
    with service.state.transaction() as c:
        if damage == "noncanonical-request":
            request_path.write_bytes(request_path.read_bytes() + b" ")
        elif damage == "unreproducible-request":
            changed = json.loads(request_path.read_bytes())
            changed["code_commit"] = "b" * 40
            raw = canonical(changed)
            request_path.write_bytes(raw)
            c.execute(
                "UPDATE tasks SET raw=?,hash=? WHERE id=?", (raw.decode(), digest(changed), task)
            )
        elif damage.startswith("claim-"):
            event = c.execute(
                "SELECT seq,payload FROM events WHERE task=? AND kind='CLAIMED'", (task,)
            ).fetchone()
            payload = json.loads(event[1])
            if damage == "claim-type":
                payload["epoch"] = str(payload["epoch"])
            else:
                payload["owner"] = "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"
            c.execute(
                "UPDATE events SET payload=? WHERE seq=?", (canonical(payload).decode(), event[0])
            )
        elif damage == "queued-with-slot":
            c.execute("UPDATE tasks SET status='QUEUED' WHERE id=?", (task,))
        elif damage == "missing-run-directory":
            binding = json.loads(
                c.execute(
                    "SELECT binding FROM slots WHERE task=? AND slot='R'", (task,)
                ).fetchone()[0]
            )
            source = Path(binding["physical_ledger_root"]) / binding["child_run_id"]
            assert source.resolve().is_relative_to(root.resolve())
            # Keep the original complete bytes outside W rather than deleting evidence.
            target = tmp_path / "preserved-original-run"
            assert target.resolve().is_relative_to(tmp_path.resolve()) and not target.exists()
            source.rename(target)
        elif damage == "orphan-campaign":
            old = c.execute("SELECT * FROM campaign_attempts WHERE task=?", (task,)).fetchone()
            c.execute(
                "INSERT INTO campaign_attempts VALUES (?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), *tuple(old)[1:]),
            )
        else:
            orphan = root / "research-runs" / str(uuid.uuid4())
            orphan.mkdir()
            (orphan / "ORPHAN.json").write_bytes(
                canonical({"declared_unowned_negative_probe": True})
            )
    refused_without_changes(
        service.state, root, lambda: TaskState(root), "ADMISSION_HISTORY_UNVERIFIED"
    )
    assert not service.state.budget.anchor.exists()
    assert "admissions" not in database_rows(service.state)


@pytest.fixture(scope="module")
def actual_pipeline_and_replays(tmp_path_factory):
    root = tmp_path_factory.mktemp("actual-task-proof-controls")
    initialize(root, "a" * 40)
    service = TaskService(root)
    task = service.submit(service.freeze({**DRAFT, "kind": "engineering_pipeline"}), "source")[
        "task_id"
    ]
    assert service.work(task)["status"] == "SUCCEEDED"
    replay = service.submit(service.freeze({"kind": "replay", "source_task": task}), "replay")[
        "task_id"
    ]
    assert service.work(replay)["status"] == "SUCCEEDED"
    cancelled = service.submit(
        service.freeze({"kind": "replay", "source_task": task}), "cancelled-replay"
    )["task_id"]

    def cancel(point):
        if point == "COMPLETION_BEFORE_SQL":
            service.cancel(cancelled)

    assert TaskService(root, fault=cancel).work(cancelled)["status"] == "CANCELLED"
    return service, task, replay, cancelled


@contextmanager
def resealed_fault(binding, *, changes=None, extra=None):
    """Coherent hostile checksum update still cannot supply semantic authority."""
    root = Path(binding["physical_ledger_root"]) / binding["child_run_id"]
    originals = {
        p: p.read_bytes() for p in root.iterdir() if p.suffix in (".json", ".jsonl", ".html")
    }
    try:
        manifest = json.loads((root / "manifest.json").read_bytes())
        for name, mutate in (changes or {}).items():
            path = root / name
            value = json.loads(path.read_bytes())
            mutate(value)
            path.write_bytes(canonical(value))
        for name, value in (extra or {}).items():
            path = root / name
            assert path.parent == root and not path.exists()
            path.write_bytes(canonical(value))
            manifest["files"].append({"path": name, "sha256": ""})
        for entry in manifest["files"]:
            entry["sha256"] = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
        raw = canonical(manifest)
        (root / "manifest.json").write_bytes(raw)
        lines = (root / "events.jsonl").read_bytes().splitlines()
        terminal = json.loads(lines[-1])
        terminal["payload"]["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        terminal["hash"] = digest({k: v for k, v in terminal.items() if k != "hash"})
        (root / "events.jsonl").write_bytes(b"\n".join([*lines[:-1], canonical(terminal)]) + b"\n")
        yield
    finally:
        for path, raw in originals.items():
            path.write_bytes(raw)
        for name in extra or {}:
            (root / name).unlink()


@pytest.mark.parametrize(
    "damage", ["artifact-name", "unknown-with-cash", "replay-projection", "source-plan"]
)
def test_public_readers_reject_resealed_but_semantically_invalid_proofs(
    actual_pipeline_and_replays, damage
):
    service, task, replay, cancelled = actual_pipeline_and_replays
    original = original_files(service.root)
    if damage == "source-plan":
        path = service.root / "tasks" / task / "resolved-plan.json"
        raw = path.read_bytes()
        value = json.loads(raw)
        value["request_sha256"] = "0" * 64
        try:
            path.write_bytes(canonical(value))
            result = service.status(replay)
            assert result["status"] == "INTEGRITY_ERROR"
            assert result["error"] == "TASK_REPLAY_SELECTION_CHANGED"
        finally:
            path.write_bytes(raw)
    else:
        target, slot = (
            (cancelled, "E")
            if damage == "replay-projection"
            else (task, "R" if damage == "artifact-name" else "B")
        )
        binding = service.state.slots(target)[slot]["binding"]
        if damage == "artifact-name":
            with resealed_fault(binding, extra={"Unexpected.json": {"untrusted_name": True}}):
                result = service.status(task)
                assert (
                    result["status"] == "INTEGRITY_ERROR"
                    and result["error"] == "TASK_ARTIFACT_BOUNDARY"
                )
        elif damage == "unknown-with-cash":
            with resealed_fault(
                binding,
                changes={
                    "result.json": lambda x: x.update(
                        status="FAILED",
                        committed_state_verification={"financial_state_known": False},
                    )
                },
            ):
                with pytest.raises(ContractError, match="TASK_FINANCIAL_RESULT_UNKNOWN"):
                    service.financial_result(task)
        else:
            with resealed_fault(
                binding, changes={"result.json": lambda x: x.update(state_sha256="0" * 64)}
            ):
                result = service.status(cancelled)
                assert result["status"] == "INTEGRITY_ERROR"
                assert result["financial_verification_error"] == "TASK_FINANCIAL_RESULT_CHANGED"
    assert original_files(service.root) == original
    assert service.status(task)["status"] == service.status(replay)["status"] == "SUCCEEDED"
    assert service.status(cancelled)["status"] == "CANCELLED"


@pytest.mark.parametrize("conflicting", [False, True])
def test_completion_crash_recovery_reuses_only_exact_preexisting_epoch_receipt(
    tmp_path, conflicting
):
    initialize(tmp_path, "a" * 40)
    service = TaskService(tmp_path)
    task = service.submit(service.freeze({**DRAFT, "kind": "engineering_pipeline"}), "crash")[
        "task_id"
    ]

    def crash(point):
        if point == "COMPLETION_BEFORE_SQL":
            raise SystemExit("DECLARED_OWNER_CRASH_AFTER_DURABLE_COMPLETION")

    with pytest.raises(SystemExit, match="DECLARED_OWNER_CRASH"):
        TaskService(tmp_path, fault=crash).work(task)
    directory = tmp_path / "tasks" / task
    original = (directory / "completion.json").read_bytes()
    row = service.state.get(task)
    assert row["status"] == "RUNNING" and row["epoch"] == 1
    future = json.loads(original)
    future["claim_epoch"] = 2
    future["previous_completion_sha256"] = hashlib.sha256(original).hexdigest()
    if conflicting:
        future["financial_approval"] = "UNTRUSTED"
    future_path = directory / "completion-2.json"
    future_raw = canonical(future)
    future_path.write_bytes(future_raw)
    service.state.abandon(task, row["owner"], row["epoch"])
    result = service.work(task, recover=True)
    assert result["status"] == ("FAILED" if conflicting else "SUCCEEDED"), result
    if conflicting:
        assert result["error"] == "TASK_COMPLETION_CHANGED" and "result" not in result
    assert (directory / "completion.json").read_bytes() == original
    assert future_path.read_bytes() == future_raw
    with service.state.transaction() as c:
        history = service.state.budget.history(c)
    assert history["admitted_units"] == history["registered_trials"] == 1
    assert len([p for p in (tmp_path / "research-runs").iterdir() if p.is_dir()]) == 1
