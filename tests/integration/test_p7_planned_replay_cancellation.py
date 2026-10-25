"""The planned zero-research cancellation retains the real original financial proof."""

import hashlib
import importlib.util
import json
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import (
    advance_actor,
    complete_actor,
    install_execution_plan,
    open_protocol_driver,
)
from aqrp.services.task_requests import catalogue, initialize
from aqrp.services.tasks import TaskService


def test_planned_queued_replay_cancel_rechecks_original_physical_source(tmp_path):
    initialize(tmp_path, "a" * 40)
    source_request = TaskService(tmp_path).freeze(
        {
            "kind": "engineering_pipeline",
            "start": "2024-01-06",
            "end": "2024-01-06",
            "horizons": [1],
        }
    )
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
        "purpose": "PLANNED_CANCEL_SOURCE_PHYSICAL_PROOF_REGRESSION_NOT_MAIN_E2E",
        "data_hash": cat["snapshot"]["manifest_hash"],
        "catalogue_hash": digest(cat),
        **identity,
        "slots": [
            {
                "slot_id": "source",
                "service_kind": "TASK",
                "request_hash": source_request.config_hash,
                "output_root": str(tmp_path / "research-runs"),
                "requested_units": 1,
                "grant_capacity": 1,
                "max_admitted_owners": 1,
                "expected_status": "SUCCEEDED",
            },
            {
                "slot_id": "cancel",
                "service_kind": "TASK_REPLAY",
                "source_slot": "source",
                "originalsource_request_hash": source_request.config_hash,
                "request_hash": None,
                "profile": "P5_NUMERICAL",
                "request_template": {
                    "schema": "task-request/1",
                    "kind": "replay",
                    "defaults_revision": 0,
                    "payload": {"source_task": "$SOURCE_TASK", "profile": "P5_NUMERICAL"},
                },
                "output_root": str(tmp_path / "replay-runs"),
                "requested_units": 0,
                "grant_capacity": 0,
                "max_admitted_owners": 1,
                "expected_status": "CANCELLED",
            },
        ],
    }
    # Freeze the actual request envelope spelling, including its schema field.
    template = json.loads(
        TaskService(tmp_path)
        .freeze(
            {
                "kind": "replay",
                "source_task": "a" * 8
                + "-"
                + "a" * 4
                + "-"
                + "a" * 4
                + "-"
                + "a" * 4
                + "-"
                + "a" * 12,
            }
        )
        .raw
    )
    template["payload"]["source_task"] = "$SOURCE_TASK"
    plan["slots"][1]["request_template"] = template
    fixed = install_execution_plan(tmp_path, plan, identity)
    driver = open_protocol_driver(tmp_path, fixed, identity)
    advance_actor(driver, -1)
    first = TaskService(tmp_path)
    task = first.submit(source_request, "source")["task_id"]
    result = first.work(task)
    assert result["status"] == "SUCCEEDED", result
    path = tmp_path / "tasks" / task / "request.json"
    complete_actor(
        driver,
        {
            "owner_id": task,
            "status": "SUCCEEDED",
            "evidence": [
                {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            ],
        },
    )
    advance_actor(driver, 0)
    second = TaskService(tmp_path)
    replay = second.submit(second.freeze({"kind": "replay", "source_task": task}), "cancel")[
        "task_id"
    ]
    assert second.state.slots(replay) == {}
    binding = first.state.slots(task)["B"]["binding"]
    transaction_root = (
        Path(binding["physical_ledger_root"]) / binding["child_run_id"] / "transactions"
    )
    target = sorted(transaction_root.glob("commit-*.json"))[-1]
    original = target.read_bytes()
    target.write_bytes(original + b" ")
    with pytest.raises(ContractError, match="TASK_CANCEL_SOURCE_UNVERIFIED"):
        second.cancel(replay)
    assert second.state.get(replay)["status"] == "QUEUED"
    assert target.read_bytes() == original + b" "
    target.write_bytes(original)
    assert second.cancel(replay) == "CANCELLED"
    assert second.status(replay)["status"] == "CANCELLED"
    target.write_bytes(original + b" ")
    public = second.status(replay)
    assert public["status"] == "INTEGRITY_ERROR" and public["usable"] is False
    assert public["financial_verification_error"] == "TASK_CANCEL_SOURCE_UNVERIFIED"
    assert second.state.get(replay)["status"] == "CANCELLED"
    target.write_bytes(original)
    assert second.status(replay)["status"] == "CANCELLED"
    assert not (tmp_path / "replay-runs").exists()


def test_cancelled_planned_replay_harness_requires_managed_idempotency_code(tmp_path, monkeypatch):
    """Real managed history; the evidence seam is headless, never a browser claim."""
    root, output = tmp_path / "workspace", tmp_path / "unit-protocol"
    initialize(root, "a" * 40)
    service = TaskService(root)
    common = {"start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}
    service.register_campaign(
        "cancel-harness",
        [{**common, "factor_ids": [factor]} for factor in ("momentum", "reversal")],
    )
    requests = [
        service.freeze(
            {
                **common,
                "kind": "engineering_pipeline",
                "factor_ids": [factor],
                "campaign_id": "cancel-harness",
            }
        )
        for factor in ("momentum", "reversal")
    ]
    research = service.freeze({**common, "campaign_id": "cancel-harness"})
    requests.extend([research] * 10)
    cat = catalogue(root)
    runner = Path(__file__).resolve()
    identity = {
        "runner_path": str(runner),
        "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }
    replay_template = json.loads(
        service.freeze(
            {"kind": "replay", "source_task": "00000000-0000-0000-0000-000000000001"}
        ).raw
    )
    replay_template["payload"]["source_task"] = "$SOURCE_TASK"
    slots = [
        {
            "slot_id": "source" if i == 0 else "actual-research-" + str(i),
            "service_kind": "TASK",
            "request_hash": request.config_hash,
            "output_root": str(root / "research-runs"),
            "requested_units": 1,
            "grant_capacity": 1,
            "max_admitted_owners": 1,
            "expected_status": "SUCCEEDED",
        }
        for i, request in enumerate(requests)
    ]
    slots.append(
        {
            "slot_id": "browser-cancel-replay",
            "service_kind": "TASK_REPLAY",
            "source_slot": "source",
            "originalsource_request_hash": requests[0].config_hash,
            "request_hash": None,
            "profile": "P5_NUMERICAL",
            "request_template": replay_template,
            "output_root": str(root / "replay-runs"),
            "requested_units": 0,
            "grant_capacity": 0,
            "max_admitted_owners": 1,
            "expected_status": "CANCELLED",
        }
    )
    plan_hash = install_execution_plan(
        root,
        {
            "schema": "p7-execution-plan/1",
            "purpose": "CANCELLED_REPLAY_HARNESS_UNIT_REGRESSION_NOT_REAL_BROWSER_OR_MAIN_E2E",
            "data_hash": cat["snapshot"]["manifest_hash"],
            "catalogue_hash": digest(cat),
            **identity,
            "slots": slots,
        },
        identity,
    )
    authority = open_protocol_driver(root, plan_hash, identity)
    completed = []
    for i, request in enumerate(requests):
        advance_actor(authority, i - 1)
        current = TaskService(root)
        task = current.submit(request, "actual-" + str(i))["task_id"]
        row = current.work(task)
        assert row["status"] == "SUCCEEDED", row
        completed.append(row)
        path = root / "tasks" / task / "request.json"
        complete_actor(
            authority,
            {
                "owner_id": task,
                "status": "SUCCEEDED",
                "evidence": [
                    {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                ],
            },
        )
    # Execute the candidate runner branch itself, using actual services and history.
    # Only the GUI evidence seam and the test's already trusted driver are supplied.
    tools = Path(__file__).resolve().parents[2] / "tools"
    monkeypatch.syspath_prepend(str(tools))
    spec = importlib.util.spec_from_file_location(
        "p7_cancelled_replay_harness_regression", tools / "e2e_smoke.py"
    )
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    monkeypatch.setattr(harness, "driver", lambda *_: authority)
    monkeypatch.setattr(
        harness,
        "browser_evidence",
        lambda _path, slot, task, _root: {
            "type": "HEADLESS_UNIT_ONLY_NOT_REAL_BROWSER",
            "slot_id": slot,
            "task_id": task,
        },
    )
    metadata = {"main": {"workspace": str(root)}}
    harness.save(output / "actors/sdk-main-momentum.json", {"task": completed[0]})
    harness.save(output / "actors/sdk-main-reversal.json", {"task": completed[1]})
    queued = harness.enqueue_cancel(output, metadata)
    replay = queued["task_id"]
    current = TaskService(root)
    assert current.cancel(replay) == "CANCELLED"
    assert current.status(replay)["slots"] == {}

    def immutable_state():
        # WAL/SHM coordination bytes are transient, not financial/authority payloads.
        files = {
            p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*")
            if p.is_file() and not p.name.endswith(("-wal", "-shm"))
        }
        with closing(
            sqlite3.connect(
                "file:" + (root / "task-control/tasks.sqlite").as_posix() + "?mode=ro", uri=True
            )
        ) as connection:
            names = [
                row[0]
                for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            ]
            tables = {
                name: sorted(
                    connection.execute('SELECT * FROM "' + name + '"').fetchall(), key=repr
                )
                for name in names
            }
        return files, tables

    before = immutable_state()
    before_counts = harness.counts(root)
    assert before_counts["admitted_units"] == before_counts["trials"] == 12
    original = current.submit(
        current.freeze({"kind": "replay", "source_task": completed[0]["task_id"]}),
        "p7-browser-cancel-replay-01",
    )
    assert original["task_id"] == replay and original["status"] == "CANCELLED"
    with pytest.raises(ContractError) as raised:
        current.submit(
            current.freeze({"kind": "replay", "source_task": completed[1]["task_id"]}),
            "p7-browser-cancel-replay-01",
        )
    # Frozen G1 COMMON_BUDGET_ADMISSION_DESIGN §3.3 and BUD-012, not product output.
    assert raised.value.code == "ADMISSION_IDEMPOTENCY_CONFLICT"
    assert immutable_state() == before
    assert harness.counts(root) == before_counts
    assert not (root / "replay-runs").exists()
    original_finish = harness.finish

    def finish_after_unchanged_conflict(*args, **kwargs):
        # Completion may append its legitimate receipt only AFTER this invariant.
        assert immutable_state() == before
        return original_finish(*args, **kwargs)

    monkeypatch.setattr(harness, "finish", finish_after_unchanged_conflict)
    result = harness.complete_browser(output, metadata, "main", output / "headless-unit.json")
    assert result["task_id"] == replay and result["status"] == "CANCELLED"
    control = json.loads((output / "controls/cancel-replay-different-request.json").read_bytes())
    assert control["rejected"] == "ADMISSION_IDEMPOTENCY_CONFLICT"
    assert control["before"] == control["after"] == before_counts
    assert not (root / "replay-runs").exists()
