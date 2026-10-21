"""HAC with preregistered growing bandwidth; no inference from ICIR."""

import math

import numpy as np

from aqrp.core.errors import ContractError
from aqrp.research.numerics import array


def bandwidth(n, horizon, dependence):
    if (
        any(type(v) is not int for v in (n, horizon, dependence))
        or n < 1
        or horizon < 1
        or dependence < 0
    ):
        raise ContractError("INVALID_BANDWIDTH_PROFILE")
    low, high = 0, n + 1
    while high - low > 1:
        middle = (low + high) // 2
        if middle**5 <= n:
            low = middle
        else:
            high = middle
    return max(horizon - 1, dependence, low)


def hac(values, lag, *, mode="ARITHMETIC_REFERENCE", qualification=None):
    x = array(values)
    n = len(x)
    if type(lag) is not int or not 0 <= lag < n or not np.isfinite(x).all():
        raise ContractError("INVALID_HAC_INPUT")
    if mode not in ("ARITHMETIC_REFERENCE", "ENGINEERING_DEMO", "FORMAL_ASYMPTOTIC"):
        raise ContractError("INVALID_INFERENCE_MODE")
    u = x - x.mean()
    gamma = [float(u[k:] @ u[: n - k] / n) for k in range(lag + 1)]
    s = gamma[0] + 2 * sum((1 - k / (lag + 1)) * gamma[k] for k in range(1, lag + 1))
    variance = s / n
    se = math.sqrt(variance) if variance > 0 else None
    approximate = math.erfc(abs(float(x.mean())) / (math.sqrt(2) * se)) if se else None
    result = {
        "mean": float(x.mean()),
        "n": n,
        "lag": lag,
        "gamma": gamma,
        "S": s,
        "variance": variance,
        "se": se,
        "p": None,
        "p_approx": approximate,
        "inference": "NON_FORMAL",
        "reason": "NON_FORMAL_MODE",
        "small_sample_correction": "none",
    }
    if mode != "FORMAL_ASYMPTOTIC":
        return result
    q = qualification or {}
    reason = "NONE"
    planned = q.get("planned_session_grid", [])
    actual = q.get("actual_session_grid", [])
    if (
        q.get("planned_n") != n
        or not q.get("complete_session_grid")
        or len(planned) != n
        or actual != planned
        or planned != sorted(set(planned))
    ):
        reason = "PLANNED_SAMPLE_MISMATCH"
    elif (
        q.get("horizon") not in (1, 5, 10, 20)
        or type(q.get("m0")) is not int
        or q["m0"] < 0
        or lag != bandwidth(n, q["horizon"], q["m0"])
    ):
        reason = "UNREGISTERED_BANDWIDTH"
    elif n < max(252, 20 * (lag + 1)):
        reason = "INSUFFICIENT_HAC_SAMPLE"
    elif q.get("model") != "BOUNDED_STATIONARY_M_DEPENDENT" or not q.get("proof_artifact_sha256"):
        reason = "DEPENDENCE_MODEL_UNVERIFIED"
    elif not q.get("method_review_record"):
        reason = "METHOD_REVIEW_REQUIRED"
    elif not q.get("human_protocol_record"):
        reason = "FORMAL_PROTOCOL_UNAPPROVED"
    elif se is None:
        reason = "NONPOSITIVE_LONG_RUN_VARIANCE"
    result.update(
        reason=reason,
        p=approximate if reason == "NONE" else None,
        inference="ASYMPTOTIC_NORMAL" if reason == "NONE" else "REJECTED",
    )
    return result


def adjust_pvalues(raw, method, *, bh_evidence=None):
    if not raw or method not in ("holm", "by", "bh") or (method == "bh" and not bh_evidence):
        raise ContractError("INVALID_MULTIPLICITY_PROFILE")
    if any(
        p is not None and (type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1)
        for p in raw
    ):
        raise ContractError("INVALID_MARGINAL_P")
    p = [1.0 if x is None else float(x) for x in raw]
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    out = [0.0] * m
    running = 0.0 if method == "holm" else 1.0
    harmonic = sum(1 / k for k in range(1, m + 1)) if method == "by" else 1
    indices = range(m) if method == "holm" else range(m - 1, -1, -1)
    for k in indices:
        value = p[order[k]] * (m - k) if method == "holm" else p[order[k]] * m * harmonic / (k + 1)
        running = max(running, min(1, value)) if method == "holm" else min(running, value)
        out[order[k]] = running
    return {
        "raw": list(raw),
        "adjusted": out,
        "method": method,
        "m": m,
        "complete": all(x is not None for x in raw),
        "failed_slots": [i for i, x in enumerate(raw) if x is None],
        "bh_evidence": bh_evidence,
    }
