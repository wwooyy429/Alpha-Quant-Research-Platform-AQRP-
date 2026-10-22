import hashlib
import json
from copy import deepcopy
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.portfolio.construct import build_candidate, compute
from aqrp.portfolio.contracts import F, PortfolioRequest, TargetCandidate, load
from aqrp.portfolio.service import construct_approved, construct_engineering, replay_engineering
from aqrp.risk.checks import assess, check_target

from .helpers import FIXTURES, fixture, reseal

COMMIT = "a" * 40


@pytest.mark.parametrize("name", ["base", "x01", "x03", "x04", "odd_hold", "short_close"])
def test_frozen_independent_full_inputs(name, tmp_path):
    x = fixture(name)
    before = deepcopy(x)
    result = construct_engineering(PortfolioRequest.create(x), tmp_path, COMMIT).read()
    expected = json.loads((FIXTURES / "expected.json").read_bytes())["cases"][name]
    assert result["status"] == expected["status"]
    assert x == before
    assert result["executable"] is False and result["financial_approval"] == "NONE"
    assert result["input_lineage"]["environment_hash"] == digest(
        result["input_lineage"]["environment"]
    )
    assert result["context"]["currency"] == "CCY"
    assert "rounding_residual" in result["rounding"] and "ranked" in result["selection"]
    assert (
        result["risk"]["candidate_hash"]
        == hashlib.sha256((tmp_path / result["run_id"] / "candidate.json").read_bytes()).hexdigest()
    )
    if result["status"] == "SUCCEEDED":
        assert result["target"]["quantities"] == expected["quantities"]
        assert result["target"]["cash"] == expected["cash"]
        assert all(
            not p["executable"] and p["delta_qty"] != "0" for p in result["rebalance_proposals"]
        )
        assert (
            Decimal(result["target"]["cash"])
            + sum(
                Decimal(result["target"]["quantities"][s])
                * Decimal(x["inputs"]["prices"]["data"][i]["price"])
                for i, s in enumerate(("SYNTH:A", "SYNTH:B"))
            )
            == 1000
        )
    else:
        assert expected["reason"] in result["reasons"]
        assert "target" not in result
    if name == "x03":
        assert result["risk"]["pre"]["metrics"]["beta"] == "0"
        assert result["risk"]["post"]["metrics"]["beta"] == "-0.5"
        assert result["risk"]["post"]["metrics"]["free_cash"] == "500"
    if name == "x04":
        assert result["risk"]["pre"]["metrics"]["turnover"] == "0.6"
        assert result["risk"]["post"]["metrics"]["turnover"] == "1.1"
    replay = replay_engineering(tmp_path, result["run_id"])
    assert replay["result"]["status"] == result["status"]


@pytest.mark.parametrize(
    "current,target,flag,reason",
    [
        ("15", "20", True, "DELTA_LOT_MISMATCH"),
        ("15", "15", False, None),
        ("15", "0", True, None),
        ("15", "0", False, "DELTA_LOT_MISMATCH"),
        ("-15", "0", True, None),
        ("-15", "0", False, "DELTA_LOT_MISMATCH"),
        ("15", "-10", True, "DELTA_LOT_MISMATCH"),
        ("-15", "10", True, "DELTA_LOT_MISMATCH"),
        ("10", "20", False, None),
        ("-15", "-10", True, "DELTA_LOT_MISMATCH"),
        ("-15", "-20", True, "DELTA_LOT_MISMATCH"),
        ("-15", "-15", False, None),
        ("10", "15", True, "TARGET_LOT_MISMATCH"),
    ],
)
def test_exact_quantity_gate_reference(current, target, flag, reason):
    x, m, p, _, _, _, _ = compute(reseal(fixture()))
    x["profile"]["allow_full_close_odd_lot"] = flag
    m["prices"]["SYNTH:A"]["lot"] = "10"
    p["SYNTH:A"] = F(current)
    d = assess(x, m, p, {"SYNTH:A": F(target), "SYNTH:B": F(0)}, post=True)
    failures = [
        c["code"] for c in d["checks"] if c["code"].endswith("LOT_MISMATCH") and not c["passed"]
    ]
    assert (reason in failures) if reason else not failures


@pytest.mark.parametrize("flag", [True, False])
def test_full_close_is_not_a_tradability_or_sellable_waiver(flag):
    x, m, p, _, _, _, _ = compute(reseal(fixture()))
    x["profile"]["allow_full_close_odd_lot"] = flag
    m["prices"]["SYNTH:A"]["lot"] = "10"
    m["status"]["SYNTH:A"]["tradable"] = False
    m["permissions"]["SYNTH:A"]["sellable_qty"] = "0"
    p["SYNTH:A"] = F(15)
    d = assess(x, m, p, {"SYNTH:A": F(0), "SYNTH:B": F(0)}, post=True)
    assert not d["passed"]
    assert {"NOT_TRADABLE", "SELLABLE"} <= {c["code"] for c in d["checks"] if not c["passed"]}
    hold = assess(x, m, p, dict(p), post=True)
    assert not any(c["code"] == "NOT_TRADABLE" for c in hold["checks"])


def test_candidate_tamper_and_wrong_request():
    req = reseal(fixture())
    candidate = build_candidate(req)
    assert (
        check_target(candidate, req)["candidate_hash"] == hashlib.sha256(candidate.raw).hexdigest()
    )
    with pytest.raises(ContractError, match="CANDIDATE_TAMPERED"):
        check_target(TargetCandidate(candidate.raw + b" ", candidate.request_hash), req)
    with pytest.raises(ContractError, match="CANDIDATE_REQUEST_MISMATCH"):
        check_target(TargetCandidate(candidate.raw, "0" * 64), req)


def test_formal_cannot_use_engineering_flags(tmp_path):
    x = fixture()
    x["source"]["financial_approval"] = "ResearchValidated"
    result = construct_approved(PortfolioRequest.create(x), tmp_path, COMMIT).read()
    assert result["reasons"] == ["APPROVAL_REQUIRED"] and "target" not in result


@given(st.integers(1, 1000), st.integers(1, 1000), st.integers(1, 1000))
def test_score_scale_order_and_rounding_properties(a, b, scale):
    x = fixture()
    x["inputs"]["scores"][0]["data"]["rows"][0]["score"] = str(a)
    x["inputs"]["scores"][0]["data"]["rows"][1]["score"] = str(b)
    original = compute(reseal(x))
    w = original[5]["scores"]
    y = deepcopy(x)
    for r in y["inputs"]["scores"][0]["data"]["rows"]:
        r["score"] = str(int(r["score"]) * scale)
    y["inputs"]["scores"][0]["data"]["rows"].reverse()
    changed = compute(reseal(y))
    assert original[3:5] == changed[3:5]
    assert all(abs(original[4][s]) <= abs(original[3][s]) for s in w)


@pytest.mark.parametrize("weighting", ["equal", "score"])
def test_long_short_real_two_legs(weighting):
    x = fixture()
    x["policy"].update(mode="LONG_SHORT", weighting=weighting, gross="1", net="0")
    req = reseal(x)
    candidate = build_candidate(req)
    d = check_target(candidate, req)
    assert d["passed"]
    assert d["post"]["metrics"]["weights"] == {"SYNTH:A": "0.5", "SYNTH:B": "-0.5"}
    assert d["post"]["metrics"]["gross"] == "1" and d["post"]["metrics"]["net"] == "0"


def test_multifactor_intersection_signed_coefficients():
    x = fixture()
    s = deepcopy(x["inputs"]["scores"][0])
    s["ref"] = "second"
    s["data"]["factor_key"] = "F2"
    s["data"]["rows"][0]["score"] = "4"
    s["data"]["rows"][1]["score"] = "2"
    x["inputs"]["scores"][0]["data"]["rows"][0]["score"] = "2"
    x["inputs"]["scores"][0]["data"]["rows"][1]["score"] = "4"
    x["inputs"]["scores"].append(s)
    x["policy"]["factor_weights"] = {"F1": "3", "F2": "1"}
    data = load(build_candidate(reseal(x)).raw)
    assert data["selection"]["scores"] == {"SYNTH:A": "2.5", "SYNTH:B": "3.5"}
    assert data["rounded"] == {"SYNTH:A": "41", "SYNTH:B": "58"}
    s["data"]["rows"][0].update(valid=False, score=None)
    assert load(build_candidate(reseal(x)).raw)["rounded"] == {"SYNTH:A": "0", "SYNTH:B": "100"}


@pytest.mark.parametrize(
    "mode,weighting,values,expected",
    [
        ("LONG_ONLY", "score", ("-1", "-2"), "NO_POSITIVE_SCORE"),
        ("LONG_ONLY", "equal", ("-1", "-2"), "NONE"),
        ("LONG_SHORT", "score", ("1", "1"), "INFEASIBLE_EMPTY_LEG"),
    ],
)
def test_zero_negative_and_empty_leg(mode, weighting, values, expected, tmp_path):
    x = fixture()
    x["policy"].update(mode=mode, weighting=weighting, net="0" if mode == "LONG_SHORT" else "1")
    for r, s in zip(x["inputs"]["scores"][0]["data"]["rows"], values):
        r["score"] = s
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    if expected.startswith("INFEASIBLE"):
        assert r["status"] == "INFEASIBLE" and expected in r["reasons"]
    else:
        assert r["status"] == "SUCCEEDED"


def test_risk_reasons_no_silent_repair(tmp_path):
    x = fixture()
    x["constraints"]["per_asset"]["SYNTH:A"] = "0.7"
    result = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert result["status"] == "REJECTED" and "ASSET_WEIGHT" in result["reasons"]
    assert "target" not in result


def test_failure_and_immutable_terminal_evidence(tmp_path):
    req = PortfolioRequest(b"{broken")
    r = construct_engineering(req, tmp_path, COMMIT).read()
    assert r["reasons"] == ["INVALID_JSON"] and r["manifest"]["status"] == "FAILED"
    path = tmp_path / r["run_id"] / "result.json"
    path.write_bytes(b"{}")
    with pytest.raises(ContractError):
        replay_engineering(tmp_path, r["run_id"])


@pytest.mark.parametrize(
    "mode,net,quantities,cash,gross,free",
    [
        ("LONG_ONLY", "1", {"SYNTH:A": "10", "SYNTH:B": "10"}, "300", "0.7", "300"),
        ("LONG_SHORT", "0", {"SYNTH:A": "10", "SYNTH:B": "-10"}, "1100", "0.7", "300"),
    ],
)
def test_golden_g10_g11_complete_public_service(mode, net, quantities, cash, gross, free, tmp_path):
    x = fixture()
    x["policy"].update(mode=mode, weighting="equal", gross="1", net=net)
    for row, price in zip(x["inputs"]["prices"]["data"], ["30", "40"]):
        row.update(price=price, lot="10")
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert r["status"] == "SUCCEEDED"
    assert r["target"]["quantities"] == quantities
    assert (r["target"]["cash"], r["target"]["gross"], r["target"]["free_cash"]) == (
        cash,
        gross,
        free,
    )
