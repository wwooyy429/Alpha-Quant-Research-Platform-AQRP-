"""G2-001 literal service-boundary answers, including captured post-commit faults."""

import json
import subprocess
import sys
from copy import deepcopy

import pytest

from aqrp.backtest.engine import Simulator
from aqrp.backtest.exact import F, freeze, present, thaw
from aqrp.backtest.ledger import account
from aqrp.backtest.synthetic import fixture_request
from aqrp.backtest.transactions import TransactionStore
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
@pytest.mark.parametrize("exc_type", [KeyboardInterrupt, ContractError, RuntimeError])
def test_caught_service_fault_reports_actual_durable_fill_prefix(
    tmp_path, monkeypatch, stage, exc_type
):
    import aqrp.services.backtest as service

    class BoundarySimulator(Simulator):
        def __init__(self, config, root, commit):
            def fault(current):
                if current != stage:
                    return
                pattern = "prepared-*.json" if current == "BEFORE_COMMIT" else "commit-*.json"
                for path in (root / "transactions").glob(pattern):
                    if any(x["kind"] == "Fill" for x in json.loads(path.read_bytes())["children"]):
                        raise exc_type("G2_LITERAL_COMMIT_BOUNDARY")

            super().__init__(config, root, commit, fault=fault)

    monkeypatch.setattr(service, "Simulator", BoundarySimulator)
    request = fixture_request()
    (tmp_path / "original-request.json").write_bytes(request.raw)
    root = tmp_path / "runs"
    if exc_type is RuntimeError:
        with pytest.raises(RuntimeError, match="G2_LITERAL_COMMIT_BOUNDARY"):
            service.simulate_engineering(request, root, "a" * 40)
        run = next(p for p in root.iterdir() if p.is_dir())
        result = service.result_engineering(root, run.name)
    else:
        returned = service.simulate_engineering(request, root, "a" * 40)
        (tmp_path / "actual-return.json").write_bytes(returned.raw)
        result = returned.read()
        run = root / result["run_id"]
        assert service.result_engineering(root, run.name) == {
            k: v for k, v in result.items() if k != "manifest"
        }
    expected_status = "CANCELLED" if exc_type is KeyboardInterrupt else "FAILED"
    assert result["status"] == expected_status
    # Predeclared arithmetic: 1000 - 9*100.1 - 1 = 98.1. No tested function supplies it.
    after = stage == "AFTER_COMMIT"
    expected_cash, count = ("98.1", 9) if after else ("1000", 8)
    assert result["last_committed_account"]["cash_total"] == expected_cash
    assert result["committed_state_verification"]["status"] == "VERIFIED_COMMITTED_PREFIX"
    disk = TransactionStore(run / "transactions")
    state = thaw(json.loads((run / "failed-state.json").read_bytes()))
    assert state == disk.state
    assert json.loads((run / "transactions.json").read_bytes()) == disk.records
    assert len(disk.records) == count
    assert len(state["fills"]) == int(after) and state["fees"] == int(after)
    assert state["assets"]["SYNTH:0"]["quantity"] == (9 if after else 0)
    assert present(account(state)) == result["last_committed_account"]
    assert account(state)["cash_total"] == F(expected_cash)
    # Two observed positive opening slices start at ten shares each; this map is remaining capacity.
    assert sum(state["capacity"].values()) == (11 if after else 20)
    assert result["committed_state_verification"]["commit_count"] == count
    assert result["committed_state_verification"]["state_sha256"] == digest(freeze(state))
    assert len(json.loads((run / "committed-trace.json").read_bytes())) == count
    ledger = ExperimentLedger(root)
    assert ledger.verify(run.name)["status"] == expected_status
    before = {p.name: p.read_bytes() for p in (run / "transactions").iterdir() if p.name != ".lock"}
    with pytest.raises(ContractError, match="NONRUNNING_SIMULATION_CANNOT_RESUME"):
        service.resume_engineering(root, run.name)
    assert before == {
        p.name: p.read_bytes() for p in (run / "transactions").iterdir() if p.name != ".lock"
    }


@pytest.mark.parametrize("damage", ["chain", "read_error", "economic_state"])
def test_uncertain_durable_state_never_claims_cached_balance(tmp_path, monkeypatch, damage):
    import aqrp.services.backtest as service

    faulted = False
    original_recover = TransactionStore.recover

    def recover(store):
        if faulted and damage == "read_error":
            raise PermissionError("G2_READ_DENIED")
        return original_recover(store)

    monkeypatch.setattr(TransactionStore, "recover", recover)

    class BoundarySimulator(Simulator):
        def __init__(self, config, root, commit):
            def fault(current):
                nonlocal faulted
                if current != "AFTER_COMMIT":
                    return
                paths = sorted((root / "transactions").glob("commit-*.json"))
                path = paths[-1]
                item = json.loads(path.read_bytes())
                if not any(x["kind"] == "Fill" for x in item["children"]):
                    return
                (tmp_path / "original-valid-commit.json").write_bytes(path.read_bytes())
                if damage == "chain":
                    item["post_hash"] = "0" * 64
                    path.write_bytes(canonical(item))
                if damage == "economic_state":
                    changed = thaw(deepcopy(item["post_state"]))
                    changed["cash_set"] += 1
                    item["post_state"] = freeze(changed)
                    item["post_hash"] = digest(item["post_state"])
                    item["sha256"] = digest({k: v for k, v in item.items() if k != "sha256"})
                    path.write_bytes(canonical(item))
                faulted = True
                raise ContractError("G2_CAPTURED_FAULT")

            super().__init__(config, root, commit, fault=fault)

    monkeypatch.setattr(service, "Simulator", BoundarySimulator)
    root = tmp_path / "runs"
    result = service.simulate_engineering(fixture_request(), root, "a" * 40).read()
    run = root / result["run_id"]
    assert result["status"] == "FAILED"
    assert "last_committed_account" not in result
    assert result["committed_state_verification"]["status"] == "UNVERIFIED_COMMITTED_STATE"
    assert "COMMITTED_STATE_UNVERIFIED" in result["reasons"]
    assert not (run / "failed-state.json").exists()
    assert not (run / "transactions.json").exists()
    assert (run / "transactions/commit-000000000009.json").exists()
    assert (run / "failure-recovery.json").exists()
    assert ExperimentLedger(root).verify(run.name)["status"] == "FAILED"


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_real_service_process_exit_resumes_original_run_without_double_execution(tmp_path, stage):
    import aqrp.services.backtest as service

    script = tmp_path / "exit_at_commit.py"
    script.write_text(
        """import json,os,sys
from pathlib import Path
from aqrp.backtest.engine import Simulator
from aqrp.backtest.synthetic import fixture_request
import aqrp.services.backtest as service
class ExitSimulator(Simulator):
 def __init__(self,config,root,commit):
  def fault(current):
   if current!=sys.argv[2]:return
   pattern='prepared-*.json' if current=='BEFORE_COMMIT' else 'commit-*.json'
   for path in (root/'transactions').glob(pattern):
    if any(c['kind']=='Fill' for c in json.loads(path.read_bytes())['children']):os._exit(74)
  super().__init__(config,root,commit,fault=fault)
service.Simulator=ExitSimulator
service.simulate_engineering(fixture_request(),Path(sys.argv[1]),'a'*40)
""",
        encoding="utf-8",
    )
    root = tmp_path / "runs"
    cp = subprocess.run([sys.executable, str(script), str(root), stage], capture_output=True)
    (tmp_path / "child.stdout.log").write_bytes(cp.stdout)
    (tmp_path / "child.stderr.log").write_bytes(cp.stderr)
    assert cp.returncode == 74
    run_id = next(p.name for p in root.iterdir() if p.is_dir())
    assert not (root / run_id / "manifest.json").exists()
    result = service.resume_engineering(root, run_id).read()
    assert result["run_id"] == run_id and result["status"] == "SUCCEEDED"
    assert result["account"]["cash_total"] == "98.1"
    assert len(result["fills"]) == 1 and result["performance"]["commission"] == "1"
    assert result["positions"]["SYNTH:0"]["quantity"] == "9"
    assert (
        service.replay_engineering(root, run_id, tmp_path / "replay")["status"]
        == "NUMERICAL_REPLAY_VERIFIED"
    )


def test_interruption_during_partial_publication_keeps_same_durable_prefix(tmp_path, monkeypatch):
    import aqrp.services.backtest as service

    original = ExperimentLedger.artifact

    def interrupted(ledger, run_id, name, payload):
        original(ledger, run_id, name, payload)
        if name == "trace.json" and not (ledger.path(run_id) / "failed-state.json").exists():
            raise ContractError("CAPTURED_PARTIAL_PUBLICATION")

    monkeypatch.setattr(ExperimentLedger, "artifact", interrupted)
    result = service.simulate_engineering(fixture_request(), tmp_path, "a" * 40).read()
    path = tmp_path / result["run_id"]
    assert result["status"] == "FAILED" and "performance" not in result
    assert result["last_committed_account"]["cash_total"] == "98.1"
    assert (path / "state.json").read_bytes() == (path / "failed-state.json").read_bytes()
    assert result["committed_state_verification"]["commit_count"] == len(
        TransactionStore(path / "transactions").records
    )


def test_failure_publication_conflict_preserves_original_bytes_and_remains_nonterminal(
    tmp_path, monkeypatch
):
    import aqrp.services.backtest as service

    original = ExperimentLedger.artifact

    def damaged(ledger, run_id, name, payload):
        original(ledger, run_id, name, payload)
        if name == "trace.json":
            (ledger.path(run_id) / name).write_bytes(b'[{"original_failure":"preserve"}]')
            raise ContractError("CAPTURED_PUBLICATION_CORRUPTION")

    monkeypatch.setattr(ExperimentLedger, "artifact", damaged)
    with pytest.raises(ContractError, match="FAILURE_PUBLICATION_CONFLICT"):
        service.simulate_engineering(fixture_request(), tmp_path, "a" * 40)
    path = next(p for p in tmp_path.iterdir() if p.is_dir())
    assert (path / "trace.json").read_bytes() == b'[{"original_failure":"preserve"}]'
    assert not (path / "manifest.json").exists() and not (path / "result.json").exists()
