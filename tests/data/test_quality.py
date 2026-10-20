from copy import deepcopy
from datetime import date
from decimal import Decimal

import pytest

from aqrp.core.errors import DataQualityError
from aqrp.core.time import utc
from aqrp.data.quality import normalize, validate_dataset, validate_table
from aqrp.data.synthetic import load_synthetic, record


def test_data_006_classification_and_conservation(tables):
    base = tables["bars_daily"][0]
    good, zero, duplicate, missing, negative, high = [deepcopy(base) for _ in range(6)]
    for i, row in enumerate([good, zero, missing, negative, high]):
        row["revision_id"] = i + 1
    zero.update(volume=Decimal(0), source_volume="0")
    missing["close"] = None
    negative["close"] = Decimal(-1)
    high["close"] = Decimal(101)
    result = validate_table("bars_daily", [good, zero, duplicate, missing, negative, high])
    q = result.report
    assert (q.input, q.valid, q.duplicate, q.missing, q.rejected) == (6, 2, 1, 1, 2)
    assert sum((q.valid, q.duplicate, q.missing, q.rejected)) == 6
    assert any(r["close"] is None for r in result.table.to_pylist())
    assert any(
        r["volume"] == 0 and r["quality_status"] == "VALID" for r in result.table.to_pylist()
    )
    conflict = deepcopy(base)
    conflict.update(close=Decimal(101), high=Decimal(101))
    assert validate_table("bars_daily", [base, conflict]).report.rejected == 1
    tables["bars_daily"] = [base, conflict]
    with pytest.raises(DataQualityError, match="QUARANTINED"):
        validate_dataset(tables)


@pytest.mark.parametrize(
    "table,field,bad",
    [
        ("bars_daily", "close", 1.25),
        ("bars_daily", "source_scale", 9),
        ("bars_daily", "source_scale", -1),
        ("bars_daily", "source_scale", "2"),
        ("bars_daily", "price_basis", "ADJUSTED"),
        ("bars_daily", "currency", "USD"),
        ("bars_daily", "market_id", "UNKNOWN"),
        ("bars_daily", "quality_status", "BAD"),
        ("bars_daily", "quality_status", "INVALID"),
        ("bars_daily", "source_id", None),
        ("bars_daily", "source_id", 2),
        ("bars_daily", "source_id", ""),
        ("bars_daily", "schema_version", "2"),
        ("bars_daily", "volume", Decimal(-1)),
        ("bars_daily", "amount", Decimal(-1)),
        ("bars_daily", "close", Decimal("1.001")),
        ("bars_daily", "session_date", "invalid"),
        ("bars_daily", "session_date", 1),
        ("bars_daily", "session_date", utc("2024-01-02T00:00:00Z")),
        ("bars_daily", "available_at", utc("2024-01-01T00:00:00Z")),
        ("calendar", "close_at", None),
        ("calendar", "open_at", None),
        ("calendar", "close_at", utc("2024-01-01T00:00:00Z")),
        ("calendar", "event_time", utc("2024-01-01T00:00:00Z")),
        ("calendar", "session_date", date(2024, 1, 1)),
        ("security_status", "status", "BAD"),
        ("universe_membership", "effective_to", utc("2023-01-01T00:00:00Z")),
    ],
)
def test_data_006_invalid_rows(tables, table, field, bad):
    row = deepcopy(tables[table][0])
    row[field] = bad
    assert validate_table(table, [row]).report.rejected == 1


def test_data_003_cross_relations(tables):
    assert all(r.report.rejected == 0 for r in validate_dataset(tables).values())
    for field, bad in [
        ("session_date", date(2024, 1, 4)),
        ("event_time", utc("2024-01-02T15:00:00Z")),
        ("market_id", "SYN_B"),
        ("security_id", "ABSENT"),
    ]:
        changed = deepcopy(tables)
        changed["bars_daily"][0][field] = bad
        with pytest.raises(DataQualityError):
            validate_dataset(changed)
    changed = deepcopy(tables)
    changed["calendar"] = []
    with pytest.raises(DataQualityError):
        validate_dataset(changed)
    changed = deepcopy(tables)
    del changed["calendar"]
    with pytest.raises(DataQualityError):
        validate_dataset(changed)
    changed = deepcopy(tables)
    revision = deepcopy(changed["security_master"][0])
    revision.update(revision_id=2, market_id="SYN_B")
    changed["security_master"].append(revision)
    with pytest.raises(DataQualityError, match="REUSED"):
        validate_dataset(changed)
    changed = deepcopy(tables)
    changed["bars_daily"][0]["available_at"] = None
    with pytest.raises(DataQualityError, match="UNKNOWN_AVAILABILITY"):
        validate_dataset(changed)
    assert validate_dataset(changed, exploratory=True)["bars_daily"].report.missing == 1
    with pytest.raises(ValueError):
        load_synthetic("seed")
    assert load_synthetic(17) == load_synthetic(17)


def test_schema_inputs(tables):
    bad = deepcopy(tables["bars_daily"][0])
    del bad["close"]
    assert validate_table("bars_daily", [bad]).report.rejected == 1
    with pytest.raises(ValueError):
        validate_table("not-supported", [])
    row = deepcopy(tables["bars_daily"][0])
    row["session_date"] = "2024-01-02"
    assert normalize("bars_daily", row)["session_date"] == date(2024, 1, 2)
    result = validate_dataset(tables)
    assert (
        validate_dataset({k: v.table for k, v in result.items()})["bars_daily"].table.schema
        == result["bars_daily"].table.schema
    )
    action = record(
        "adjustment_factors",
        security_id="SYN_A:001",
        effective_at=utc("2024-01-03T00:00:00Z"),
        revision_id=1,
        ratio=Decimal(2),
        action_id="s1",
        method="SPLIT",
        view_cutoff=utc("2024-01-03T00:00:00Z"),
    )
    assert validate_table("adjustment_factors", [action]).report.valid == 1
    action["ratio"] = Decimal(0)
    assert validate_table("adjustment_factors", [action]).report.rejected == 1
