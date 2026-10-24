"""Executed only by the original P6 interpreter/wheel, with four literal answers."""

import importlib.metadata
import json
import platform
import sys
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from pathlib import Path

import aqrp
from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, load_synthetic
from aqrp.factors import FactorEngine, FactorRegistry, builtin_spec, write_run
from aqrp.factors.admission import bundle_hash, bundle_manifest


def main():
    assert aqrp.__version__ == "0.6.0.dev5"
    assert bundle_hash() == "28c3cc049efcce8fc3e55b4056e8e116f98deca39eeb1d2c8822799c8e98855b"
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
    snapshot = publish_snapshot(tables, PROVENANCE, output / "dataset")
    query = QuerySpec(
        ("SYN_A:001",),
        "SYN_A",
        "SYN_A_CAL",
        (date(2024, 1, 2), date(2024, 1, 4)),
        ("close", "volume"),
        "split_adjusted",
    )
    registry, values = FactorRegistry(), {}
    # Independent literals: 121/100-1=.21; negative reversal; 200/125-1=.6;
    # price-volume=(121/110-1)*.6=.06. Never compute expected with the product.
    for factor, expected in (
        ("momentum", 0.21),
        ("reversal", -0.21),
        ("volume", 0.6),
        ("price_volume", 0.06),
    ):
        spec = builtin_spec(factor)
        registry.register(
            spec.implementation_version,
            spec,
            actor="developer-original-package-replay",
            reason="Fixed P6 approved engineering builtin",
            evidence=spec.review_ref,
        )
        pin = registry.resolve(spec.ref)
        batch = FactorEngine(registry).run_pinned(
            pin, query, "2024-01-04T12:05:00Z", snapshot, parameters={"lookback": 2}
        )
        assert batch.rows[0].factor_value == expected
        write_run(batch, output / "factor-runs", registry)
        values[factor] = {
            "ref": asdict(spec.ref),
            "actual": batch.rows[0].factor_value,
            "expected_literal": expected,
            "logical_hash": batch.logical_hash,
        }
    result = {
        "scope": "Developer actual original P6 four pinned FactorRef executions, not historical host equivalence or financial approval",
        "package": str(Path(aqrp.__file__).resolve()),
        "version": aqrp.__version__,
        "bundle": bundle_hash(),
        "modules": bundle_manifest(),
        "factor_refs": {k: v["ref"] for k, v in values.items()},
        "four_original_executions": values,
        "runtime": {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "distributions": sorted(
                [
                    {"name": d.metadata["Name"], "version": d.version}
                    for d in importlib.metadata.distributions()
                ],
                key=lambda d: d["name"].lower(),
            ),
        },
    }
    (output / "four-original-refs.json").write_bytes(canonical(result))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
