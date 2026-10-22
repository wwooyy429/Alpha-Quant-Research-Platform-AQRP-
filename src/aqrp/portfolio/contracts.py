"""Strict hash-bound PIT inputs; exact rationals and fixed Decimal output projection."""

import hashlib
import json
import math
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Context, Decimal, localcontext
from fractions import Fraction

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.factors.contracts import FactorRef

F = Fraction
RATIO_TOL = F(1, 10**12)
CASH_TOL = F(1, 10**8)
CONTEXT = {
    "decision_time",
    "currency",
    "market_id",
    "calendar_id",
    "snapshot_id",
    "snapshot_sha256",
    "session_index",
}
CLOCKS = {"event_time", "available_at", "as_of"}
INPUT_NAMES = {"securities", "prices", "status", "exposures", "permissions", "account", "scores"}


def fail(code, field=""):
    raise ContractError(code, field)


def fields(value, names, field=""):
    if not isinstance(value, dict) or set(value) != set(names):
        fail("INVALID_FIELDS", field)
    return value


def identifier(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        fail("INVALID_IDENTIFIER")
    return value


def checksum(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        fail("INVALID_HASH")
    return value


def boolean(value):
    if type(value) is not bool:
        fail("BOOLEAN_REQUIRED")
    return value


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        fail("INTEGER_REQUIRED")
    return value


def number(value, *, score=False):
    if score and type(value) in (float, int):
        if type(value) is float and not math.isfinite(value):
            fail("NONFINITE_NUMBER")
        value = str(value)
    if not isinstance(value, str) or len(value) > 128:
        fail("DECIMAL_STRING_REQUIRED")
    try:
        n = Decimal(value)
    except ArithmeticError:
        fail("INVALID_DECIMAL")
    if not n.is_finite() or len(n.as_tuple().digits) > 34 or abs(n.as_tuple().exponent) > 100:
        fail("DECIMAL_OUT_OF_DOMAIN")
    return F(n)


def project(value):
    """Canonical finite 34-digit decimal projection, independent of caller context."""
    if isinstance(value, F):
        with localcontext(Context(prec=34, rounding=ROUND_HALF_EVEN)):
            out = Decimal(value.numerator) / Decimal(value.denominator)
            return format(out, "f") if out else "0"
    if isinstance(value, dict):
        return {k: project(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [project(v) for v in value]
    return value


def load(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                fail("DUPLICATE_JSON_KEY", k)
            result[k] = v
        return result

    try:
        return json.loads(
            raw, object_pairs_hook=pairs, parse_constant=lambda _: fail("NONFINITE_NUMBER")
        )
    except (ValueError, UnicodeError, TypeError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise ContractError("INVALID_JSON") from exc


@dataclass(frozen=True)
class PortfolioRequest:
    raw: bytes

    def __post_init__(self):
        if not isinstance(self.raw, bytes):
            fail("IMMUTABLE_REQUEST_BYTES_REQUIRED")

    @classmethod
    def create(cls, value):
        return cls(canonical(value))

    @property
    def content_hash(self):
        return hashlib.sha256(self.raw).hexdigest()


@dataclass(frozen=True)
class TargetCandidate:
    """Unvalidated computation only. Public risk entry reconstructs it from the request."""

    raw: bytes
    request_hash: str

    def __post_init__(self):
        if not isinstance(self.raw, bytes):
            fail("IMMUTABLE_CANDIDATE_BYTES_REQUIRED")
        checksum(self.request_hash)


@dataclass(frozen=True)
class PortfolioResult:
    raw: bytes

    def read(self):
        return load(self.raw)


def clock(value, decision):
    event, available, as_of = (utc(value[k]) for k in ("event_time", "available_at", "as_of"))
    if as_of != decision or event > available or available > decision:
        fail("PIT_CLOCK_VIOLATION")


def same_context(value, context):
    fields(value, CONTEXT, "context")
    if any(value[k] != context[k] for k in CONTEXT - {"decision_time"}) or utc(
        value["decision_time"]
    ) != utc(context["decision_time"]):
        fail("CONTEXT_MISMATCH")


def envelope(value, kind, context, manifest):
    fields(
        value, {"schema_version", "kind", "ref", "context", "data", "content_sha256"} | CLOCKS, kind
    )
    if value["schema_version"] != "portfolio-input/1.0.0" or value["kind"] != kind:
        fail("INVALID_INPUT_SCHEMA", kind)
    checksum(value["content_sha256"])
    identifier(value["ref"])
    if (
        digest({k: v for k, v in value.items() if k != "content_sha256"}) != value["content_sha256"]
        or manifest.get(value["ref"]) != value["content_sha256"]
    ):
        fail("INPUT_HASH_MISMATCH", kind)
    same_context(value["context"], context)
    clock(value, utc(context["decision_time"]))
    identifier(value["ref"])
    return value["data"]


def row_map(rows, names, context, header):
    if not isinstance(rows, list):
        fail("ROWS_REQUIRED")
    result = {}
    for row in rows:
        fields(row, set(names) | {"security_id"} | CLOCKS, "row")
        sid = identifier(row["security_id"])
        if sid in result:
            fail("DUPLICATE_SECURITY", sid)
        clock(row, utc(context["decision_time"]))
        if utc(row["available_at"]) > utc(header["available_at"]):
            fail("ROW_AFTER_ENVELOPE", sid)
        result[sid] = row
    return result


def prepare(request):
    if not isinstance(request, PortfolioRequest) or not isinstance(request.raw, bytes):
        fail("FROZEN_REQUEST_REQUIRED")
    x = load(request.raw)
    fields(
        x,
        {"schema_version", "context", "profile", "policy", "constraints", "source", "inputs"},
        "request",
    )
    if x["schema_version"] != "portfolio-request/1.0.0":
        fail("INVALID_REQUEST_SCHEMA")
    c = fields(x["context"], CONTEXT, "context")
    utc(c["decision_time"])
    if c["calendar_id"] != "SYNTHETIC_V1":
        fail("UNSUPPORTED_SYNTHETIC_CALENDAR")
    for k in CONTEXT - {"decision_time", "session_index", "snapshot_sha256"}:
        identifier(c[k])
    checksum(c["snapshot_sha256"])
    integer(c["session_index"])
    source_keys = {"kind", "scope", "dataset_kind", "financial_approval", "fixture_manifest"}
    if isinstance(x["source"], dict) and x["source"].get("kind") == "RESEARCH_ARTIFACT":
        source_keys.add("research_bindings")
    source = fields(
        x["source"],
        source_keys,
        "source",
    )
    if source["kind"] not in ("DECLARED_FIXTURE", "RESEARCH_ARTIFACT") or (
        source["scope"],
        source["dataset_kind"],
        source["financial_approval"],
    ) != (
        "ENGINEERING_TEST_ONLY",
        "SYNTHETIC",
        "NONE",
    ):
        fail("ENGINEERING_SOURCE_REQUIRED")
    manifest = source["fixture_manifest"]
    if not isinstance(manifest, dict):
        fail("FIXTURE_MANIFEST_REQUIRED")
    p = fields(
        x["profile"],
        {"profile_id", "max_age_sessions", "allow_full_close_odd_lot", "fee_reserve"},
        "profile",
    )
    if p["profile_id"] != "SYNTHETIC_PORTFOLIO_1" or integer(p["max_age_sessions"]) != 0:
        fail("UNAPPROVED_PROFILE")
    boolean(p["allow_full_close_odd_lot"])
    if number(p["fee_reserve"]) < 0:
        fail("NEGATIVE_RESERVE")
    policy = fields(
        x["policy"],
        {"mode", "weighting", "top_k", "long_k", "short_k", "gross", "net", "factor_weights"},
        "policy",
    )
    if policy["mode"] not in ("LONG_ONLY", "LONG_SHORT") or policy["weighting"] not in (
        "equal",
        "score",
    ):
        fail("INVALID_WEIGHT_POLICY")
    for k in ("top_k", "long_k", "short_k"):
        integer(policy[k], 1)
    g, n = number(policy["gross"]), number(policy["net"])
    if g < abs(n) or g < 0 or (policy["mode"] == "LONG_ONLY" and (g, n) != (1, 1)):
        fail("INVALID_GROSS_NET")
    inputs = fields(x["inputs"], INPUT_NAMES, "inputs")
    schemas = {
        "securities": {"symbol", "market_id", "currency"},
        "prices": {"price", "lot"},
        "status": {"tradable", "in_universe"},
        "exposures": {"industry", "beta"},
        "permissions": {"short_permission", "borrow_limit_total", "sellable_qty"},
    }
    maps = {}
    refs = []
    for name, schema in schemas.items():
        value = envelope(inputs[name], name, c, manifest)
        maps[name] = row_map(value, schema, c, inputs[name])
        refs.append(inputs[name]["ref"])
    assets = maps["securities"]
    if not assets or any(set(m) != set(assets) for m in maps.values()):
        fail("MISSING_SECURITY_INPUT")
    for sid in assets:
        sec = assets[sid]
        if (sec["market_id"], sec["currency"]) != (c["market_id"], c["currency"]):
            fail("ASSET_MARKET_CURRENCY_MISMATCH", sid)
        identifier(sec["symbol"])
        if number(maps["prices"][sid]["price"]) <= 0 or number(maps["prices"][sid]["lot"]) <= 0:
            fail("INVALID_PRICE_OR_LOT", sid)
        for k in ("tradable", "in_universe"):
            boolean(maps["status"][sid][k])
        identifier(maps["exposures"][sid]["industry"])
        number(maps["exposures"][sid]["beta"])
        permission = maps["permissions"][sid]
        boolean(permission["short_permission"])
        if min(number(permission["borrow_limit_total"]), number(permission["sellable_qty"])) < 0:
            fail("NEGATIVE_PERMISSION_QUANTITY")
    account = envelope(inputs["account"], "account", c, manifest)
    fields(
        account,
        {
            "equity",
            "total_cash",
            "restricted_cash",
            "short_restriction",
            "nonshort_restriction",
            "positions",
            "valuation_time",
            "price_ref",
        },
        "account",
    )
    refs.append(inputs["account"]["ref"])
    if (
        utc(account["valuation_time"]) != utc(c["decision_time"])
        or account["price_ref"] != inputs["prices"]["ref"]
    ):
        fail("ACCOUNT_VALUATION_MISMATCH")
    if not isinstance(account["positions"], list):
        fail("POSITIONS_REQUIRED")
    positions = {}
    for row in account["positions"]:
        fields(row, {"security_id", "quantity"}, "position")
        sid = identifier(row["security_id"])
        if sid not in assets or sid in positions:
            fail("INVALID_POSITION", str(sid))
        positions[sid] = number(row["quantity"])
    positions = {sid: positions.get(sid, F(0)) for sid in assets}
    equity, cash = number(account["equity"]), number(account["total_cash"])
    restricted, short, nonshort = (
        number(account[k]) for k in ("restricted_cash", "short_restriction", "nonshort_restriction")
    )
    marked = sum(q * number(maps["prices"][s]["price"]) for s, q in positions.items())
    short_value = sum(max(-q * number(maps["prices"][s]["price"]), 0) for s, q in positions.items())
    if (
        equity <= 0
        or min(cash, restricted, short, nonshort) < 0
        or restricted > cash
        or abs(equity - cash - marked) > CASH_TOL
        or abs(restricted - short - nonshort) > CASH_TOL
        or abs(short - short_value) > CASH_TOL
    ):
        fail("ACCOUNT_RECONCILIATION")
    limits = fields(
        x["constraints"],
        {
            "per_asset",
            "gross_max",
            "net_min",
            "net_max",
            "leverage_max",
            "turnover_max",
            "beta_min",
            "beta_max",
            "industries",
            "allow_cash_only",
        },
        "constraints",
    )
    boolean(limits["allow_cash_only"])
    if (
        not isinstance(limits["per_asset"], dict)
        or set(limits["per_asset"]) != set(assets)
        or any(number(v) < 0 for v in limits["per_asset"].values())
    ):
        fail("INVALID_ASSET_LIMITS")
    for key in ("gross_max", "leverage_max", "turnover_max"):
        if number(limits[key]) < 0:
            fail("NEGATIVE_RISK_LIMIT")
    if number(limits["net_min"]) > number(limits["net_max"]) or number(limits["beta_min"]) > number(
        limits["beta_max"]
    ):
        fail("CONFLICTING_LIMITS")
    sectors = {m["industry"] for m in maps["exposures"].values()}
    if not isinstance(limits["industries"], dict) or set(limits["industries"]) != sectors:
        fail("MISSING_INDUSTRY_LIMITS")
    for sector in limits["industries"].values():
        fields(sector, {"net_min", "net_max", "gross_max"}, "industry_limit")
        if number(sector["net_min"]) > number(sector["net_max"]) or number(sector["gross_max"]) < 0:
            fail("CONFLICTING_INDUSTRY_LIMITS")
    if not isinstance(inputs["scores"], list) or not inputs["scores"]:
        fail("SCORES_REQUIRED")
    scores = {}
    for item in inputs["scores"]:
        score = envelope(item, "scores", c, manifest)
        fields(score, {"factor_key", "factor_ref", "params_hash", "stage", "rows"}, "score")
        key = identifier(score["factor_key"])
        if key in scores or score["stage"] not in (
            "raw",
            "clean",
            "standardized",
            "neutralized",
            "final",
        ):
            fail("INVALID_SCORE_IDENTITY")
        fields(
            score["factor_ref"],
            {"factor_id", "factor_version", "implementation_hash"},
            "factor_ref",
        )
        FactorRef(**score["factor_ref"])
        identifier(score["factor_ref"]["factor_id"])
        identifier(score["factor_ref"]["factor_version"])
        checksum(score["factor_ref"]["implementation_hash"])
        checksum(score["params_hash"])
        rows = row_map(score["rows"], {"score", "valid", "signal_time", "session_index"}, c, item)
        for sid, row in rows.items():
            if sid not in assets:
                fail("UNKNOWN_SCORE_ASSET")
            boolean(row["valid"])
            if row["valid"]:
                number(row["score"], score=True)
            elif row["score"] is not None:
                fail("INVALID_SCORE_NULL_SEMANTICS")
            age = c["session_index"] - integer(row["session_index"])
            if (
                utc(row["signal_time"]) != utc(row["event_time"])
                or utc(row["signal_time"]).date() != utc(c["decision_time"]).date()
            ):
                fail("SCORE_SESSION_MAPPING_MISMATCH")
            if not 0 <= age <= p["max_age_sessions"] or utc(row["signal_time"]) > utc(
                row["available_at"]
            ):
                fail("STALE_OR_FUTURE_SCORE")
        scores[key] = rows
        refs.append(item["ref"])
    if len(refs) != len(set(refs)) or set(refs) != set(manifest):
        fail("MANIFEST_MEMBERSHIP_MISMATCH")
    if (
        not isinstance(policy["factor_weights"], dict)
        or set(policy["factor_weights"]) != set(scores)
        or not sum(abs(number(v)) for v in policy["factor_weights"].values())
    ):
        fail("INVALID_FACTOR_WEIGHTS")
    if source["kind"] == "RESEARCH_ARTIFACT":
        from .research_input import verify_bindings

        verify_bindings(x)
    return x, maps, positions, scores
