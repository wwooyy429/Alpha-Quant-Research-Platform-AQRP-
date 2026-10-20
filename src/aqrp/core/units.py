"""Exact synthetic units. No float-to-money coercion."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext

from .errors import ContractError, UnsupportedCurrency


@dataclass(frozen=True)
class MarketProfile:
    profile_id: str = "SYNTHETIC_V1"
    currency: str = "SYNCCY"
    markets: tuple = ("SYN_A", "SYN_B")
    tick: Decimal = Decimal("0.01")
    share_unit: Decimal = Decimal("1")
    schema_version: str = "data/1.0.0"


PROFILE = MarketProfile()


def decimal(value, field="value"):
    if isinstance(value, (float, bool)) or not isinstance(value, (str, int, Decimal)):
        raise ContractError("DECIMAL_SOURCE_REQUIRED", field)
    try:
        result = Decimal(value)
        with localcontext() as ctx:
            ctx.prec = 80
            fixed = result.quantize(Decimal("0.00000001"))
        if not result.is_finite() or fixed != result or abs(result) >= Decimal("1e20"):
            raise ContractError("DECIMAL128_OVERFLOW_OR_SCALE", field)
        return fixed
    except InvalidOperation:
        raise ContractError("INVALID_DECIMAL", field) from None


def convert(value, unit, *, currency="SYNCCY", profile=PROFILE, lot_size=None):
    if profile != PROFILE:
        raise ContractError("UNKNOWN_PROFILE", "profile")
    if currency != profile.currency:
        raise UnsupportedCurrency("UNSUPPORTED_CURRENCY", "currency")
    factors = {"share": Decimal(1), "currency": Decimal(1), "thousand_currency": Decimal(1000)}
    if unit == "lot":
        factor = decimal(lot_size, "lot_size")
        if factor <= 0 or factor % 1:
            raise ContractError("INVALID_LOT_SIZE", "lot_size")
    elif unit in factors:
        factor = factors[unit]
    else:
        raise ContractError("UNKNOWN_UNIT", "unit")
    with localcontext() as ctx:
        ctx.prec = 80
        result = decimal(decimal(value) * factor)
    if result < 0 or (unit in ("share", "lot") and result % profile.share_unit):
        raise ContractError("INVALID_QUANTITY", "value")
    return result
