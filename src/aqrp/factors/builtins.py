"""Only reviewed builtins. Pure ratios; no files, network, labels or accounts."""

from fractions import Fraction

from aqrp.factors.contracts import Signal, SignalBatch, config_bytes
from aqrp.factors.input import windows


class BuiltinFactor:
    def compute(self, view, context):
        signals = []
        factor_id = context.spec.factor_id
        for sid, signal_time, rows, reason in windows(view, context):
            value = None
            if reason == "NONE":
                if factor_id in ("volume", "price_volume"):
                    mean = sum((Fraction(r["volume"]) for r in rows[:-1]), Fraction(0)) / (
                        len(rows) - 1
                    )
                    if mean == 0:
                        reason = "ZERO_BASE_VOLUME"
                    else:
                        value = float(Fraction(rows[-1]["volume"]) / mean - 1)
                        if factor_id == "price_volume":
                            value = float(
                                (Fraction(rows[-1]["close"]) / Fraction(rows[-2]["close"]) - 1)
                                * (Fraction(rows[-1]["volume"]) / mean - 1)
                            )
                else:
                    ratio = Fraction(rows[-1]["close"]) / Fraction(rows[0]["close"]) - 1
                    value = float(-ratio if factor_id == "reversal" else ratio)
            signals.append(
                Signal(
                    signal_time,
                    sid,
                    dict(context.symbols).get(sid),
                    context.market_id,
                    factor_id,
                    context.spec.factor_version,
                    value,
                    context.decision_time,
                    "VALID" if reason == "NONE" else "INVALID",
                    reason,
                    context.snapshot_id,
                    context.params_hash,
                    context.run_id,
                    context.computation_id,
                    context.spec.implementation_version,
                )
            )
        return SignalBatch(tuple(signals), config_bytes(context))
