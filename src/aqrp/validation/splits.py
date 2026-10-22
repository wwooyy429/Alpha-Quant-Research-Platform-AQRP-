"""Deterministic chronological splits, information-interval purge and walk-forward."""

from datetime import date

from aqrp.core.errors import ContractError
from aqrp.core.time import utc


def validate_splits(spec):
    previous = None
    for name in ("train", "validation", "test"):
        start, end = map(date.fromisoformat, spec[name])
        if start >= end or (previous is not None and start < previous):
            raise ContractError("INVALID_CHRONOLOGICAL_SPLIT")
        previous = end
    if type(spec["embargo_sessions"]) is not int or spec["embargo_sessions"] < 0:
        raise ContractError("INVALID_EMBARGO")


def partition(session, spec):
    day = date.fromisoformat(str(session))
    for name in ("train", "validation", "test"):
        start, end = map(date.fromisoformat, spec[name])
        if start <= day < end:
            return name
    return "outside"


def overlaps(a, b):
    return max(utc(a[0]), utc(b[0])) <= min(utc(a[1]), utc(b[1]))


def purged_train(labels, fit_range, eval_range, fit_cutoff, calendar, embargo, protected_labels=()):
    start, end = fit_range
    eval_start, eval_end = eval_range
    held = [r for r in labels if eval_start <= r["session"] < eval_end and r["label"] is not None]
    protected = [r["information_interval"] for r in [*held, *protected_labels]]
    days = [str(s) for s in calendar]
    forbidden = set()
    for r in [*held, *protected_labels]:
        end_day = utc(r["available_at"]).date().isoformat()
        after = [d for d in days if d > end_day][:embargo]
        forbidden.update(after)
    accepted = []
    rejected = []
    for r in labels:
        if not start <= r["session"] < end:
            continue
        reason = None
        if r["label"] is None:
            reason = "INVALID_LABEL"
        elif utc(r["available_at"]) > utc(fit_cutoff):
            reason = "LABEL_NOT_AVAILABLE_AT_FIT"
        elif any(overlaps(r["information_interval"], interval) for interval in protected):
            reason = "PURGED_INFORMATION_OVERLAP"
        elif r["session"] in forbidden:
            reason = "EMBARGO"
        (rejected if reason else accepted).append({**r, "split_reason": reason or "NONE"})
    return {
        "train": accepted,
        "rejected": rejected,
        "eval": held,
        "fit_cutoff": utc(fit_cutoff),
        "embargo_days": sorted(forbidden),
    }


def walk_forward(labels, windows, calendar, embargo):
    seen = set()
    output = []
    history = []
    for number, w in enumerate(windows):
        if not w["fit"][0] < w["fit"][1] <= w["evaluate"][0] < w["evaluate"][1]:
            raise ContractError("INVALID_WALK_FORWARD_WINDOW")
        if utc(w["fit_cutoff"]) > utc(w["evaluate"][0] + "T00:00:00Z"):
            raise ContractError("FIT_CUTOFF_AFTER_EVALUATION_START")
        fold = purged_train(
            labels, w["fit"], w["evaluate"], w["fit_cutoff"], calendar, embargo, history
        )
        history.extend(fold["eval"])
        unique = []
        for r in fold["eval"]:
            key = (r["security_id"], r["session"], r["horizon"])
            if key not in seen:
                seen.add(key)
                unique.append(r)
        output.append(
            {
                **fold,
                "window": number,
                "eval": unique,
                "cross_fold_policy": "ALL_PRIOR_HELDOUT_PROTECTED",
            }
        )
    return output
