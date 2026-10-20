"""Strict normalization, mutually exclusive quality counts, and relational checks."""

from dataclasses import dataclass
from datetime import date, datetime

import pyarrow as pa

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError, DataQualityError
from aqrp.core.time import iana, utc
from aqrp.core.units import PROFILE, convert, decimal

from .schemas import KEYS, LOGICAL_KEYS, QUALITY, SCHEMAS


@dataclass(frozen=True)
class QualityReport:
    input: int
    valid: int
    duplicate: int
    missing: int
    rejected: int
    reasons: tuple


@dataclass(frozen=True)
class ValidationResult:
    table: pa.Table
    report: QualityReport


def normalize(name, row):
    schema = SCHEMAS[name]
    if set(row) != set(schema.names):
        raise ContractError("FIELDS_MISMATCH", name)
    r = dict(row)
    iana(r["source_timezone"])
    for field in schema:
        v = r[field.name]
        if v is None:
            continue
        if pa.types.is_timestamp(field.type):
            # Persistent timestamps are canonical UTC; offset-bearing source clocks
            # must additionally agree with the retained source IANA zone.
            if isinstance(v, str):
                r[field.name] = utc(v, field=field.name)
                original = datetime.fromisoformat(v)
            else:
                r[field.name] = utc(v, field=field.name)
                original = v
            if original.utcoffset().total_seconds() != 0:
                utc(original, r["source_timezone"], field.name)
        elif pa.types.is_decimal(field.type):
            r[field.name] = decimal(v, field.name)
        elif pa.types.is_date(field.type):
            if isinstance(v, str):
                r[field.name] = date.fromisoformat(v)
            elif not isinstance(v, date) or isinstance(v, datetime):
                raise ContractError("DATE_REQUIRED", field.name)
        elif pa.types.is_integer(field.type):
            if type(v) is not int or v < 0:
                raise ContractError("NONNEGATIVE_INTEGER_REQUIRED", field.name)
        elif not isinstance(v, str) or not v:
            raise ContractError("NONEMPTY_STRING_REQUIRED", field.name)
    required = {
        "schema_version",
        "snapshot_id",
        "source_id",
        "source_record_id",
        "ingested_at",
        "quality_status",
        "reason_code",
        "source_timezone",
        "event_time",
        *KEYS[name],
    }
    if any(r[k] is None for k in required) or r["schema_version"] != PROFILE.schema_version:
        raise ContractError("REQUIRED_LINEAGE_OR_KEY", name)
    if r["quality_status"] not in QUALITY:
        raise ContractError("UNKNOWN_QUALITY", name)
    mandatory = {
        "security_master": (
            "market_id",
            "venue_mic",
            "asset_type",
            "currency",
            "listing_at",
            "known_at",
        ),
        "calendar": ("market_id", "open_at", "close_at", "calendar_version"),
        "bars_daily": ("market_id", "calendar_id", "currency", "price_basis", "source_scale"),
        "symbol_alias": ("security_id",),
        "security_status": ("status",),
        "corporate_actions": (
            "security_id",
            "type",
            "announcement_at",
            "effective_at",
            "ex_date",
            "currency",
        ),
        "adjustment_factors": ("ratio", "action_id", "method", "view_cutoff"),
        "universe_membership": (),
    }
    if any(r[k] is None for k in mandatory[name]):
        raise ContractError("REQUIRED_TABLE_FIELD", name)
    if name == "security_master" and (
        r["known_at"] > r["available_at"] if r["available_at"] is not None else False
    ):
        raise ContractError("MASTER_KNOWN_AFTER_AVAILABLE", name)
    if r["available_at"] is None:
        r["quality_status"] = "UNKNOWN_AVAILABILITY"
        r["reason_code"] = "NO_HISTORICAL_AVAILABILITY"
    if "currency" in r and r["currency"] != PROFILE.currency:
        raise ContractError("UNSUPPORTED_CURRENCY", "currency")
    if "market_id" in r and r["market_id"] not in PROFILE.markets:
        raise ContractError("UNKNOWN_MARKET", "market_id")
    if (
        "effective_to" in r
        and r["effective_to"] is not None
        and r["effective_to"] <= r["effective_from"]
    ):
        raise ContractError("INVALID_INTERVAL", name)
    if name == "calendar":
        if r["open_at"] is None or r["close_at"] is None or r["open_at"] >= r["close_at"]:
            raise ContractError("INVALID_SESSION", name)
        if (
            r["event_time"] != r["open_at"]
            or r["event_time"].astimezone(iana(r["source_timezone"])).date() != r["session_date"]
        ):
            raise ContractError("INVALID_SESSION_DATE", name)
    if name == "bars_daily":
        if r["price_basis"] != "RAW" or r["source_scale"] is None or r["source_scale"] > 8:
            raise ContractError("RAW_OR_SOURCE_SCALE", name)
        prices = [r[f] for f in ("open", "high", "low", "close")]
        if any(v is not None and (v <= 0 or v % PROFILE.tick) for v in prices):
            raise ContractError("INVALID_PRICE", name)
        if all(v is not None for v in prices) and not (
            r["low"] <= min(r["open"], r["close"]) <= max(r["open"], r["close"]) <= r["high"]
        ):
            raise ContractError("OHLC_ORDER", name)
        if r["volume"] is not None:
            expected = convert(r["source_volume"], r["source_volume_unit"], lot_size=r["lot_size"])
            if r["volume"] != expected:
                raise ContractError("VOLUME_UNIT_MISMATCH", name)
        if r["amount"] is not None:
            if r["amount"] != convert(r["source_amount"], r["source_amount_unit"]):
                raise ContractError("AMOUNT_UNIT_MISMATCH", name)
        if r["available_at"] is not None and r["available_at"] < r["event_time"]:
            raise ContractError("BAR_BEFORE_CLOSE", name)
        if any(r[f] is None for f in ("open", "high", "low", "close", "volume", "amount")):
            r["quality_status"], r["reason_code"] = "MISSING", "NULL_OBSERVATION"
    if name == "corporate_actions":
        if (
            r["type"] not in ("SPLIT", "CASH_DIVIDEND")
            or r["announcement_at"] is None
            or r["effective_at"] is None
        ):
            raise ContractError("INVALID_ACTION", name)
        if r["event_time"] != r["announcement_at"] or (
            r["available_at"] is not None and r["available_at"] < r["announcement_at"]
        ):
            raise ContractError("ACTION_AVAILABILITY", name)
        if r["type"] == "SPLIT" and (r["split_ratio"] is None or r["split_ratio"] <= 0):
            raise ContractError("INVALID_SPLIT", name)
        if r["type"] == "CASH_DIVIDEND" and (
            r["cash_per_share"] is None
            or r["cash_per_share"] < 0
            or r["dividend_basis"] != "PER_OLD_SHARE"
        ):
            raise ContractError("UNKNOWN_DIVIDEND_BASIS", name)
    if name == "security_status" and r["status"] not in ("TRADABLE", "SUSPENDED", "DELISTED"):
        raise ContractError("UNKNOWN_STATUS", name)
    if name == "adjustment_factors" and (
        r["ratio"] is None or r["ratio"] <= 0 or r["method"] != "SPLIT"
    ):
        raise ContractError("INVALID_ADJUSTMENT", name)
    return r


def validate_table(name, rows):
    if name not in SCHEMAS:
        raise ContractError("UNSUPPORTED_TABLE", name)
    accepted, reasons, seen = [], [], {}
    counts = dict(valid=0, duplicate=0, missing=0, rejected=0)
    rows = list(rows)
    for i, row in enumerate(rows):
        try:
            r = normalize(name, row)
            key = tuple(r[k] for k in KEYS[name])
            content = canonical(r)
            if key in seen:
                if seen[key] != content:
                    raise DataQualityError("CONFLICTING_PHYSICAL_KEY", name)
                counts["duplicate"] += 1
                reasons.append((i, "EXACT_DUPLICATE"))
                continue
            seen[key] = content
            if r["quality_status"] in ("INVALID", "STALE", "INSUFFICIENT_HISTORY"):
                raise DataQualityError("UNPUBLISHABLE_QUALITY", name)
            accepted.append(r)
            counts[
                "missing" if r["quality_status"] in ("MISSING", "UNKNOWN_AVAILABILITY") else "valid"
            ] += 1
        except (ContractError, ValueError, TypeError) as e:
            counts["rejected"] += 1
            reasons.append((i, getattr(e, "code", "INVALID_TYPE")))
    accepted.sort(key=lambda r: canonical([r[k] for k in KEYS[name]]))
    return ValidationResult(
        pa.Table.from_pylist(accepted, schema=SCHEMAS[name]),
        QualityReport(len(rows), **counts, reasons=tuple(reasons)),
    )


def validate_dataset(tables, *, exploratory=False):
    if set(tables) != set(SCHEMAS):
        raise DataQualityError("REQUIRED_TABLE_SET", "tables")
    validated = {
        n: validate_table(n, t.to_pylist() if isinstance(t, pa.Table) else t)
        for n, t in tables.items()
    }
    if any(v.report.rejected for v in validated.values()):
        raise DataQualityError("QUARANTINED_ROWS", "tables")
    rows = {n: v.table.to_pylist() for n, v in validated.items()}
    if not rows["security_master"] or not rows["calendar"]:
        raise DataQualityError("EMPTY_MASTER_OR_CALENDAR", "tables")
    if not exploratory and any(r["available_at"] is None for t in rows.values() for r in t):
        raise DataQualityError("UNKNOWN_AVAILABILITY", "available_at")
    master = {}
    for r in rows["security_master"]:
        identity = (r["market_id"], r["currency"], r["venue_mic"], r["asset_type"])
        if r["security_id"] in master and master[r["security_id"]] != identity:
            raise DataQualityError("SECURITY_ID_REUSED", "security_id")
        master[r["security_id"]] = identity
    sessions = {(r["calendar_id"], r["session_date"]): r for r in rows["calendar"]}
    for n, records in rows.items():
        revisions = {}
        for r in records:
            if "revision_id" in r:
                revisions.setdefault(tuple(r[k] for k in LOGICAL_KEYS[n]), []).append(r)
            if "security_id" in r and r["security_id"] not in master:
                raise DataQualityError("UNKNOWN_SECURITY", n)
            if (
                "security_id" in r
                and "market_id" in r
                and r["market_id"] != master[r["security_id"]][0]
            ):
                raise DataQualityError("SECURITY_MARKET_MISMATCH", n)
            if n == "bars_daily":
                session = sessions.get((r["calendar_id"], r["session_date"]))
                if (
                    not session
                    or session["close_at"] != r["event_time"]
                    or session["market_id"] != r["market_id"]
                ):
                    raise DataQualityError("BAR_SESSION_MISMATCH", n)
        for group in revisions.values():
            ordered = sorted(
                (r for r in group if r["available_at"] is not None), key=lambda r: r["revision_id"]
            )
            if any(a["available_at"] > b["available_at"] for a, b in zip(ordered, ordered[1:])):
                raise DataQualityError("NONMONOTONIC_REVISION", n)
    for factor in rows["adjustment_factors"]:
        matches = [
            a
            for a in rows["corporate_actions"]
            if a["action_id"] == factor["action_id"]
            and a["security_id"] == factor["security_id"]
            and a["type"] == "SPLIT"
            and a["effective_at"] == factor["effective_at"]
            and a["split_ratio"] == factor["ratio"]
            and a["available_at"] is not None
            and factor["available_at"] is not None
            and a["available_at"] <= factor["available_at"]
        ]
        if not matches:
            raise DataQualityError("UNVERIFIABLE_ADJUSTMENT_FACTOR", "action_id")
    return validated
