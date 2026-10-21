"""The single restricted Data API ingress. Every path verifies the snapshot first."""

from dataclasses import asdict

import pyarrow as pa

from aqrp.core.canonical import digest
from aqrp.core.contracts import DataView, QuerySpec
from aqrp.core.errors import ContractError, DataQualityError, TimeLeakageError
from aqrp.core.time import utc
from aqrp.core.units import PROFILE

from .actions import action_view
from .pit import visible_rows
from .schemas import SCHEMAS
from .store import read_snapshot

IDENTITY = (
    "security_id",
    "market_id",
    "calendar_id",
    "session_date",
    "event_time",
    "available_at",
    "revision_id",
    "quality_status",
    "reason_code",
)
FIELDS = {
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "currency",
    "price_basis",
    "total_return_index",
}


def _load(ref, as_of):
    cutoff = utc(as_of, field="as_of")
    manifest, tables = read_snapshot(ref)
    if manifest["pit_status"] != "PIT_VERIFIED":
        raise TimeLeakageError("EXPLORATORY_SNAPSHOT", "snapshot")
    if manifest["provenance"]["profile_id"] != PROFILE.profile_id:
        raise ContractError("UNKNOWN_PROFILE", "snapshot")
    return cutoff, manifest, {n: t.to_pylist() for n, t in tables.items()}


def _effective(name, rows, cutoff, filters):
    records = visible_rows(name, rows, cutoff)
    records = [r for r in records if all(r[k] == v for k, v in filters.items())]
    if name == "corporate_actions":
        records = [r for r in records if r["effective_at"] <= cutoff]
    if name in ("security_status", "symbol_alias", "universe_membership"):
        keys = {
            "security_status": ("security_id",),
            "symbol_alias": ("market_id", "symbol"),
            "universe_membership": ("universe_id", "security_id"),
        }[name]
        seen = set()
        for r in records:
            key = tuple(r[k] for k in keys)
            if key in seen:
                raise DataQualityError("OVERLAPPING_EFFECTIVE_INTERVAL", name)
            seen.add(key)
    return records


def _lookup(name, ref, as_of, filters, announcements=False):
    cutoff, _, tables = _load(ref, as_of)
    if announcements:
        return tuple(dict(r) for r in visible_rows(name, tables[name], cutoff))
    return tuple(dict(r) for r in _effective(name, tables[name], cutoff, filters))


def universe_at(universe_id, as_of, snapshot_ref):
    return _lookup("universe_membership", snapshot_ref, as_of, {"universe_id": universe_id})


def status_at(security_id, as_of, snapshot_ref):
    return _lookup("security_status", snapshot_ref, as_of, {"security_id": security_id})


def aliases_at(market_id, symbol, as_of, snapshot_ref):
    return _lookup("symbol_alias", snapshot_ref, as_of, {"market_id": market_id, "symbol": symbol})


def actions_as_of(as_of, snapshot_ref):
    return _lookup("corporate_actions", snapshot_ref, as_of, {})


def announcements_as_of(as_of, snapshot_ref):
    return _lookup("corporate_actions", snapshot_ref, as_of, {}, announcements=True)


def query(spec, as_of, snapshot_ref):
    if not isinstance(spec, QuerySpec):
        raise ContractError("QUERYSPEC_REQUIRED", "query")
    cutoff, manifest, tables = _load(snapshot_ref, as_of)
    if (
        spec.market_id not in PROFILE.markets
        or any(f not in FIELDS for f in spec.fields)
        or ("total_return_index" in spec.fields and spec.price_basis != "total_return")
    ):
        raise ContractError("UNKNOWN_MARKET_OR_FIELD", "QuerySpec", spec.request_id)
    securities = {
        r["security_id"]: r
        for r in visible_rows("security_master", tables["security_master"], cutoff)
    }
    if any(
        s not in securities or securities[s]["market_id"] != spec.market_id
        for s in spec.security_ids
    ):
        raise ContractError("UNKNOWN_OR_CROSS_MARKET_SECURITY", "security_ids", spec.request_id)
    all_sessions = [
        r
        for r in tables["calendar"]
        if r["calendar_id"] == spec.calendar_id and r["market_id"] == spec.market_id
    ]
    if not all_sessions:
        raise ContractError("UNKNOWN_CALENDAR", "calendar_id", spec.request_id)
    visible_sessions = visible_rows("calendar", all_sessions, cutoff)
    session_dates = {r["session_date"] for r in visible_sessions}
    bars = [
        r
        for r in visible_rows("bars_daily", tables["bars_daily"], cutoff)
        if r["security_id"] in spec.security_ids
        and r["market_id"] == spec.market_id
        and r["calendar_id"] == spec.calendar_id
        and r["session_date"] in session_dates
        and spec.session_range[0] <= r["session_date"] <= spec.session_range[1]
    ]
    actions = _effective("corporate_actions", tables["corporate_actions"], cutoff, {})
    if any(a["quality_status"] != "VALID" for a in actions):
        raise DataQualityError("INVALID_ACTION_QUALITY", "action")
    bars = action_view(bars, actions, spec.price_basis, session_dates)
    bars.sort(key=lambda r: (r["event_time"], r["security_id"], r["revision_id"]))
    columns = list(IDENTITY) + list(spec.fields)
    schema = pa.schema(
        [
            pa.field(f, pa.float64())
            if f == "total_return_index"
            else SCHEMAS["bars_daily"].field(f)
            for f in columns
        ]
    )
    table = pa.Table.from_pylist([{f: r[f] for f in columns} for r in bars], schema=schema)
    config = asdict(spec)
    del config["request_id"]
    query_hash = digest(
        {
            "snapshot": asdict(snapshot_ref) | {"root": str(snapshot_ref.root)},
            "cutoff": cutoff,
            "spec": config,
            "rule_version": "pit/1.0.0",
            "provenance": manifest["provenance"],
        }
    )
    counts = {
        "rows": len(bars),
        "missing": sum(r["quality_status"] == "MISSING" for r in bars),
        "empty": int(not bars),
        "rejected": 0,
    }
    return DataView.from_table(
        table,
        query_hash=query_hash,
        snapshot_ref=snapshot_ref,
        lineage=tuple(
            sorted(
                {
                    "profile_id": PROFILE.profile_id,
                    "as_of": cutoff.isoformat(),
                    "calendar_id": spec.calendar_id,
                    "calendar_version": manifest["provenance"]["calendar_version"],
                    "price_basis": spec.price_basis,
                    "rule_version": "pit/1.0.0",
                    "empty_reason": "NO_VISIBLE_OBSERVATIONS" if not bars else "NONE",
                }.items()
            )
        ),
        quality_counts=tuple(counts.items()),
        request_id=spec.request_id,
    )
