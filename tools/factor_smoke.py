"""Installed-wheel engineering-only factor run; standalone fixed manual expectations."""

import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, load_synthetic
from aqrp.factors import FactorEngine, FactorRegistry, builtin_spec, write_run


def main():
    output = Path(sys.argv[1])
    tables = load_synthetic(sessions=[(date(2024, 1, d), "12:00:00") for d in (2, 3, 4)])
    for row in tables["bars_daily"]:
        i = row["session_date"].day - 2
        price, volume = Decimal((100, 110, 121)[i]), Decimal((100, 150, 200)[i])
        row.update({f: price for f in ("open", "high", "low", "close")})
        row.update(
            volume=volume,
            source_volume=str(volume),
            amount=price * volume,
            source_amount=str(price * volume),
        )
    snapshot = publish_snapshot(tables, PROVENANCE, output / "factor-dataset")
    query = QuerySpec(
        ("SYN_A:001",),
        "SYN_A",
        "SYN_A_CAL",
        (date(2024, 1, 2), date(2024, 1, 4)),
        ("close", "volume"),
        "split_adjusted",
    )
    registry = FactorRegistry()
    results = {}
    for name, expected in (("momentum", 0.21), ("reversal", -0.21), ("volume", 0.6)):
        spec = builtin_spec(name)
        registry.register(
            spec.implementation_version,
            spec,
            actor="developer-smoke",
            reason="reviewed builtin",
            evidence=spec.review_ref,
        )
        batch = FactorEngine(registry).run(
            spec.ref, query, "2024-01-04T12:05:00Z", snapshot, parameters={"lookback": 2}
        )
        assert batch.rows[0].factor_value == expected
        write_run(batch, output / "factor-runs", registry)
        results[name] = {"value": batch.rows[0].factor_value, "logical_hash": batch.logical_hash}
    (output / "factor-result.json").write_bytes(canonical(results))
    (output / "factor-code-approval.json").write_text(
        json.dumps(
            {
                "implementation_hash": spec.implementation_version,
                "review_ref": spec.review_ref,
                "state": "ENGINEERING_APPROVED",
                "environment": "TEST_ONLY",
                "financial_approval": "NONE",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("Reviewed builtin factor smoke PASS; no research/strategy approval")


if __name__ == "__main__":
    main()
