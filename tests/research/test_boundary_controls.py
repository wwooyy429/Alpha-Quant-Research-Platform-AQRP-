from copy import deepcopy
from datetime import date
from types import SimpleNamespace

import pytest

from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.exposures import exposures_as_of, publish_exposures
from aqrp.data.synthetic import load_synthetic, record
from aqrp.validation import labels as module
from aqrp.validation.labels import CoverageRef, _coverage, make_labels


def test_coverage_revisions_are_selected_before_sufficiency():
    parent = "a" * 64
    rows = [
        {
            "coverage_id": "w",
            "event_time": "2024-01-03T12:00:00Z",
            "available_at": "2024-01-03T12:00:00Z",
            "complete_through": "2024-01-03T12:00:00Z",
            "revision_id": 1,
        },
        {
            "coverage_id": "w",
            "event_time": "2024-01-03T12:00:00Z",
            "available_at": "2024-01-04T12:00:00Z",
            "complete_through": "2024-01-02T12:00:00Z",
            "revision_id": 2,
        },
    ]
    c = CoverageRef.create(parent, rows, authority="unit-fixture", scope="PUBLIC_ENGINEERING")
    assert _coverage(c, parent, utc("2024-01-05T00:00:00Z"), utc("2024-01-03T09:00:00Z")) is None
    rows[1]["available_at"] = rows[0]["available_at"]
    with pytest.raises(ContractError, match="AMBIGUOUS_COVERAGE_REVISION"):
        _coverage(
            CoverageRef.create(parent, rows, authority="unit", scope="PUBLIC_ENGINEERING"),
            parent,
            utc("2024-01-05T00:00:00Z"),
            utc("2024-01-03T09:00:00Z"),
        )
    rows[1]["available_at"] = "2024-01-01T00:00:00Z"
    with pytest.raises(ContractError, match="INVALID_COVERAGE_TIME"):
        _coverage(
            CoverageRef.create(parent, rows, authority="unit", scope="PUBLIC_ENGINEERING"),
            parent,
            utc("2024-01-05T00:00:00Z"),
            utc("2024-01-03T09:00:00Z"),
        )


def test_label_defensive_guards_on_unit_reader(make_snapshot, monkeypatch):
    tables = load_synthetic(sessions=[(date(2024, 1, i), "12:00:00") for i in (2, 3, 4, 5)])
    s = make_snapshot(tables)

    def reader(_):
        return {}, {
            k: SimpleNamespace(to_pylist=lambda rows=v: deepcopy(rows)) for k, v in tables.items()
        }

    monkeypatch.setattr(module, "read_snapshot", reader)
    c = CoverageRef.create(
        s.manifest_hash,
        [
            {
                "event_time": "2024-01-05T12:00:00Z",
                "available_at": "2024-01-05T12:00:00Z",
                "complete_through": "2024-01-05T12:00:00Z",
                "revision_id": 1,
            }
        ],
        authority="unit",
        scope="PUBLIC_ENGINEERING",
    )
    decision = {"session": date(2024, 1, 2), "decision_time": "2024-01-02T12:05:00Z"}

    def execute():
        return make_labels(s, [decision], ["SYN_A:001"], [1], "2024-01-05T12:05:00Z", c)

    assert execute()[0]["reason"] == "NONE"
    decision["decision_time"] = "2024-01-03T09:00:00Z"
    with pytest.raises(ContractError, match="SIGNAL_NOT_BEFORE_ENTRY"):
        execute()
    decision["decision_time"] = "2024-01-02T12:05:00Z"
    entry = next(
        r
        for r in tables["bars_daily"]
        if r["security_id"] == "SYN_A:001" and r["session_date"].day == 3
    )
    entry["currency"] = "wrong"
    with pytest.raises(ContractError, match="LABEL_UNITS_OR_PRICE_BASIS"):
        execute()
    entry["currency"] = "SYNCCY"
    entry["open"] = 0
    with pytest.raises(ContractError, match="INVALID_FORWARD_PRICE"):
        execute()
    entry["open"] = 100
    duplicate = deepcopy(tables["calendar"][0])
    duplicate["calendar_id"] = "another-synthetic-calendar"
    tables["calendar"].append(duplicate)
    with pytest.raises(ContractError, match="AMBIGUOUS_LABEL_CALENDAR"):
        execute()


def test_exposure_nulls_duplicates_conflicts_overlap_and_missing(make_snapshot, tmp_path):
    s = make_snapshot(load_synthetic())
    row = {
        "security_id": "SYN_A:001",
        "market_id": "SYN_A",
        "currency": "SYNCCY",
        "industry_version": "1",
        "industry": None,
        "market_cap": None,
        "event_time": "2024-01-01T00:00:00Z",
        "available_at": "2024-01-01T00:00:00Z",
        "effective_from": "2024-01-01T00:00:00Z",
        "effective_to": None,
        "revision_id": 1,
        "risk_exposures": {"beta": None},
    }
    ref = publish_exposures([row], s, tmp_path / "valid")
    actual = exposures_as_of(ref, "2024-01-04T00:00:00Z", "SYN_A", "SYNCCY", {"SYN_A:001"})[
        "SYN_A:001"
    ]
    assert actual["market_cap"] is None and actual["risk_exposures"]["beta"] is None
    for records, code in (
        ([], "EMPTY_EXPOSURES"),
        ([row, row], "DUPLICATE_EXPOSURE"),
        ([{**row, "industry": ""}], "INVALID_INDUSTRY"),
        ([{**row, "security_id": "unknown"}], "EXPOSURE_PARENT_IDENTITY_MISMATCH"),
        ([{**row, "risk_exposures": {"beta": float("inf")}}], "INVALID_RISK_EXPOSURE"),
    ):
        with pytest.raises(ContractError, match=code):
            publish_exposures(records, s, tmp_path / "invalid")
    r2 = {**row, "revision_id": 2}
    ref = publish_exposures([row, r2], s, tmp_path / "conflict")
    with pytest.raises(ContractError, match="CONFLICTING_VISIBLE_EXPOSURE"):
        exposures_as_of(ref, "2024-01-04T00:00:00Z", "SYN_A", "SYNCCY", {"SYN_A:001"})
    r2.update(effective_from="2024-01-02T00:00:00Z")
    ref = publish_exposures([row, r2], s, tmp_path / "overlap")
    with pytest.raises(ContractError, match="OVERLAPPING_EXPOSURE_INTERVAL"):
        exposures_as_of(ref, "2024-01-04T00:00:00Z", "SYN_A", "SYNCCY", {"SYN_A:001"})
    row["effective_to"] = "2024-01-03T00:00:00Z"
    ref = publish_exposures([row], s, tmp_path / "expired")
    assert exposures_as_of(ref, "2024-01-04T00:00:00Z", "SYN_A", "SYNCCY", {"SYN_A:001"}) == {}


def test_action_defensive_unit_guards_and_status_ties(make_snapshot, monkeypatch):
    from decimal import Decimal

    tables = load_synthetic(sessions=[(date(2024, 1, i), "12:00:00") for i in (2, 3, 4, 5)])
    s = make_snapshot(tables)
    monkeypatch.setattr(
        module,
        "read_snapshot",
        lambda _: (
            {},
            {
                k: SimpleNamespace(to_pylist=lambda rows=v: deepcopy(rows))
                for k, v in tables.items()
            },
        ),
    )
    coverage = CoverageRef.create(
        s.manifest_hash,
        [
            {
                "event_time": "2024-01-05T12:00:00Z",
                "available_at": "2024-01-05T12:00:00Z",
                "complete_through": "2024-01-05T12:00:00Z",
                "revision_id": 1,
            }
        ],
        authority="unit-fixture",
        scope="PUBLIC_ENGINEERING",
    )

    def execute(horizon=1):
        return make_labels(
            s,
            [{"session": date(2024, 1, 2), "decision_time": "2024-01-02T12:05:00Z"}],
            ["SYN_A:001"],
            [horizon],
            "2024-01-05T12:05:00Z",
            coverage,
        )

    assert execute(10)[0]["reason"] == "INSUFFICIENT_FORWARD_SESSIONS"
    action = record(
        "corporate_actions",
        action_id="div",
        security_id="SYN_A:001",
        revision_id=1,
        type="CASH_DIVIDEND",
        currency="wrong",
        dividend_basis="PER_OLD_SHARE",
        cash_per_share=Decimal(2),
        effective_at=utc("2024-01-03T11:00:00Z"),
    )
    tables["corporate_actions"] = [action]
    with pytest.raises(ContractError, match="LABEL_ACTION_CURRENCY"):
        execute()
    action["currency"] = "SYNCCY"
    action["dividend_basis"] = "wrong"
    with pytest.raises(ContractError, match="LABEL_DIVIDEND_BASIS"):
        execute()
    action["dividend_basis"] = "PER_OLD_SHARE"
    closes = [r["close_at"] for r in tables["calendar"]]
    for row in tables["calendar"]:
        row["close_at"] = utc("2024-01-06T12:00:00Z")
    with pytest.raises(ContractError, match="MISSING_ACTION_UNIT_ANCHOR"):
        execute()
    for row, close in zip(tables["calendar"], closes):
        row["close_at"] = close
    tables["corporate_actions"] += [
        {
            **action,
            "action_id": f"split{i}",
            "type": "SPLIT",
            "effective_at": utc(f"2024-01-03T{hour}:00:00Z"),
            "split_ratio": Decimal(2),
        }
        for i, hour in enumerate(("09", "10"))
    ]
    with pytest.raises(ContractError, match="UNSUPPORTED_ACTION_CHAIN"):
        execute()
    tables["corporate_actions"] = []
    status = deepcopy(tables["security_status"][0])
    status["revision_id"] = 2
    tables["security_status"].append(status)
    with pytest.raises(ContractError, match="CONFLICTING_VISIBLE_STATUS"):
        execute()
    tables["security_status"].append(
        {**status, "revision_id": 3, "available_at": utc("2024-01-02T00:00:00Z")}
    )
    assert execute()[0]["reason"] == "NONE"
    tables["security_status"].append(
        {
            **status,
            "revision_id": 4,
            "available_at": utc("2024-01-06T00:00:00Z"),
            "status": "SUSPENDED",
        }
    )
    assert execute()[0]["reason"] == "NONE"
