"""Complete real history imports reject single-fault evidence without a new budget."""

import hashlib
import json
import sqlite3
import uuid
from pathlib import Path

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.services.task_requests import initialize
from aqrp.services.task_state import TaskState
from aqrp.services.tasks import TaskService

DRAFT = {"factor_ids": ["momentum"], "start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}
PIPELINE_CASES = {"required-p4", "plan-request", "plan-selection", "adapted-request"}
CASES = [
    "pointer-traversal",
    "pointer-absolute",
    "pointer-extra",
    "pointer-noncanonical",
    "completion-noncanonical",
    "completion-epoch",
    "proof-binding",
    "proof-manifest",
    "proof-status",
    "required-r",
    "completion-config",
    "completion-plan-hash",
    "task-epoch",
    "task-invalid-status",
    "coherent-epoch-forgery",
    "missing-claim",
    "duplicate-claim",
    "invalid-claim-owner",
    "missing-terminal-event",
    "noncanonical-event",
    "slot-task",
    "slot-workspace",
    "slot-request",
    "missing-campaign",
    "missing-submission",
    "duplicate-submission",
    "missing-request",
    "missing-trial",
    "missing-core",
    "defaults-hash",
    *sorted(PIPELINE_CASES),
]


def strip_control_schema(state):
    """Declared pre-control fixture; all original business rows and files remain."""
    with state.transaction() as c:
        names = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for name in names:
            if name.startswith(("admission_", "execution_plan")) or name in {
                "budget_domains",
                "admissions",
                "trial_claims",
                "legacy_execution_owners",
            }:
                c.execute('DROP TABLE "' + name + '"')
    state.budget.anchor.unlink()


def legacy_rows(state):
    with sqlite3.connect(state.db) as c:
        c.row_factory = sqlite3.Row
        return {
            name: [dict(r) for r in c.execute("SELECT * FROM " + name + " ORDER BY rowid")]
            for name in (
                "workspace",
                "tasks",
                "slots",
                "events",
                "campaign_attempts",
                "adapted_requests",
                "defaults",
            )
        }


def original_bytes(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and p.suffix in (".json", ".jsonl", ".html")
    }


@pytest.mark.parametrize("case", CASES)
def test_incomplete_or_changed_history_refuses_import_and_new_grant(tmp_path, case):
    root = tmp_path / "workspace"
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    initialize(root, "a" * 40)
    service = TaskService(root)
    if case == "defaults-hash":
        service.save_defaults(0, {"lookback": 2})
    kind = "engineering_pipeline" if case in PIPELINE_CASES else "research"
    task = service.submit(service.freeze({**DRAFT, "kind": kind}), "original")["task_id"]
    done = service.work(task)
    assert done["status"] == "SUCCEEDED", done
    (evidence / "ORIGINAL_SUCCEEDED_STATUS.json").write_bytes(canonical(done))
    original = original_bytes(root)
    (evidence / "ORIGINAL_FILE_HASHES.json").write_bytes(
        canonical({k: hashlib.sha256(v).hexdigest() for k, v in original.items()})
    )
    strip_control_schema(service.state)
    row = service.state.get(task)
    pointer = json.loads(row["completion"])
    completion_path = root / "tasks" / task / pointer["file"]
    completion_raw = completion_path.read_bytes()
    completion = json.loads(completion_raw)
    (evidence / "ORIGINAL_COMPLETION.json").write_bytes(completion_raw)
    reseal_completion = False
    with service.state.transaction() as c:
        if case in ("pointer-traversal", "pointer-absolute"):
            relocated = root / "relocated-original-completion.json"
            relocated.write_bytes(completion_raw)
            pointer["file"] = (
                "../../" + relocated.name if case == "pointer-traversal" else str(relocated)
            )
        elif case == "pointer-extra":
            pointer["unexpected"] = True
        elif case == "pointer-noncanonical":
            c.execute(
                "UPDATE tasks SET completion=? WHERE id=?", (json.dumps(pointer, indent=2), task)
            )
        elif case == "completion-noncanonical":
            completion_raw = json.dumps(completion, indent=2).encode()
            completion_path.write_bytes(completion_raw)
            pointer["sha256"] = hashlib.sha256(completion_raw).hexdigest()
        elif case == "completion-epoch":
            completion["claim_epoch"] += 1
            reseal_completion = True
        elif case.startswith("proof-"):
            field = {
                "proof-binding": "binding_hash",
                "proof-manifest": "manifest_hash",
                "proof-status": "status",
            }[case]
            completion["core_proofs"]["R"][field] = "FAILED" if field == "status" else "0" * 64
            reseal_completion = True
        elif case == "required-r":
            c.execute("DELETE FROM slots WHERE task=? AND slot='R'", (task,))
            del completion["core_proofs"]["R"]
            reseal_completion = True
        elif case == "completion-config":
            completion["config_hash"] = "0" * 64
            reseal_completion = True
        elif case == "completion-plan-hash":
            completion["resolved_plan_sha256"] = "0" * 64
            reseal_completion = True
        elif case == "task-epoch":
            c.execute("UPDATE tasks SET epoch=epoch+1 WHERE id=?", (task,))
        elif case == "coherent-epoch-forgery":
            c.execute("UPDATE tasks SET epoch=epoch+1 WHERE id=?", (task,))
            completion["claim_epoch"] += 1
            reseal_completion = True
        elif case == "missing-claim":
            c.execute("DELETE FROM events WHERE task=? AND kind='CLAIMED'", (task,))
        elif case == "duplicate-claim":
            payload = c.execute(
                "SELECT payload FROM events WHERE task=? AND kind='CLAIMED'", (task,)
            ).fetchone()[0]
            service.state.event(c, task, "CLAIMED", json.loads(payload))
        elif case == "invalid-claim-owner":
            payload = json.loads(
                c.execute(
                    "SELECT payload FROM events WHERE task=? AND kind='CLAIMED'", (task,)
                ).fetchone()[0]
            )
            payload["owner"] = "unverifiable-owner"
            c.execute(
                "UPDATE events SET payload=? WHERE task=? AND kind='CLAIMED'",
                (canonical(payload).decode(), task),
            )
        elif case == "missing-terminal-event":
            c.execute("DELETE FROM events WHERE task=? AND kind='SUCCEEDED'", (task,))
        elif case == "noncanonical-event":
            payload = c.execute(
                "SELECT payload FROM events WHERE task=? AND kind='CLAIMED'", (task,)
            ).fetchone()[0]
            c.execute(
                "UPDATE events SET payload=? WHERE task=? AND kind='CLAIMED'",
                (json.dumps(json.loads(payload), indent=2), task),
            )
        elif case == "task-invalid-status":
            c.execute("UPDATE tasks SET status='UNKNOWN_LEGACY_STATE' WHERE id=?", (task,))
        elif case.startswith("slot-"):
            binding = json.loads(
                c.execute(
                    "SELECT binding FROM slots WHERE task=? AND slot='R'", (task,)
                ).fetchone()[0]
            )
            field = {
                "slot-task": "task_id",
                "slot-workspace": "workspace_id",
                "slot-request": "plan_hash",
            }[case]
            binding[field] = "0" * 64 if field == "plan_hash" else str(uuid.uuid4())
            c.execute(
                "UPDATE slots SET binding=? WHERE task=? AND slot='R'",
                (canonical(binding).decode(), task),
            )
        elif case == "missing-campaign":
            c.execute("DELETE FROM campaign_attempts WHERE task=?", (task,))
        elif case == "missing-submission":
            c.execute("DELETE FROM events WHERE task=? AND kind='SUBMITTED'", (task,))
        elif case == "duplicate-submission":
            payload = c.execute(
                "SELECT payload FROM events WHERE task=? AND kind='SUBMITTED'", (task,)
            ).fetchone()[0]
            service.state.event(c, task, "SUBMITTED", json.loads(payload))
        elif case == "missing-request":
            (root / "tasks" / task / "request.json").unlink()
        elif case == "missing-trial":
            (root / "research-runs/trials.jsonl").unlink()
        elif case == "missing-core":
            b = done["slots"]["R"]["binding"]
            (Path(b["physical_ledger_root"]) / b["child_run_id"] / "metrics.json").unlink()
        elif case == "defaults-hash":
            c.execute("UPDATE defaults SET hash=?", ("0" * 64,))
        else:
            plan_path = root / "tasks" / task / "resolved-plan.json"
            plan = json.loads(plan_path.read_bytes())
            if case == "required-p4":
                c.execute("DELETE FROM slots WHERE task=? AND slot='P:0'", (task,))
                del completion["core_proofs"]["P:0"]
                del plan["slots"]["P:0"]
            elif case == "plan-request":
                plan["request_sha256"] = "0" * 64
            elif case == "plan-selection":
                plan["execution_selection"]["resolved"][0]["research_ordinal"] = 1
            else:
                c.execute("UPDATE adapted_requests SET hash=? WHERE task=?", ("0" * 64, task))
            plan_path.write_bytes(canonical(plan))
            completion["resolved_plan_sha256"] = hashlib.sha256(plan_path.read_bytes()).hexdigest()
            reseal_completion = True
        if reseal_completion:
            completion_path.write_bytes(canonical(completion))
            pointer["sha256"] = hashlib.sha256(completion_path.read_bytes()).hexdigest()
        if case != "pointer-noncanonical":
            c.execute(
                "UPDATE tasks SET completion=? WHERE id=?", (canonical(pointer).decode(), task)
            )
    changed_bytes, before_rows = original_bytes(root), legacy_rows(service.state)
    (evidence / "DECLARED_NEGATIVE.json").write_bytes(
        canonical(
            {"case": case, "expected": "ADMISSION_HISTORY_UNVERIFIED", "new_admission": False}
        )
    )
    (evidence / "BEFORE_LOGICAL_ROWS.json").write_bytes(canonical(before_rows))
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED") as error:
        TaskState(root)
    assert error.value.code == "ADMISSION_HISTORY_UNVERIFIED"
    assert not service.state.budget.anchor.exists()
    assert legacy_rows(service.state) == before_rows
    assert original_bytes(root) == changed_bytes
    with sqlite3.connect(service.state.db) as c:
        assert (
            c.execute("SELECT count(*) FROM sqlite_master WHERE name='admissions'").fetchone()[0]
            == 0
        )
    # Reopening through the public service cannot turn refusal into a fresh grant.
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        TaskService(root)
    assert legacy_rows(service.state) == before_rows
    (evidence / "AFTER_LOGICAL_ROWS.json").write_bytes(canonical(legacy_rows(service.state)))
    (evidence / "ACTUAL_REFUSAL.json").write_bytes(
        canonical(
            {
                "case": case,
                "code": error.value.code,
                "original_corrupt_bytes_preserved": True,
                "new_admission": False,
            }
        )
    )


@pytest.mark.parametrize(
    "target,damage",
    [("pipeline", None), ("replay-child", None)]
    + [
        (target, damage)
        for target in ("pipeline", "replay-child", "replay-source")
        for damage in ("bytes", "missing")
    ],
)
def test_cancelled_financial_history_uses_actual_durable_prefix_on_import(tmp_path, target, damage):
    root = tmp_path / "workspace"
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    initialize(root, "a" * 40)
    service = TaskService(root)
    task = service.submit(service.freeze({**DRAFT, "kind": "engineering_pipeline"}), "source")[
        "task_id"
    ]
    source = task
    if target != "pipeline":
        assert service.work(source)["status"] == "SUCCEEDED"
        task = service.submit(service.freeze({"kind": "replay", "source_task": source}), "replay")[
            "task_id"
        ]

    def cancel(point):
        if point == "COMPLETION_BEFORE_SQL":
            assert service.cancel(task) == "CANCEL_REQUESTED"

    cancelled = TaskService(root, fault=cancel).work(task)
    assert cancelled["status"] == "CANCELLED", cancelled
    (evidence / "ORIGINAL_CANCELLED_STATUS.json").write_bytes(canonical(cancelled))
    target_task = source if target == "replay-source" else task
    slot = "E" if target == "replay-child" else "B"
    binding = service.state.slots(target_task)[slot]["binding"]
    transactions = Path(binding["physical_ledger_root"]) / binding["child_run_id"] / "transactions"
    commit = sorted(transactions.glob("commit-*.json"))[-1]
    original = commit.read_bytes()
    (evidence / "ORIGINAL_COMMIT.json").write_bytes(original)
    if damage == "bytes":
        commit.write_bytes(original + b" ")
    elif damage == "missing":
        commit.unlink()
    live = service.status(task)
    assert live["status"] == ("CANCELLED" if damage is None else "INTEGRITY_ERROR")
    (evidence / "ACTUAL_LIVE_STATUS.json").write_bytes(canonical(live))
    strip_control_schema(service.state)
    before_bytes, before_rows = original_bytes(root), legacy_rows(service.state)
    if damage is None:
        TaskState(root)
        actual = TaskService(root).status(task)
        assert actual["status"] == "CANCELLED", actual
        with service.state.budget.transaction() as c:
            stats = service.state.budget.history(c)
        assert stats["admitted_units"] == 1 and stats["registered_trials"] == 1
        assert all((root / name).read_bytes() == raw for name, raw in before_bytes.items())
    else:
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
            TaskState(root)
        assert not service.state.budget.anchor.exists()
        assert legacy_rows(service.state) == before_rows
        assert original_bytes(root) == before_bytes
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
            TaskService(root)
        with sqlite3.connect(service.state.db) as c:
            assert (
                c.execute("SELECT count(*) FROM sqlite_master WHERE name='admissions'").fetchone()[
                    0
                ]
                == 0
            )
    (evidence / "ACTUAL_IMPORT_RESULT.json").write_bytes(
        canonical(
            {
                "target": target,
                "damage": damage,
                "new_admission": False,
                "expected_import": "VERIFIED_CANCELLED_PREFIX"
                if damage is None
                else "ADMISSION_HISTORY_UNVERIFIED",
                "original_committed_bytes_sha256": hashlib.sha256(original).hexdigest(),
            }
        )
    )
