"""G2-002: real FAILED parents retain independently verified physical finances."""

import hashlib
import json
import os
import sqlite3
from pathlib import Path

import pytest

from aqrp.backtest.engine import Simulator
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.services.task_requests import initialize
from aqrp.services.task_state import TaskState
from aqrp.services.tasks import TaskService, read_core

DRAFT = {
    "kind": "engineering_pipeline",
    "factor_ids": ["momentum"],
    "horizons": [1],
    "start": "2024-01-06",
    "end": "2024-01-06",
    "policy": {"top_k": 1},
}
BUSINESS = (
    "workspace",
    "tasks",
    "slots",
    "events",
    "campaign_attempts",
    "adapted_requests",
    "defaults",
)


def business_rows(state):
    with sqlite3.connect(state.db) as c:
        c.row_factory = sqlite3.Row
        return {
            name: [dict(r) for r in c.execute('SELECT * FROM "' + name + '" ORDER BY rowid')]
            for name in BUSINESS
        }


def original_files(root):
    result = {}

    def error(exc):
        raise exc

    for directory, _, names in os.walk(root, onerror=error, followlinks=False):
        for name in names:
            path = Path(directory) / name
            relative = path.relative_to(root)
            if relative.parts[0] != "task-control" and name != ".lock":
                assert not path.is_symlink() and not path.is_junction()
                result[relative.as_posix()] = path.read_bytes()
    return result


def strip_declared_controls(state):
    """Same-bundle pre-control fixture; preserve all seven original business tables."""
    with state.transaction() as c:
        names = [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for name in names:
            if name.startswith(("admission_", "execution_plan")) or name in {
                "budget_domains",
                "admissions",
                "trial_claims",
                "legacy_execution_owners",
            }:
                c.execute('DROP TABLE "' + name + '"')
    state.budget.anchor.unlink()


def migration_evidence(state):
    with state.transaction() as c:
        records = list(c.execute("SELECT payload FROM admission_events WHERE kind='MIGRATED'"))
    assert len(records) == 1
    return json.loads(records[0][0])["evidence"]


def assert_import_refused_unchanged(root, state, before_rows, before_files):
    for open_state in (TaskState, TaskService):
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED") as raised:
            open_state(root)
        assert raised.value.code == "ADMISSION_HISTORY_UNVERIFIED"
        assert not state.budget.anchor.exists()
        assert business_rows(state) == before_rows
        assert original_files(root) == before_files
        with sqlite3.connect(state.db) as c:
            assert (
                c.execute("SELECT count(*) FROM sqlite_master WHERE name='admissions'").fetchone()[
                    0
                ]
                == 0
            )


def assert_financial_files_remembered(evidence, binding, expected):
    prefix = Path(binding["physical_ledger_root"]) / binding["child_run_id"] / "transactions"
    rows = {Path(row["path"]): row for row in evidence["files"]}
    for relative, raw in expected.items():
        path = prefix / relative
        assert path in rows
        assert rows[path]["bytes"] == len(raw)
        assert rows[path]["sha256"] == hashlib.sha256(raw).hexdigest()


@pytest.mark.parametrize("target", ["risk-parent-B", "failed-replay-E", "failed-replay-source"])
@pytest.mark.parametrize("damage", [None, "bytes", "missing", "truncated", "initial-missing"])
def test_failed_parent_existing_financial_prefix_blocks_bad_history(tmp_path, target, damage):
    root, evidence = tmp_path / "workspace", tmp_path / "evidence"
    evidence.mkdir()
    initialize(root, "a" * 40)
    service = TaskService(root)
    draft = {**DRAFT, **({"constraints": {"gross_max": "0"}} if target == "risk-parent-B" else {})}
    source = service.submit(service.freeze(draft), "source")["task_id"]
    source_done = service.work(source)
    task = source
    if target == "risk-parent-B":
        assert (
            source_done["status"] == "FAILED" and source_done["error"] == "REQUIRED_STAGE_REJECTED"
        )
        result = service.financial_result(source)
        assert result["status"] == "SUCCEEDED" and result["fills"] == []
        assert result["account"]["cash_total"] == result["account"]["equity"] == "1000"
    else:
        assert source_done["status"] == "SUCCEEDED"
        task = service.submit(service.freeze({"kind": "replay", "source_task": source}), "replay")[
            "task_id"
        ]

        def after_success(point):
            if point == "COMPLETION_BEFORE_SQL":
                raise RuntimeError("DECLARED_FAILED_PARENT_AFTER_SUCCESSFUL_REPLAY")

        failed = TaskService(root, fault=after_success).work(task)
        assert failed["status"] == "FAILED" and failed["error"] == "RuntimeError"
    target_task = source if target != "failed-replay-E" else task
    slot = "E" if target == "failed-replay-E" else "B"
    binding = service.state.slots(target_task)[slot]["binding"]
    transactions = Path(binding["physical_ledger_root"]) / binding["child_run_id"] / "transactions"
    transaction_bytes = {
        p.name: p.read_bytes() for p in transactions.iterdir() if p.name != ".lock"
    }
    commit = sorted(transactions.glob("commit-*.json"))[-1]
    original = commit.read_bytes()
    (evidence / "ORIGINAL_COMMIT.json").write_bytes(original)
    (evidence / "ORIGINAL_PARENT_STATUS.json").write_bytes(canonical(service.status(task)))
    if damage == "bytes":
        commit.write_bytes(original + b" ")
    elif damage == "missing":
        commit.unlink()
    elif damage == "truncated":
        commit.write_bytes(original[:-1])
    elif damage == "initial-missing":
        (transactions / "initial.json").unlink()
    if damage is not None:
        if slot == "B":
            with pytest.raises((ContractError, OSError)):
                service.financial_result(target_task)
        else:
            with pytest.raises((ContractError, OSError)):
                TaskService._verified_financial_prefix(binding)
    strip_declared_controls(service.state)
    before_rows, before_files = business_rows(service.state), original_files(root)
    (evidence / "BEFORE_BUSINESS_ROWS.json").write_bytes(canonical(before_rows))
    if damage is not None:
        assert_import_refused_unchanged(root, service.state, before_rows, before_files)
    else:
        migrated = TaskState(root)
        assert business_rows(migrated) == before_rows and original_files(root) == before_files
        proof = migration_evidence(migrated)
        assert_financial_files_remembered(proof, binding, transaction_bytes)
        matching = [
            p for p in proof["financial_children"] if p["child_run_id"] == binding["child_run_id"]
        ]
        assert len(matching) == 1 and matching[0]["physical_prefix_verified"] is True
        assert matching[0]["original_opaque_unknown_failure"] is False
        after = TaskService(root)
        assert after.status(task)["status"] == "FAILED"
        with migrated.budget.transaction() as c:
            before = migrated.budget.history(c)
        assert before["admitted_units"] == before["registered_trials"] == 1
        new = after.submit(
            after.freeze(
                {
                    "factor_ids": ["momentum"],
                    "horizons": [1],
                    "start": "2024-01-06",
                    "end": "2024-01-06",
                }
            ),
            "after-verified-history",
        )
        assert new["status"] == "QUEUED"
        with migrated.budget.transaction() as c:
            assert migrated.budget.history(c)["admitted_units"] == 2
    (evidence / "RESULT.json").write_bytes(
        canonical(
            {
                "target": target,
                "damage": damage,
                "expected": "ADMISSION_HISTORY_UNVERIFIED"
                if damage
                else "ORIGINAL_FAILED_PARENT_PRESERVED_AND_PREFIX_VERIFIED",
                "developer_self_test_only": True,
            }
        )
    )


@pytest.mark.parametrize("opaque", [False, True])
def test_original_failed_financial_state_keeps_known_or_opaque_semantics(
    tmp_path, monkeypatch, opaque
):
    import aqrp.services.backtest as backtest

    root = tmp_path / "workspace"
    initialize(root, "a" * 40)

    class OriginalFailure(Simulator):
        def __init__(self, config, directory, commit, *, task_context=None):
            def fault(point):
                if point == "AFTER_COMMIT":
                    if opaque:
                        path = sorted((directory / "transactions").glob("commit-*.json"))[-1]
                        path.write_bytes(path.read_bytes() + b" ")
                    raise RuntimeError("DECLARED_ORIGINAL_ENGINE_FAILURE")

            super().__init__(config, directory, commit, task_context=task_context, fault=fault)

    monkeypatch.setattr(backtest, "Simulator", OriginalFailure)
    service = TaskService(root)
    task = service.submit(service.freeze(DRAFT), "original-failure")["task_id"]
    failed = service.work(task)
    assert failed["status"] == "FAILED"
    result = service.financial_result(task)
    assert result["status"] == "FAILED"
    if opaque:
        assert result["committed_state_verification"]["financial_state_known"] is False
        assert "account" not in result and "last_committed_account" not in result
    else:
        assert result["committed_state_verification"]["financial_state_known"] is True
        assert result["last_committed_account"]["cash_total"] == "1000"
    binding = service.state.slots(task)["B"]["binding"]
    transactions = Path(binding["physical_ledger_root"]) / binding["child_run_id"] / "transactions"
    original = {p.name: p.read_bytes() for p in transactions.iterdir() if p.name != ".lock"}
    strip_declared_controls(service.state)
    before_rows, before_files = business_rows(service.state), original_files(root)
    migrated = TaskState(root)
    assert business_rows(migrated) == before_rows and original_files(root) == before_files
    after = TaskService(root)
    assert after.status(task)["status"] == "FAILED" and after.financial_result(task) == result
    proof = migration_evidence(migrated)
    assert_financial_files_remembered(proof, binding, original)
    matching = [
        p for p in proof["financial_children"] if p["child_run_id"] == binding["child_run_id"]
    ]
    assert len(matching) == 1
    assert matching[0]["physical_prefix_verified"] is (not opaque)
    assert matching[0]["original_opaque_unknown_failure"] is opaque
    with migrated.budget.transaction() as c:
        stats = migrated.budget.history(c)
    assert stats["admitted_units"] == stats["registered_trials"] == 1


@pytest.mark.parametrize("damage", [None, "real-prefix", "cash", "last-committed-cash"])
def test_original_not_started_failure_is_retained_only_without_financial_claims(
    tmp_path, monkeypatch, damage
):
    import aqrp.services.backtest as backtest

    root = tmp_path / "workspace"
    initialize(root, "a" * 40)
    captured = {}

    class BeforeInitialization:
        def __init__(self, config, directory, commit, *, task_context=None):
            captured.update(config=config, directory=directory, commit=commit)
            raise RuntimeError("DECLARED_ENGINE_FAILURE_BEFORE_TRANSACTION_INITIALIZATION")

    monkeypatch.setattr(backtest, "Simulator", BeforeInitialization)
    service = TaskService(root)
    task = service.submit(service.freeze(DRAFT), "not-started")["task_id"]
    assert service.work(task)["status"] == "FAILED"
    binding = service.state.slots(task)["B"]["binding"]
    _, contents = read_core(binding)
    original = json.loads(contents["result.json"])
    assert original["status"] == "FAILED"
    assert original["committed_state_verification"] == {"status": "NOT_STARTED"}
    assert "account" not in original and "last_committed_account" not in original
    child = Path(binding["physical_ledger_root"]) / binding["child_run_id"]
    assert not (child / "transactions").exists()
    if damage == "real-prefix":
        # A real initial TransactionStore prefix appearing after NOT_STARTED
        # contradicts that frozen claim, even before its first committed event.
        Simulator(captured["config"], captured["directory"], captured["commit"])
        assert (child / "transactions/initial.json").is_file()
    elif damage is not None:
        field = "account" if damage == "cash" else "last_committed_account"
        altered = {**original, field: {"cash_total": "1000"}}
        (child / "result.json").write_bytes(canonical(altered))
        manifest = json.loads((child / "manifest.json").read_bytes())
        for item in manifest["files"]:
            item["sha256"] = hashlib.sha256((child / item["path"]).read_bytes()).hexdigest()
        manifest_raw = canonical(manifest)
        (child / "manifest.json").write_bytes(manifest_raw)
        lines = (child / "events.jsonl").read_bytes().splitlines()
        terminal = json.loads(lines[-1])
        terminal["payload"]["manifest_sha256"] = hashlib.sha256(manifest_raw).hexdigest()
        terminal["hash"] = digest({k: v for k, v in terminal.items() if k != "hash"})
        (child / "events.jsonl").write_bytes(b"\n".join([*lines[:-1], canonical(terminal)]) + b"\n")
        # The coherent artifact seal is not a financial authority certificate.
        assert json.loads(read_core(binding)[1]["result.json"])[field]["cash_total"] == "1000"
    strip_declared_controls(service.state)
    before_rows, before_files = business_rows(service.state), original_files(root)
    if damage is not None:
        assert_import_refused_unchanged(root, service.state, before_rows, before_files)
    else:
        migrated = TaskState(root)
        assert business_rows(migrated) == before_rows and original_files(root) == before_files
        proof = migration_evidence(migrated)
        matching = [
            p for p in proof["financial_children"] if p["child_run_id"] == binding["child_run_id"]
        ]
        assert len(matching) == 1
        assert matching[0]["original_not_started_failure"] is True
        assert matching[0]["physical_prefix_verified"] is False
        assert matching[0]["original_opaque_unknown_failure"] is False
        after = TaskService(root)
        assert after.status(task)["status"] == "FAILED"
        assert json.loads(read_core(binding)[1]["result.json"]) == original
        with pytest.raises(ContractError, match="TASK_TRANSACTION_FILES_MISSING"):
            after.financial_result(task)
        with migrated.budget.transaction() as c:
            assert migrated.budget.history(c)["admitted_units"] == 1
        new = after.submit(after.freeze({**DRAFT, "kind": "research"}), "after-not-started")
        assert new["status"] == "QUEUED"
        with migrated.budget.transaction() as c:
            assert migrated.budget.history(c)["admitted_units"] == 2
