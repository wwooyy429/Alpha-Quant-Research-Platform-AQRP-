"""Literal full-service partial, odd-lot split/close and pending-order answers."""

from copy import deepcopy

import pytest

from aqrp.backtest.contracts import validate
from aqrp.backtest.exact import F
from aqrp.backtest.synthetic import seal_sidecar
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError

from .test_engine_service import data, put_portfolio, reseal_portfolio, run


def retime(p, t, index):
    p = deepcopy(p)
    p["context"].update(decision_time=t, session_index=index)
    for name, value in p["inputs"].items():
        for e in value if name == "scores" else [value]:
            e["context"] = p["context"]
            e.update(event_time=t, available_at=t, as_of=t)
            if name == "account":
                e["data"]["valuation_time"] = t
            else:
                for row in e["data"]["rows"] if name == "scores" else e["data"]:
                    row.update(event_time=t, available_at=t, as_of=t)
                    if name == "scores":
                        row.update(signal_time=t, session_index=index)
    entries = [e for k, e in p["inputs"].items() if k != "scores"] + p["inputs"]["scores"]
    for e in entries:
        e["content_sha256"] = digest({k: v for k, v in e.items() if k != "content_sha256"})
    p["source"]["fixture_manifest"] = {e["ref"]: e["content_sha256"] for e in entries}
    return p


@pytest.mark.parametrize(
    "time_in_force,quantity,cash,fees", [("DAY", 10, "598", "1"), ("GTC", 15, "96.5", "2")]
)
def test_real_partial_order_day_expiry_and_gtc_second_fill(
    tmp_path, time_in_force, quantity, cash, fees
):
    x = data()
    x.update(initial_cash="1600", fee_budget="20")
    x["decisions"][0]["time_in_force"] = time_in_force
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    assert r["positions"]["SYNTH:0"]["quantity"] == str(quantity)
    assert r["account"]["cash_total"] == cash and r["performance"]["commission"] == fees
    order = next(iter(r["orders"].values()))
    assert order["status"] == ("EXPIRED" if time_in_force == "DAY" else "FILLED")
    assert order["expired_remaining"] == ("5" if time_in_force == "DAY" else "0")
    assert all(F(f["signed_qty"]) <= 10 for f in r["fills"])


def test_rebalance_with_existing_partial_orders_cannot_duplicate_delta(tmp_path):
    x = data()
    x.update(initial_cash="1600", fee_budget="20")
    x["decisions"][0]["time_in_force"] = "GTC"
    second = deepcopy(x["decisions"][0])
    second["portfolio_request_utf8"] = canonical(
        retime(reseal_portfolio(x), x["sessions"][1]["close"], 1)
    ).decode()
    x["decisions"].append(second)
    r = run(x, tmp_path)
    assert r["status"] == "FAILED" and r["reasons"] == ["REBALANCE_PENDING_ORDERS"]
    assert r["last_committed_account"]["marked_value"] == "1000"


@pytest.mark.parametrize("budget_turnover_limit,closed", [("4", False), ("8", True)])
def test_split_odd_holding_full_close_preserves_exact_delta_and_equity(
    tmp_path, budget_turnover_limit, closed
):
    x = data()
    x["initial_cash"] = "710"
    for a in x["assets"]:
        a["lot"] = "2"
    p = reseal_portfolio(x)
    # Independent P4 budget turnover600/98.4=250/41; P5 actual turnover uses
    # predecision E708.4. Keep both constraints; no runtime threshold widening.
    p["constraints"]["turnover_max"] = budget_turnover_limit
    for row in p["inputs"]["prices"]["data"]:
        row["lot"] = "2"
    put_portfolio(x, p)
    action_id = "123d617e-22e8-442d-aee0-4ef7de5754d7"
    x["actions"] = [
        {
            "action_id": action_id,
            "kind": "SPLIT",
            "security_id": "SYNTH:0",
            "effective_at": x["sessions"][2]["open"],
            "available_at": x["sessions"][1]["close"],
            "value": "0.5",
            "unit": "RATIO",
            "pay_at": None,
        }
    ]
    for r in x["sidecar"]["rows"]:
        if r["session_id"] >= x["sessions"][2]["session_id"]:
            r["in_universe"] = False
            if r["security_id"] == "SYNTH:0":
                r["price"] = "200"
    second = deepcopy(x["decisions"][0])
    second["portfolio_request_utf8"] = canonical(
        retime(reseal_portfolio(x), x["sessions"][2]["close"], 2)
    ).decode()
    x["decisions"].append(second)
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    if not closed:
        assert [f["signed_qty"] for f in r["fills"]] == ["6"]
        assert any(
            o["status"] == "CANCELLED" and o["history"][-1]["reason"] == "RISK_RECHECK_FAILED"
            for o in r["orders"].values()
        )
        return
    assert [f["signed_qty"] for f in r["fills"]] == ["6", "-3"]
    assert r["account"]["equity"] == "706.8"
    assert r["positions"]["SYNTH:0"]["quantity"] == "0"
    assert r["fragments"][0]["net"] == "-3.2"


def test_no_future_session_has_explicit_order_refusal(tmp_path):
    x = data()
    p = retime(reseal_portfolio(x), x["sessions"][-1]["close"], 3)
    put_portfolio(x, p)
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED" and r["orders"] == {} and r["fills"] == []


def test_p4_wide_output_is_consumed_exactly_before_fee_budget_refusal(tmp_path):
    x = data()
    x["initial_cash"] = "1e35"
    p = reseal_portfolio(x)
    for row in p["inputs"]["prices"]["data"]:
        row["price"] = "1"
    put_portfolio(x, p)
    for row in x["sidecar"]["rows"]:
        row["price"] = "1"
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    order = next(iter(r["orders"].values()))
    assert order["original_qty"] == "99999999999999999999999999999999990"
    assert order["status"] == "REJECTED" and r["fills"] == []
    assert F(r["account"]["cash_total"]) == 10**35


@pytest.mark.parametrize("field", ["decisions", "actions", "cashflows", "cancellations"])
def test_event_containers_are_not_silently_coerced(field):
    x = data()
    x[field] = None
    with pytest.raises(ContractError, match="SIMULATION_EVENT_LIST_REQUIRED"):
        validate(seal_sidecar(x))


@pytest.mark.parametrize(
    "kind",
    [
        "sidecar_list",
        "portfolio_bytes",
        "canonical_uuid",
        "control_phase",
        "control_clock",
        "decision_horizon",
    ],
)
def test_strict_public_type_and_time_domains(kind):
    x = data()
    if kind == "sidecar_list":
        x["sidecar"]["rows"] = None
    elif kind == "portfolio_bytes":
        x["decisions"][0]["portfolio_request_utf8"] = 1
    elif kind == "canonical_uuid":
        x["request_id"] = x["request_id"].upper()
    elif kind in ("control_phase", "control_clock"):
        x["cancellations"] = [
            {
                "control_id": x["request_id"],
                "order_id": x["request_id"],
                "requested_at": x["sessions"][1]["open"],
                "available_at": x["sessions"][0]["open"]
                if kind == "control_clock"
                else x["sessions"][1]["open"],
                "received_at": x["sessions"][1]["open"],
                "received_phase": 19 if kind == "control_phase" else 65,
            }
        ]
    else:
        p = retime(reseal_portfolio(x), "2024-03-01T16:00:00Z", 100)
        put_portfolio(x, p)
    with pytest.raises(ContractError):
        validate(seal_sidecar(x))
