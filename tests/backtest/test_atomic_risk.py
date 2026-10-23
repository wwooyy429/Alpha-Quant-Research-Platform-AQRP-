"""Actual production match boundaries with predeclared latest-state/capacity answers."""

import uuid
from copy import deepcopy

import pytest

from aqrp.backtest.contracts import validate
from aqrp.backtest.engine import Simulator
from aqrp.backtest.exact import F, freeze
from aqrp.backtest.ledger import _post, account, initial_state
from aqrp.backtest.synthetic import fixture_request, seal_sidecar
from aqrp.backtest.transactions import TransactionStore
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.portfolio.contracts import load


def prepared(tmp_path, *, qty=1, lot=1, cash=1000, per_asset="0.15", budget=10):
    x = load(fixture_request().raw)
    p = load(x["decisions"][0]["portfolio_request_utf8"])
    p["constraints"]["per_asset"]["SYNTH:0"] = per_asset
    for r in p["inputs"]["prices"]["data"]:
        r["lot"] = str(lot)
    entries = [v for k, v in p["inputs"].items() if k != "scores"] + p["inputs"]["scores"]
    for e in entries:
        e["content_sha256"] = digest({k: v for k, v in e.items() if k != "content_sha256"})
    p["source"]["fixture_manifest"] = {e["ref"]: e["content_sha256"] for e in entries}
    x["decisions"] = []
    config = validate(seal_sidecar(x))
    sim = Simulator(config, tmp_path / "simulation", "a" * 40)
    s = initial_state(F(cash), x["assets"])
    s["session"] = 1
    for a in s["assets"].values():
        a.update(mark=F(100), tradable=True, in_universe=True, lot=F(lot))
    b = str(uuid.UUID(int=9))
    s["budgets"][b] = {
        "total": F(budget),
        "paid": F(0),
        "turnover_notional": F(0),
        "decision_equity": F(cash),
    }
    s["current_budget"] = b
    row = next(
        r
        for r in x["sidecar"]["rows"]
        if r["kind"] == "OPEN"
        and r["session_id"] == x["sessions"][1]["session_id"]
        and r["security_id"] == "SYNTH:0"
    )
    s["capacity"][row["slice_id"]] = F(10)
    orders = []
    for i in (1, 2):
        oid = str(uuid.UUID(int=i))
        orders.append(oid)
        s["orders"][oid] = {
            "order_id": oid,
            "security_id": "SYNTH:0",
            "original_qty": F(qty),
            "filled_qty": F(0),
            "cancelled_qty": F(0),
            "expired_remaining": F(0),
            "remaining": F(qty),
            "signed_remaining": F(qty),
            "side": "BUY",
            "kind": "MARKET",
            "time_in_force": "GTC",
            "submitted_at": x["sessions"][0]["close"],
            "eligible_at": x["sessions"][1]["open"],
            "expires_session": 3,
            "low": F(95),
            "high": F(105),
            "lot": F(lot),
            "reserve_notional": F(qty * 105),
            "budget_id": b,
            "constraints": p["constraints"],
            "P4_request_utf8": canonical(p).decode(),
            "status": "ACCEPTED",
            "history": [
                {"status": "CREATED", "reason": None},
                {"status": "SUBMITTED", "reason": None},
                {"status": "ACCEPTED", "reason": None},
            ],
        }
    sim.store = TransactionStore(tmp_path / "prepared-store", s)
    sim.current_key = (utc(row["event_time"]), 70, 1)
    return sim, row, orders


def test_same_slice_second_order_reads_first_committed_state(tmp_path):
    sim, row, ids = prepared(tmp_path)
    sim._match({"order_id": ids[0], "slice": row})
    sim.current_key = (*sim.current_key[:2], 2)
    sim._match({"order_id": ids[1], "slice": row})
    s = sim.store.state
    assert len(s["fills"]) == 1 and s["fees"] == 1
    assert s["orders"][ids[0]]["status"] == "FILLED"
    assert s["orders"][ids[1]]["status"] == "CANCELLED"
    assert s["assets"]["SYNTH:0"]["quantity"] == 1
    assert s["capacity"][row["slice_id"]] == 9
    assert account(s)["cash_total"] == F("898.9")
    tx = sim.store.records
    assert tx[1]["pre_hash"] == tx[0]["post_hash"]
    assert [r["local_stage"] for r in tx[0]["children"]] == [80, 90]
    assert not any(c["kind"] == "Fill" for c in tx[1]["children"])


def test_actual_shared_capacity_not_reset_per_order(tmp_path):
    sim, row, ids = prepared(tmp_path, qty=6, lot=3, cash=10000, per_asset="1", budget=20)
    for i, oid in enumerate(ids):
        sim.current_key = (*sim.current_key[:2], i + 1)
        sim._match({"order_id": oid, "slice": row})
    s = sim.store.state
    assert [f["signed_qty"] for f in s["fills"]] == [6, 3]
    assert s["capacity"][row["slice_id"]] == 1
    assert s["orders"][ids[1]]["status"] == "PARTIALLY_FILLED"
    sim._match({"order_id": ids[1], "slice": row})
    assert len(sim.store.state["fills"]) == 2


def test_fee_injection_cannot_consume_fill_cash_or_capacity(tmp_path, monkeypatch):
    import aqrp.backtest.engine as engine

    sim, row, ids = prepared(tmp_path, budget=3, per_asset="1")

    def prior_fee(s):
        s["orders"].pop(ids[1])
        s["budgets"][s["current_budget"]]["paid"] = F(2)
        s["fees"] = F(2)
        s["cash_set"] -= 2
        _post(s, "prior-fee", "COMMISSION", {"cash_set": F(-2), "commission_expense": F(2)})
        return [{"kind": "FixturePriorFee", "local_stage": 60}]

    sim.current_key = (sim.current_key[0], 60, 1)
    sim._commit("PRIOR_FEE", {}, prior_fee)
    before = deepcopy(sim.store.state)
    monkeypatch.setattr(engine, "commission", lambda *_: F(2))
    sim.current_key = (sim.current_key[0], 70, 2)
    sim._match({"order_id": ids[0], "slice": row})
    s = sim.store.state
    assert s["fills"] == [] and s["fees"] == 2
    assert s["cash_set"] == before["cash_set"] and s["capacity"] == before["capacity"]
    assert s["orders"][ids[0]]["status"] == "CANCELLED"


@pytest.mark.parametrize("corrupt", ["hash", "sequence", "pre", "post", "payload", "name"])
def test_durable_chain_corruption_fails_closed(tmp_path, corrupt):
    s = {"cash": F(1000)}
    store = TransactionStore(tmp_path, s)
    key = str(uuid.uuid4())

    def op(s):
        s["cash"] -= 1
        return [{"kind": "Cash", "local_stage": 90}]

    store.commit(key, {"amount": "1"}, ["time", 70, 1], op)
    original = store.commit(key, {"amount": "1"}, ["time", 70, 1], op)
    assert store.state["cash"] == 999 and original["commit_seq"] == 1
    with pytest.raises(ContractError, match="TRANSACTION_IDEMPOTENCY_CONFLICT"):
        store.commit(key, {"amount": "2"}, ["time", 70, 1], op)
    path = tmp_path / "commit-000000000001.json"
    raw = load(path.read_bytes())
    if corrupt == "name":
        path.rename(tmp_path / "commit-bad.json")
    else:
        if corrupt == "hash":
            raw["sha256"] = "0" * 64
        elif corrupt == "sequence":
            raw["commit_seq"] = 2
        elif corrupt == "pre":
            raw["pre_hash"] = "0" * 64
        elif corrupt == "post":
            raw["post_hash"] = "0" * 64
        else:
            raw["post_state"]["cash"] = freeze(F(9999))
        if corrupt != "hash":
            raw["sha256"] = digest({k: v for k, v in raw.items() if k != "sha256"})
        path.write_bytes(canonical(raw))
    with pytest.raises(ContractError):
        TransactionStore(tmp_path)


def test_initial_state_and_uncommitted_preparation_rules(tmp_path):
    with pytest.raises(ContractError, match="TRANSACTION_INITIAL_STATE_MISSING"):
        TransactionStore(tmp_path / "missing")
    root = tmp_path / "book"
    TransactionStore(root, {"x": F(1)})
    with pytest.raises(ContractError, match="TRANSACTION_INITIAL_STATE_CONFLICT"):
        TransactionStore(root, {"x": F(2)})
    (root / "prepared-previous-failure.json").write_bytes(b"partial failed bytes retained")
    assert TransactionStore(root).state == {"x": F(1)}
    (root / "initial.json").write_bytes(b'{"x": 1}\n')
    with pytest.raises(ContractError, match="TRANSACTION_NONCANONICAL_INITIAL"):
        TransactionStore(root)
