"""Independent closed-form answers frozen before implementation; no tested oracle."""

import math

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from aqrp.core.errors import ContractError
from aqrp.research.numerics import (
    array,
    clean,
    conditional,
    correlation,
    group_metrics,
    ic_summary,
    ols,
    ranks,
    rolling,
    standardize,
)


def test_golden_ic_rank_and_ddof():
    x = [-2, -1, 0, 1, 2]
    y = [-0.04, 0.01, -0.01, 0.02, 0.05]
    assert correlation(x, y)["value"] == pytest.approx(0.19 / math.sqrt(0.0452), abs=1e-12)
    assert correlation(x, y, rank=True)["value"] == pytest.approx(0.9)
    assert ranks([1, 1, 3]).tolist() == [1.5, 1.5, 3]
    assert correlation([1, 1, 3], [1, 2, 3], rank=True)["value"] == pytest.approx(math.sqrt(3) / 2)
    assert standardize(x, "zscore") == pytest.approx([v / math.sqrt(2.5) for v in x])
    summary = ic_summary([0.1, 0.2, 0.3, None])
    assert summary["mean"] == pytest.approx(0.2)
    assert summary["std_ddof1"] == pytest.approx(0.1)
    assert summary["icir"] == pytest.approx(2)
    assert not summary["annualized"]
    assert ic_summary([])["mean"] is None
    assert ic_summary([0])["icir"] is None
    assert correlation([1, 1, 1], [1, 2, 3])["reason"] == "ZERO_VARIANCE"
    assert correlation([1, None, 3], [1, 2, 3])["n"] == 2


@pytest.mark.parametrize(
    "op,expected",
    [
        ("mean", [None, 1.5, 2.5, 3.5]),
        ("sum", [None, 3, 5, 7]),
        ("min", [None, 1, 2, 3]),
        ("max", [None, 2, 3, 4]),
        ("std", [None, math.sqrt(0.5), math.sqrt(0.5), math.sqrt(0.5)]),
        ("delay", [None, None, 1, 2]),
        ("delta", [None, None, 2, 2]),
        ("ts_rank", [None, 1, 1, 1]),
        ("correlation", [None, -1, -1, -1]),
    ],
)
def test_rolling_closed_form(op, expected):
    values = rolling([1, 2, 3, 4], 2, op, [4, 3, 2, 1])
    for actual, answer in zip(values, expected):
        assert actual is None if answer is None else actual == pytest.approx(answer)


def test_missing_grid_and_conditional():
    assert rolling([1, None, 3, 4], 2, "mean") == [None, None, None, 3.5]
    assert rolling([1], 1, "std") == [None]
    assert rolling([1, 2], 2, "correlation", [None, 3]) == [None, None]
    assert conditional([1, None, 3], "gt", [2, 2, 2], [10] * 3, [0] * 3) == [0, None, 10]
    assert standardize([1, None, 1], "rank") == [0.75, None, 0.75]
    assert standardize([1, 1], "zscore") == [None, None]
    assert clean([1, 2, 100, None], "mad", {"k": 1}) == [1, 2, 3, None]
    assert clean([0, 10, 20, 30, None], "quantile", {"quantiles": [0.25, 0.75]}) == [
        7.5,
        10,
        20,
        22.5,
        None,
    ]
    assert clean([1, 1], "mad", {"k": 1}) == [None, None]
    assert clean([1, float("inf")], "none", {}) == [1, None]
    assert standardize([1, float("inf")], "none") == [1, None]


def test_ols_independent_normal_equations():
    # X'X=diag(4,20), X'y=(12,16): beta=(3,.8); residual orthogonal.
    design = [[1, -3], [1, -1], [1, 1], [1, 3]]
    y = [1, 1, 5, 5]
    fit = ols(y, design)
    assert fit["beta"] == pytest.approx([3, 0.8])
    assert fit["residual"] == pytest.approx([0.4, -1.2, 1.2, -0.4])
    assert np.asarray(design).T @ np.array(fit["residual"]) == pytest.approx([0, 0], abs=1e-12)
    assert ols([1, 2], [[1, 0], [1, 1]])["reason"] == "INSUFFICIENT_OLS_SAMPLE"
    assert ols([1, 2, 3], [[1, 1]] * 3)["reason"] == "RANK_DEFICIENT"
    groups = group_metrics([1, 1, 3, 4], [0.1, 0.3, 0.4, 0.8], 2, 1)
    assert groups["counts"] == [2, 2]
    assert groups["means"] == pytest.approx([0.2, 0.6])
    assert groups["tmb"] == pytest.approx(0.4)
    assert group_metrics([], [], 3, 1)["tmb"] is None


@pytest.mark.parametrize(
    "call",
    [
        lambda: array([object()]),
        lambda: ranks([None]),
        lambda: correlation([1], []),
        lambda: rolling([1], True, "mean"),
        lambda: rolling([1], 1, "eval"),
        lambda: rolling([1], 1, "correlation"),
        lambda: conditional([1], "eval", [1], [1], [0]),
        lambda: clean([1], "unknown", {}),
        lambda: clean([1], "mad", {"k": 0}),
        lambda: clean([1], "quantile", {"quantiles": [0.8, 0.2]}),
        lambda: standardize([1], "unknown"),
        lambda: ols([1], [[float("nan")]]),
        lambda: group_metrics([1], [], 2, 1),
        lambda: group_metrics([], [], 1, 1),
    ],
)
def test_invalid_contracts(call):
    with pytest.raises(ContractError):
        call()


@given(st.lists(st.integers(-100, 100), min_size=3, max_size=20))
def test_correlation_affine_and_z_properties(values):
    if len(set(values)) < 2:
        return
    assert correlation(values, [2 * x + 7 for x in values])["value"] == pytest.approx(1)
    z = standardize(values, "zscore")
    assert sum(z) == pytest.approx(0, abs=1e-12)
    assert sum(x * x for x in z) == pytest.approx(len(z) - 1)
