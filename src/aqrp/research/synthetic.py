"""Public engineering dataset generator. It supplies inputs, never test answers."""

from copy import deepcopy
from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal

from aqrp.core.time import utc
from aqrp.data.exposures import publish_exposures
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, load_synthetic
from aqrp.factors.admission import builtin_spec
from aqrp.validation.labels import CoverageRef


def synthetic_research(destination, *, sessions=36, assets=8, factor_ids=("momentum",), seed=17):
    if sessions < 24 or assets < 6:
        raise ValueError("public integration profile requires 24 sessions / 6 assets")
    days = [date(2024, 1, 2) + timedelta(days=i) for i in range(sessions)]
    tables = load_synthetic(seed=seed, sessions=[(d, "12:00:00") for d in days])
    for asset in range(2, assets + 1):
        for name in (
            "security_master",
            "symbol_alias",
            "security_status",
            "universe_membership",
            "bars_daily",
        ):
            for original in list(tables[name]):
                if original["security_id"] == "SYN_A:001":
                    row = deepcopy(original)
                    row["security_id"] = f"SYN_A:{asset:03d}"
                    if name == "symbol_alias":
                        row["symbol"] = f"A{asset}"
                    tables[name].append(row)
    for row in tables["bars_daily"]:
        i = days.index(row["session_date"])
        asset = int(row["security_id"].split(":")[1])
        price = Decimal(100 + asset * 3 + ((i * i + asset * i * 7) % (asset * 5 + 17)))
        volume = Decimal(100 + ((asset * 13 + i * i * 3 + asset * i) % 61))
        row.update({k: price for k in ("open", "high", "low", "close")})
        row.update(
            volume=volume,
            source_volume=str(volume),
            amount=price * volume,
            source_amount=str(price * volume),
        )
    snapshot = publish_snapshot(tables, PROVENANCE, destination / "dataset")
    exposures = publish_exposures(
        [
            {
                "security_id": f"SYN_A:{i:03d}",
                "market_id": "SYN_A",
                "currency": "SYNCCY",
                "industry_version": "public-engineering/1",
                "industry": "A" if i % 2 else "B",
                "market_cap": str(1000 + i * i * 113),
                "event_time": "2024-01-01T00:00:00Z",
                "available_at": "2024-01-01T00:00:00Z",
                "effective_from": "2024-01-01T00:00:00Z",
                "effective_to": None,
                "revision_id": 1,
            }
            for i in range(1, assets + 1)
        ],
        snapshot,
        destination / "exposures",
    )
    cutoff = days[-1].isoformat() + "T12:10:00Z"
    coverage = CoverageRef.create(
        snapshot.manifest_hash,
        [
            {
                "coverage_id": str(day),
                "event_time": str(day) + "T12:00:00Z",
                "available_at": str(day) + "T12:05:00Z",
                "complete_through": str(day) + "T12:00:00Z",
                "revision_id": 1,
            }
            for day in days
        ],
        authority="public-synthetic-generator",
        scope="PUBLIC_ENGINEERING",
    )
    candidates = [
        {
            "ref": asdict(builtin_spec(name).ref),
            "parameters": {"lookback": 2},
            "direction": 1,
            "hypothesis": name,
        }
        for name in factor_ids
    ]
    split1, split2 = days[sessions // 3].isoformat(), days[2 * sessions // 3].isoformat()
    config = {
        "schema": "research/1",
        "purpose": "ENGINEERING_DEMO",
        "seed": seed,
        "market_id": "SYN_A",
        "calendar_id": "SYN_A_CAL",
        "currency": "SYNCCY",
        "universe_id": "SYN_U",
        "candidates": candidates,
        "horizons": [1, 2],
        "min_ic_n": 3,
        "groups": 3,
        "min_group_n": 1,
        "decisions": [
            {"session": d.isoformat(), "decision_time": d.isoformat() + "T12:05:00Z"}
            for d in days[2:-3]
        ],
        "evaluation_cutoff": cutoff,
        "development_cutoff": cutoff,
        "pipeline": {
            "clean": {"method": "quantile", "quantiles": [0.05, 0.95]},
            "standardized": {"method": "zscore"},
            "neutralize": True,
        },
        "splits": {
            "train": [days[0].isoformat(), split1],
            "validation": [split1, split2],
            "test": [split2, (days[-1] + timedelta(days=1)).isoformat()],
            "embargo_sessions": 1,
        },
        "fit_cutoff": utc(split1 + "T00:00:00Z"),
        "walk_forward": [
            {
                "fit": [days[0].isoformat(), split1],
                "evaluate": [split1, split2],
                "fit_cutoff": split1 + "T00:00:00Z",
            }
        ],
        "family": {
            "id": "public-synthetic-" + "-".join(factor_ids),
            "hypotheses": list(factor_ids),
            "budget": 12,
            "method": "holm",
        },
        "inference": {"horizon": 1, "m0": 0},
    }
    from aqrp.services.research import hypotheses, hypothesis_definition

    config["family"]["hypotheses"] = [r["hypothesis"] for r in hypotheses(config)]
    config["family"]["definitions"] = {
        c["hypothesis"]: hypothesis_definition(
            c, config, snapshot.manifest_hash, exposures.manifest_hash, coverage.checksum
        )
        for c in hypotheses(config)
    }
    return config, snapshot, exposures, coverage
