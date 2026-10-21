"""Deliberately restricted SemVer syntax; no floating selectors."""

import re

from aqrp.core.errors import ContractError


def version(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value
    ):
        raise ContractError("INVALID_FACTOR_VERSION", "version")
    return tuple(int(x) for x in value.split("."))


def compatible(declaration, host="1.0.0"):
    if not isinstance(declaration, str):
        raise ContractError("INVALID_API_RANGE", "api_compatibility")
    match = re.fullmatch(r">=([^,]+),<([^,]+)", declaration)
    if not match:
        raise ContractError("INVALID_API_RANGE", "api_compatibility")
    lower, upper = (version(x) for x in match.groups())
    if lower >= upper:
        raise ContractError("INVALID_API_RANGE", "api_compatibility")
    return lower <= version(host) < upper
