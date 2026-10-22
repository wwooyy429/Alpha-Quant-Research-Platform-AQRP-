"""Lossless persisted rationals; currency rounding independent of Decimal context."""

from fractions import Fraction

from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import finite_decimal, number, project

F = Fraction


def money(value):
    return number(value)


def integral(value, *, positive=False):
    n = money(value)
    if n.denominator != 1 or (positive and n <= 0):
        raise ContractError("INTEGER_SHARE_REQUIRED")
    return n


def round_cent(n):
    sign = -1 if n < 0 else 1
    n = abs(n) * 100
    return sign * F((2 * n.numerator + n.denominator) // (2 * n.denominator), 100)


def ceil_tick(n, tick=F(1, 100)):
    x = n / tick
    return -(-x.numerator // x.denominator) * tick


def floor_tick(n, tick=F(1, 100)):
    x = n / tick
    return (x.numerator // x.denominator) * tick


def price(value):
    n = money(value)
    if n <= 0 or n * 100 != int(n * 100):
        raise ContractError("POSITIVE_CENT_PRICE_REQUIRED")
    return n


def p4_input(value):
    """Lossless scientific encoding within the original P4 34-digit input contract."""
    text = finite_decimal(value)
    if text is None:
        raise ContractError("P4_PROJECTION_NUMERIC_DOMAIN_EXCEEDED")
    if value == 0:
        return "0"
    whole, _, fraction = text.lstrip("-").partition(".")
    digits = (whole + fraction).lstrip("0")
    exponent = -len(fraction)
    trailing = len(digits) - len(digits.rstrip("0"))
    digits = digits.rstrip("0")
    exponent += trailing
    if len(digits) > 34 or abs(exponent) > 100:
        raise ContractError("P4_PROJECTION_NUMERIC_DOMAIN_EXCEEDED")
    return ("-" if value < 0 else "") + digits + ("e" + str(exponent) if exponent else "")


def freeze(value):
    if isinstance(value, F):
        return {"$fraction": [str(value.numerator), str(value.denominator)]}
    if isinstance(value, dict):
        return {k: freeze(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [freeze(v) for v in value]
    return value


def thaw(value):
    if isinstance(value, dict):
        if set(value) == {"$fraction"}:
            a, b = value["$fraction"]
            return F(int(a), int(b))
        return {k: thaw(v) for k, v in value.items()}
    if isinstance(value, list):
        return [thaw(v) for v in value]
    return value


def present(value):
    if isinstance(value, F):
        decimal = finite_decimal(value)
        return (
            decimal
            if decimal is not None
            else {
                "numerator": str(value.numerator),
                "denominator": str(value.denominator),
                "display": project(value),
            }
        )
    if isinstance(value, dict):
        return {k: present(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [present(v) for v in value]
    return value
