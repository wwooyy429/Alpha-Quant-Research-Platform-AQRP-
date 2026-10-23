"""Actual P1/P3/nested-P4/P5 execution and post-publication negative controls."""

import json
import subprocess
import sys
import uuid

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger, read_chain
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService

SINGLE = {
    "kind": "engineering_pipeline",
    "factor_ids": ["momentum"],
    "start": "2024-01-06",
    "end": "2024-01-06",
    "horizons": [1],
}


@pytest.fixture(scope="module")
def completed(tmp_path_factory):
    root = tmp_path_factory.mktemp("real-task")
    initialize(root, "a" * 40)
    s = TaskService(root)
    task = s.submit(s.freeze(SINGLE), "known-answer")
    result = s.work(task["task_id"])
    assert result["status"] == "SUCCEEDED", result
    return s, result


def test_real_task_literal_cash_quantity_and_exact_ref(completed):
    s, r = completed
    assert set(r["slots"]) == {"R", "B", "P:0"}
    assert all(slot["state"] == "VERIFIED_SUCCESS" for slot in r["slots"].values())
    b = json.loads(s.artifact(r["task_id"], "B", "result.json"))
    # Independent arithmetic: buy9*100, slippage0.9, fee1; mark9*100.
    assert b["account"]["cash_total"] == "98.1"
    assert b["account"]["equity"] == "998.1"
    assert len(b["fills"]) == 1 and b["fills"][0]["signed_qty"] == "9"
    assert b["fills"][0]["direction"] == "LONG"
    lineage = json.loads(s.artifact(r["task_id"], "B", "portfolio-lineage.json"))
    assert lineage[0]["result"]["run_id"] == r["slots"]["P:0"]["binding"]["child_run_id"]
    assert s.work(r["task_id"])["result"] == r["result"]
    assert s.cancel(r["task_id"]) == "TOO_LATE"
    assert s.compare(r["task_id"], r["task_id"])["numeric_equal"]
    assert s.logs(r["task_id"])[-1]["kind"] == "SUCCEEDED"


@pytest.mark.parametrize(
    "name", ["../result.json", "result.json/../config.json", "x.py", "manifest.json", "late.json"]
)
def test_unmanifested_and_escaped_artifacts_refused(completed, name):
    s, r = completed
    with pytest.raises(ContractError):
        s.artifact(r["task_id"], "B", name)


def test_no_unknown_slot_or_unverified_comparison(completed):
    s, r = completed
    with pytest.raises(ContractError, match="UNKNOWN_TASK_SLOT"):
        s.artifact(r["task_id"], "unknown", "result.json")
    pending = s.submit(s.freeze({"kind": "research"}), "comparison-pending")
    with pytest.raises(ContractError, match="VERIFIED_SUCCESS_REQUIRED"):
        s.compare(r["task_id"], pending["task_id"])
    assert s.cancel(pending["task_id"]) == "CANCELLED"


@pytest.mark.parametrize("target", ["completion", "result", "transaction", "resolved-plan"])
def test_tampered_actual_bytes_never_remain_success(completed, target):
    s, r = completed
    row = s.state.get(r["task_id"])
    pointer = json.loads(row["completion"])
    paths = {
        "completion": s.root / "tasks" / r["task_id"] / pointer["file"],
        "resolved-plan": s.root / "tasks" / r["task_id"] / "resolved-plan.json",
    }
    binding = r["slots"]["B"]["binding"]
    root = ExperimentLedger(binding["physical_ledger_root"]).path(binding["child_run_id"])
    paths.update(
        result=root / "result.json", transaction=next((root / "transactions").glob("commit-*.json"))
    )
    path = paths[target]
    raw = path.read_bytes()
    try:
        path.write_bytes(raw + b" ")
        assert s.status(r["task_id"])["status"] == "INTEGRITY_ERROR"
        assert s.state.get(r["task_id"])["status"] == "SUCCEEDED"  # original record is retained
        assert any(x["status"] == "INTEGRITY_ERROR" for x in s.list())
    finally:
        path.write_bytes(raw)
    assert s.status(r["task_id"])["status"] == "SUCCEEDED"


@pytest.mark.parametrize(
    "field",
    [
        "workspace_id",
        "task_id",
        "plan_hash",
        "parent_execution_run_id",
        "physical_ledger_root",
        "adapted_request_hash",
        "source_request_hash",
        "decision_time_UTC",
    ],
)
def test_valid_uuid_and_wrong_parent_or_slot_identity_rejected(completed, field):
    s, r = completed
    task = r["task_id"]
    with s.state.transaction() as c:
        original = c.execute(
            "SELECT binding FROM slots WHERE task=? AND slot='P:0'", (task,)
        ).fetchone()[0]
    value = json.loads(original)
    value[field] = str(uuid.uuid4()) if field.endswith("id") else "wrong"
    try:
        with s.state.transaction() as c:
            c.execute(
                "UPDATE slots SET binding=? WHERE task=? AND slot='P:0'",
                (canonical(value).decode(), task),
            )
        assert s.status(task)["status"] == "INTEGRITY_ERROR"
    finally:
        with s.state.transaction() as c:
            c.execute("UPDATE slots SET binding=? WHERE task=? AND slot='P:0'", (original, task))


def test_unknown_directory_child_and_omitted_slot_fail_closed(completed):
    s, r = completed
    task = r["task_id"]
    b = r["slots"]["B"]["binding"]
    root = ExperimentLedger(b["physical_ledger_root"]).path(b["child_run_id"]) / "portfolio-runs"
    extra = root / str(uuid.uuid4())
    extra.mkdir()
    try:
        assert s.status(task)["status"] == "INTEGRITY_ERROR"
    finally:
        extra.rmdir()
    with s.state.transaction() as c:
        row = dict(c.execute("SELECT * FROM slots WHERE task=? AND slot='P:0'", (task,)).fetchone())
        c.execute("DELETE FROM slots WHERE task=? AND slot='P:0'", (task,))
    try:
        assert s.status(task)["status"] == "INTEGRITY_ERROR"
    finally:
        with s.state.transaction() as c:
            c.execute(
                "INSERT INTO slots VALUES (?,?,?,?)",
                (row["task"], row["slot"], row["binding"], row["state"]),
            )


def test_legitimate_risk_rejection_is_task_failure_with_original_p5_result(tmp_path):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    task = s.submit(s.freeze({**SINGLE, "constraints": {"gross_max": "0"}}), "risk-reject")
    result = s.work(task["task_id"])
    assert result["status"] == "FAILED" and result["error"] == "REQUIRED_STAGE_REJECTED"
    raw = json.loads(s.artifact(task["task_id"], "B", "result.json"))
    assert raw["status"] == "SUCCEEDED" and raw["fills"] == []
    assert raw["account"]["cash_total"] == "1000"
    child = json.loads(s.artifact(task["task_id"], "P:0", "result.json"))
    assert child["status"] == "REJECTED"


def test_real_numerical_replay_new_ownership_original_bytes_unchanged(completed):
    s, r = completed
    source = s.artifact(r["task_id"], "B", "result.json")
    task = s.submit(s.freeze({"kind": "replay", "source_task": r["task_id"]}), "actual-replay")
    result = s.work(task["task_id"])
    assert result["status"] == "SUCCEEDED", result
    assert result["result"]["replay"]["status"] == "NUMERICAL_REPLAY_VERIFIED"
    assert (
        result["slots"]["P:0"]["binding"]["parent_execution_run_id"]
        == result["slots"]["E"]["binding"]["child_run_id"]
    )
    assert (
        result["slots"]["P:0"]["binding"]["child_run_id"]
        != r["slots"]["P:0"]["binding"]["child_run_id"]
    )
    assert source == s.artifact(r["task_id"], "B", "result.json")
    assert s.compare(task["task_id"], r["task_id"])["numeric_equal"]
    from test_task_proofs import reseal

    binding = result["slots"]["E"]["binding"]
    with reseal(binding, changes={"comparison.json": lambda x: x.update(equal=False)}):
        with pytest.raises(ContractError, match="TASK_REPLAY_COMPARISON_CHANGED"):
            s._proofs(task["task_id"])


def test_single_research_core_success_does_not_complete_pipeline(tmp_path):
    initialize(tmp_path, "a" * 40)

    def stop(name):
        if name == "R_TERMINAL_BEFORE_MAPPING":
            raise RuntimeError("injected-boundary")

    s = TaskService(tmp_path, fault=stop)
    r = s.submit(s.freeze(SINGLE), "incomplete")
    actual = s.work(r["task_id"])
    assert actual["status"] == "FAILED" and "result" not in actual
    assert set(actual["slots"]) == {"R"}
    assert json.loads(s.artifact(r["task_id"], "R", "report.json"))["financial_approval"] == "NONE"


@pytest.mark.parametrize("boundary", ["R_TERMINAL_BEFORE_MAPPING", "COMPLETION_BEFORE_SQL"])
def test_real_process_crash_recovery_reuses_research_and_retains_receipts(tmp_path, boundary):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    t = s.submit(
        s.freeze({"kind": "research", "start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}),
        "crash",
    )
    script = "import os,sys; from aqrp.services.tasks import TaskService; s=TaskService(sys.argv[1],fault=lambda point: os._exit(73) if point==sys.argv[3] else None); s.work(sys.argv[2])"
    p = subprocess.run(
        [sys.executable, "-I", "-c", script, str(tmp_path), t["task_id"], boundary],
        capture_output=True,
        timeout=180,
    )
    (tmp_path / "crash.stdout.log").write_bytes(p.stdout)
    (tmp_path / "crash.stderr.log").write_bytes(p.stderr)
    assert p.returncode == 73
    row = s.state.get(t["task_id"])
    assert row["status"] == "RUNNING"
    before = s.state.slots(t["task_id"])["R"]["binding"]["child_run_id"]
    trial_count = len(read_chain(tmp_path / "research-runs/trials.jsonl"))
    # Explicit trusted release after the child has actually exited, never PID/mtime inference.
    s.state.abandon(t["task_id"], row["owner"], row["epoch"])
    result = s.work(t["task_id"], recover=True)
    assert result["status"] == "SUCCEEDED", result
    assert result["slots"]["R"]["binding"]["child_run_id"] == before
    assert len(read_chain(tmp_path / "research-runs/trials.jsonl")) == trial_count
    receipt = json.loads(s.state.get(t["task_id"])["completion"])
    if boundary == "COMPLETION_BEFORE_SQL":
        assert receipt["file"] == "completion-2.json"
        assert (tmp_path / "tasks" / t["task_id"] / "completion.json").exists()
