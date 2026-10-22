"""Frozen G1 Price-Volume answers; Volume itself remains a different signal."""

from decimal import Decimal

import pytest

from aqrp.factors import builtin_spec


@pytest.mark.parametrize("current,expected", [(200, 0.06), (0, -0.1)])
def test_price_volume_exact_formula(
    factor_tables, factor_query, factor_registry, factor_engine, make_snapshot, current, expected
):
    for r in factor_tables["bars_daily"]:
        if r["security_id"] == "SYN_A:001" and r["session_date"].day == 4:
            r.update(
                volume=Decimal(current),
                source_volume=str(current),
                amount=r["close"] * current,
                source_amount=str(r["close"] * current),
            )
    spec = builtin_spec("price_volume")
    factor_registry.register(
        spec.implementation_version,
        spec,
        actor="developer",
        reason="g1-approved-formula",
        evidence=spec.review_ref,
    )
    batch = factor_engine.run(
        spec.ref,
        factor_query,
        "2024-01-04T12:05:00Z",
        make_snapshot(factor_tables),
        parameters={"lookback": 2},
    )
    assert batch.rows[0].factor_value == pytest.approx(expected, abs=1e-12)
    assert spec.required_fields == ("close", "volume")
