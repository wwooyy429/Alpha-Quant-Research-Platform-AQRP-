"""UTC microsecond ingress with a pinned package-only IANA database."""

import re
from datetime import UTC, datetime, timedelta, timezone
from importlib.resources import files
from zoneinfo import ZoneInfo

from .errors import ContractError, TimestampResolutionError


def iana(name):
    # Validate portable IANA components before joinpath: Windows drives and
    # backslashes must never turn a resource key into an external file path.
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+)*", name):
        raise ContractError("INVALID_TIMEZONE", "source_timezone")
    try:
        with files("tzdata.zoneinfo").joinpath(*name.split("/")).open("rb") as f:
            return ZoneInfo.from_file(f, key=name)
    except (OSError, ValueError):
        raise ContractError("INVALID_TIMEZONE", "source_timezone") from None


def utc(value, source_timezone=None, field="timestamp"):
    if isinstance(value, str):
        # ISO-8601 with explicit offset only. No silent nanosecond rounding.
        fractions = re.findall(r"[.,]([0-9]+)", value)
        if any(any(c != "0" for c in part[6:]) for part in fractions):
            raise TimestampResolutionError("SUB_MICROSECOND", field)
        if "T" not in value and " " not in value:
            raise ContractError("DATE_IS_NOT_TIMESTAMP", field)
        # Fractions apply only to seconds, including optional offset seconds.
        # Validate before fromisoformat can truncate or normalize unsupported text.
        match = re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}:[0-9]{2}"
            r"(?:[.,][0-9]+)?(?P<offset>Z|[+-][0-9]{2}:[0-9]{2}"
            r"(?::[0-9]{2}(?:[.,][0-9]+)?)?)?",
            value,
        )
        if not match:
            raise ContractError("INVALID_TIMESTAMP", field)
        try:
            value = datetime.fromisoformat(value)
            offset = match["offset"]
            if offset and offset != "Z":
                parts = re.split(r"[:.,]", offset[1:])
                hours, minutes = map(int, parts[:2])
                seconds = int(parts[2]) if len(parts) > 2 else 0
                micros = int((parts[3] + "000000")[:6]) if len(parts) > 3 else 0
                if hours > 23 or minutes > 59 or seconds > 59:
                    raise ValueError("offset out of range")
                delta = timedelta(
                    hours=hours, minutes=minutes, seconds=seconds, microseconds=micros
                )
                value = value.replace(tzinfo=timezone(delta if offset[0] == "+" else -delta))
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
