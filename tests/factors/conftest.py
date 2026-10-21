from copy import deepcopy
from datetime import date
from decimal import Decimal

import pytest

from aqrp.core.contracts import QuerySpec
from aqrp.data.synthetic import load_synthetic
from aqrp.factors import FactorEngine, FactorRegistry, builtin_spec


@pytest.fixture
def factor_tables():
    tables = load_synthetic(sessions=[(date(2024, 1, d), "12:00:00") for d in (2, 3, 4)])
    for name in ("security_master", "symbol_alias", "security_status", "universe_membership"):
        row = deepcopy(next(r for r in tables[name] if r["security_id"] == "SYN_A:001"))
        row["security_id"] = "SYN_A:002"
        if name == "symbol_alias":
            row["symbol"] = "B"
        tables[name].append(row)
    for row in list(tables["bars_daily"]):
        if row["market_id"] == "SYN_A":
            clone = deepcopy(row)
            clone["security_id"] = "SYN_A:002"
            tables["bars_daily"].append(clone)
    for row in tables["bars_daily"]:
        index = row["session_date"].day - 2
        prices, volumes = (
            ([200, 180, 160], [40, 60, 50])
            if row["security_id"] == "SYN_A:002"
            else ([100, 110, 121], [100, 150, 200])
        )
        price, volume = Decimal(prices[index]), Decimal(volumes[index])
        for field in ("open", "high", "low", "close"):
            row[field] = price
        row.update(
            volume=volume,
            source_volume=str(volume),
            amount=price * volume,
            source_amount=str(price * volume),
        )
    return tables


@pytest.fixture
def factor_query():
    return QuerySpec(
        ("SYN_A:001", "SYN_A:002"),
        "SYN_A",
        "SYN_A_CAL",
        (date(2024, 1, 2), date(2024, 1, 4)),
        ("close", "volume"),
        "split_adjusted",
    )


@pytest.fixture
def factor_registry():
    registry = FactorRegistry()
    for name in ("momentum", "reversal", "volume"):
        spec = builtin_spec(name)
        registry.register(
            spec.implementation_version,
            spec,
            actor="developer-test",
            reason="reviewed builtin test",
            evidence=spec.review_ref,
        )
    return registry


@pytest.fixture
def factor_engine(factor_registry):
    return FactorEngine(factor_registry)


@pytest.fixture
def input_case(factor_tables, factor_query, make_snapshot):
    from aqrp.core.time import utc
    from aqrp.data.query import query
    from aqrp.factors.contracts import FactorContext, freeze_parameters

    spec = builtin_spec("momentum")
    snapshot = make_snapshot(factor_tables)
    cutoff = utc("2024-01-04T12:05:00Z")
    view = query(factor_query, cutoff, snapshot)
    params, checksum = freeze_parameters(spec, {"lookback": 2})
    context = FactorContext(
        spec,
        "00000000-0000-0000-0000-000000000001",
        "00000000-0000-0000-0000-000000000002",
        cutoff,
        date(2024, 1, 4),
        snapshot.snapshot_id,
        snapshot.manifest_hash,
        view.query_hash,
        "SYN_A_CAL",
        view.metadata["calendar_version"],
        tuple((date(2024, 1, d), utc(f"2024-01-0{d}T12:00:00Z")) for d in (2, 3, 4)),
        (("SYN_A:001", "DUP"), ("SYN_A:002", "B")),
        "SYN_A",
        factor_query.security_ids,
        params,
        checksum,
    )
    return view, context
