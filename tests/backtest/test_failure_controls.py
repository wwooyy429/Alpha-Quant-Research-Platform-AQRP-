"""Fault injection, independent publication checks and platform driver boundaries."""

import json
import os
import uuid
from copy import deepcopy
from types import SimpleNamespace

import pytest

from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.backtest.exact import F
from aqrp.backtest.ledger import initial_state
from aqrp.backtest.provider import SignalProvider, adapt_portfolio, verify_portfolio_result
from aqrp.backtest.transactions import TransactionStore, guard_path
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.performance.metrics import finite_stat, performance, summary
from aqrp.portfolio.contracts import PortfolioRequest
from aqrp.portfolio.service import construct_engineering
from aqrp.services.backtest import _bound_read, projection, resume_engineering, simulate_engineering

from .test_atomic_risk import prepared
from .test_engine_service import data, run
from .test_exact_ledger import book, fill


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_fault_callback_preserves_only_whole_commit(tmp_path, stage):
    store = TransactionStore(tmp_path, {"cash": F(1000)})

    def apply(s):
        s["cash"] -= 101
        return [{"kind": "Fill", "local_stage": 80}, {"kind": "AccountUpdated", "local_stage": 90}]

    def fault(current):
        if stage == current:
            raise RuntimeError("injected crash")

    key = str(uuid.uuid4())
    with pytest.raises(RuntimeError):
        store.commit(key, {}, ["time", 70, 1], apply, fault=fault)
    restored = TransactionStore(tmp_path)
    assert restored.state["cash"] == (1000 if stage == "BEFORE_COMMIT" else 899)
    restored.commit(key, {}, ["time", 70, 1], apply)
    assert restored.state["cash"] == 899 and len(restored.records) == 1


def test_directory_flush_driver_and_alias_rejection(tmp_path, monkeypatch):
    import aqrp.backtest.transactions as transactions

    store = TransactionStore(tmp_path / "store", {"x": F(1)})
    calls = []
    real_replace = os.replace
    driver = SimpleNamespace(
        name="posix",
        O_RDONLY=0,
        replace=real_replace,
        open=lambda *_: calls.append("open") or 17,
        fsync=lambda fd: calls.append(("fsync", fd)),
        close=lambda fd: calls.append(("close", fd)),
    )
    monkeypatch.setattr(transactions, "os", driver)
    store.commit(str(uuid.uuid4()), {}, ["time", 70, 1], lambda s: s.update(x=F(2)) or [])
    assert calls == ["open", ("fsync", 17), ("close", 17)]
    original = tmp_path / "original"
    original.write_bytes(b"raw")
    alias = tmp_path / "alias"
    os.link(original, alias)
    with pytest.raises(ContractError, match="SIMULATION_LINK_PATH_FORBIDDEN"):
        guard_path(alias)


def test_latest_state_and_recovery_comparison_fault_controls(tmp_path, monkeypatch):
    sim, row, ids = prepared(tmp_path)
    original = sim.store.commit

    def stale(*args, **kwargs):
        sim.store.initial["cash_set"] -= 1
        # Invoke the guarded proposed transition on a changed candidate, never publish it.
        changed = deepcopy(sim.store.state)
        changed["cash_set"] -= 1
        args[3](changed)

    monkeypatch.setattr(sim.store, "commit", stale)
    with pytest.raises(ContractError, match="STALE_TRANSACTION_PRESTATE"):
        sim._match({"order_id": ids[0], "slice": row})
    monkeypatch.setattr(sim.store, "commit", original)
    sim.store.initial["cash_set"] += 1
    sim._match({"order_id": ids[0], "slice": row})
    with pytest.raises(ContractError, match="EVENT_INSERTION_BEFORE_CURRENT_PHASE"):
        sim.enqueue(sim.current_key[0], 20, "MARKET", {})
    before = len(sim.store.records)
    sim._match({"order_id": ids[0], "slice": row})
    assert len(sim.store.records) == before
    record = deepcopy(sim.store.records[0])
    record["post_hash"] = "0" * 64
    monkeypatch.setattr(sim.store, "commit", lambda *_a, **_k: record)
    sim.current_key = (utc(row["event_time"]), 70, 2)
    with pytest.raises(ContractError, match="RECOVERY_NONDETERMINISTIC_TRANSACTION"):
        sim._commit("OTHER", {}, lambda s: s.update(other=1) or [])


def test_provider_and_budget_projection_failures(tmp_path):
    x = data()
    with pytest.raises(ContractError, match="DUPLICATE_DECISION_TIME"):
        SignalProvider(x["decisions"] * 2)
    p = PortfolioRequest(x["decisions"][0]["portfolio_request_utf8"].encode())
    s = initial_state(F(1000), x["assets"])
    with pytest.raises(ContractError, match="NO_VISIBLE_DECISION_MARK"):
        adapt_portfolio(p, s)
    s["cash_set"] = F(-1)
    with pytest.raises(ContractError, match="INFEASIBLE_P4_BUDGET_PROJECTION"):
        adapt_portfolio(p, s)
    s["cash_set"] = F(1000)
    s["orders"] = {
        "pending": {
            "status": "ACCEPTED",
            "reserve_notional": F(0),
            "remaining": F(1),
            "high": F(105),
        }
    }
    with pytest.raises(ContractError, match="REBALANCE_PENDING_ORDERS"):
        adapt_portfolio(p, s)


@pytest.mark.parametrize("mode", ["absent", "bytes", "candidate", "risk", "audit"])
def test_p4_terminal_members_and_bytes_are_not_replaced_by_flags(tmp_path, monkeypatch, mode):
    x = data()
    req = PortfolioRequest(x["decisions"][0]["portfolio_request_utf8"].encode())
    result = construct_engineering(req, tmp_path, "a" * 40).read()
    ledger = ExperimentLedger(tmp_path)
    original = ExperimentLedger.verify
    name = (
        "result.json"
        if mode in ("absent", "bytes")
        else "candidate.json"
        if mode == "candidate"
        else "risk.json"
        if mode == "risk"
        else "published-byte-audit.json"
    )
    if mode == "absent":

        def altered(self, run):
            m = original(self, run)
            m["files"] = [e for e in m["files"] if e["path"] != name]
            result["manifest"] = m
            return m

        monkeypatch.setattr(ExperimentLedger, "verify", altered)
    else:
        path = ledger.path(result["run_id"]) / name
        path.write_bytes(b"{}")
        m = deepcopy(result["manifest"])
        import hashlib

        next(e for e in m["files"] if e["path"] == name)["sha256"] = hashlib.sha256(
            b"{}"
        ).hexdigest()
        # Isolate byte/member audit from the separately tested outer seal verifier.
        if mode == "bytes":
            m = deepcopy(result["manifest"])
        else:
            result["manifest"] = m
        monkeypatch.setattr(ExperimentLedger, "verify", lambda *_: m)
    with pytest.raises(ContractError):
        verify_portfolio_result(req, result, tmp_path)


def test_statistics_financial_boundaries_and_aggregate_attribution():
    assert finite_stat(lambda: float("nan"))["reason"] == "NUMERIC_RANGE"
    assert finite_stat(lambda: 1 / 0)["reason"] == "NUMERIC_RANGE"
    assert summary([F(-2)], [F(1), F(1)])["annual_return"]["reason"] == "NONPOSITIVE_GROWTH"
    s = book()
    fill(s, 2)
    fill(s, -1, 104)
    m = performance(s)
    assert m["contribution"]["LONG"] == 2 and m["fifo"]["count"] == 1
    s["cash_set"] += 1
    with pytest.raises(ContractError, match="LONG_SHORT_ATTRIBUTION_MISMATCH"):
        performance(s)


def test_actual_journal_state_mismatch_and_bound_read_guard(tmp_path):
    s = book()
    s["cash_set"] += 1
    with pytest.raises(ContractError, match="RAW_JOURNAL_ACCOUNT_RECONCILIATION_FAILED"):
        projection(s)
    ledger = ExperimentLedger(tmp_path)
    run_id = ledger.start(
        {},
        {
            "code_commit": "a" * 40,
            "code_bundle": "x",
            "data_hash": "x",
            "environment": {},
            "protocol_hash": "x",
            "permission_domain": "TEST",
            "seed": 0,
        },
    )
    ledger.artifact(run_id, "result.json", {"original": True})
    m = ledger.finish(run_id, "SUCCEEDED")
    (ledger.path(run_id) / "result.json").write_bytes(b"{}")
    with pytest.raises(ContractError, match="SIMULATION_ARTIFACT_BYTES_CHANGED"):
        _bound_read(ledger, run_id, "result.json", m)


@pytest.mark.parametrize(
    "exc_type,status", [(RuntimeError, "FAILED"), (KeyboardInterrupt, "CANCELLED")]
)
def test_unexpected_error_and_cancel_keep_terminal_account_evidence(
    tmp_path, monkeypatch, exc_type, status
):
    import aqrp.services.backtest as service

    def interrupted(self):
        raise exc_type("injected")

    monkeypatch.setattr(service.Simulator, "run", interrupted)
    if exc_type is RuntimeError:
        with pytest.raises(RuntimeError):
            run(data(), tmp_path)
    else:
        assert run(data(), tmp_path)["status"] == status
    run_id = next(p.name for p in tmp_path.iterdir() if p.is_dir())
    m = ExperimentLedger(tmp_path).verify(run_id)
    assert m["status"] == status and "failed-state.json" in {e["path"] for e in m["files"]}
    with pytest.raises(ContractError, match="NONRUNNING_SIMULATION_CANNOT_RESUME"):
        resume_engineering(tmp_path, run_id)


def test_invalid_utf8_preserved_as_original_bytes(tmp_path):
    r = simulate_engineering(EngineeringBacktestRequest(b"\xff"), tmp_path, "a" * 40).read()
    assert r["status"] == "FAILED" and r["reasons"] == ["INVALID_JSON"]
    config = json.loads((tmp_path / r["run_id"] / "config.json").read_bytes())
    assert config["raw_request_hex"] == "ff"
