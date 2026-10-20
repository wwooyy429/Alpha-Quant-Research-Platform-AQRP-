"""Only the Phase 1 G-RET primitive; no factor or strategy statistics."""

from dataclasses import dataclass
from decimal import localcontext

from .errors import ContractError
from .units import decimal


@dataclass(frozen=True)
class ReturnValue:
    value: float | None
    validity: str


def simple_price_return(previous, current):
    if previous is None or current is None:
        return ReturnValue(None, "MISSING")
    previous, current = decimal(previous), decimal(current)
    if previous <= 0 or current <= 0:
        raise ContractError("NONPOSITIVE_PRICE", "price")
    with localcontext() as ctx:
        ctx.prec = 60
        return ReturnValue(float(current / previous - 1), "VALID")
