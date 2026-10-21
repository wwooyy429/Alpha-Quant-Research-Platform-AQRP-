"""Versioned deterministic logical projections; explicit Decimal/time encoding."""

import hashlib
import json
from datetime import date, datetime
from decimal import Decimal

from .time import utc


def default(value):
    if isinstance(value, datetime):
        return utc(value).isoformat(timespec="microseconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    raise TypeError(type(value).__name__)


def canonical(value):
    return json.dumps(
        value,
        default=default,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()
