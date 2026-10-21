"""Independent semantic regressions for WORK-P1-001/002/003, frozen answers unchanged."""

from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from itertools import product

import pytest

from aqrp.core.contracts import QuerySpec
from aqrp.core.errors import DataQualityError
from aqrp.core.time import utc
from aqrp.data.quality import validate_dataset, validate_table
from aqrp.data.query import actions_as_of, query
from aqrp.data.synthetic import load_synthetic, record


@pytest.mark.parametrize(
    "field,unit,source,value",
    [
        ("volume", "currency", "1.25", "1.25"),
        ("volume", "currency", "3", "3"),
        ("volume", "thousand_currency", "1", "1000"),
        ("amount", "share", "3", "3"),
        ("amount", "lot", "3", "300"),
    ],
)
def test_work_p1_001_field_dimensions(tables, make_snapshot, field, unit, source, value):
    tables["bars_daily"][0].update(
        {field: Decimal(value), f"source_{field}": source, f"source_{field}_unit": unit}
    )
    tables["bars_daily"][0]["lot_size"] = Decimal(100)
    result = validate_table("bars_daily", [tables["bars_daily"][0]])
    assert result.report.rejected == 1
    assert result.report.reasons[0][1] == f"INVALID_{field.upper()}_UNIT"
    with pytest.raises(DataQualityError, match="QUARANTINED_ROWS"):
        make_snapshot(tables)


@pytest.mark.parametrize("field,unit", [("volume", "currency"), ("amount", "share")])
def test_known_wrong_dimension_not_hidden_by_null(tables, field, unit):
    row = tables["bars_daily"][0]
    row.update({field: None, f"source_{field}_unit": unit})
    assert validate_table("bars_daily", [row]).report.rejected == 1


@pytest.mark.parametrize(
    "field,unit,source,value",
    [
        ("volume", "share", "0", "0"),
        ("volume", "share", "10", "10"),
        ("volume", "lot", "3", "300"),
        ("volume", "lot", "0.01", "1"),
        ("amount", "currency", "1.25", "1.25"),
        ("amount", "thousand_currency", "1.25", "1250"),
    ],
)
def test_work_p1_001_legal_units(tables, make_snapshot, spec, field, unit, source, value):
    tables["bars_daily"][0].update(
        {
            field: Decimal(value),
            f"source_{field}": source,
            f"source_{field}_unit": unit,
            "lot_size": Decimal(100),
        }
    )
    view = query(replace(spec, fields=(field,)), "2024-01-02T16:05:00Z", make_snapshot(tables))
    assert view.table[field].to_pylist() == [Decimal(value)]


@pytest.mark.parametrize("unit,source,value", [("share", "1.25", "1.25"), ("lot", ".005", ".5")])
def test_work_p1_001_fractional_target_shares(tables, unit, source, value):
    tables["bars_daily"][0].update(
        volume=Decimal(value), source_volume=source, source_volume_unit=unit, lot_size=Decimal(100)
    )
    assert validate_table("bars_daily", [tables["bars_daily"][0]]).report.rejected == 1


@pytest.mark.parametrize(
    "values",
    [
        {"open": 100, "high": 90, "low": 95, "close": None},
        {"open": 102, "high": 101, "low": 99, "close": None},
        {"open": None, "high": 101, "low": 99, "close": 102},
        {"open": None, "high": None, "low": 99, "close": 98},
        {"open": None, "high": 101, "low": None, "close": 102},
        {"open": None, "high": 90, "low": 95, "close": None},
    ],
)
def test_work_p1_003_known_price_contradictions(tables, make_snapshot, values):
    tables["bars_daily"][0].update(values)
    result = validate_table("bars_daily", [tables["bars_daily"][0]])
    assert result.report.rejected == 1
    assert result.report.reasons[0][1] == "OHLC_ORDER"
    with pytest.raises(DataQualityError, match="QUARANTINED_ROWS"):
        make_snapshot(tables)


@pytest.mark.parametrize("missing", list(product((False, True), repeat=4)))
def test_work_p1_003_all_legal_missing_patterns(tables, missing):
    row = tables["bars_daily"][0]
    for field, absent in zip(("open", "high", "low", "close"), missing):
        if absent:
            row[field] = None
    report = validate_table("bars_daily", [row]).report
    assert report.rejected == 0
    assert report.missing == int(any(missing))
    assert report.valid + report.missing == report.input == 1


def dividend(**changes):
    fields = dict(
        action_id="div-validation",
        revision_id=1,
        security_id="SYN_A:001",
        type="CASH_DIVIDEND",
        announcement_at=utc("2024-01-01T00:00:00Z"),
        effective_at=utc("2024-01-03T00:00:00Z"),
        ex_date=date(2024, 1, 3),
        cash_per_share=Decimal(2),
        currency="SYNCCY",
        dividend_basis="PER_OLD_SHARE",
    )
    fields.update(changes)
    return record("corporate_actions", **fields)


@pytest.mark.parametrize(
    "changes,code",
    [
        ({"ex_date": date(2024, 1, 4)}, "ACTION_EX_SESSION_UNRESOLVED"),
        ({"ex_date": date(2024, 1, 2)}, "ACTION_EX_DATE_MISMATCH"),
        ({"effective_at": utc("2024-01-03T12:00:00.000001Z")}, "ACTION_EX_DATE_MISMATCH"),
    ],
)
def test_work_p1_002_reject_conflicting_dates(tables, make_snapshot, changes, code):
    tables["corporate_actions"] = [dividend(**changes)]
    with pytest.raises(DataQualityError, match=code):
        make_snapshot(tables)


@pytest.mark.parametrize("effective", ["2024-01-03T00:00:00Z", "2024-01-03T12:00:00Z"])
def test_work_p1_002_valid_ex_session_return(tables, make_snapshot, spec, effective):
    for r in tables["bars_daily"]:
        if r["security_id"] == "SYN_A:001" and r["session_date"] == date(2024, 1, 3):
            r.update({f: Decimal(98) for f in ("open", "high", "low", "close")})
    tables["corporate_actions"] = [dividend(effective_at=utc(effective))]
    ref = make_snapshot(tables)
    tr = replace(spec, fields=("total_return_index",), price_basis="total_return")
    assert query(tr, "2024-01-03T12:05:00Z", ref).table["total_return_index"].to_pylist() == [
        1.0,
        1.0,
    ]
    assert actions_as_of("2024-01-02T16:05:00Z", ref) == ()


def test_work_p1_002_late_revision_preserves_pit(tables, make_snapshot, spec):
    for r in tables["bars_daily"]:
        if r["security_id"] == "SYN_A:001" and r["session_date"] == date(2024, 1, 3):
            r.update({f: Decimal(98) for f in ("open", "high", "low", "close")})
    old = dividend()
    late = dict(
        old, revision_id=2, available_at=utc("2024-01-04T00:00:00Z"), cash_per_share=Decimal(4)
    )
    tables["corporate_actions"] = [old, late]
    ref = make_snapshot(tables)
    tr = replace(spec, fields=("total_return_index",), price_basis="total_return")
    assert query(tr, "2024-01-03T12:05:00Z", ref).table["total_return_index"].to_pylist() == [
        1.0,
        1.0,
    ]
    assert query(tr, "2024-01-04T12:05:00Z", ref).table["total_return_index"].to_pylist() == [
        1.0,
        1.02,
    ]


def test_work_p1_002_market_session_date_not_utc_or_feed_zone(make_snapshot):
    tables = load_synthetic(sessions=[(date(2024, 4, d), "12:00:00") for d in (1, 2)])
    for day in (1, 2):
        cal = next(
            r
            for r in tables["calendar"]
            if r["market_id"] == "SYN_A" and r["session_date"] == date(2024, 4, day)
        )
        open_at = utc(f"2024-04-0{day}T00:01:00+08:00")
        close_at = utc(f"2024-04-0{day}T00:30:00+08:00")
        cal.update(
            open_at=open_at, close_at=close_at, event_time=open_at, source_timezone="Asia/Shanghai"
        )
        bar = next(
            r
            for r in tables["bars_daily"]
            if r["security_id"] == "SYN_A:001" and r["session_date"] == date(2024, 4, day)
        )
        price = Decimal(100 if day == 1 else 98)
        bar.update({f: price for f in ("open", "high", "low", "close")})
        bar.update(
            event_time=close_at,
            available_at=close_at + timedelta(minutes=5),
            source_timezone="Asia/Shanghai",
        )
    # The feed clock is UTC; ex_date is the market's Apr2 session, effective is Apr1 UTC.
    tables["corporate_actions"] = [
        dividend(ex_date=date(2024, 4, 2), effective_at=utc("2024-04-01T16:00:00Z"))
    ]
    ref = make_snapshot(tables)
    spec = QuerySpec(
        ("SYN_A:001",),
        "SYN_A",
        "SYN_A_CAL",
        (date(2024, 4, 1), date(2024, 4, 2)),
        ("total_return_index",),
        "total_return",
    )
    assert query(spec, "2024-04-01T16:35:00Z", ref).table["total_return_index"].to_pylist() == [
        1.0,
        1.0,
    ]
    tables["corporate_actions"][0]["ex_date"] = date(2024, 4, 1)
    with pytest.raises(DataQualityError, match="ACTION_EX_DATE_MISMATCH"):
        make_snapshot(tables)


def test_work_p1_002_ambiguous_market_calendar_rejected(tables):
    other = deepcopy(tables["calendar"][1])
    other.update(calendar_id="SECOND_CAL", close_at=utc("2024-01-03T14:00:00Z"))
    tables["calendar"].append(other)
    tables["corporate_actions"] = [dividend()]
    with pytest.raises(DataQualityError, match="ACTION_EX_SESSION_UNRESOLVED"):
        validate_dataset(tables)


def test_work_p1_002_overnight_action_not_silently_normalized(tables):
    tables["calendar"][1]["close_at"] = utc("2024-01-04T01:00:00Z")
    tables["bars_daily"][1].update(
        event_time=utc("2024-01-04T01:00:00Z"), available_at=utc("2024-01-04T01:05:00Z")
    )
    tables["corporate_actions"] = [dividend()]
    with pytest.raises(DataQualityError, match="ACTION_SESSION_UNSUPPORTED"):
        validate_dataset(tables)
