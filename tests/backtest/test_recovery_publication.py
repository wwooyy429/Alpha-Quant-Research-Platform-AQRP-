"""Original-run recovery and byte/hash faults, without altering any archived evidence."""

import json
from copy import deepcopy
from datetime import datetime

import pytest

from aqrp.backtest.contracts import validate
from aqrp.backtest.engine import Simulator
from aqrp.backtest.exact import F
from aqrp.backtest.ledger import account, initial_state, record_valuation
from aqrp.backtest.risk import assess
from aqrp.backtest.synthetic import fixture_request
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.factors.admission import reviewed_policy
from aqrp.portfolio.contracts import load
from aqrp.services.backtest import PROTOCOL, replay_engineering, resume_engineering

from .test_engine_service import data, run
from .test_exact_ledger import book, fill


def unfinished(root, *, change=None):
    request = fixture_request()
    policy = reviewed_policy()
    config = {
        "schema_version": "simulation-run/1.0.0",
        "raw_request_hex": request.raw.hex(),
        "request_sha256": request.content_hash,
        "protocol": PROTOCOL,
    }
    lineage = {
        "code_commit": "a" * 40,
        "code_bundle": policy["bundle_sha256"],
        "data_hash": request.content_hash,
        "environment": {},
        "protocol_hash": digest(PROTOCOL),
        "permission_domain": "ENGINEERING_TEST_ONLY",
        "seed": 0,
    }
    if change:
        change(config, lineage)
    ledger = ExperimentLedger(root)
    return ledger, ledger.start(config, lineage)


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_sdk_resumes_same_original_run_after_match_boundary_crash(tmp_path, stage):
    ledger, run_id = unfinished(tmp_path / "runs")
    root = ledger.path(run_id)

    def fault(current):
        if current == stage:
            paths = list(
                (root / "transactions").glob(
                    "prepared-*.json" if current == "BEFORE_COMMIT" else "commit-*.json"
                )
            )
            record = json.loads(max(paths, key=lambda p: p.stat().st_mtime_ns).read_bytes())
            if any(v["kind"] == "Fill" for v in record["children"]):
                raise RuntimeError("actual persisted boundary injection")

    with pytest.raises(RuntimeError):
        Simulator(validate(fixture_request()), root, "a" * 40, fault=fault).run()
    r = resume_engineering(tmp_path / "runs", run_id).read()
    assert r["status"] == "SUCCEEDED" and r["run_id"] == run_id
    assert r["account"]["cash_total"] == "98.1" and len(r["fills"]) == 1
    assert r["performance"]["commission"] == "1"
    assert ledger.verify(run_id)["status"] == "SUCCEEDED"


@pytest.mark.parametrize(
    "kind",
    ["config", "lineage", "domain", "bundle", "protocol", "partial", "request_hash", "data_hash"],
)
def test_resume_rejects_changed_or_nonengineering_origin(tmp_path, kind):
    def change(c, line):
        if kind == "domain":
            line["permission_domain"] = "FORMAL_APPROVAL_GATE"
        if kind == "bundle":
            line["code_bundle"] = "0" * 64
        if kind == "protocol":
            c["protocol"] = {"future": True}
        if kind == "request_hash":
            c["request_sha256"] = "0" * 64
        if kind == "data_hash":
            line["data_hash"] = "0" * 64

    ledger, key = unfinished(tmp_path, change=change)
    if kind in ("config", "lineage"):
        path = ledger.path(key) / (kind + ".json")
        x = load(path.read_bytes())
        x["tamper"] = True
        path.write_bytes(canonical(x))
    if kind == "partial":
        ledger.artifact(key, "state.json", {"partial": True})
    with pytest.raises(ContractError):
        resume_engineering(tmp_path, key)
    assert not (ledger.path(key) / "result.json").exists()


def test_return_wire_cannot_change_after_persisted_audit(tmp_path, monkeypatch):
    import aqrp.services.backtest as service

    original = service.canonical

    def wire(x):
        if (
            isinstance(x, dict)
            and x.get("schema_version") == "simulation-result/1.0.0"
            and "manifest" in x
        ):
            x = deepcopy(x)
            x["account"]["cash_total"] = "99.1"
        return original(x)

    monkeypatch.setattr(service, "canonical", wire)
    with pytest.raises(ContractError, match="SIMULATION_RETURN_BYTES_CHANGED"):
        run(data(), tmp_path)


@pytest.mark.parametrize("kind", ["package", "config", "state", "transaction", "recompute"])
def test_numerical_replay_checks_source_state_files_and_recomputed_projection(
    tmp_path, monkeypatch, kind
):
    import aqrp.services.backtest as service

    r = run(data(), tmp_path / "runs")
    if kind == "package":
        policy = reviewed_policy()
        policy["bundle_sha256"] = "0" * 64
        monkeypatch.setattr(service, "reviewed_policy", lambda: policy)
    elif kind == "transaction":
        path = tmp_path / "runs" / r["run_id"] / "transactions" / "initial.json"
        path.write_bytes(b"{}")
    elif kind in ("config", "state"):
        original = service._bound_read

        def changed(*args):
            raw = original(*args)
            if args[2] == kind + ".json":
                x = load(raw)
                x["protocol"] = {"future": True} if kind == "config" else x.get("protocol")
                if kind == "state":
                    x["tamper"] = True
                return canonical(x)
            return raw

        monkeypatch.setattr(service, "_bound_read", changed)
    else:
        original = service.Simulator.run

        def altered(self):
            s = original(self)
            s["capacity"][next(iter(s["capacity"]))] += 1
            return s

        monkeypatch.setattr(service.Simulator, "run", altered)
    with pytest.raises(ContractError):
        replay_engineering(tmp_path / "runs", r["run_id"], tmp_path / "replay")


def test_true_risk_uses_equity_unknown_industry_and_cash_only_boundaries():
    x = data()
    s = initial_state(F(1000), x["assets"])
    limits = load(x["decisions"][0]["portfolio_request_utf8"])["constraints"]
    limits["allow_cash_only"] = False
    assert not assess(s, limits)["passed"]
    s["assets"]["SYNTH:0"]["industry"] = "UNKNOWN"
    assert any(c["code"] == "INDUSTRY_UNKNOWN:UNKNOWN" for c in assess(s, limits)["checks"])
    s["cash_set"] = F(-1)
    assert not assess(s, limits)["passed"]


def test_actual_borrow_and_dividend_margin_failure_remain_committed(tmp_path):
    x = data()
    x["decisions"] = []
    sim = Simulator(validate(fixture_request()), tmp_path / "sim", "a" * 40)
    s = book()
    fill(s, -1)
    s["assets"]["A"]["mark"] = F(999)
    record_valuation(s, "A", "known999")
    from aqrp.backtest.transactions import TransactionStore

    sim.store = TransactionStore(tmp_path / "borrow", s)
    sim.current_key = (datetime.fromisoformat("2024-02-01T16:00:00+00:00"), 95, 1)
    with pytest.raises(ContractError, match="BORROW_OR_MARGIN_BREACH"):
        sim._borrow({"session": 0})
    assert sim.store.state["borrow"] == F("0.04")
    assert account(sim.store.state)["available"] == F("-0.04")
