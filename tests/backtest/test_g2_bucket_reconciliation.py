"""G2-003: literal bucket answers and rehashed real-service corruption controls."""

import json
from copy import deepcopy
from itertools import permutations

import pytest

from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.backtest.engine import Simulator
from aqrp.backtest.exact import F, freeze, thaw
from aqrp.backtest.ledger import account, accrue, record_valuation, settle, split
from aqrp.backtest.synthetic import fixture_request
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.services.backtest import _reconciled_account, projection

from .test_exact_ledger import book, fill


def source_event(kind, payload, phase=10):
    """Explicit read-side unit inputs; public-service tests use actual durable files."""
    return {
        "payload": payload,
        "children": [{"kind": kind}],
        "dispatch_key": ["2024-02-01T09:00:00Z", phase, 1],
    }


def begin_history(s):
    settle(s, 0, "unit-start")
    s["session"] = 0
    return [
        source_event("AccountUpdated", {"session": 0}),
        source_event("MarketConfirmed", {"rows": [{"security_id": "A", "price": "100"}]}, 20),
    ]


def fill_source(f):
    return {
        "payload": {},
        "children": [{"kind": "Fill", "fill": deepcopy(f)}],
        "dispatch_key": [f["at"], 70, 1],
    }


def short_request():
    x = json.loads(fixture_request().raw)
    p = json.loads(x["decisions"][0]["portfolio_request_utf8"])
    p["policy"].update(mode="LONG_SHORT", gross="0.4", net="0")
    x["decisions"][0]["portfolio_request_utf8"] = canonical(p).decode()
    return EngineeringBacktestRequest.create(x)


def transfer(s, source, destination):
    """Intentionally inconsistent classification; Journal remains unchanged."""
    for key, amount in ((source, F(-1)), (destination, F(1))):
        if key == "cash_set":
            s[key] += amount
        elif key == "U_short":
            next(c for c in s["cashlots"] if c["kind"] == "SHORT")["amount"] += amount
        else:
            existing = next((c for c in s["cashlots"] if c["kind"] == "FREE"), None)
            if existing is not None:
                existing["amount"] += amount
            else:
                s["cashlots"].append(
                    dict(
                        id="fault-free-" + str(amount),
                        entry_id=None,
                        kind="FREE",
                        amount=amount,
                        settled=False,
                        due=2,
                    )
                )


@pytest.mark.parametrize(
    "source,destination",
    list(permutations(("cash_set", "U_free", "U_short"), 2)) + [("receivable", "payable")],
)
def test_real_service_rejects_constant_total_bucket_reclassification(
    tmp_path, monkeypatch, source, destination
):
    import aqrp.services.backtest as service

    class Fault(Simulator):
        def __init__(self, config, root, commit):
            def fault(stage):
                if stage != "AFTER_COMMIT":
                    return
                path = sorted((root / "transactions").glob("commit-*.json"))[-1]
                item = json.loads(path.read_bytes())
                if not any(
                    c["kind"] == "Fill" and thaw(c["fill"]["signed_qty"]) < 0
                    for c in item["children"]
                ):
                    return
                (tmp_path / "original-valid-commit.json").write_bytes(path.read_bytes())
                state = thaw(deepcopy(item["post_state"]))
                # Independent raw-Journal accumulation, not a tested read-side function.
                buckets = dict(cash_set=F(1000), U_free=F(0), U_short=F(0))
                for event in state["journal"]:
                    for e in event["entries"]:
                        if e["unit"] == "CCY" and e["account"] in buckets:
                            buckets[e["account"]] += e["amount"]
                assert buckets == dict(cash_set=F("897.9"), U_free=0, U_short=F("99.9"))
                assert account(state)["available"] == F("797.9")
                if source == "receivable":
                    state["rights"].update(
                        fault_r=dict(amount=F(1), pay_at=None, security_id="SYNTH:0"),
                        fault_p=dict(amount=F(-1), pay_at=None, security_id="SYNTH:0"),
                    )
                else:
                    transfer(state, source, destination)
                item["post_state"] = freeze(state)
                item["post_hash"] = digest(item["post_state"])
                item["sha256"] = digest({k: v for k, v in item.items() if k != "sha256"})
                path.write_bytes(canonical(item))
                (tmp_path / "original-rehashed-fault.json").write_bytes(path.read_bytes())
                raise ContractError("G2_003_BUCKET_FAULT")

            super().__init__(config, root, commit, fault=fault)

    monkeypatch.setattr(service, "Simulator", Fault)
    root = tmp_path / "runs"
    returned = service.simulate_engineering(short_request(), root, "a" * 40)
    (tmp_path / "actual-return.json").write_bytes(returned.raw)
    result = returned.read()
    assert result["status"] == "FAILED" and result["reasons"][0] == "G2_003_BUCKET_FAULT"
    assert result["committed_state_verification"]["status"] == "UNVERIFIED_COMMITTED_STATE"
    assert result["committed_state_verification"]["financial_state_known"] is False
    assert "COMMITTED_STATE_UNVERIFIED" in result["reasons"]
    assert "last_committed_account" not in result
    run = root / result["run_id"]
    assert not (run / "failed-state.json").exists()
    assert not (run / "transactions.json").exists()
    assert (
        sorted((run / "transactions").glob("commit-*.json"))[-1].read_bytes()
        == (tmp_path / "original-rehashed-fault.json").read_bytes()
    )
    assert ExperimentLedger(root).verify(run.name)["status"] == "FAILED"


def test_receivable_and_payable_cannot_cancel_each_other():
    s = book()
    records = begin_history(s)
    accrue(s, "right", "A", F(7), kind="DIVIDEND_EX")
    accrue(s, "obligation", "A", F(-3), kind="DIVIDEND_EX")
    assert [account(s)[k] for k in ("receivable", "payable", "equity")] == [7, 3, 1004]
    _reconciled_account(s, records)
    s["rights"]["right"]["amount"] += 1
    s["rights"]["obligation"]["amount"] -= 1
    assert account(s)["equity"] == 1004
    with pytest.raises(ContractError, match="RECONCILIATION"):
        projection(s)


@pytest.mark.parametrize(
    "source,destination", list(permutations(("cash_set", "U_free", "U_short"), 2))
)
def test_all_six_nonnegative_bucket_transfers_fail_normal_projection(source, destination):
    s = book()
    records = begin_history(s)
    fill(s, 2, name="long")
    fill(s, -3, name="cross")
    assert [account(s)[k] for k in ("cash_set", "U_free", "U_short")] == [798, 200, 100]
    records += [fill_source(f) for f in s["fills"]]
    _reconciled_account(s, records)
    transfer(s, source, destination)
    c = account(s)
    assert min(c[k] for k in ("cash_set", "U_free", "U_short")) >= 0
    assert c["cash_total"] == 1098
    with pytest.raises(ContractError, match="RECONCILIATION"):
        projection(s)


@pytest.mark.parametrize(
    "field", ["fees", "borrow", "dividends", "realized_long", "realized_short", "external_flows"]
)
def test_individual_financial_accounts_cannot_be_relabelled(field):
    s = book()
    s[field] += 1
    with pytest.raises(ContractError, match="RECONCILIATION"):
        projection(s)


def test_valid_margin_loss_does_not_require_nonnegative_available():
    s = book()
    records = begin_history(s)
    fill(s, -2, name="short")
    records.append(fill_source(s["fills"][0]))
    s["assets"]["A"]["mark"] = F(1000)
    record_valuation(s, "A", "margin-mark")
    records.append(
        source_event("MarketConfirmed", {"rows": [{"security_id": "A", "price": "1000"}]}, 20)
    )
    # Actual available = 999 - 2000 = -1001, not an unknown ledger.
    assert _reconciled_account(s, records)[0]["available"] == -1001


@pytest.mark.parametrize("settled", [False, True])
@pytest.mark.parametrize("ratio", [1, 2])
def test_legal_partial_short_cover_and_settlement_are_exact(settled, ratio):
    s = book()
    records = begin_history(s)
    fill(s, -2, name="short")
    records.append(fill_source(s["fills"][0]))
    if ratio == 2:
        split(s, "split", "A", F(2))
        records.append(source_event("SPLIT", {"security_id": "A", "value": "2"}))
    if settled:
        settle(s, 1, "settle-first")
        s["session"] = 1
        records.append(source_event("AccountUpdated", {"session": 1}))
    fill(s, ratio, 90 / ratio, name="cover")
    records.append(fill_source(s["fills"][-1]))
    _reconciled_account(s, records)
    settle(s, 1, "settle-final")
    s["session"] = 1
    records.append(source_event("AccountUpdated", {"session": 1}))
    c, _ = _reconciled_account(s, records)
    assert [c[k] for k in ("cash_set", "U_free", "U_short", "S_set")] == [1108, 0, 0, 100]
    fill(s, ratio, 90 / ratio, session=1, name="cover-rest")
    records.append(fill_source(s["fills"][-1]))
    assert _reconciled_account(s, records)[0]["S_set"] == 0


@pytest.mark.parametrize(
    "damage", ["negative", "orphan", "duplicate", "early", "late", "gross", "due", "subset"]
)
def test_restricted_short_proceeds_structure_must_be_proven(damage):
    s = book()
    fill(s, -2, name="short")
    if damage in ("late", "subset"):
        settle(s, 1, "settlement")
    c = s["cashlots"][0]
    if damage == "negative":
        c["amount"] = F(-200)
    elif damage == "orphan":
        c["entry_id"] = "unknown"
    elif damage == "duplicate":
        s["cashlots"].append({**c, "id": "duplicate"})
    elif damage == "early":
        c["settled"] = True
        s["cash_set"] += 200
    elif damage == "late":
        c["settled"] = False
        s["cash_set"] -= 200
    elif damage == "gross":
        # Cash buckets still match Journal; only original short-lot backing is false.
        s["assets"]["A"]["lots"][0]["price"] += 1
    elif damage == "due":
        c["due"] += 1
    elif damage == "subset":
        s["cash_set"] = F(199)
        s["journal"].append(
            dict(
                event_id="withdrawal",
                kind="EXTERNAL_FLOW",
                entries=[
                    dict(account="cash_set", unit="CCY", amount=F(-1000)),
                    dict(account="external_capital", unit="CCY", amount=F(1000)),
                ],
            )
        )
        s["external_flows"] = F(-1000)
    with pytest.raises(ContractError):
        projection(s)


@pytest.mark.parametrize(
    "damage",
    [
        "missing-session",
        "negative-session",
        "backward",
        "missing-lot",
        "duplicate-entry",
        "free-entry",
        "extra-field",
        "empty-id",
        "integer-flag",
        "negative-due",
    ],
)
def test_lot_and_settlement_proof_rejects_incomplete_or_ambiguous_evidence(damage):
    s = book()
    fill(s, -2, name="short")
    settle(s, 1, "settlement")
    if damage == "missing-session":
        s["journal"][-1].pop("settlement_session")
    elif damage == "negative-session":
        s["journal"][-1]["settlement_session"] = -1
    elif damage == "backward":
        settle(s, 0, "backward")
    elif damage == "missing-lot":
        s["cashlots"] = []
    elif damage == "duplicate-entry":
        s["assets"]["A"]["lots"].append(deepcopy(s["assets"]["A"]["lots"][0]))
    elif damage == "free-entry":
        s["cashlots"].append(
            dict(id="bad-free", entry_id="short", kind="FREE", amount=F(0), settled=True, due=1)
        )
    elif damage == "extra-field":
        s["cashlots"][0]["surprise"] = True
    elif damage == "empty-id":
        s["cashlots"][0]["id"] = ""
    elif damage == "integer-flag":
        s["cashlots"][0]["settled"] = 1
    elif damage == "negative-due":
        s["cashlots"][0]["due"] = -1
    with pytest.raises(ContractError):
        projection(s)
