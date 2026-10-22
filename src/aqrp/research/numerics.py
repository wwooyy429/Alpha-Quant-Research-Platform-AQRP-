"""Explicit scalar/section conventions; invalid observations retain null semantics."""

import math
import operator

import numpy as np

from aqrp.core.errors import ContractError


def array(values):
    try:
        return np.array([np.nan if x is None else float(x) for x in values], dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ContractError("NON_NUMERIC_INPUT") from exc


def ranks(values):
    x = array(values)
    if not np.isfinite(x).all():
        raise ContractError("NONFINITE_RANK_INPUT")
    return np.array([1 + sum(x < v) + (sum(x == v) - 1) / 2 for v in x], dtype=float)


def correlation(x, y, *, rank=False, min_n=3):
    a, b = array(x), array(y)
    if len(a) != len(b):
        raise ContractError("PAIR_LENGTH_MISMATCH")
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    n = len(a)
    if n < min_n:
        return {"value": None, "n": n, "reason": "INSUFFICIENT_PAIRS"}
    if rank:
        a, b = ranks(a), ranks(b)
    a, b = a - a.mean(), b - b.mean()
    scale = float(np.linalg.norm(a) * np.linalg.norm(b))
    return {
        "value": float(np.clip(a @ b / scale, -1, 1)) if scale else None,
        "n": n,
        "reason": "NONE" if scale else "ZERO_VARIANCE",
    }


def ic_summary(values):
    x = array(values)
    x = x[np.isfinite(x)]
    n = len(x)
    mean = float(x.mean()) if n else None
    sd = float(x.std(ddof=1)) if n > 1 else None
    return {
        "n": n,
        "mean": mean,
        "std_ddof1": sd,
        "icir": mean / sd if sd else None,
        "annualized": False,
        "positive_fraction": float(sum(x > 0) / n) if n else None,
        "zero_fraction": float(sum(x == 0) / n) if n else None,
    }


def rolling(values, length, op, other=None):
    if type(length) is not int or length < 1:
        raise ContractError("INVALID_WINDOW")
    x = array(values)
    y = array(other) if other is not None else None
    allowed = {"mean", "std", "sum", "min", "max", "correlation", "ts_rank", "delay", "delta"}
    if op not in allowed or (op == "correlation" and (y is None or len(y) != len(x))):
        raise ContractError("INVALID_OPERATOR")
    out = []
    for i in range(len(x)):
        if op in ("delay", "delta"):
            value = x[i - length] if i >= length else np.nan
            if op == "delta":
                value = x[i] - value
        else:
            w = x[max(0, i - length + 1) : i + 1]
            value = np.nan
            if len(w) == length and np.isfinite(w).all():
                if op == "correlation":
                    v = y[i - length + 1 : i + 1]
                    value = correlation(w, v, min_n=2)["value"] if np.isfinite(v).all() else None
                elif op == "ts_rank":
                    value = ranks(w)[-1] / length
                elif op == "std":
                    value = w.std(ddof=1) if length > 1 else np.nan
                else:
                    value = getattr(w, op)()
        out.append(float(value) if value is not None and np.isfinite(value) else None)
    return out


def conditional(left, comparison, right, yes, no):
    ops = {
        "lt": operator.lt,
        "le": operator.le,
        "gt": operator.gt,
        "ge": operator.ge,
        "eq": operator.eq,
        "ne": operator.ne,
    }
    if comparison not in ops or not all(len(v) == len(left) for v in (right, yes, no)):
        raise ContractError("INVALID_CONDITIONAL")
    return [
        None
        if a is None or b is None or not math.isfinite(a) or not math.isfinite(b)
        else (t if ops[comparison](a, b) else f)
        for a, b, t, f in zip(left, right, yes, no)
    ]


def clean(values, method, parameters):
    x = array(values)
    valid = np.isfinite(x)
    x[~valid] = np.nan
    v = x[valid]
    if method not in ("none", "mad", "quantile"):
        raise ContractError("INVALID_CLEAN_METHOD")
    if len(v) and method == "mad":
        k = parameters["k"]
        if not math.isfinite(k) or k <= 0:
            raise ContractError("INVALID_MAD_K")
        median = np.median(v)
        mad = np.median(abs(v - median))
        if mad == 0:
            x[:] = np.nan
        else:
            x[valid] = np.clip(v, median - k * mad, median + k * mad)
    if len(v) and method == "quantile":
        low, high = parameters["quantiles"]
        if not 0 <= low < high <= 1:
            raise ContractError("INVALID_QUANTILES")
        x[valid] = np.clip(v, *np.quantile(v, [low, high], method="linear"))
    return [float(v) if np.isfinite(v) else None for v in x]


def standardize(values, method):
    x = array(values)
    mask = np.isfinite(x)
    v = x[mask]
    if method not in ("none", "zscore", "rank"):
        raise ContractError("INVALID_STANDARDIZATION")
    if method == "rank" and len(v):
        x[mask] = ranks(v) / len(v)
    if method == "zscore":
        if len(v) < 2 or v.std(ddof=1) == 0:
            x[:] = np.nan
        else:
            x[mask] = (v - v.mean()) / v.std(ddof=1)
    return [float(v) if np.isfinite(v) else None for v in x]


def ols(y, design):
    x, y = np.asarray(design, dtype=float), array(y)
    if x.ndim != 2 or x.shape[0] != len(y) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ContractError("INVALID_OLS_INPUT")
    if len(y) <= x.shape[1]:
        return {"residual": [None] * len(y), "reason": "INSUFFICIENT_OLS_SAMPLE"}
    beta, _, rank, singular = np.linalg.lstsq(x, y, rcond=1e-12)
    if rank != x.shape[1]:
        return {"residual": [None] * len(y), "reason": "RANK_DEFICIENT"}
    return {
        "residual": (y - x @ beta).tolist(),
        "beta": beta.tolist(),
        "rank": int(rank),
        "singular": singular.tolist(),
        "reason": "NONE",
        "rcond": 1e-12,
    }


def group_metrics(scores, labels, groups, min_group_n):
    if type(groups) is not int or groups < 2 or type(min_group_n) is not int or min_group_n < 1:
        raise ContractError("INVALID_GROUP_PROFILE")
    x, y = array(scores), array(labels)
    if len(x) != len(y):
        raise ContractError("PAIR_LENGTH_MISMATCH")
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    bins = (
        np.minimum(groups - 1, np.floor((ranks(x) - 1) * groups / len(x))).astype(int)
        if len(x)
        else []
    )
    counts = [int(sum(bins == k)) if len(x) else 0 for k in range(groups)]
    means = [
        float(y[bins == k].mean()) if counts[k] >= min_group_n else None for k in range(groups)
    ]
    qualified = [i for i, v in enumerate(means) if v is not None]
    monotonicity = correlation(qualified, [means[k] for k in qualified], rank=True, min_n=2)
    return {
        "means": means,
        "counts": counts,
        "n": len(x),
        "tmb": means[-1] - means[0] if means[0] is not None and means[-1] is not None else None,
        "monotonicity": monotonicity,
        "adjacent_violations": sum(
            means[k] > means[k + 1]
            for k in range(groups - 1)
            if means[k] is not None and means[k + 1] is not None
        ),
    }
