from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from aqrp.core.canonical import digest
from aqrp.core.contracts import QuerySpec
from aqrp.core.errors import ContractError, DataQualityError, TimeLeakageError
from aqrp.core.time import utc
from aqrp.data.pit import visible_rows
from aqrp.data.query import (
    actions_as_of,
    aliases_at,
    announcements_as_of,
    query,
    status_at,
    universe_at,
)
from aqrp.data.synthetic import record


def price(row, value):
    for f in ("open", "high", "low", "close"):
        row[f] = Decimal(value)


def test_data_001_002_pit_microseconds_and_revisions(tables, make_snapshot, spec):
    original = tables["bars_daily"][0]
    revision = deepcopy(original)
    price(revision, "101")
    revision.update(revision_id=2, available_at=utc("2024-01-03T10:00:00Z"))
    tables["bars_daily"].append(revision)
    ref = make_snapshot(tables)
    cases = [
        ("2024-01-02T16:04:59.999999Z", []),
        ("2024-01-02T16:05:00Z", [Decimal(100)]),
        ("2024-01-03T09:59:59.999999Z", [Decimal(100)]),
        ("2024-01-03T10:00:00Z", [Decimal(101)]),
    ]
    for cutoff, expected in cases:
        assert query(spec, cutoff, ref).table["close"].to_pylist() == expected
    micro = deepcopy(tables)
    micro["bars_daily"][0]["available_at"] += timedelta(microseconds=1)
    micro_ref = make_snapshot(micro)
    assert query(spec, "2024-01-02T16:05:00Z", micro_ref).table.num_rows == 0
    assert query(spec, "2024-01-02T16:05:00.000001Z", micro_ref).table["close"].to_pylist() == [
        Decimal(100)
    ]
    bspec = replace(spec, security_ids=("SYN_B:001",), market_id="SYN_B", calendar_id="SYN_B_CAL")
    assert query(bspec, "2024-01-02T16:05:00Z", ref).table["close"].to_pylist() == [Decimal(200)]
    view = query(spec, "2024-01-02T16:05:00Z", ref)
    assert view.schema == view.table.schema
    frame = view.to_pandas()
    frame.loc[0, "close"] = Decimal(-99)
    assert view.table["close"].to_pylist() == [Decimal(100)]
    with pytest.raises(TypeError):
        view.metadata["as_of"] = "fake"
    assert (
        view.query_hash
        == query(replace(spec, request_id="other"), "2024-01-02T16:05:00Z", ref).query_hash
    )


def test_data_002_unknown_and_conflicting_revisions(tables, make_snapshot, spec):
    tables["bars_daily"][0]["available_at"] = None
    ref = make_snapshot(tables, exploratory=True)
    with pytest.raises(TimeLeakageError, match="EXPLORATORY"):
        query(spec, "2024-01-03T16:00:00Z", ref)
    with pytest.raises(TimeLeakageError, match="UNKNOWN_AVAILABILITY"):
        visible_rows("bars_daily", tables["bars_daily"], "2024-01-03T16:00:00Z")
    tables["bars_daily"][0]["available_at"] = utc("2024-01-02T16:05:00Z")
    revision = deepcopy(tables["bars_daily"][0])
    revision["revision_id"] = 2
    tables["bars_daily"].append(revision)
    ref = make_snapshot(tables)
    with pytest.raises(DataQualityError, match="CONFLICTING_VISIBLE"):
        query(spec, "2024-01-02T16:05:00Z", ref)


def test_data_005_late_status_universe_and_alias(tables, make_snapshot):
    cutoff = utc("2024-01-03T00:00:00Z")
    late = deepcopy(tables["security_status"][0])
    late.update(
        revision_id=2,
        effective_from=cutoff,
        event_time=cutoff,
        available_at=utc("2024-01-03T10:00:00Z"),
        status="SUSPENDED",
    )
    # Close the previous interval only in a later visible revision.
    end = deepcopy(tables["security_status"][0])
    end.update(revision_id=2, effective_to=cutoff, available_at=late["available_at"])
    tables["security_status"].extend([end, late])
    member = deepcopy(tables["universe_membership"][1])
    member.update(
        revision_id=2,
        effective_to=utc("2024-01-04T00:00:00Z"),
        available_at=utc("2024-01-03T18:00:00Z"),
    )
    tables["universe_membership"].append(member)
    old = tables["symbol_alias"][0]
    old["symbol"] = "OLD"
    end_alias = deepcopy(old)
    end_alias.update(revision_id=2, effective_to=cutoff, available_at=utc("2024-01-03T01:00:00Z"))
    new_alias = deepcopy(old)
    new_alias.update(
        symbol="NEW",
        effective_from=cutoff,
        event_time=cutoff,
        available_at=utc("2024-01-03T01:00:00Z"),
    )
    tables["symbol_alias"].extend([end_alias, new_alias])
    ref = make_snapshot(tables)
    assert status_at("SYN_A:001", "2024-01-03T09:59:59Z", ref)[0]["status"] == "TRADABLE"
    assert status_at("SYN_A:001", "2024-01-03T10:00:00Z", ref)[0]["status"] == "SUSPENDED"
    assert len(universe_at("SYN_U", "2024-01-03T17:00:00Z", ref)) == 2
    assert [r["security_id"] for r in universe_at("SYN_U", "2024-01-04T00:00:00Z", ref)] == [
        "SYN_A:001"
    ]
    assert aliases_at("SYN_A", "NEW", "2024-01-03T00:30:00Z", ref) == ()
    assert aliases_at("SYN_A", "OLD", "2024-01-03T00:30:00Z", ref)[0]["security_id"] == "SYN_A:001"
    assert aliases_at("SYN_A", "OLD", "2024-01-03T01:00:00Z", ref) == ()
    assert aliases_at("SYN_A", "NEW", "2024-01-03T01:00:00Z", ref)[0]["security_id"] == "SYN_A:001"
    bspec = QuerySpec(("SYN_B:001",), "SYN_B", "SYN_B_CAL", (date(2024, 1, 2), date(2024, 1, 3)))
    assert query(bspec, "2024-01-04T00:00:00Z", ref).table.num_rows == 2


def action(kind="SPLIT", **kwargs):
    return record(
        "corporate_actions",
        action_id="action-1",
        revision_id=1,
        security_id="SYN_A:001",
        type=kind,
        announcement_at=utc("2024-01-01T00:00:00Z"),
        effective_at=utc("2024-01-03T00:00:00Z"),
        ex_date=date(2024, 1, 3),
        split_ratio=Decimal(2) if kind == "SPLIT" else None,
        cash_per_share=Decimal(2) if kind == "CASH_DIVIDEND" else None,
        currency="SYNCCY",
        dividend_basis="PER_OLD_SHARE" if kind == "CASH_DIVIDEND" else None,
        **kwargs,
    )


def test_data_004_split_dividend_and_future_action(tables, make_snapshot, spec):
    second = tables["bars_daily"][1]
    price(second, "50")
    second.update(volume=Decimal(20), source_volume="20")
    tables["corporate_actions"] = [action()]
    ref = make_snapshot(tables)
    split = query(replace(spec, price_basis="split_adjusted"), "2024-01-03T12:05:00Z", ref)
    assert split.table["close"].to_pylist() == [Decimal(50), Decimal(50)]
    assert split.table["volume"].to_pylist() == [Decimal(20), Decimal(20)]
    assert query(spec, "2024-01-03T12:05:00Z", ref).table["close"].to_pylist() == [
        Decimal(100),
        Decimal(50),
    ]
    assert query(replace(spec, price_basis="split_adjusted"), "2024-01-02T16:05:00Z", ref).table[
        "close"
    ].to_pylist() == [Decimal(100)]
    assert len(announcements_as_of("2024-01-02T16:05:00Z", ref)) == 1
    assert actions_as_of("2024-01-02T16:05:00Z", ref) == ()
    tr_spec = replace(spec, price_basis="total_return", fields=("total_return_index",))
    assert query(tr_spec, "2024-01-03T12:05:00Z", ref).table["total_return_index"].to_pylist() == [
        1.0,
        1.0,
    ]
    price(second, "98")
    second.update(volume=Decimal(10), source_volume="10")
    tables["corporate_actions"] = [action("CASH_DIVIDEND")]
    dividend = make_snapshot(tables)
    assert query(tr_spec, "2024-01-03T12:05:00Z", dividend).table[
        "total_return_index"
    ].to_pylist() == [1.0, 1.0]
    assert query(spec, "2024-01-03T12:05:00Z", dividend).table["close"].to_pylist() == [
        Decimal(100),
        Decimal(98),
    ]
    # Announcement late, effective in the past: no retroactive use before visibility.
    tables["corporate_actions"][0]["available_at"] = utc("2024-01-04T00:00:00Z")
    late = make_snapshot(tables)
    assert query(tr_spec, "2024-01-03T12:05:00Z", late).table["total_return_index"].to_pylist() == [
        1.0,
        0.98,
    ]


def test_data_009_mutations_and_positive_control(tables, make_snapshot, spec):
    ref = make_snapshot(tables)
    cutoff = "2024-01-02T16:05:00Z"
    before = query(spec, cutoff, ref).table.to_pylist()
    future = deepcopy(tables)
    price(future["bars_daily"][1], "999")
    late = deepcopy(future["bars_daily"][0])
    price(late, "555")
    late.update(revision_id=2, available_at=utc("2024-01-04T00:00:00Z"))
    future["bars_daily"].append(late)
    future["corporate_actions"] = [action()]
    future["calendar"][1]["available_at"] = utc("2024-01-05T00:00:00Z")
    member = deepcopy(future["universe_membership"][0])
    member.update(
        revision_id=2,
        effective_to=utc("2024-01-02T00:00:00Z"),
        available_at=utc("2024-01-05T00:00:00Z"),
    )
    future["universe_membership"].append(member)
    changed = make_snapshot(future)
    assert digest(query(spec, cutoff, changed).table.to_pylist()) == digest(before)
    assert universe_at("SYN_U", cutoff, changed) == universe_at("SYN_U", cutoff, ref) or {
        r["security_id"] for r in universe_at("SYN_U", cutoff, changed)
    } == {"SYN_A:001", "SYN_B:001"}
    positive = deepcopy(tables)
    price(positive["bars_daily"][0], "110")
    assert query(spec, cutoff, make_snapshot(positive)).table["close"].to_pylist() == [Decimal(110)]
    assert query(spec, cutoff, ref).table.to_pylist() == before


@given(st.permutations([0, 1, 2, 3]))
def test_data_009_order_independent_reference(order):
    records = []
    for sid, revision, available, value in [
        ("A", 1, "2024-01-02T16:05:00Z", "100"),
        ("A", 2, "2024-01-03T10:00:00Z", "101"),
        ("B", 1, "2024-01-02T16:05:00Z", "200"),
        ("A", 3, "2024-01-04T00:00:00Z", "999"),
    ]:
        records.append(
            dict(
                security_id=sid,
                session_date=date(2024, 1, 2),
                revision_id=revision,
                event_time=utc("2024-01-02T16:00:00Z"),
                available_at=utc(available),
                close=Decimal(value),
            )
        )
    # Independently enumerated answer at cutoff; no SDK/helper generates expectations.
    result = visible_rows("bars_daily", [records[i] for i in order], "2024-01-03T10:00:00Z")
    assert [(r["security_id"], r["close"]) for r in result] == [
        ("A", Decimal(101)),
        ("B", Decimal(200)),
    ]


def test_query_errors_and_empty(tables, make_snapshot, spec):
    ref = make_snapshot(tables)
    with pytest.raises(ContractError):
        query(None, "2024-01-03T16:00:00Z", ref)
    for changes in [
        dict(market_id="UNKNOWN"),
        dict(fields=("SQL",)),
        dict(fields=("total_return_index",)),
        dict(security_ids=("ABSENT",)),
        dict(security_ids=("SYN_B:001",)),
        dict(calendar_id="unknown"),
    ]:
        with pytest.raises(ContractError):
            query(replace(spec, **changes), "2024-01-03T16:00:00Z", ref)
    empty = query(spec, "2024-01-02T16:00:00Z", ref)
    assert empty.table.num_rows == 0 and empty.metadata["empty_reason"] == "NO_VISIBLE_OBSERVATIONS"
    assert dict(empty.quality_counts)["empty"] == 1
    for changes in [
        dict(security_ids=[]),
        dict(security_ids=()),
        dict(security_ids=("A", "A")),
        dict(security_ids=(1,)),
        dict(fields=[]),
        dict(fields=()),
        dict(fields=("close", "close")),
        dict(session_range=(date(2024, 1, 3), date(2024, 1, 2))),
        dict(session_range=("2024-01-01", date(2024, 1, 2))),
        dict(session_range=()),
        dict(schema_version="wrong"),
        dict(price_basis="wrong"),
    ]:
        with pytest.raises(ContractError):
            replace(spec, **changes)
    overlap = deepcopy(tables["security_status"][0])
    overlap["effective_from"] += timedelta(hours=1)
    tables["security_status"].append(overlap)
    with pytest.raises(DataQualityError, match="OVERLAPPING"):
        status_at("SYN_A:001", "2024-01-03T00:00:00Z", make_snapshot(tables))
