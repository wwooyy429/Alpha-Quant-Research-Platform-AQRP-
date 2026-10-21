"""RAW next-open labels under approved synthetic entitlement and PIT conventions."""

from dataclasses import dataclass
from decimal import Decimal, localcontext

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.pit import visible_rows
from aqrp.data.store import read_snapshot


@dataclass(frozen=True)
class CoverageRef:
    payload: bytes
    checksum: str

    def read(self, parent):
        import json

        data = json.loads(self.payload)
        if (
            digest(data) != self.checksum
            or data["parent_hash"] != parent
            or data["schema"] != "label-coverage/1"
        ):
            raise ContractError("COVERAGE_HASH_OR_PARENT_MISMATCH")
        return data

    @classmethod
    def create(cls, parent, versions, *, authority, scope):
        if not authority or scope not in ("PUBLIC_ENGINEERING", "OPERATOR_SEALED"):
            raise ContractError("INVALID_COVERAGE_AUTHORITY")
        data = {
            "schema": "label-coverage/1",
            "parent_hash": parent,
            "authority": authority,
            "scope": scope,
            "versions": versions,
        }
        return cls(canonical(data), digest(data))


def _coverage(ref, parent, cutoff, end):
    data = ref.read(parent)
    rows = []
    for r in data["versions"]:
        event, available = utc(r["event_time"]), utc(r["available_at"])
        if available < event:
            raise ContractError("INVALID_COVERAGE_TIME")
        if event <= cutoff and available <= cutoff:
            rows.append(r)
    if not rows:
        return None
    # A watermark has revisions; later independent daily watermarks do not
    # retroactively delay already established historical completeness.
    grouped = {}
    for row in rows:
        key = row.get("coverage_id", row["complete_through"])
        grouped.setdefault(key, []).append(row)
    versions = {}
    for key, revisions in grouped.items():
        latest = max(utc(r["available_at"]) for r in revisions)
        selected = [r for r in revisions if utc(r["available_at"]) == latest]
        if len(selected) != 1:
            raise ContractError("AMBIGUOUS_COVERAGE_REVISION")
        versions[key] = selected[0]
    sufficient = [r for r in versions.values() if utc(r["complete_through"]) >= end]
    return (
        min(sufficient, key=lambda r: (utc(r["complete_through"]), utc(r["available_at"])))
        if sufficient
        else None
    )


def make_labels(snapshot, decisions, security_ids, horizons, evaluation_cutoff, coverage):
    cutoff = utc(evaluation_cutoff)
    if not horizons or any(type(h) is not int or h < 1 for h in horizons):
        raise ContractError("INVALID_LABEL_HORIZON")
    _, tables = read_snapshot(snapshot)
    data = {name: t.to_pylist() for name, t in tables.items()}
    master = {
        r["security_id"]: r
        for r in visible_rows("security_master", data["security_master"], cutoff)
    }
    bars = visible_rows("bars_daily", data["bars_daily"], cutoff)
    actions = visible_rows("corporate_actions", data["corporate_actions"], cutoff)
    calendar = visible_rows("calendar", data["calendar"], cutoff)
    # Status revisions are selected at the evaluation cutoff, then evaluated at
    # the historical entry/exit instant (not at today's effective interval).
    grouped_status = {}
    for r in data["security_status"]:
        if r["event_time"] <= cutoff and r["available_at"] <= cutoff:
            key = (r["security_id"], r["effective_from"])
            grouped_status.setdefault(key, []).append(r)
    status_versions = {}
    for key, versions in grouped_status.items():
        latest = max(r["available_at"] for r in versions)
        selected = [r for r in versions if r["available_at"] == latest]
        if len(selected) != 1:
            raise ContractError("CONFLICTING_VISIBLE_STATUS")
        status_versions[key] = selected[0]
    output = []
    for sid in security_ids:
        if sid not in master:
            raise ContractError("UNKNOWN_LABEL_SECURITY")
        security = master[sid]
        sessions = sorted(
            [r for r in calendar if r["market_id"] == security["market_id"]],
            key=lambda r: r["session_date"],
        )
        index = {r["session_date"]: i for i, r in enumerate(sessions)}
        if len(index) != len(sessions):
            raise ContractError("AMBIGUOUS_LABEL_CALENDAR")
        lookup = {r["session_date"]: r for r in bars if r["security_id"] == sid}
        economic = [a for a in actions if a["security_id"] == sid]
        for decision in decisions:
            day = decision["session"]
            for horizon in horizons:
                row = {
                    "security_id": sid,
                    "session": str(day),
                    "horizon": horizon,
                    "label": None,
                    "decision_time": utc(decision["decision_time"]),
                    "available_at": None,
                    "entry_at": None,
                    "exit_at": None,
                    "shares": None,
                    "credit": None,
                    "reason": "INSUFFICIENT_FORWARD_SESSIONS",
                    "snapshot_hash": snapshot.manifest_hash,
                    "coverage_hash": coverage.checksum,
                    "profile": "SYNTHETIC_V1_LABEL_1",
                }
                output.append(row)
                if day not in index or index[day] + 1 + horizon >= len(sessions):
                    continue
                a, b = sessions[index[day] + 1], sessions[index[day] + 1 + horizon]
                entry, exit = a["open_at"], b["open_at"]
                row.update(entry_at=entry, exit_at=exit)
                statuses = []
                for instant in (entry, exit):
                    active = [
                        r
                        for r in status_versions.values()
                        if r["security_id"] == sid
                        and r["effective_from"] <= instant
                        and (r["effective_to"] is None or instant < r["effective_to"])
                    ]
                    statuses.extend(active)
                    if len(active) != 1 or active[0]["status"] != "TRADABLE":
                        row["reason"] = "FORWARD_STATUS_UNTRADABLE_OR_UNKNOWN"
                if (
                    entry < security["listing_at"]
                    or row["reason"] == "FORWARD_STATUS_UNTRADABLE_OR_UNKNOWN"
                    or (
                        security.get("delisting_at") is not None
                        and security["delisting_at"] <= exit
                    )
                ):
                    row["reason"] = "FORWARD_STATUS_UNTRADABLE_OR_UNKNOWN"
                    continue
                if row["decision_time"] >= entry:
                    raise ContractError("SIGNAL_NOT_BEFORE_ENTRY")
                cov = _coverage(coverage, snapshot.manifest_hash, cutoff, exit)
                if cov is None:
                    row["reason"] = "UNKNOWN_ACTION_COVERAGE"
                    continue
                start, end = lookup.get(a["session_date"]), lookup.get(b["session_date"])
                if any(
                    v is None or v["quality_status"] != "VALID" or v["open"] is None
                    for v in (start, end)
                ):
                    row["reason"] = "MISSING_FORWARD_OPEN"
                    continue
                if (
                    start["currency"] != end["currency"]
                    or start["price_basis"] != "RAW"
                    or end["price_basis"] != "RAW"
                ):
                    raise ContractError("LABEL_UNITS_OR_PRICE_BASIS")
                if start["open"] <= 0 or end["open"] <= 0:
                    raise ContractError("INVALID_FORWARD_PRICE")
                n, credit = Decimal(1), Decimal(0)
                deps = [start, end, a, b, cov, *statuses]
                period = sorted(
                    [v for v in economic if entry < v["effective_at"] <= exit],
                    key=lambda v: (
                        v["effective_at"],
                        0 if v["type"] == "SPLIT" else 1,
                        v["action_id"],
                    ),
                )
                with localcontext() as ctx:
                    ctx.prec = 80
                    for action in period:
                        if action["currency"] != start["currency"]:
                            raise ContractError("LABEL_ACTION_CURRENCY")
                        deps.append(action)
                        if action["type"] == "SPLIT":
                            n *= action["split_ratio"]
                        else:
                            if action["dividend_basis"] != "PER_OLD_SHARE":
                                raise ContractError("LABEL_DIVIDEND_BASIS")
                            anchors = [
                                s for s in sessions if s["close_at"] < action["effective_at"]
                            ]
                            if not anchors:
                                raise ContractError("MISSING_ACTION_UNIT_ANCHOR")
                            anchor = max(anchors, key=lambda s: s["close_at"])
                            deps.append(anchor)
                            splits = [
                                v
                                for v in economic
                                if v["type"] == "SPLIT"
                                and anchor["close_at"] < v["effective_at"] <= action["effective_at"]
                            ]
                            if len({s["effective_at"] for s in splits}) > 1:
                                raise ContractError("UNSUPPORTED_ACTION_CHAIN")
                            ratio = Decimal(1)
                            for split in splits:
                                ratio *= split["split_ratio"]
                                deps.append(split)
                            credit += n * action["cash_per_share"] / ratio
                    value = (n * end["open"] + credit) / start["open"] - 1
                available = max(utc(v[k]) for v in deps for k in ("event_time", "available_at"))
                row.update(
                    label=float(value),
                    available_at=available,
                    shares=str(n),
                    credit=str(credit),
                    reason="NONE",
                    dependency_hash=digest(deps),
                    information_interval=[row["decision_time"], available],
                    entitlement_interval=[entry, exit],
                    coverage_revision=cov["revision_id"],
                )
    return output
