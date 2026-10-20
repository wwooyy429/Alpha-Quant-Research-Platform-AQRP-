import hashlib
import json
from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from aqrp.core.contracts import QuerySpec
from aqrp.core.errors import DataQualityError
from aqrp.core.time import utc
from aqrp.data.actions import action_view
from aqrp.data.query import aliases_at, query, universe_at
from aqrp.data.snapshot import verify_snapshot
from aqrp.data.synthetic import record


@pytest.mark.parametrize(
    "day,zone,open_clock,close_clock,expected_event",
    [
        (
            date(2024, 3, 8),
            "America/New_York",
            "2024-03-08T09:30:00-05:00",
            "2024-03-08T16:00:00-05:00",
            "2024-03-08T21:00:00Z",
        ),
        (
            date(2024, 3, 11),
            "America/New_York",
            "2024-03-11T09:30:00-04:00",
            "2024-03-11T16:00:00-04:00",
            "2024-03-11T20:00:00Z",
        ),
        (
            date(2024, 4, 2),
            "Asia/Shanghai",
            "2024-04-02T00:01:00+08:00",
            "2024-04-02T00:30:00+08:00",
            "2024-04-01T16:30:00Z",
        ),
    ],
)
def test_data_003_008_cross_timezone_roundtrip(
    tables, make_snapshot, day, zone, open_clock, close_clock, expected_event
):
    tables["calendar"] = [
        record(
            "calendar",
            market_id="SYN_A",
            calendar_id="SYN_A_CAL",
            session_date=day,
            source_timezone=zone,
            open_at=open_clock,
            close_at=close_clock,
            event_time=open_clock,
            calendar_version="synthetic-calendar/1",
        )
    ]
    bar = deepcopy(tables["bars_daily"][0])
    bar.update(
        source_timezone=zone,
        event_time=close_clock,
        available_at=utc(expected_event) + timedelta(minutes=5),
        session_date=day,
    )
    tables["bars_daily"] = [bar]
    ref = make_snapshot(tables)
    spec = QuerySpec(("SYN_A:001",), "SYN_A", "SYN_A_CAL", (day, day))
    view = query(spec, utc(expected_event) + timedelta(minutes=5), ref)
    assert view.table["event_time"].to_pylist() == [utc(expected_event)]
    assert view.table["session_date"].to_pylist() == [day]
    assert verify_snapshot(ref)[1]["bars_daily"]["source_timezone"].to_pylist() == [zone]


def test_data_011_source_units_survive_pipeline(tables, make_snapshot, spec):
    tables["bars_daily"][0].update(
        volume=Decimal(300),
        source_volume="3",
        source_volume_unit="lot",
        lot_size=Decimal(100),
        amount=Decimal(1250),
        source_amount="1.25",
        source_amount_unit="thousand_currency",
    )
    ref = make_snapshot(tables)
    view = query(replace(spec, fields=("close", "volume", "amount")), "2024-01-02T16:05:00Z", ref)
    assert view.table["volume"].to_pylist() == [Decimal(300)]
    assert view.table["amount"].to_pylist() == [Decimal(1250)]
    source = verify_snapshot(ref)[1]["bars_daily"].to_pylist()[0]
    assert (source["source_volume"], source["source_volume_unit"], source["source_amount"]) == (
        "3",
        "lot",
        "1.25",
    )


def test_data_005_overlapping_alias_and_universe(tables, make_snapshot):
    for table in ("symbol_alias", "universe_membership"):
        changed = deepcopy(tables)
        row = deepcopy(changed[table][0])
        row["effective_from"] += timedelta(hours=1)
        changed[table].append(row)
        ref = make_snapshot(changed)
        with pytest.raises(DataQualityError, match="OVERLAPPING"):
            if table == "symbol_alias":
                aliases_at("SYN_A", "DUP", "2024-01-02T16:05:00Z", ref)
            else:
                universe_at("SYN_U", "2024-01-02T16:05:00Z", ref)


@given(st.integers(1, 10000), st.integers(1, 10000), st.sampled_from([2, 4, 5, 10]))
def test_data_004_split_exact_conservation(price, shares, ratio):
    bars = [
        dict(
            security_id="SYN_A:001",
            event_time=utc("2024-01-02T16:00:00Z"),
            open=Decimal(price),
            high=Decimal(price),
            low=Decimal(price),
            close=Decimal(price),
            volume=Decimal(shares),
        )
    ]
    actions = [
        dict(
            type="SPLIT",
            security_id="SYN_A:001",
            effective_at=utc("2024-01-03T00:00:00Z"),
            split_ratio=Decimal(ratio),
        )
    ]
    adjusted = action_view(bars, actions, "split_adjusted", [])[0]
    assert adjusted["close"] * adjusted["volume"] == Decimal(price * shares)
    assert bars[0]["close"] == Decimal(price)


def test_golden_fixture_integrity():
    root = Path(__file__).resolve().parents[1] / "golden"
    raw = (root / "phase1_answers.json").read_bytes()
    manifest = json.loads((root / "phase1_answers_manifest.json").read_bytes())
    assert hashlib.sha256(raw).hexdigest() == manifest["sha256"]
    answers = json.loads(raw)
    assert answers["G-RET"]["expected"] == "0.10"
    assert answers["P1-QUALITY"]["expected"] == [2, 1, 1, 2]


def test_data_008_frozen_input_pipeline(make_snapshot, spec):
    root = Path(__file__).resolve().parents[1] / "golden"
    raw = (root / "phase1_input.json").read_bytes()
    manifest = json.loads((root / "phase1_input_manifest.json").read_bytes())
    assert hashlib.sha256(raw).hexdigest() == manifest["sha256"]
    ref = make_snapshot(json.loads(raw))
    result = query(spec, "2024-01-03T12:05:00Z", ref)
    assert result.table["close"].to_pylist() == [Decimal(100), Decimal(100)]
    assert result.table["session_date"].to_pylist() == [date(2024, 1, 2), date(2024, 1, 3)]


def test_required_security_fields(tables):
    from aqrp.data.quality import validate_table

    r = deepcopy(tables["security_master"][0])
    r["listing_at"] = None
    assert validate_table("security_master", [r]).report.rejected == 1
    r = deepcopy(tables["security_master"][0])
    r["known_at"] = utc("2024-01-03T00:00:00Z")
    assert validate_table("security_master", [r]).report.rejected == 1


def test_required_action_quality(tables, make_snapshot, spec):
    tables["corporate_actions"] = [
        record(
            "corporate_actions",
            action_id="a1",
            revision_id=1,
            security_id="SYN_A:001",
            type="SPLIT",
            effective_at=utc("2024-01-03T00:00:00Z"),
            announcement_at=utc("2024-01-01T00:00:00Z"),
            split_ratio=Decimal(2),
            ex_date=date(2024, 1, 3),
            currency="SYNCCY",
            quality_status="MISSING",
        )
    ]
    with pytest.raises(DataQualityError, match="ACTION_QUALITY"):
        query(spec, "2024-01-03T16:00:00Z", make_snapshot(tables))
