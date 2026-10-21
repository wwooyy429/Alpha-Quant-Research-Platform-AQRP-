"""Visibility precedes revision choice, which precedes effective interval filtering."""

from aqrp.core.errors import DataQualityError, TimeLeakageError
from aqrp.core.time import utc

from .schemas import LOGICAL_KEYS


def visible_rows(name, records, as_of):
    as_of = utc(as_of, field="as_of")
    groups = {}
    for r in records:
        if r["available_at"] is None or r.get("quality_status") == "UNKNOWN_AVAILABILITY":
            raise TimeLeakageError("UNKNOWN_AVAILABILITY", name)
        if r["event_time"] > as_of or r["available_at"] > as_of:
            continue
        key = tuple(r[k] for k in LOGICAL_KEYS[name])
        groups.setdefault(key, []).append(r)
    output = []
    for revisions in groups.values():
        latest_time = max(r["available_at"] for r in revisions)
        candidates = [r for r in revisions if r["available_at"] == latest_time]
        if len(candidates) != 1:
            raise DataQualityError("CONFLICTING_VISIBLE_REVISIONS", name)
        r = candidates[0]
        if "effective_from" in r:
            if r["effective_from"] > as_of or (
                r["effective_to"] is not None and as_of >= r["effective_to"]
            ):
                continue
        output.append(r)
    return sorted(output, key=lambda r: tuple(str(r[k]) for k in LOGICAL_KEYS[name]))
