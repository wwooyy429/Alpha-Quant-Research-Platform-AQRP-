"""Phase2 engineering-only registry; no plugin implementation imported here."""

from .admission import builtin_spec
from .contracts import Factor, FactorContext, FactorRef, FactorSpec, Signal, SignalBatch
from .engine import FactorEngine, write_run
from .registry import FactorRegistry

__all__ = [
    "Factor",
    "FactorContext",
    "FactorEngine",
    "FactorRef",
    "FactorRegistry",
    "FactorSpec",
    "Signal",
    "SignalBatch",
    "builtin_spec",
    "write_run",
]
