"""PIT company-action research views; no accounts, fills or dividend ledger."""

from decimal import Decimal, localcontext

from aqrp.core.errors import DataQualityError
from aqrp.core.units import decimal


def action_view(bars, actions, basis, sessions):
    output = [dict(r) for r in bars]
    if basis == "RAW":
        return output
    if basis == "split_adjusted":
        for r in output:
            ratio = Decimal(1)
            for a in actions:
                if (
                    a["type"] == "SPLIT"
                    and a["security_id"] == r["security_id"]
                    and a["effective_at"] > r["event_time"]
                ):
                    ratio *= a["split_ratio"]
            with localcontext() as ctx:
                ctx.prec = 80
                for f in ("open", "high", "low", "close"):
                    r[f] = decimal(r[f] / ratio) if r[f] is not None else None
                r["volume"] = decimal(r["volume"] * ratio) if r["volume"] is not None else None
            r["price_basis"] = basis
        return output
    if basis != "total_return":
        raise DataQualityError("UNKNOWN_PRICE_BASIS", "price_basis")
    by_security = {}
    for r in output:
        by_security.setdefault(r["security_id"], []).append(r)
    indices = {s: i for i, s in enumerate(sorted(sessions))}
    for rows in by_security.values():
        rows.sort(key=lambda r: r["session_date"])
        previous, index = None, Decimal(1)
        for r in rows:
            if r["close"] is None or r["quality_status"] != "VALID":
                raise DataQualityError("RETURN_GAP", "close")
            if previous is not None:
                if indices[r["session_date"]] != indices[previous["session_date"]] + 1:
                    raise DataQualityError("RETURN_SESSION_GAP", "session_date")
                split, cash = Decimal(1), Decimal(0)
                period_actions = [
                    a
                    for a in actions
                    if a["security_id"] == r["security_id"]
                    and previous["event_time"] < a["effective_at"] <= r["event_time"]
                ]
                if len({a["effective_at"] for a in period_actions if a["type"] == "SPLIT"}) > 1:
                    raise DataQualityError("MULTI_SPLIT_PERIOD_UNSUPPORTED", "action")
                for a in period_actions:
                    if a["type"] == "SPLIT":
                        split *= a["split_ratio"]
                    elif a["type"] == "CASH_DIVIDEND":
                        if a["dividend_basis"] != "PER_OLD_SHARE":
                            raise DataQualityError("UNKNOWN_DIVIDEND_BASIS", "action")
                        cash += a["cash_per_share"]
                with localcontext() as ctx:
                    ctx.prec = 80
                    index *= (split * r["close"] + cash) / previous["close"]
            r["total_return_index"] = float(index)
            r["price_basis"] = basis
            previous = r
    return output
