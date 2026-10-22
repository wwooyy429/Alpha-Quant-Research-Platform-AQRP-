"""BT-004: past volume, latest visible revision, exact ADV and shared execution cap."""

from copy import deepcopy

import pytest

from aqrp.backtest.contracts import validate
from aqrp.backtest.synthetic import seal_sidecar
from aqrp.core.errors import ContractError
from aqrp.execution.liquidity import visible_adv

from .test_engine_service import data, run


def test_asof_adv_never_reads_future_volume_or_revision():
    x = data()
    assert (
        visible_adv(x, "SYNTH:0", x["sessions"][0]["open"])["reason"] == "ADV_HISTORY_NOT_AVAILABLE"
    )
    t = x["sessions"][0]["close"]
    assert visible_adv(x, "SYNTH:0", t)["average"] == 100
    future = deepcopy(x["sidecar"]["volume_history"][0])
    future.update(shares="0", revision_id=2, available_at=x["sessions"][2]["open"])
    x["sidecar"]["volume_history"].append(future)
    assert visible_adv(x, "SYNTH:0", t)["average"] == 100
    x["liquidity"]["lookback_sessions"] = 2
    assert visible_adv(x, "SYNTH:0", t)["average"] is None
    out = visible_adv(x, "SYNTH:0", x["sessions"][2]["open"])
    assert out["average"] == 50 and out["history_revisions"] == [2, 1]
    x["sidecar"]["volume_history"].reverse()
    assert visible_adv(x, "SYNTH:0", x["sessions"][2]["open"])["average"] == 50
    x["liquidity"]["minimum_adv"] = "60"
    assert (
        visible_adv(x, "SYNTH:0", x["sessions"][2]["open"])["reason"]
        == "ADV_BELOW_REGISTERED_MINIMUM"
    )


@pytest.mark.parametrize("mode", ["missing", "null", "late", "below"])
def test_missing_null_late_or_low_history_rejects_submission(tmp_path, mode):
    x = data()
    history = x["sidecar"]["volume_history"]
    if mode == "missing":
        x["sidecar"]["volume_history"] = history[1:]
    elif mode == "null":
        history[0]["shares"] = None
    elif mode == "late":
        history[0]["available_at"] = x["sessions"][1]["open"]
    else:
        history[0]["shares"] = "9.99"
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED" and r["fills"] == []
    assert (
        next(iter(r["orders"].values()))["history"][-1]["reason"]
        == "ADV_HISTORY_OR_THRESHOLD_REJECTED"
    )


def test_adv_five_limits_physical_ten_capacity_then_gtc_can_finish(tmp_path):
    x = data()
    x["liquidity"]["minimum_adv"] = "1"
    x["sidecar"]["volume_history"][0]["shares"] = "5"
    x["decisions"][0]["time_in_force"] = "GTC"
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    assert [f["signed_qty"] for f in r["fills"]] == ["5", "4"]
    assert r["performance"]["commission"] == "2"
    assert r["account"]["cash_total"] == "97.1"


def test_gtc_rechecks_new_visible_history_without_refunding_paid_fees(tmp_path):
    x = data()
    x.update(initial_cash="1600", fee_budget="20")
    x["decisions"][0]["time_in_force"] = "GTC"
    for r in x["sidecar"]["volume_history"]:
        if r["security_id"] == "SYNTH:0" and r["session_id"] != x["sessions"][0]["session_id"]:
            r["shares"] = "0"
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    assert len(r["fills"]) == 1 and r["performance"]["commission"] == "1"
    assert next(iter(r["orders"].values()))["expired_remaining"] == "5"


@pytest.mark.parametrize(
    "mode", ["lookback", "minimum", "list", "duplicate", "negative", "clock", "future_event"]
)
def test_history_schema_and_clock_integrity(mode):
    x = data()
    if mode == "lookback":
        x["liquidity"]["lookback_sessions"] = 0
    elif mode == "minimum":
        x["liquidity"]["minimum_adv"] = "0"
    elif mode == "list":
        x["sidecar"]["volume_history"] = None
    elif mode == "duplicate":
        x["sidecar"]["volume_history"].append(deepcopy(x["sidecar"]["volume_history"][0]))
    elif mode == "negative":
        x["sidecar"]["volume_history"][0]["shares"] = "-1"
    elif mode == "clock":
        x["sidecar"]["volume_history"][0]["available_at"] = x["sessions"][0]["open"]
    else:
        x["sidecar"]["volume_history"][0]["event_time"] = x["sessions"][1]["close"]
    with pytest.raises(ContractError):
        validate(seal_sidecar(x))
