"""Direct implementation checks against immutable G1 answers, including old q arithmetic."""

import json
import math
from fractions import Fraction
from pathlib import Path

import pandas as pd
import pytest

from aqrp.research.numerics import clean, group_metrics, ols, rolling
from aqrp.research.pipeline import compose
from aqrp.validation.inference import adjust_pvalues, bandwidth, hac

ROOT = Path(__file__).resolve().parents[2] / "docs/audits/phase-3"


def floats(values):
    return [float(Fraction(v)) if v is not None else None for v in values]


def test_frozen_original_operator_clean_ols_group_and_hac_answers():
    cases = {r["id"]: r for r in json.loads((ROOT / "golden_cases.json").read_bytes())["cases"]}
    r = cases["P3-ROLL"]
    for op, answer in (
        ("mean", 2),
        ("std", 1),
        ("sum", 6),
        ("min", 1),
        ("max", 3),
        ("correlation", -1),
    ):
        assert rolling(r["input"]["x"], 3, op, r["input"]["y"])[-1] == pytest.approx(answer)
    assert rolling([1, 2, 2], 3, "ts_rank")[-1] == pytest.approx(5 / 6)
    r = cases["P3-WINSOR"]
    assert clean(r["input"]["x"], "quantile", {"quantiles": [0.25, 0.75]}) == floats(r["expected"])
    r = cases["P3-MAD"]
    assert clean(r["input"]["x"], "mad", {"k": r["input"]["k"]}) == floats(r["expected"])
    r = cases["P3-OLS"]
    actual = ols(r["input"]["y"], r["input"]["X"])
    assert actual["beta"] == pytest.approx(floats(r["expected_beta"]))
    assert actual["residual"] == pytest.approx(floats(r["expected_residual"]))
    r = cases["P3-GROUP"]
    actual = group_metrics(r["input"]["score"], r["input"]["labels"], r["input"]["q"], 1)
    assert actual["means"] == pytest.approx(floats(r["expected_group_mean"]))
    assert actual["tmb"] == pytest.approx(float(Fraction(r["expected_tmb"])))
    r = hac([1, -1, 1, -1], 1)
    assert r["gamma"] == [1, -0.75] and r["S"] == 0.25 and r["variance"] == 0.0625


def test_supplemental_composite_and_hac_nonzero_answers():
    cases = {
        r["id"]: r
        for r in json.loads((ROOT / "supplemental_cases.json").read_bytes())["other_cases"]
    }
    for name in (
        "COMPOSITE-SIGNED-SCALE",
        "COMPOSITE-POSITIVE-DIRECTION",
        "COMPOSITE-MISSING-INTERSECTION",
    ):
        r = cases[name]
        inp = r["input"]
        frame = pd.DataFrame(
            [
                {
                    "factor_key": key,
                    "security_id": str(i),
                    "session": "2024-01-01",
                    "stage": "final",
                    "score": value,
                }
                for key in ("A", "B")
                for i, value in enumerate(floats(inp[key]))
            ]
        )
        spec = {
            "factor_keys": ["A", "B"],
            "weights": floats(inp["weights"]),
            "directions": inp["directions"],
            "direction_applied": False,
            "input_stage": "final",
            "normalization": inp["normalization"],
            "min_n": 2,
            "redundancy": None,
        }
        actual = compose(frame, spec)
        expected = (
            [-1 / math.sqrt(2), 1 / math.sqrt(2)]
            if name.endswith("INTERSECTION")
            else floats(r["expected"]["composite"])
        )
        assert [row["score"] for row in actual["scores"]] == pytest.approx(expected)
    for name in ("HAC-NONZERO-Q1", "HAC-NONZERO-Q2"):
        r = cases[name]
        actual = hac(floats(r["input"]["IC"]), r["input"]["q"])
        for key in ("mean", "S", "variance"):
            assert actual[key] == pytest.approx(float(Fraction(r["expected"][key])))
        assert actual["gamma"] == pytest.approx(floats(r["expected"]["gamma"]))
        assert actual["p_approx"] == pytest.approx(float(r["expected"]["p_approx"]), rel=1e-10)
        assert actual["p"] is None
    r = cases["MULTI-FAILED-FAMILY"]
    for method in ("holm", "by", "bh"):
        actual = adjust_pvalues(
            floats(r["input"]["raw_p"]), method, bh_evidence="preregistered-test-evidence"
        )
        assert actual["adjusted"] == pytest.approx(
            floats(r["expected"][method.upper() if method != "holm" else "Holm"])
        )
        assert not actual["complete"]


def test_growth_profile_integer_boundaries():
    profile = json.loads((ROOT / "hac_growth_cases.json").read_bytes())
    for row in profile["integer_root_boundaries"]:
        assert bandwidth(row["N"], 1, 0) == row["r"]
    for row in profile["profile_cases"]:
        assert bandwidth(row["N"], row["h"], row["m0"]) == row["q"]
        assert (row["N"] >= max(252, 20 * (row["q"] + 1))) == row["numeric_screen"]
