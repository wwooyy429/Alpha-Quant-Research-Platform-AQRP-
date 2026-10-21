"""Frozen G1 visibility inputs lifted explicitly into valid P1 eight-table fixtures."""

import json
from copy import deepcopy
from datetime import date
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.synthetic import load_synthetic, record
from aqrp.validation.labels import CoverageRef, make_labels

G1 = Path(__file__).resolve().parents[2] / "docs/audits/phase-3"
CASES = json.loads((G1 / "label_visibility_v2.json").read_bytes())["cases"]


def fixture(case):
    """Adapter only: no financial expected results calculated here.

    P1 per-session calendar event=open is required by its frozen contract;
    source calendar metadata is a prior schedule catalogue, not a P1 row.
    Frozen financial/time values are copied without defaults or inferred times.
    Public master/status/unit metadata is supplied by P1 synthetic profile.
    """
    days = [date.fromisoformat(r["date"]) for r in case["calendar"]["sessions"]]
    tables = load_synthetic(sessions=[(d, "16:00:00") for d in days])
    for row in tables["calendar"]:
        source = next(
            r for r in case["calendar"]["sessions"] if r["date"] == str(row["session_date"])
        )
        row.update(
            open_at=utc(source["open_at"]),
            close_at=utc(source["close_at"]),
            event_time=utc(source["open_at"]),
        )
    bars = []
    for b in case["bars"]:
        row = deepcopy(
            next(
                r
                for r in tables["bars_daily"]
                if r["security_id"] == "SYN_A:001" and str(r["session_date"]) == b["session_date"]
            )
        )
        price = Decimal(b["open"])
        row.update({f: price for f in ("open", "close", "high", "low")})
        row.update(
            amount=price * 10,
            source_amount=str(price * 10),
            revision_id=b["revision_id"],
            event_time=utc(b["event_time"]),
            available_at=utc(b["available_at"]),
        )
        bars.append(row)
    tables["bars_daily"] = bars
    tables["corporate_actions"] = [
        record(
            "corporate_actions",
            action_id=a["action_id"],
            security_id="SYN_A:001",
            revision_id=a["revision_id"],
            type=a["type"],
            announcement_at=utc(a["announcement_at"]),
            event_time=utc(a["event_time"]),
            available_at=utc(a["available_at"]),
            effective_at=utc(a["effective_at"]),
            ex_date=date.fromisoformat(a["ex_date"]),
            record_date=date.fromisoformat(a["record_date"]),
            pay_date=date.fromisoformat(a["pay_date"]),
            split_ratio=Decimal(a["split_ratio"]) if a["split_ratio"] is not None else None,
            cash_per_share=Decimal(a["cash_per_share"])
            if a["cash_per_share"] is not None
            else None,
            dividend_basis=a["dividend_basis"],
            currency="SYNCCY",
        )
        for a in case["actions"]
    ]
    return tables


def execute(case, snapshot):
    versions = [
        {
            "event_time": r["event_time"],
            "available_at": r["available_at"],
            "complete_through": r["actions_complete_through"],
            "revision_id": r["revision_id"],
        }
        for r in case["coverage_versions"]
    ]
    coverage = CoverageRef.create(
        snapshot.manifest_hash, versions, authority="frozen-g1-input", scope="PUBLIC_ENGINEERING"
    )
    return make_labels(
        snapshot,
        [
            {
                "session": date.fromisoformat(case["calendar"]["sessions"][0]["date"]),
                "decision_time": case["signal_decision_time"],
            }
        ],
        ["SYN_A:001"],
        [case["h"]],
        case["evaluation_cutoff"],
        coverage,
    )[0]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_all_frozen_visibility_cases(case, make_snapshot):
    result = execute(case, make_snapshot(fixture(case)))
    expected = case["expected"]
    if expected["return"] is None:
        assert result["label"] is None and result["available_at"] is None
    else:
        assert result["label"] == pytest.approx(
            float(Fraction(expected["return"])), rel=1e-10, abs=1e-12
        )
        assert Decimal(result["shares"]) == Decimal(expected["shares"])
        assert Decimal(result["credit"]) == Decimal(expected["credit"])
        assert result["available_at"] == utc(expected["label_available_at"])


def test_invalid_or_untradable_forward_data(make_snapshot):
    case = CASES[0]
    tables = fixture(case)
    tables["bars_daily"] = []
    assert execute(case, make_snapshot(tables))["reason"] == "MISSING_FORWARD_OPEN"
    tables = fixture(case)
    tables["security_status"][0]["status"] = "SUSPENDED"
    assert execute(case, make_snapshot(tables))["reason"] == "FORWARD_STATUS_UNTRADABLE_OR_UNKNOWN"
    tables = fixture(case)
    tables["security_master"][0]["delisting_at"] = utc(case["exit_at"])
    assert execute(case, make_snapshot(tables))["label"] is None


def test_coverage_integrity_and_invalid_inputs(make_snapshot):
    s = make_snapshot(fixture(CASES[0]))
    with pytest.raises(ContractError, match="INVALID_COVERAGE_AUTHORITY"):
        CoverageRef.create(s.manifest_hash, [], authority="", scope="PUBLIC_ENGINEERING")
    ref = CoverageRef.create(s.manifest_hash, [], authority="test", scope="PUBLIC_ENGINEERING")
    with pytest.raises(ContractError):
        ref.read("a" * 64)
    for horizon in ([], [0], [True]):
        with pytest.raises(ContractError):
            make_labels(s, [], ["SYN_A:001"], horizon, CASES[0]["evaluation_cutoff"], ref)
    with pytest.raises(ContractError, match="UNKNOWN_LABEL_SECURITY"):
        make_labels(s, [], ["unknown"], [1], CASES[0]["evaluation_cutoff"], ref)
