"""Real processes and transaction-boundary fault injection; core computations remain real."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from crash_support import CHILD_CRASH_SUPPORT, assert_crash_marker

from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import read_chain
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService

DRAFT = {
    "kind": "engineering_pipeline",
    "start": "2024-01-06",
    "end": "2024-01-06",
    "horizons": [1],
}


def run_child(tmp_path, source, *args):
    p = subprocess.run(
        [sys.executable, "-I", "-c", source, str(tmp_path), *args], capture_output=True, timeout=240
    )
    (tmp_path / "child.stdout.log").write_bytes(p.stdout)
    (tmp_path / "child.stderr.log").write_bytes(p.stderr)
    return p


@pytest.mark.parametrize("boundary", ["BOUND", "P4_TERMINAL", "P4_PARTIAL"])
def test_real_process_nested_p4_crash_resume_never_constructs_second_child(tmp_path, boundary):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    t = s.submit(s.freeze(DRAFT), "p4-crash")["task_id"]
    script = (
        CHILD_CRASH_SUPPORT
        + """
import os,sys
import aqrp.backtest.engine as engine
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.services.tasks import TaskService
boundary=sys.argv[3]
old=engine.construct_engineering
def wrapped(*a,**k):
    if boundary=='BOUND': hard_exit(74, boundary)
    r=old(*a,**k)
    if boundary=='P4_TERMINAL': hard_exit(74, boundary)
    return r
engine.construct_engineering=wrapped
finish=ExperimentLedger.finish
def partial(self,run,status):
    import json
    line=json.loads((self.path(run)/'lineage.json').read_bytes())
    if boundary=='P4_PARTIAL' and line.get('task_binding',{}).get('service_kind')=='P4': hard_exit(74, boundary)
    return finish(self,run,status)
ExperimentLedger.finish=partial
TaskService(sys.argv[1]).work(sys.argv[2])
"""
    )
    p = run_child(tmp_path, script, t, boundary)
    assert p.returncode == 74, p.stderr.decode(errors="replace")
    assert_crash_marker(tmp_path, t, boundary, 74)
    row = s.state.get(t)
    slots = s.state.slots(t)
    child = slots["P:0"]["binding"]
    run = child["child_run_id"]
    assert slots["P:0"]["state"] in ("BOUND", "START_INTENT")
    with s.state.transaction() as c:
        adapted = c.execute("SELECT raw,hash FROM adapted_requests WHERE task=?", (t,)).fetchone()
    assert adapted is not None
    s.state.abandon(t, row["owner"], row["epoch"])
    result = s.work(t, recover=True)
    assert result["slots"]["P:0"]["binding"]["child_run_id"] == run
    children = list(Path(child["physical_ledger_root"]).iterdir())
    assert [p.name for p in children] == [run]
    if boundary == "P4_PARTIAL":
        assert result["status"] == "FAILED" and result["error"] == "TASK_BACKTEST_FAILED"
        original = json.loads(s.artifact(t, "B", "result.json"))
        assert original["reasons"] == ["RECOVERY_REQUIRED"]
    else:
        assert result["status"] == "SUCCEEDED", result
        assert result["slots"]["P:0"]["state"] == "VERIFIED_SUCCESS"
        if boundary == "P4_TERMINAL":
            events = read_chain(Path(child["physical_ledger_root"]) / run / "events.jsonl")
            assert sum(e["kind"] == "SUCCEEDED" for e in events) == 1


@pytest.mark.parametrize(
    "boundary", ["R_TERMINAL_BEFORE_MAPPING", "PLAN_FROZEN_BEFORE_B", "COMPLETION_BEFORE_SQL"]
)
def test_cancel_at_real_stage_and_completion_boundary_cannot_publish_success(tmp_path, boundary):
    initialize(tmp_path, "a" * 40)
    base = TaskService(tmp_path)
    t = base.submit(base.freeze(DRAFT), "cancel-boundary")["task_id"]
    accepted = []

    def cancel(point):
        if point == boundary:
            accepted.append(base.cancel(t))

    actual = TaskService(tmp_path, fault=cancel).work(t)
    assert accepted == ["CANCEL_REQUESTED"]
    assert actual["status"] == "CANCELLED" and "result" not in actual
    if boundary == "COMPLETION_BEFORE_SQL":
        assert (tmp_path / "tasks" / t / "completion.json").exists()
        assert json.loads(base.artifact(t, "B", "result.json"))["account"]["cash_total"] == "98.1"


@pytest.mark.parametrize("corrupt", [False, True])
def test_post_commit_cancellation_uses_durable_cash_or_fails_unknown(
    tmp_path, monkeypatch, corrupt
):
    from aqrp.backtest.engine import Simulator

    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    t = s.submit(s.freeze(DRAFT), "post-match-cancel")["task_id"]
    old = Simulator._commit
    observed = []

    def commit(self, kind, *a, **k):
        result = old(self, kind, *a, **k)
        if kind == "MATCH":
            observed.append(s.cancel(t))
            if corrupt:
                path = next((self.root / "transactions").glob("commit-*.json"))
                path.write_bytes(path.read_bytes() + b" ")
        return result

    monkeypatch.setattr(Simulator, "_commit", commit)
    actual = s.work(t)
    assert observed == ["CANCEL_REQUESTED"]
    b = json.loads(s.artifact(t, "B", "result.json"))
    assert s.financial_result(t) == b
    if corrupt:
        assert actual["status"] == "FAILED"
        assert actual["error"] == "COMMITTED_STATE_UNVERIFIED"
        assert b["committed_state_verification"]["financial_state_known"] is False
        assert "account" not in b and "last_committed_account" not in b
    else:
        assert actual["status"] == "CANCELLED"
        assert b["committed_state_verification"]["financial_state_known"] is True
        assert b["last_committed_account"]["cash_total"] == "98.1"


def test_ten_real_workers_execute_exactly_one_research_run(tmp_path):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    t = s.submit(s.freeze({**DRAFT, "kind": "research"}), "ten-workers")["task_id"]
    script = """
import json,sys
from aqrp.services.tasks import TaskService
from aqrp.core.errors import ContractError
try: print(json.dumps(TaskService(sys.argv[1]).work(sys.argv[2])))
except ContractError as e: print(json.dumps({'code':e.code}))
"""
    procs = [
        subprocess.Popen(
            [sys.executable, "-I", "-c", script, str(tmp_path), t],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(10)
    ]
    results = []
    for i, p in enumerate(procs):
        out, err = p.communicate(timeout=240)
        (tmp_path / f"worker-{i}.stdout.log").write_bytes(out)
        (tmp_path / f"worker-{i}.stderr.log").write_bytes(err)
        assert p.returncode == 0, err.decode(errors="replace")
        results.append(json.loads(out))
    assert any(r.get("status") == "SUCCEEDED" for r in results)
    assert all(
        r.get("status") == "SUCCEEDED" or r.get("code") == "TASK_ALREADY_CLAIMED" for r in results
    )
    assert s.status(t)["status"] == "SUCCEEDED"
    runs = [p for p in (tmp_path / "research-runs").iterdir() if p.is_dir()]
    assert len(runs) == 1
    claims = [e for e in s.logs(t) if e["kind"] == "CLAIMED"]
    assert len(claims) == 1


def test_same_config_new_task_uses_shared_family_and_retains_duplicate_trial(tmp_path):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    frozen = s.freeze({**DRAFT, "kind": "research"})
    runs = []
    tasks = []
    for key in ("trial-a", "trial-b"):
        task = s.submit(frozen, key)
        row = s.work(task["task_id"])
        assert row["status"] == "SUCCEEDED", row
        runs.append(row["result"]["research_run_id"])
        tasks.append(row["task_id"])
    assert len(set(runs)) == 2
    assert s.compare(*tasks)["numeric_equal"]
    trials = read_chain(tmp_path / "research-runs/trials.jsonl")
    assert len(trials) == 2
    assert trials[0]["payload"]["family"] == trials[1]["payload"]["family"]
    assert trials[1]["payload"]["repeat_of"] == [runs[0]]
    assert trials[1]["payload"]["prior_data_attempts"] == 1


def test_replay_defaults_are_ignored_and_source_must_be_verified_pipeline(tmp_path):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    t = s.submit(s.freeze({**DRAFT, "kind": "research"}), "research-only")
    r = s.work(t["task_id"])
    assert r["status"] == "SUCCEEDED"
    s.save_defaults(0, {"factor_ids": ["reversal"], "lookback": 3})
    replay = s.submit(s.freeze({"kind": "replay", "source_task": t["task_id"]}), "not-pipeline")
    actual = s.work(replay["task_id"])
    assert actual["status"] == "FAILED" and actual["error"] == "VERIFIED_PIPELINE_SOURCE_REQUIRED"
    with pytest.raises(ContractError, match="REPLAY_REQUIRES_EXPLICIT_SOURCE"):
        s.save_defaults(1, {"kind": "replay", "source_task": t["task_id"]})


def test_stale_worker_cannot_commit_or_append_failure_for_new_owner(tmp_path):
    initialize(tmp_path, "a" * 40)
    base = TaskService(tmp_path)
    t = base.submit(base.freeze({**DRAFT, "kind": "research"}), "stale-completion")["task_id"]

    def replace(point):
        if point == "COMPLETION_BEFORE_SQL":
            row = base.state.get(t)
            base.state.abandon(t, row["owner"], row["epoch"])
            base.state.claim(t, recover=True)

    result = TaskService(tmp_path, fault=replace).work(t)
    assert result["status"] == "RUNNING" and result["error"] is None
    assert base.logs(t)[-1]["kind"] == "CLAIMED"
    row = base.state.get(t)
    base.state.abandon(t, row["owner"], row["epoch"])
    done = base.work(t, recover=True)
    assert done["status"] == "SUCCEEDED", done
    assert base.cancel(t) == "TOO_LATE"


def test_real_process_b_terminal_before_mapping_reuses_same_run(tmp_path):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    t = s.submit(s.freeze(DRAFT), "b-terminal-crash")["task_id"]
    script = (
        CHILD_CRASH_SUPPORT
        + "from aqrp.services.tasks import TaskService; TaskService(sys.argv[1],fault=lambda p:hard_exit(75, p) if p=='B_TERMINAL_BEFORE_MAPPING' else None).work(sys.argv[2])"
    )
    p = run_child(tmp_path, script, t)
    assert p.returncode == 75, p.stderr.decode(errors="replace")
    assert_crash_marker(tmp_path, t, "B_TERMINAL_BEFORE_MAPPING", 75)
    row = s.state.get(t)
    before = s.state.slots(t)
    b = before["B"]["binding"]
    root = Path(b["physical_ledger_root"]) / b["child_run_id"]
    files = {p.name: p.read_bytes() for p in root.iterdir() if p.suffix in (".json", ".jsonl")}
    s.state.abandon(t, row["owner"], row["epoch"])
    actual = s.work(t, recover=True)
    assert actual["status"] == "SUCCEEDED", actual
    assert actual["slots"]["B"]["binding"]["child_run_id"] == b["child_run_id"]
    assert all((root / n).read_bytes() == raw for n, raw in files.items())


def test_preexisting_corrupt_completion_is_retained_and_refused(tmp_path):
    initialize(tmp_path, "a" * 40)
    base = TaskService(tmp_path)
    t = base.submit(base.freeze({**DRAFT, "kind": "research"}), "bad-completion")["task_id"]
    path = tmp_path / "tasks" / t / "completion.json"
    raw = b'{"claim_epoch":1,"not_the_frozen_completion":true}'

    def corrupt(point):
        if point == "BEFORE_COMPLETION":
            path.write_bytes(raw)

    actual = TaskService(tmp_path, fault=corrupt).work(t)
    assert actual["status"] == "FAILED" and actual["error"] == "TASK_COMPLETION_CHANGED"
    assert path.read_bytes() == raw


@pytest.mark.parametrize("cause", ["raw-corrupt", "false-flag"])
def test_cancel_after_terminal_b_rechecks_all_original_financial_evidence(tmp_path, cause):
    from contextlib import ExitStack

    from test_task_proofs import reseal

    initialize(tmp_path, "a" * 40)
    base = TaskService(tmp_path)
    t = base.submit(base.freeze(DRAFT), "terminal-cancel-unknown")["task_id"]
    originals = []
    with ExitStack() as stack:

        def cancel(point):
            if point == "B_TERMINAL_BEFORE_MAPPING":
                b = base.state.slots(t)["B"]["binding"]
                if cause == "false-flag":
                    stack.enter_context(
                        reseal(
                            b,
                            changes={
                                "result.json": lambda x: x.update(
                                    committed_state_verification={"financial_state_known": False}
                                )
                            },
                        )
                    )
                else:
                    path = Path(b["physical_ledger_root"]) / b["child_run_id"] / "result.json"
                    originals.append((path, path.read_bytes()))
                    path.write_bytes(path.read_bytes() + b" ")
                base.cancel(t)
                raise KeyboardInterrupt("injected-after-terminal")

        try:
            actual = TaskService(tmp_path, fault=cancel).work(t)
            assert actual["status"] == "FAILED" and actual["error"] == "COMMITTED_STATE_UNVERIFIED"
        finally:
            for path, raw in originals:
                path.write_bytes(raw)
