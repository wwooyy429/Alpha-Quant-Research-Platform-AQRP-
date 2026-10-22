"""Strict profile boundaries and complete financial failure evidence."""

import uuid
from copy import deepcopy

import pytest

from aqrp.backtest.contracts import BacktestResult, EngineeringBacktestRequest, timestamp, validate
from aqrp.backtest.exact import F
from aqrp.backtest.provider import SignalProvider
from aqrp.backtest.synthetic import fixture_request, seal_sidecar
from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import load

from .test_engine_service import data, put_portfolio, reseal_portfolio, run


@pytest.mark.parametrize(
    "mutator",
    [
        lambda x: x.update(assets=[]),
        lambda x: x.update(sessions=[]),
        lambda x: x["assets"][0].update(borrow_limit="-1"),
        lambda x: x["assets"][0].update(market_id="OTHER"),
        lambda x: x["sidecar"]["rows"][0].update(borrow_limit="-1"),
        lambda x: x["sidecar"]["rows"][0].update(kind="INTRADAY"),
        lambda x: x["sidecar"].update(schema_version="future"),
        lambda x: x["decisions"][0].update(order_type="STOP"),
        lambda x: x["decisions"][0].update(time_in_force="IOC"),
        lambda x: x["decisions"][0].update(expires_session="absent"),
        lambda x: x["decisions"][0].update(order_type="LIMIT", limit_prices={}),
        lambda x: x["decisions"][0].update(limit_prices={"SYNTH:0": "100"}),
    ],
)
def test_strict_profile_negative_controls(mutator):
    x = data()
    mutator(x)
    with pytest.raises(ContractError):
        validate(seal_sidecar(x))


@pytest.mark.parametrize(
    "kind,value,unit,pay",
    [
        ("SPLIT", "0", "RATIO", None),
        ("SPLIT", "2", "WRONG", None),
        ("DIVIDEND", "-1", "PER_CURRENT_SHARE", "2024-02-03T09:00:00Z"),
        ("DIVIDEND", "1", "WRONG", "2024-02-03T09:00:00Z"),
        ("DIVIDEND", "1", "PER_CURRENT_SHARE", "2024-02-01T09:00:00Z"),
        ("DELIST", "1.001", "CCY_PER_SHARE", None),
        ("DELIST", "1", "WRONG", None),
        ("MERGER", "1", "RATIO", None),
    ],
)
def test_corporate_action_domain_controls(kind, value, unit, pay):
    x = data()
    x["actions"] = [
        {
            "action_id": str(uuid.uuid4()),
            "kind": kind,
            "security_id": "SYNTH:0",
            "effective_at": x["sessions"][2]["open"],
            "available_at": x["sessions"][1]["close"],
            "value": value,
            "unit": unit,
            "pay_at": pay,
        }
    ]
    with pytest.raises(ContractError):
        validate(seal_sidecar(x))


@pytest.mark.parametrize("which", ["action", "flow", "control"])
def test_duplicate_economic_event_identity_rejected(which):
    x = data()
    key = str(uuid.uuid4())
    t = x["sessions"][1]["open"]
    if which == "action":
        row = {
            "action_id": key,
            "kind": "SPLIT",
            "security_id": "SYNTH:0",
            "effective_at": t,
            "available_at": t,
            "value": "2",
            "unit": "RATIO",
            "pay_at": None,
        }
        x["actions"] = [row, deepcopy(row)]
    elif which == "flow":
        row = {"flow_id": key, "at": t, "amount": "100"}
        x["cashflows"] = [row, deepcopy(row)]
    else:
        row = {
            "control_id": key,
            "order_id": str(uuid.uuid4()),
            "requested_at": t,
            "available_at": t,
            "received_at": t,
            "received_phase": 65,
        }
        x["cancellations"] = [row, deepcopy(row)]
    with pytest.raises(ContractError):
        validate(seal_sidecar(x))


def test_frozen_objects_and_no_early_provider_release():
    with pytest.raises(ContractError):
        EngineeringBacktestRequest({})
    with pytest.raises(ContractError):
        validate({})
    request = fixture_request()
    with pytest.raises(Exception):
        request.raw = b"tampered"
    provider = SignalProvider(load(request.raw)["decisions"])
    with pytest.raises(ContractError, match="SIGNAL_NOT_AVAILABLE_AT_DECISION"):
        provider.release("2024-02-01T15:59:59Z")
    assert BacktestResult(b"{}").read() == {}
    assert timestamp("2024-02-01T08:00:00+08:00") == "2024-02-01T00:00:00.000000+00:00"


@pytest.mark.parametrize("price", ["80", "0"])
def test_known_delisting_cash_recovery_never_fabricates_unknown_zero(tmp_path, price):
    x = data()
    t = x["sessions"][2]["open"]
    x["actions"] = [
        {
            "action_id": str(uuid.uuid4()),
            "kind": "DELIST",
            "security_id": "SYNTH:0",
            "effective_at": t,
            "available_at": t,
            "value": price,
            "unit": "CCY_PER_SHARE",
            "pay_at": None,
        }
    ]
    for row in x["sidecar"]["rows"]:
        if row["security_id"] == "SYNTH:0" and row["session_id"] >= x["sessions"][2]["session_id"]:
            row.update(status="DELISTED", tradable=False, in_universe=False, price=None)
    result = run(x, tmp_path)
    assert result["status"] == "SUCCEEDED", result
    assert result["positions"]["SYNTH:0"]["quantity"] == "0"
    assert result["account"]["cash_total"] == ("818.1" if price == "80" else "98.1")
    assert len(result["liquidations"]) == 1 and len(result["fills"]) == 1
    assert result["performance"]["commission"] == "1"


def test_unknown_delisting_and_stale_marks_fail_with_position_preserved(tmp_path):
    x = data()
    for row in x["sidecar"]["rows"]:
        if row["security_id"] == "SYNTH:0" and row["session_id"] >= x["sessions"][2]["session_id"]:
            row.update(status="DELISTED", tradable=False, in_universe=False, price=None)
    r = run(x, tmp_path / "unknown")
    assert r["status"] == "FAILED" and r["reasons"] == ["UNRESOLVED_DELISTING"]
    assert r["last_committed_account"]["marked_value"] == "900"
    for row in x["sidecar"]["rows"]:
        if row["status"] == "DELISTED":
            row["status"] = "SUSPENDED"
    r = run(x, tmp_path / "stale")
    assert r["status"] == "FAILED" and r["reasons"] == ["STALE_POSITION_MARK"]


def test_external_flow_is_not_strategy_profit(tmp_path):
    x = data()
    x["cashflows"] = [{"flow_id": str(uuid.uuid4()), "at": "2024-02-03T10:00:00Z", "amount": "500"}]
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    assert r["account"]["cash_total"] == "598.1"
    assert r["performance"]["net_pnl"] == "-1.9"
    assert F(r["performance"]["cumulative_return"]["value"]) == F(-19, 10000)
    assert r["performance"]["session_intervals"] == 4


def test_infeasible_p4_never_generates_orders(tmp_path):
    x = data()
    p = reseal_portfolio(x)
    p["constraints"]["per_asset"] = {a["security_id"]: "0.01" for a in x["assets"]}
    put_portfolio(x, p)
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED" and r["orders"] == {} and r["fills"] == []


def test_unknown_cancel_and_expiry_before_eligibility_are_recorded_failures(tmp_path):
    x = data()
    t = x["sessions"][1]["open"]
    x["cancellations"] = [
        {
            "control_id": str(uuid.uuid4()),
            "order_id": str(uuid.uuid4()),
            "requested_at": t,
            "available_at": t,
            "received_at": t,
            "received_phase": 60,
        }
    ]
    r = run(x, tmp_path / "cancel")
    assert r["reasons"] == ["UNKNOWN_CANCELLATION_ORDER"]
    x["cancellations"] = []
    x["decisions"][0].update(time_in_force="GTC", expires_session=x["sessions"][0]["session_id"])
    r = run(x, tmp_path / "expiry")
    assert r["reasons"] == ["EXPIRY_BEFORE_ELIGIBILITY"]
