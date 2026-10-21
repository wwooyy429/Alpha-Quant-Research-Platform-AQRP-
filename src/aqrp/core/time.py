"""UTC microsecond ingress with a pinned package-only IANA database."""

import re
from datetime import UTC, datetime
from importlib.resources import files
from zoneinfo import ZoneInfo

from .errors import ContractError, TimestampResolutionError


def iana(name):
    if not isinstance(name, str) or any(p in ("", ".", "..") for p in name.split("/")):
        raise ContractError("INVALID_TIMEZONE", "source_timezone")
    try:
        with files("tzdata.zoneinfo").joinpath(*name.split("/")).open("rb") as f:
            return ZoneInfo.from_file(f, key=name)
    except (OSError, ValueError):
        raise ContractError("INVALID_TIMEZONE", "source_timezone") from None


def utc(value, source_timezone=None, field="timestamp"):
    if isinstance(value, str):
        # ISO-8601 with explicit offset only. No silent nanosecond rounding.
        fractional = re.search(r"[.,](\d+)", value)
        if fractional and len(fractional[1]) > 6 and any(c != "0" for c in fractional[1][6:]):
            raise TimestampResolutionError("SUB_MICROSECOND", field)
        if "T" not in value and " " not in value:
            raise ContractError("DATE_IS_NOT_TIMESTAMP", field)
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            raise ContractError("INVALID_TIMESTAMP", field) from None
    if getattr(value, "nanosecond", 0):
        raise TimestampResolutionError("SUB_MICROSECOND", field)
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ContractError("AWARE_TIMESTAMP_REQUIRED", field)
    if source_timezone is not None:
        zone = iana(source_timezone)
        actual = value.astimezone(UTC).astimezone(zone)
        if (
            actual.replace(tzinfo=None) != value.replace(tzinfo=None)
            or actual.utcoffset() != value.utcoffset()
        ):
            raise ContractError("IANA_OFFSET_MISMATCH", field)
    return value.astimezone(UTC)


def localize(value, source_timezone, fold=None):
    """Explicit wall-clock adapter. Ambiguous clocks require a stated fold."""
    if not isinstance(value, datetime) or value.tzinfo is not None or fold not in (None, 0, 1):
        raise ContractError("NAIVE_WALL_CLOCK_REQUIRED", "local_time")
    zone = iana(source_timezone)
    candidates = []
    for f in (0, 1):
        c = value.replace(tzinfo=zone, fold=f)
        if c.astimezone(UTC).astimezone(zone).replace(tzinfo=None) == value:
            candidates.append(c)
    if not candidates:
        raise ContractError("NONEXISTENT_LOCAL_TIME", "local_time")
    if fold is None and len({c.utcoffset() for c in candidates}) > 1:
        raise ContractError("AMBIGUOUS_LOCAL_TIME", "local_time")
    return utc(value.replace(tzinfo=zone, fold=fold or 0), source_timezone)
