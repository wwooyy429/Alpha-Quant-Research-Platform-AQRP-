"""Small deterministic, explicit sessions. No vendor or exchange claims."""

import random
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from aqrp.core.time import utc

from .schemas import SCHEMAS

PROVENANCE = {
    "source_version": "synthetic/1",
    "source_license": "project-generated-test-data",
    "unit_version": "synthetic-units/1",
    "calendar_version": "synthetic-calendar/1",
    "universe_version": "synthetic-universe/1",
    "actions_version": "synthetic-actions/1",
    "profile_id": "SYNTHETIC_V1",
    "parent_snapshot": None,
}


def record(name, **fields):
    """Fixture/source construction only. It never computes expected query answers."""
    row = dict.fromkeys(SCHEMAS[name].names)
    row.update(
        schema_version="data/1.0.0",
        snapshot_id="unpublished",
        source_id="SYNTHETIC",
        source_record_id="synthetic-row",
        ingested_at=utc("2024-02-01T00:00:00Z"),
        quality_status="VALID",
        reason_code="NONE",
        source_timezone="UTC",
        event_time=utc("2024-01-01T00:00:00Z"),
        available_at=utc("2024-01-01T00:00:00Z"),
    )
    row.update(fields)
    return row


def load_synthetic(seed=17, *, sessions=None):
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if sessions is None:
        sessions = [(date(2024, 1, 2), "16:00:00"), (date(2024, 1, 3), "12:00:00")]
    randomizer = random.Random(seed)
    tables = {name: [] for name in SCHEMAS}
    for market in ("SYN_A", "SYN_B"):
        sid, cal = market + ":001", market + "_CAL"
        tables["security_master"].append(
            record(
                "security_master",
                security_id=sid,
                revision_id=1,
                market_id=market,
                venue_mic="SYN_VENUE",
                asset_type="SYN_EQUITY",
                currency="SYNCCY",
                listing_at=utc("2024-01-01T00:00:00Z"),
                known_at=utc("2024-01-01T00:00:00Z"),
            )
        )
        tables["symbol_alias"].append(
            record(
                "symbol_alias",
                security_id=sid,
                market_id=market,
                symbol="DUP",
                effective_from=utc("2024-01-01T00:00:00Z"),
                revision_id=1,
            )
        )
        tables["security_status"].append(
            record(
                "security_status",
                security_id=sid,
                effective_from=utc("2024-01-01T00:00:00Z"),
                revision_id=1,
                status="TRADABLE",
            )
        )
        tables["universe_membership"].append(
            record(
                "universe_membership",
                security_id=sid,
                universe_id="SYN_U",
                effective_from=utc("2024-01-01T00:00:00Z"),
                revision_id=1,
            )
        )
        for session_date, close in sessions:
            open_at = datetime.combine(
                session_date, datetime.strptime("09:00:00", "%H:%M:%S").time(), UTC
            )
            close_at = utc(session_date.isoformat() + "T" + close + "Z")
            tables["calendar"].append(
                record(
                    "calendar",
                    calendar_id=cal,
                    market_id=market,
                    session_date=session_date,
                    open_at=open_at,
                    close_at=close_at,
                    calendar_version=PROVENANCE["calendar_version"],
                    event_time=open_at,
                )
            )
            price = Decimal(100 if market == "SYN_A" else 200) + Decimal(randomizer.randint(0, 5))
            tables["bars_daily"].append(
                record(
                    "bars_daily",
                    security_id=sid,
                    market_id=market,
                    calendar_id=cal,
                    session_date=session_date,
                    revision_id=1,
                    currency="SYNCCY",
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=Decimal(10),
                    amount=price * 10,
                    price_basis="RAW",
                    source_scale=2,
                    source_volume_unit="share",
                    source_volume="10",
                    source_amount_unit="currency",
                    source_amount=str(price * 10),
                    event_time=close_at,
                    available_at=close_at + timedelta(minutes=5),
                )
            )
    return tables
