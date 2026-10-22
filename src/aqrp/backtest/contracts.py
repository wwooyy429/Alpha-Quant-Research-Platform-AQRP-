"""Frozen engineering requests and independently hash-bound opening sidecars."""

import uuid
from dataclasses import dataclass

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.portfolio.contracts import (
    PortfolioRequest,
    boolean,
    checksum,
    fields,
    identifier,
    integer,
    load,
    prepare,
)

from .exact import integral, money, price


def uid(value):
    try:
        if str(uuid.UUID(value)) != value:
            raise ValueError
    except (ValueError, AttributeError, TypeError) as exc:
        raise ContractError("SIMULATION_UUID_REQUIRED") from exc
    return value


def timestamp(value):
    return utc(value).isoformat(timespec="microseconds")


@dataclass(frozen=True)
class EngineeringBacktestRequest:
    raw: bytes

    def __post_init__(self):
        if not isinstance(self.raw, bytes):
            raise ContractError("IMMUTABLE_REQUEST_BYTES_REQUIRED")

    @classmethod
    def create(cls, data):
        return cls(canonical(data))

    @property
    def content_hash(self):
        import hashlib

        return hashlib.sha256(self.raw).hexdigest()


@dataclass(frozen=True)
class BacktestResult:
    raw: bytes

    def read(self):
        return load(self.raw)


def validate(request):
    if not isinstance(request, EngineeringBacktestRequest):
        raise ContractError("FROZEN_SIMULATION_REQUEST_REQUIRED")
    x = load(request.raw)
    fields(
        x,
        {
            "schema_version",
            "request_id",
            "scope",
            "financial_approval",
            "currency",
            "calendar_id",
            "initial_cash",
            "fee_budget",
            "liquidity",
            "assets",
            "sessions",
            "sidecar",
            "decisions",
            "actions",
            "cashflows",
            "cancellations",
        },
    )
    if (x["schema_version"], x["scope"], x["financial_approval"], x["calendar_id"]) != (
        "simulation-request/1.0.0",
        "ENGINEERING_TEST_ONLY",
        "NONE",
        "SYNTHETIC_V1",
    ):
        raise ContractError("ENGINEERING_SIMULATION_PROFILE_REQUIRED")
    uid(x["request_id"])
    for name in ("decisions", "actions", "cashflows", "cancellations"):
        if not isinstance(x[name], list):
            raise ContractError("SIMULATION_EVENT_LIST_REQUIRED", name)
    identifier(x["currency"])
    if money(x["initial_cash"]) <= 0 or money(x["fee_budget"]) < 0:
        raise ContractError("INVALID_INITIAL_CASH_OR_BUDGET")
    liquidity = fields(x["liquidity"], {"lookback_sessions", "minimum_adv"})
    integer(liquidity["lookback_sessions"], 1)
    if money(liquidity["minimum_adv"]) <= 0:
        raise ContractError("INVALID_ADV_THRESHOLD")
    assets = {}
    if not isinstance(x["assets"], list) or not x["assets"]:
        raise ContractError("SIMULATION_ASSETS_REQUIRED")
    for a in x["assets"]:
        fields(
            a,
            {
                "security_id",
                "lot",
                "industry",
                "beta",
                "short_permission",
                "borrow_limit",
                "market_id",
            },
        )
        sid = identifier(a["security_id"])
        if sid in assets:
            raise ContractError("DUPLICATE_SECURITY")
        integral(a["lot"], positive=True)
        integral(a["borrow_limit"])
        if money(a["borrow_limit"]) < 0:
            raise ContractError("NEGATIVE_PERMISSION_QUANTITY")
        identifier(a["industry"])
        identifier(a["market_id"])
        money(a["beta"])
        boolean(a["short_permission"])
        assets[sid] = a
    if not isinstance(x["sessions"], list) or not x["sessions"]:
        raise ContractError("SESSIONS_REQUIRED")
    sessions = {}
    last = None
    for index, s in enumerate(x["sessions"]):
        fields(s, {"session_id", "open", "close"})
        sid = identifier(s["session_id"])
        op, cl = utc(s["open"]), utc(s["close"])
        if sid in sessions or not op < cl or (last is not None and op <= last):
            raise ContractError("INVALID_SESSION_ORDER")
        sessions[sid] = index
        last = cl
    sidecar = fields(
        x["sidecar"],
        {
            "schema_version",
            "snapshot_id",
            "snapshot_sha256",
            "rows",
            "volume_history",
            "content_sha256",
        },
    )
    if sidecar["schema_version"] != "execution-sidecar/1.0.0" or digest(
        {k: v for k, v in sidecar.items() if k != "content_sha256"}
    ) != checksum(sidecar["content_sha256"]):
        raise ContractError("EXECUTION_SIDECAR_HASH_MISMATCH")
    identifier(sidecar["snapshot_id"])
    checksum(sidecar["snapshot_sha256"])
    if not isinstance(sidecar["rows"], list):
        raise ContractError("EXECUTION_SLICE_LIST_REQUIRED")
    identifiers = set()
    row_keys = set()
    if not isinstance(sidecar["volume_history"], list):
        raise ContractError("VOLUME_HISTORY_LIST_REQUIRED")
    volume_keys = set()
    for r in sidecar["volume_history"]:
        fields(
            r, {"security_id", "session_id", "shares", "event_time", "available_at", "revision_id"}
        )
        integer(r["revision_id"], 1)
        key = (r["security_id"], r["session_id"], r["revision_id"])
        if key in volume_keys or r["security_id"] not in assets or r["session_id"] not in sessions:
            raise ContractError("INVALID_OR_DUPLICATE_VOLUME_HISTORY")
        volume_keys.add(key)
        session = x["sessions"][sessions[r["session_id"]]]
        if utc(r["event_time"]) != utc(session["close"]) or utc(r["available_at"]) < utc(
            r["event_time"]
        ):
            raise ContractError("VOLUME_HISTORY_CLOCK_MISMATCH")
        if r["shares"] is not None and money(r["shares"]) < 0:
            raise ContractError("NEGATIVE_HISTORICAL_VOLUME")
    for r in sidecar["rows"]:
        fields(
            r,
            {
                "slice_id",
                "security_id",
                "session_id",
                "kind",
                "event_time",
                "available_at",
                "known_at",
                "price",
                "tradable",
                "in_universe",
                "short_permission",
                "borrow_limit",
                "industry",
                "beta",
                "status",
            },
        )
        uid(r["slice_id"])
        key = (r["security_id"], r["session_id"], r["kind"])
        if (
            r["slice_id"] in identifiers
            or key in row_keys
            or r["security_id"] not in assets
            or r["session_id"] not in sessions
            or r["kind"] not in ("OPEN", "CLOSE")
        ):
            raise ContractError("INVALID_OR_DUPLICATE_EXECUTION_SLICE")
        identifiers.add(r["slice_id"])
        row_keys.add(key)
        session = x["sessions"][sessions[r["session_id"]]]
        if (
            utc(r["event_time"]) != utc(session[r["kind"].lower()])
            or utc(r["available_at"]) < utc(r["event_time"])
            or utc(r["known_at"]) > utc(r["available_at"])
        ):
            raise ContractError("EXECUTION_SLICE_CLOCK_MISMATCH")
        if r["price"] is not None:
            price(r["price"])
        for k in ("tradable", "in_universe", "short_permission"):
            boolean(r[k])
        if r["status"] not in ("ACTIVE", "SUSPENDED", "DELISTED") or (
            r["tradable"] and r["status"] != "ACTIVE"
        ):
            raise ContractError("INVALID_EXECUTION_SECURITY_STATUS")
        if integral(r["borrow_limit"]) < 0:
            raise ContractError("NEGATIVE_PERMISSION_QUANTITY")
        money(r["beta"])
        identifier(r["industry"])
    for d in x["decisions"]:
        fields(
            d,
            {
                "portfolio_request_utf8",
                "order_type",
                "limit_prices",
                "time_in_force",
                "expires_session",
            },
        )
        if not isinstance(d["portfolio_request_utf8"], str):
            raise ContractError("FROZEN_PORTFOLIO_UTF8_REQUIRED")
        p, maps, _, _ = prepare(PortfolioRequest(d["portfolio_request_utf8"].encode("utf-8")))
        c = p["context"]
        if set(maps["securities"]) != set(assets) or (
            c["snapshot_id"],
            c["snapshot_sha256"],
            c["currency"],
        ) != (sidecar["snapshot_id"], sidecar["snapshot_sha256"], x["currency"]):
            raise ContractError("SIMULATION_PARENT_CONTEXT_MISMATCH")
        if any(a["market_id"] != c["market_id"] for a in assets.values()):
            raise ContractError("SIMULATION_MARKET_MISMATCH")
        if not utc(x["sessions"][0]["open"]) <= utc(c["decision_time"]) <= last:
            raise ContractError("DECISION_OUTSIDE_CALENDAR")
        if (
            d["order_type"] not in ("MARKET", "LIMIT")
            or d["time_in_force"] not in ("DAY", "GTC")
            or d["expires_session"] not in sessions
            or not isinstance(d["limit_prices"], dict)
        ):
            raise ContractError("INVALID_ORDER_CONFIGURATION")
        if (d["order_type"] == "MARKET" and d["limit_prices"]) or (
            d["order_type"] == "LIMIT" and set(d["limit_prices"]) != set(assets)
        ):
            raise ContractError("INVALID_LIMIT_MEMBERSHIP")
        for v in d["limit_prices"].values():
            price(v)
    times = [
        utc(load(d["portfolio_request_utf8"])["context"]["decision_time"]) for d in x["decisions"]
    ]
    if len(times) != len(set(times)):
        raise ContractError("DUPLICATE_DECISION_TIME")
    for a in x["actions"]:
        fields(
            a,
            {
                "action_id",
                "kind",
                "security_id",
                "effective_at",
                "available_at",
                "value",
                "unit",
                "pay_at",
            },
        )
        uid(a["action_id"])
        if a["security_id"] not in assets or a["kind"] not in ("SPLIT", "DIVIDEND", "DELIST"):
            raise ContractError("INVALID_CORPORATE_ACTION")
        utc(a["effective_at"])
        utc(a["available_at"])
        if money(a["value"]) < 0 or (a["kind"] == "SPLIT" and money(a["value"]) == 0):
            raise ContractError("INVALID_ACTION_VALUE")
        if a["kind"] == "DIVIDEND":
            if a["unit"] not in ("PER_OLD_SHARE", "PER_CURRENT_SHARE") or utc(a["pay_at"]) < utc(
                a["effective_at"]
            ):
                raise ContractError("INVALID_DIVIDEND_RULE")
        elif a["unit"] != "RATIO" and a["kind"] == "SPLIT":
            raise ContractError("INVALID_SPLIT_UNIT")
        elif a["kind"] == "DELIST":
            if (
                money(a["value"]) * 100 != int(money(a["value"]) * 100)
                or a["unit"] != "CCY_PER_SHARE"
            ):
                raise ContractError("INVALID_DECLARED_RECOVERY_PRICE")
    if len({a["action_id"] for a in x["actions"]}) != len(x["actions"]):
        raise ContractError("DUPLICATE_ACTION")
    for f in x["cashflows"]:
        fields(f, {"flow_id", "at", "amount"})
        uid(f["flow_id"])
        utc(f["at"])
        money(f["amount"])
    for c in x["cancellations"]:
        fields(
            c,
            {
                "control_id",
                "order_id",
                "requested_at",
                "available_at",
                "received_at",
                "received_phase",
            },
        )
        uid(c["control_id"])
        uid(c["order_id"])
        if integer(c["received_phase"]) not in (10, 20, 30, 40, 50, 60, 65, 70, 95, 100):
            raise ContractError("INVALID_CONTROL_RECEIVED_PHASE")
        if utc(c["requested_at"]) > utc(c["available_at"]) or utc(c["available_at"]) > utc(
            c["received_at"]
        ):
            raise ContractError("INVALID_CANCELLATION_CLOCK")
    if len({f["flow_id"] for f in x["cashflows"]}) != len(x["cashflows"]) or len(
        {c["control_id"] for c in x["cancellations"]}
    ) != len(x["cancellations"]):
        raise ContractError("DUPLICATE_FLOW_OR_CONTROL_ID")
    from .provider import verify_volume_history

    verify_volume_history(x)
    return x
