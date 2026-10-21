import math

import pytest

from aqrp.core.errors import ContractError
from aqrp.validation.inference import adjust_pvalues, bandwidth, hac


def test_hac_independent_exact_arithmetic():
    # u=(-1.5,-.5,.5,1.5), gamma0=5/4, gamma1=5/16.
    r = hac([1, 2, 3, 4], 1)
    assert r["gamma"] == [1.25, 0.3125]
    assert r["S"] == 25 / 16
    assert r["variance"] == 25 / 64
    assert r["se"] == 5 / 8
    assert r["p_approx"] == pytest.approx(math.erfc(2.5 / (math.sqrt(2) * 0.625)))
    assert r["p"] is None
    assert bandwidth(252, 1, 0) == 3
    assert bandwidth(3124, 5, 2) == 4
    assert bandwidth(3125, 5, 2) == 5
    assert bandwidth(1, 20, 25) == 25


def qualification(n=252):
    from datetime import date, timedelta

    grid = [str(date(2024, 1, 1) + timedelta(days=i)) for i in range(n)]
    return {
        "planned_n": n,
        "complete_session_grid": True,
        "planned_session_grid": grid,
        "actual_session_grid": grid,
        "horizon": 1,
        "m0": 0,
        "model": "BOUNDED_STATIONARY_M_DEPENDENT",
        "proof_artifact_sha256": "a" * 64,
        "method_review_record": "independent-method-review",
        "human_protocol_record": "frozen-human-protocol",
    }


@pytest.mark.parametrize(
    "change,reason",
    [
        ({"planned_n": 251}, "PLANNED_SAMPLE_MISMATCH"),
        ({"complete_session_grid": False}, "PLANNED_SAMPLE_MISMATCH"),
        ({"horizon": 2}, "UNREGISTERED_BANDWIDTH"),
        ({"model": "ACF_GUESS"}, "DEPENDENCE_MODEL_UNVERIFIED"),
        ({"proof_artifact_sha256": None}, "DEPENDENCE_MODEL_UNVERIFIED"),
        ({"method_review_record": None}, "METHOD_REVIEW_REQUIRED"),
        ({"human_protocol_record": None}, "FORMAL_PROTOCOL_UNAPPROVED"),
    ],
)
def test_formal_rejections(change, reason):
    q = {**qualification(), **change}
    r = hac([(-1) ** i for i in range(252)], 3, mode="FORMAL_ASYMPTOTIC", qualification=q)
    assert r["p"] is None and r["reason"] == reason


def test_formal_math_qualification_not_host_authorization():
    r = hac(
        [1 + (-1) ** i for i in range(252)],
        3,
        mode="FORMAL_ASYMPTOTIC",
        qualification=qualification(),
    )
    assert r["inference"] == "ASYMPTOTIC_NORMAL"
    assert (
        hac([1] * 252, 3, mode="FORMAL_ASYMPTOTIC", qualification=qualification())["reason"]
        == "NONPOSITIVE_LONG_RUN_VARIANCE"
    )
    assert (
        hac([1, 2, 3, 4], 1, mode="FORMAL_ASYMPTOTIC", qualification=qualification(4))["reason"]
        == "INSUFFICIENT_HAC_SAMPLE"
    )
    assert hac([1, 2, 3, 4], 0, mode="FORMAL_ASYMPTOTIC")["reason"] == "PLANNED_SAMPLE_MISMATCH"


def test_multiplicity_exact_answers():
    # Sorted .01,.03,.04: Holm .03,.06,.06; BH .03,.04,.04; BY *11/6.
    assert adjust_pvalues([0.04, 0.01, 0.03], "holm")["adjusted"] == pytest.approx(
        [0.06, 0.03, 0.06]
    )
    assert adjust_pvalues([0.04, 0.01, 0.03], "bh", bh_evidence="preapproved-independent-family")[
        "adjusted"
    ] == pytest.approx([0.04, 0.03, 0.04])
    assert adjust_pvalues([0.04, 0.01, 0.03], "by")["adjusted"] == pytest.approx(
        [11 / 150, 11 / 200, 11 / 150]
    )
    r = adjust_pvalues([0.01, None], "holm")
    assert not r["complete"] and r["raw"] == [0.01, None] and r["adjusted"] == [0.02, 1]


@pytest.mark.parametrize(
    "call",
    [
        lambda: bandwidth(0, 1, 0),
        lambda: bandwidth(1, True, 0),
        lambda: hac([], 0),
        lambda: hac([1, None], 0),
        lambda: hac([1], 0, mode="guess"),
        lambda: adjust_pvalues([], "holm"),
        lambda: adjust_pvalues([0.1], "bh"),
        lambda: adjust_pvalues([float("nan")], "holm"),
        lambda: adjust_pvalues([2], "holm"),
    ],
)
def test_invalid_inference(call):
    with pytest.raises(ContractError):
        call()
