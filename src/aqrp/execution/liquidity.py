"""BT-004: completed, already available historical sessions alone enter the ADV gate."""

from aqrp.backtest.exact import F, money
from aqrp.core.time import utc


def visible_adv(config, sid, as_of):
    clock = utc(as_of)
    n = config["liquidity"]["lookback_sessions"]
    completed = [s["session_id"] for s in config["sessions"] if utc(s["close"]) <= clock]
    required = completed[-n:]
    rows = {}
    for r in config["sidecar"]["volume_history"]:
        if (
            r["security_id"] == sid
            and utc(r["available_at"]) <= clock
            and utc(r["event_time"]) <= clock
        ):
            key = r["session_id"]
            if key not in rows or (utc(r["available_at"]), r["revision_id"]) > (
                utc(rows[key]["available_at"]),
                rows[key]["revision_id"],
            ):
                rows[key] = r
    if len(required) < n or any(day not in rows or rows[day]["shares"] is None for day in required):
        return {
            "passed": False,
            "reason": "ADV_HISTORY_NOT_AVAILABLE",
            "as_of": clock.isoformat(),
            "sessions": required,
            "average": None,
        }
    average = sum((money(rows[day]["shares"]) for day in required), F(0)) / n
    passed = average >= money(config["liquidity"]["minimum_adv"])
    return {
        "passed": passed,
        "reason": None if passed else "ADV_BELOW_REGISTERED_MINIMUM",
        "as_of": clock.isoformat(),
        "sessions": required,
        "average": average,
        "minimum": money(config["liquidity"]["minimum_adv"]),
        "history_revisions": [rows[day]["revision_id"] for day in required],
    }
