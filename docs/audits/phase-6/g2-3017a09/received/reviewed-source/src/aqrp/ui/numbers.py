"""Exact presentation conversion; literal independent answers remain outside this module."""

from aqrp.core.errors import ContractError

MAX_DIGITS = 4096


class ReferenceNumberError(ContractError):
    """Explicit design-reference input refusal, never silent numeric rounding."""

    def __init__(self, code):
        super().__init__(code)


def decimal_parts(text):
    if not isinstance(text, str):
        raise ReferenceNumberError("REFERENCE_NUMERIC_TYPE")
    if len(text) > MAX_DIGITS + 2:
        raise ReferenceNumberError("REFERENCE_NUMERIC_RANGE")
    sign = -1 if text.startswith("-") else 1
    body = text[1:] if text.startswith(("-", "+")) else text
    parts = body.split(".")
    if len(parts) > 2:
        raise ReferenceNumberError("REFERENCE_NUMERIC_SYNTAX")
    whole = parts[0]
    fraction = parts[1] if len(parts) == 2 else ""
    digits = whole + fraction
    if (
        not digits
        or (len(parts) == 2 and not fraction)
        or any(c not in "0123456789" for c in digits)
    ):
        raise ReferenceNumberError("REFERENCE_NUMERIC_SYNTAX")
    if len(digits) > MAX_DIGITS:
        raise ReferenceNumberError("REFERENCE_NUMERIC_RANGE")
    return sign * int(digits), len(fraction)


def exact_text(coefficient, scale, *, trim=True):
    negative = coefficient < 0
    digits = str(abs(coefficient))
    if scale:
        digits = digits.zfill(scale + 1)
        whole, fraction = digits[:-scale], digits[-scale:]
        if trim:
            fraction = fraction.rstrip("0")
        result = whole + ("." + fraction if fraction else "")
    else:
        result = digits
    return ("-" if negative else "") + result


def rounded_units(coefficient, scale, places):
    if scale <= places:
        return coefficient * 10 ** (places - scale)
    denominator = 10 ** (scale - places)
    q, r = divmod(abs(coefficient), denominator)
    if 2 * r > denominator or (2 * r == denominator and q % 2):
        q += 1
    return -q if coefficient < 0 else q


def fixed_view(text, places, *, multiply=1, grouping=False):
    coefficient, scale = decimal_parts(text)
    value = exact_text(rounded_units(coefficient * multiply, scale, places), places, trim=False)
    if grouping:
        negative = value.startswith("-")
        whole, fraction = value.lstrip("-").split(".")
        chunks = [whole[max(0, i - 3) : i] for i in range(len(whole), 0, -3)]
        value = ("-" if negative else "") + ",".join(reversed(chunks)) + "." + fraction
    return value


def percent(text):
    coefficient, scale = decimal_parts(text)
    return exact_text(coefficient, scale + 2)
