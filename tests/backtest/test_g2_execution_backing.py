"""BT-005/007/008, G2-003: durable executions, never paired mutable witnesses."""

import json
from copy import deepcopy

import pytest

from aqrp.backtest.engine import Simulator
from aqrp.backtest.exact import F, freeze, thaw
from aqrp.backtest.ledger import liquidate, settle, split, verify_execution_backing
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger

from .test_exact_ledger import book, fill
from .test_g2_bucket_reconciliation import begin_history, fill_source, short_request, source_event


@pytest.mark.parametrize("exc_type", [ContractError, KeyboardInterrupt])
@pytest.mark.parametrize(
    "damage", ["none", "price", "cashlot", "pair", "pair-and-fill-copy", "attribution-pool"]
)
def test_settled_short_account_requires_original_durable_execution(
    tmp_path, monkeypatch, exc_type, damage
):
    import aqrp.services.backtest as service

    class Fault(Simulator):
        def __init__(self, config, root, commit):
            def fault(stage):
                if stage != "AFTER_COMMIT":
                    return
                path = sorted((root / "transactions").glob("commit-*.json"))[-1]
                item = json.loads(path.read_bytes())
                if item["payload"] != {"session": 2}:
                    return
                original = deepcopy(item)
                state = thaw(item["post_state"])
                lot = next(c for c in state["cashlots"] if c["kind"] == "SHORT" and c["settled"])
                entry = next(
                    item
                    for a in state["assets"].values()
                    for item in a["lots"]
                    if item["id"] == lot["entry_id"]
                )
                # Independent predeclared execution: one SHORT share@99.9, cash997.8,
                # restricted99.9 and mark100: available = 997.8-99.9-100 = 797.9.
                assert entry["price"] == lot["amount"] == F("99.9")
                assert state["cash_set"] == F("997.8") and entry["remaining"] == 1
                (tmp_path / "valid-commit-before.json").write_bytes(path.read_bytes())
                if damage in ("price", "pair", "pair-and-fill-copy"):
                    entry["price"] -= 1
                if damage in ("cashlot", "pair", "pair-and-fill-copy"):
                    lot["amount"] -= 1
                if damage == "pair-and-fill-copy":
                    next(f for f in state["fills"] if f["fill_id"] == entry["id"])["price"] -= 1
                if damage == "attribution-pool":
                    entry["borrow"] += 1
                assert state["journal"] == thaw(original["post_state"])["journal"]
                item["post_state"] = freeze(state)
                item["post_hash"] = digest(item["post_state"])
                item["sha256"] = digest({k: v for k, v in item.items() if k != "sha256"})
                assert (
                    item["children"] == original["children"]
                    and item["payload"] == original["payload"]
                )
                path.write_bytes(canonical(item))
                (tmp_path / "commit-at-fault.json").write_bytes(path.read_bytes())
                raise exc_type("G2_003_SETTLED_BACKING_FAULT")

            super().__init__(config, root, commit, fault=fault)

    monkeypatch.setattr(service, "Simulator", Fault)
    root = tmp_path / "runs"
    wire = service.simulate_engineering(short_request(), root, "a" * 40)
    (tmp_path / "actual-return.json").write_bytes(wire.raw)
    result = wire.read()
    run = root / result["run_id"]
    assert result["reasons"][0] == (
        "KeyboardInterrupt" if exc_type is KeyboardInterrupt else "G2_003_SETTLED_BACKING_FAULT"
    )
    if damage == "none":
        assert result["status"] == ("CANCELLED" if exc_type is KeyboardInterrupt else "FAILED")
        assert result["committed_state_verification"]["financial_state_known"] is True
        assert result["last_committed_account"]["S_set"] == "99.9"
        assert result["last_committed_account"]["available"] == "797.9"
    else:
        assert result["status"] == "FAILED"
        assert result["committed_state_verification"]["status"] == "UNVERIFIED_COMMITTED_STATE"
        assert result["committed_state_verification"]["financial_state_known"] is False
        assert "last_committed_account" not in result
        assert "COMMITTED_STATE_UNVERIFIED" in result["reasons"]
        assert not (run / "failed-state.json").exists()
        assert not (run / "transactions.json").exists()
    assert service.result_engineering(root, run.name) == {
        k: v for k, v in result.items() if k != "manifest"
    }
    assert (
        sorted((run / "transactions").glob("commit-*.json"))[-1].read_bytes()
        == (tmp_path / "commit-at-fault.json").read_bytes()
    )
    assert ExperimentLedger(root).verify(run.name)["status"] == result["status"]


@pytest.mark.parametrize("quantities", [(-2, -3, 1, 4), (2, 3, -1, -6, 2), (-2, 5, -4)])
@pytest.mark.parametrize("settled_first", [False, True])
@pytest.mark.parametrize("ratio", [1, 2])
def test_raw_prefix_multilot_cross_zero_split_and_recovery(quantities, settled_first, ratio):
    from aqrp.services.backtest import projection

    s = book(10000)
    records = begin_history(s)
    for i, n in enumerate(quantities):
        if i == 1:
            if ratio == 2:
                split(s, "split", "A", F(2))
                records.append(source_event("SPLIT", {"security_id": "A", "value": "2"}))
            if settled_first:
                settle(s, 1, "settlement")
                s["session"] = 1
                records.append(source_event("AccountUpdated", {"session": 1}))
        f = fill(s, n, 100 + i, session=s["session"], name="f" + str(i))
        records.append(fill_source(f))
        projection(s, records)
    settle(s, 2, "settle-final")
    s["session"] = 2
    records.append(source_event("AccountUpdated", {"session": 2}))
    projection(s, records)
    liquidate(
        s, event_id="delist", sid="A", recovery_price=F(80), session=2, at="2024-02-01T09:00:00Z"
    )
    records.append(
        source_event("DELIST", {"action_id": "delist", "security_id": "A", "value": "80"})
    )
    result = projection(s, records)
    assert result["account"]["S_set"] == "0" and result["account"]["marked_value"] == "0"
    assert s["assets"]["A"]["quantity"] == 0
    assert (
        result["reconciliation"]["execution_backing"]["status"]
        == "RAW_COMMITTED_EXECUTIONS_FIFO_AND_SETTLEMENT_VERIFIED"
    )


@pytest.mark.parametrize(
    "damage",
    [
        "missing",
        "duplicate",
        "sid",
        "zero",
        "no-session",
        "backward",
        "split",
        "cash-id",
        "at",
        "recovery",
        "copy",
    ],
)
def test_reconstruction_does_not_accept_missing_or_conflicting_execution_evidence(damage):
    s = book()
    records = begin_history(s)
    f = fill(s, -2, name="short")
    records.append(fill_source(f))
    if damage == "missing":
        records = None
    elif damage == "duplicate":
        records.append(deepcopy(records[-1]))
    elif damage == "sid":
        records[-1]["children"][0]["fill"]["security_id"] = "UNKNOWN"
    elif damage == "zero":
        records[-1]["children"][0]["fill"]["signed_qty"] = F(0)
    elif damage == "no-session":
        records.pop(0)
    elif damage == "backward":
        records.append(source_event("AccountUpdated", {"session": -1}))
    elif damage == "split":
        records.append(source_event("SPLIT", {"security_id": "A", "value": "0"}))
    elif damage == "cash-id":
        s["cashlots"][0]["id"] = "forged"
    elif damage == "at":
        s["assets"]["A"]["lots"][0]["at"] = "2024-02-02T00:00:00Z"
    elif damage == "recovery":
        liquidate(
            s,
            event_id="delist",
            sid="A",
            recovery_price=F(80),
            session=0,
            at="2024-02-01T09:00:00Z",
        )
        records.append(
            source_event("DELIST", {"action_id": "delist", "security_id": "A", "value": "80"})
        )
        s["liquidations"][0]["price"] += 1
    elif damage == "copy":
        s["fills"][0]["price"] += 1
    with pytest.raises(ContractError):
        verify_execution_backing(s, records)


def test_no_context_cannot_certify_an_account():
    from aqrp.services.backtest import projection

    with pytest.raises(ContractError, match="DURABLE_EXECUTION_PROVENANCE_REQUIRED"):
        projection(book())
