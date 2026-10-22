"""BT-003/004: exact ticks, fixed bidirectional domains and worst-case partial fees."""

from aqrp.backtest.exact import F, ceil_tick, floor_tick, round_cent
from aqrp.core.errors import ContractError

LIVE = {"ACCEPTED", "PARTIALLY_FILLED"}
TRANSITIONS = {
    "CREATED": {"SUBMITTED", "REJECTED"},
    "SUBMITTED": {"ACCEPTED", "REJECTED"},
    "ACCEPTED": {"PARTIALLY_FILLED", "FILLED", "CANCELLED", "EXPIRED"},
    "PARTIALLY_FILLED": {"PARTIALLY_FILLED", "FILLED", "CANCELLED", "EXPIRED"},
}


def transition(order, status, reason=None):
    if status not in TRANSITIONS.get(order["status"], set()):
        raise ContractError("ILLEGAL_ORDER_TRANSITION")
    order["status"] = status
    order["history"].append({"status": status, "reason": reason})


def commission(qty, p):
    if qty <= 0 or qty.denominator != 1 or p <= 0:
        raise ContractError("INVALID_FILL_DOMAIN")
    return round_cent(max(F(1), qty * p / 1000))


def bounds(p0, side, kind="MARKET", limit=None):
    if side not in ("BUY", "SELL") or kind not in ("MARKET", "LIMIT") or p0 <= 0:
        raise ContractError("INVALID_EXECUTION_PROFILE")
    low, high = ceil_tick(p0 * F(95, 100)), floor_tick(p0 * F(105, 100))
    if kind == "LIMIT":
        if limit is None or limit <= 0 or floor_tick(limit) != limit:
            raise ContractError("INVALID_LIMIT_PRICE")
        if side == "BUY":
            high = min(high, limit)
        else:
            low = max(low, limit)
    elif limit is not None:
        raise ContractError("MARKET_WITH_LIMIT")
    if low > high:
        raise ContractError("EMPTY_PRICE_DOMAIN")
    return low, high


def fee_upper(qty, upper):
    return qty * ceil_tick(max(F(1), upper / 1000))


def execute_price(order, raw):
    actual = (
        ceil_tick(raw * F(1001, 1000)) if order["side"] == "BUY" else floor_tick(raw * F(999, 1000))
    )
    if not order["low"] <= raw <= order["high"] or not order["low"] <= actual <= order["high"]:
        return None
    return actual


def fill_quantity(order, capacity, position):
    maximum = min(order["remaining"], capacity)
    lot = order["lot"]
    if maximum <= 0:
        return F(0)
    if (
        order["remaining"] == abs(position)
        and order["signed_remaining"] == -position
        and maximum == abs(position)
    ):
        return maximum
    return (maximum // lot) * lot
