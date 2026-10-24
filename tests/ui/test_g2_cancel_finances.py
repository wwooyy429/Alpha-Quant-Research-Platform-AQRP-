"""Real committed-prefix corruption at safe cancellation, including successful P5."""

import json
from pathlib import Path

import pytest

from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService

DRAFT = {
    "kind": "engineering_pipeline",
    "start": "2024-01-06",
    "end": "2024-01-06",
    "horizons": [1],
}


@pytest.mark.parametrize(
    "damage", ["none", "commit-bytes", "commit-missing", "initial-missing", "enumeration", "read"]
)
@pytest.mark.parametrize("replay", [False, True])
def test_completed_child_is_reverified_before_cancellation(tmp_path, monkeypatch, damage, replay):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    first = s.submit(s.freeze(DRAFT), "first")["task_id"]
    if replay:
        assert s.work(first)["status"] == "SUCCEEDED"
        task = s.submit(s.freeze({"kind": "replay", "source_task": first}), "replay")["task_id"]
    else:
        task = first
    mutations = []

    def fault(point):
        if point != "COMPLETION_BEFORE_SQL":
            return
        slot = s.state.slots(task)["E" if replay else "B"]["binding"]
        root = Path(slot["physical_ledger_root"]) / slot["child_run_id"] / "transactions"
        target = sorted(root.glob("commit-*.json"))[-1]
        # Parent's independently specified answer: buy9*100 +0.9 slippage +1 fee.
        assert s.financial_result(first)["account"]["cash_total"] == "98.1"
        if damage == "commit-bytes":
            target.write_bytes(target.read_bytes() + b" ")
        elif damage in ("commit-missing", "initial-missing"):
            (target if damage == "commit-missing" else root / "initial.json").unlink()
        elif damage == "enumeration":
            old = Path.iterdir

            def denied(path):
                if path == root:
                    raise PermissionError("actual transaction directory enumeration refused")
                return old(path)

            monkeypatch.setattr(Path, "iterdir", denied)
        elif damage == "read":
            old = Path.read_bytes

            def denied(path):
                if path == target:
                    raise OSError("actual committed file read refused")
                return old(path)

            monkeypatch.setattr(Path, "read_bytes", denied)
        mutations.append(str(target))
        assert s.cancel(task) == "CANCEL_REQUESTED"

    r = TaskService(tmp_path, fault=fault).work(task)
    assert len(mutations) == 1
    if damage == "none":
        assert r["status"] == "CANCELLED", r
    else:
        assert r["status"] == "FAILED" and r["error"] == "COMMITTED_STATE_UNVERIFIED", r
        end = s.logs(task)[-1]
        assert end["payload"]["cancellation_intent"]
        assert end["payload"]["financial_verification_error"]
        assert s.state.get(task)["cancel"] == 1
        assert "result" not in r


def test_cancelled_valid_prefix_later_corruption_is_visible_without_rewriting_history(tmp_path):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    task = s.submit(s.freeze(DRAFT), "cancelled")["task_id"]

    def cancel(point):
        if point == "COMPLETION_BEFORE_SQL":
            s.cancel(task)

    assert TaskService(tmp_path, fault=cancel).work(task)["status"] == "CANCELLED"
    b = s.state.slots(task)["B"]["binding"]
    root = Path(b["physical_ledger_root"]) / b["child_run_id"]
    path = sorted((root / "transactions").glob("commit-*.json"))[-1]
    path.write_bytes(path.read_bytes() + b" ")
    row = s.status(task)
    assert row["status"] == "INTEGRITY_ERROR" and row["usable"] is False
    assert row["original_terminal_status"] == "CANCELLED"
    assert s.state.get(task)["status"] == "CANCELLED"
    assert json.loads((root / "result.json").read_bytes())["account"]["cash_total"] == "98.1"
