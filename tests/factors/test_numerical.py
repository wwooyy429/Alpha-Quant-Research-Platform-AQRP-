import json
from copy import deepcopy
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from aqrp.core.time import utc
from aqrp.data.synthetic import record
from aqrp.factors import builtin_spec

CUTOFF = "2024-01-04T12:05:00Z"


@pytest.mark.parametrize(
    "factor_id,expected",
    [("momentum", (0.21, -0.2)), ("reversal", (-0.21, 0.2)), ("volume", (0.6, 0.0))],
)
def test_factor_004_005_006_independent_golden(
    factor_id, expected, factor_tables, factor_query, factor_engine, make_snapshot
):
    batch = factor_engine.run(
        builtin_spec(factor_id).ref,
        factor_query,
        CUTOFF,
        make_snapshot(factor_tables),
        parameters={"lookback": 2},
    )
    assert tuple(r.factor_value for r in batch.rows) == pytest.approx(
        expected, abs=1e-12, rel=1e-10
    )
    assert all(r.validity == "VALID" and r.available_at == utc(CUTOFF) for r in batch.rows)
    assert [r.security_id for r in batch.rows] == ["SYN_A:001", "SYN_A:002"]
    assert [r.symbol for r in batch.rows] == ["DUP", "B"]
    assert json.loads(batch.config_snapshot)["spec"]["factor_direction"] == 1


def test_factor_011_only_ref_changes(factor_tables, factor_query, factor_engine, make_snapshot):
    ref = make_snapshot(factor_tables)
    ids = {
        "run_id": "00000000-0000-0000-0000-000000000001",
        "computation_id": "00000000-0000-0000-0000-000000000002",
    }
    a = factor_engine.run(
        builtin_spec("momentum").ref, factor_query, CUTOFF, ref, parameters={"lookback": 2}, **ids
    )
    b = factor_engine.run(
        builtin_spec("reversal").ref, factor_query, CUTOFF, ref, parameters={"lookback": 2}, **ids
    )
    assert a.rows[0].factor_value == 0.21 and b.rows[0].factor_value == -0.21
    for x, y in zip(a.rows, b.rows, strict=True):
        assert x.factor_value == -y.factor_value
        assert x.params_hash == y.params_hash and x.snapshot_id == y.snapshot_id
    assert a.content_hash != b.content_hash


@pytest.mark.parametrize("kind,expected", [("SPLIT", (0.0, 0.0)), ("CASH_DIVIDEND", (-0.01, 0.01))])
def test_factor_action_basis(
    kind, expected, factor_tables, factor_query, factor_engine, make_snapshot
):
    for row in factor_tables["bars_daily"]:
        if row["security_id"] == "SYN_A:001":
            last = row["session_date"].day == 4
            price = Decimal(50 if last and kind == "SPLIT" else 99 if last else 100)
            volume = Decimal(20 if last and kind == "SPLIT" else 10)
            row.update({f: price for f in ("open", "high", "low", "close")})
            row.update(
                volume=volume,
                source_volume=str(volume),
                amount=price * volume,
                source_amount=str(price * volume),
            )
    factor_tables["corporate_actions"].append(
        record(
            "corporate_actions",
            action_id="A",
            security_id="SYN_A:001",
            revision_id=1,
            type=kind,
            announcement_at=utc("2024-01-03T13:00:00Z"),
            effective_at=utc("2024-01-04T09:00:00Z"),
            ex_date=date(2024, 1, 4),
            record_date=date(2024, 1, 4),
            pay_date=date(2024, 1, 5),
            split_ratio=Decimal(2) if kind == "SPLIT" else None,
            cash_per_share=Decimal(1) if kind == "CASH_DIVIDEND" else None,
            currency="SYNCCY",
            dividend_basis="PER_OLD_SHARE",
            event_time=utc("2024-01-03T13:00:00Z"),
            available_at=utc("2024-01-03T13:00:00Z"),
        )
    )
    snapshot = make_snapshot(factor_tables)
    for name, value in zip(("momentum", "reversal"), expected, strict=True):
        result = factor_engine.run(
            builtin_spec(name).ref, factor_query, CUTOFF, snapshot, parameters={"lookback": 1}
        )
        assert result.rows[0].factor_value == pytest.approx(value, abs=1e-12)
    if kind == "SPLIT":
        assert (
            factor_engine.run(
                builtin_spec("volume").ref,
                factor_query,
                CUTOFF,
                snapshot,
                parameters={"lookback": 1},
            )
            .rows[0]
            .factor_value
            == 0.0
        )


@pytest.mark.parametrize(
    "condition,reason",
    [
        ("short", "INSUFFICIENT_HISTORY"),
        ("gap", "MISSING_SESSION"),
        ("missing", "MISSING_INPUT"),
        ("future", "TARGET_NOT_VISIBLE"),
    ],
)
def test_history_boundaries(
    condition, reason, factor_tables, factor_query, factor_engine, make_snapshot
):
    params = {"lookback": 3 if condition == "short" else 2}
    if condition == "gap":
        factor_tables["bars_daily"] = [
            r
            for r in factor_tables["bars_daily"]
            if not (r["security_id"] == "SYN_A:001" and r["session_date"].day == 3)
        ]
    if condition == "missing":
        next(r for r in factor_tables["bars_daily"] if r["security_id"] == "SYN_A:001")["close"] = (
            None
        )
    cutoff = "2024-01-04T12:04:59.999999Z" if condition == "future" else CUTOFF
    result = factor_engine.run(
        builtin_spec("momentum").ref,
        factor_query,
        cutoff,
        make_snapshot(factor_tables),
        parameters=params,
    )
    assert result.rows[0].factor_value is None and result.rows[0].reason == reason
    assert result.rows[0].validity == "INVALID"


@pytest.mark.parametrize(
    "volumes,expected,reason",
    [([0, 0, 200], None, "ZERO_BASE_VOLUME"), ([100, 150, 0], -1.0, "NONE")],
)
def test_zero_volume_distinctions(
    volumes, expected, reason, factor_tables, factor_query, factor_engine, make_snapshot
):
    for row in factor_tables["bars_daily"]:
        if row["security_id"] == "SYN_A:001":
            v = Decimal(volumes[row["session_date"].day - 2])
            row.update(volume=v, source_volume=str(v))
    result = factor_engine.run(
        builtin_spec("volume").ref,
        factor_query,
        CUTOFF,
        make_snapshot(factor_tables),
        parameters={"lookback": 2},
    )
    assert result.rows[0].factor_value == expected and result.rows[0].reason == reason


def test_future_mutations_and_positive_control(
    factor_tables, factor_query, factor_engine, make_snapshot
):
    start = deepcopy(factor_tables)
    cutoff = "2024-01-03T12:05:00Z"
    qs = replace(factor_query, session_range=(date(2024, 1, 2), date(2024, 1, 3)))
    fref = builtin_spec("momentum").ref
    a = factor_engine.run(fref, qs, cutoff, make_snapshot(start), parameters={"lookback": 1})
    future = deepcopy(start)
    for row in future["bars_daily"]:
        if row["session_date"].day == 4:
            row.update({f: Decimal(999) for f in ("open", "high", "low", "close")})
    late = deepcopy(
        next(
            r
            for r in future["bars_daily"]
            if r["security_id"] == "SYN_A:001" and r["session_date"].day == 2
        )
    )
    late.update(revision_id=2, available_at=utc("2024-01-04T12:00:00Z"))
    late.update({f: Decimal(500) for f in ("open", "high", "low", "close")})
    future["bars_daily"].append(late)
    for name in ("universe_membership", "security_status"):
        late = deepcopy(next(r for r in future[name] if r["security_id"] == "SYN_A:001"))
        late.update(revision_id=2, available_at=utc("2024-01-04T12:00:00Z"))
        future[name].append(late)
    b = factor_engine.run(fref, qs, cutoff, make_snapshot(future), parameters={"lookback": 1})
    assert a.logical_hash == b.logical_hash and a.content_hash != b.content_hash
    positive = deepcopy(start)
    for row in positive["bars_daily"]:
        if row["security_id"] == "SYN_A:001" and row["session_date"].day == 3:
            row.update({f: Decimal(120) for f in ("open", "high", "low", "close")})
    c = factor_engine.run(fref, qs, cutoff, make_snapshot(positive), parameters={"lookback": 1})
    assert c.rows[0].factor_value == 0.2 != a.rows[0].factor_value


@settings(
    max_examples=8, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(scale=st.integers(min_value=1, max_value=100))
def test_ratio_scaling_property(scale, factor_tables, factor_query, factor_engine, make_snapshot):
    data = deepcopy(factor_tables)
    for row in data["bars_daily"]:
        for field in ("open", "high", "low", "close", "volume"):
            row[field] *= scale
        row.update(
            source_volume=str(row["volume"]),
            amount=row["close"] * row["volume"],
            source_amount=str(row["close"] * row["volume"]),
        )
    snapshot = make_snapshot(data)
    for name, expected in (("momentum", 0.21), ("reversal", -0.21), ("volume", 0.6)):
        assert factor_engine.run(
            builtin_spec(name).ref, factor_query, CUTOFF, snapshot, parameters={"lookback": 2}
        ).rows[0].factor_value == pytest.approx(expected)


def test_lookback_extreme_252(factor_tables, factor_query, factor_engine, make_snapshot):
    result = factor_engine.run(
        builtin_spec("momentum").ref,
        factor_query,
        CUTOFF,
        make_snapshot(factor_tables),
        parameters={"lookback": 252},
    )
    assert all(r.reason == "INSUFFICIENT_HISTORY" for r in result.rows)


def test_frozen_expected_answers():
    root = Path(__file__).resolve().parents[1] / "golden"
    answers = json.loads((root / "phase2_answers.json").read_bytes())
    assert answers["cases"][0]["expected"] == {
        "momentum": "21/100",
        "reversal": "-21/100",
        "volume": "3/5",
    }
