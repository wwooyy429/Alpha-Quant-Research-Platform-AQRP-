"""G2-002: predeclared exposure-leg semantics, one real fill and fee per execution."""

import json
from fractions import Fraction as Q

import pytest

from aqrp.backtest.exact import freeze, thaw
from aqrp.backtest.ledger import account, assert_economic_identity
from aqrp.core.canonical import canonical
from aqrp.performance.metrics import performance

from .test_engine_service import data, run
from .test_exact_ledger import book, fill


@pytest.mark.parametrize(
    "old,delta,direction,legs",
    [
        (0, 3, "LONG", [("OPEN", "LONG", 3)]),
        (0, -3, "SHORT", [("OPEN", "SHORT", -3)]),
        (2, 3, "LONG", [("OPEN", "LONG", 3)]),
        (-2, -3, "SHORT", [("OPEN", "SHORT", -3)]),
        (3, -2, "LONG", [("CLOSE", "LONG", -2)]),
        (-3, 2, "SHORT", [("CLOSE", "SHORT", 2)]),
        (3, -3, "LONG", [("CLOSE", "LONG", -3)]),
        (-3, 3, "SHORT", [("CLOSE", "SHORT", 3)]),
        (2, -5, "MIXED", [("CLOSE", "LONG", -2), ("OPEN", "SHORT", -3)]),
        (-2, 5, "MIXED", [("CLOSE", "SHORT", 2), ("OPEN", "LONG", 3)]),
    ],
)
def test_one_fill_reports_unambiguous_open_close_and_cross_zero_legs(old, delta, direction, legs):
    state = book(10000)
    if old:
        fill(state, old)
    prior_fills, prior_fees = len(state["fills"]), state["fees"]
    actual = fill(state, delta, p=100, f=1)
    assert actual["direction"] == direction
    assert actual["execution_side"] == ("BUY" if delta > 0 else "SELL")
    assert actual["position_before"] == old and actual["position_after"] == old + delta
    assert [
        (leg["effect"], leg["direction"], leg["signed_qty"]) for leg in actual["position_legs"]
    ] == legs
    assert sum(leg["signed_qty"] for leg in actual["position_legs"]) == delta
    assert sum(leg["fee"] for leg in actual["position_legs"]) == 1
    assert sum(leg["realized_gross"] for leg in actual["position_legs"]) == actual["realized_gross"]
    for leg in actual["position_legs"]:
        assert leg["quantity"] == abs(leg["signed_qty"])
        assert leg["fee"] == Q(abs(leg["signed_qty"]), abs(delta))
    assert len(state["fills"]) == prior_fills + 1 and state["fees"] == prior_fees + 1
    assert state["assets"]["A"]["quantity"] == old + delta
    assert_economic_identity(state)
    assert thaw(json.loads(canonical(freeze(actual)))) == actual
    assert account(state)["equity"] == 10000 - prior_fees - 1
    assert sum(performance(state)["contribution"].values()) == -prior_fees - 1


def test_actual_service_return_and_persisted_opening_long_direction(tmp_path):
    result = run(data(), tmp_path)
    disk = json.loads((tmp_path / result["run_id"] / "result.json").read_bytes())
    assert result["fills"] == disk["fills"]
    fill_record = result["fills"][0]
    assert fill_record["direction"] == "LONG" and fill_record["execution_side"] == "BUY"
    assert fill_record["position_legs"] == [
        {
            "effect": "OPEN",
            "direction": "LONG",
            "quantity": "9",
            "signed_qty": "9",
            "fee": "1",
            "realized_gross": "0",
        }
    ]
    assert result["account"]["cash_total"] == "98.1"
    assert result["performance"]["contribution"] == {"LONG": "-1.9", "SHORT": "0"}
