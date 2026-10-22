"""PIT signal boundary and explicit real P4 budget adapter; no factor in execution core."""

from copy import deepcopy

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.portfolio.construct import build_candidate
from aqrp.portfolio.contracts import PortfolioRequest, load, prepare
from aqrp.risk.checks import audit_published

from .exact import F, p4_input
from .ledger import account, sellable
from .transactions import guard_path


def guard_sources(request):
    """Reject link/alias substitutions, supplementing the original manifest/hash gate."""
    import json
    from pathlib import Path

    x = load(request.raw)
    for b in x["source"].get("research_bindings", []):
        root = guard_path(Path(b["ledger_root"]) / b["run_id"])
        manifest = json.loads(guard_path(root / "manifest.json").read_bytes())
        for e in manifest["files"]:
            guard_path(root / e["path"])
        source = b["snapshot"]
        root = guard_path(Path(source["root"]) / source["snapshot_id"])
        manifest = json.loads(guard_path(root / "manifest.json").read_bytes())
        for e in manifest["tables"].values():
            guard_path(root / e["path"])


def verify_volume_history(config):
    """Actual research sources bind every volume revision to original P1 table bytes."""
    from pathlib import Path

    from aqrp.core.contracts import SnapshotRef
    from aqrp.data.snapshot import verify_snapshot

    sources = {}
    for d in config["decisions"]:
        p = load(d["portfolio_request_utf8"])
        for b in p["source"].get("research_bindings", []):
            ref = b["snapshot"]
            sources[
                (ref["root"], ref["snapshot_id"], ref["manifest_hash"], b["source_calendar_id"])
            ] = ref
    if not sources:
        return
    sids = {a["security_id"] for a in config["assets"]}
    dates = {s["session_id"] for s in config["sessions"]}
    actual = {
        (
            r["security_id"],
            r["session_id"],
            r["revision_id"],
            None if r["shares"] is None else F(r["shares"]),
            utc(r["event_time"]),
            utc(r["available_at"]),
        )
        for r in config["sidecar"]["volume_history"]
    }
    for root, sid, manifest_hash, calendar in sources:
        _, tables = verify_snapshot(SnapshotRef(Path(root), sid, manifest_hash))
        expected = {
            (
                r["security_id"],
                str(r["session_date"]),
                r["revision_id"],
                None if r["volume"] is None else F(r["volume"]),
                utc(r["event_time"]),
                utc(r["available_at"]),
            )
            for r in tables["bars_daily"].to_pylist()
            if r["security_id"] in sids
            and str(r["session_date"]) in dates
            and r["calendar_id"] == calendar
        }
        if actual != expected:
            raise ContractError("HISTORICAL_VOLUME_P1_BINDING_MISMATCH")


class SignalProvider:
    def __init__(self, decisions):
        self._requests = {}
        for d in decisions:
            raw = d["portfolio_request_utf8"].encode("utf-8")
            request = PortfolioRequest(raw)
            guard_sources(request)
            x, _, _, _ = prepare(request)
            t = utc(x["context"]["decision_time"])
            if t in self._requests:
                raise ContractError("DUPLICATE_DECISION_TIME")
            self._requests[t] = raw

    def release(self, now):
        raw = self._requests.get(utc(now))
        if raw is None:
            raise ContractError("SIGNAL_NOT_AVAILABLE_AT_DECISION")
        request = PortfolioRequest(raw)
        guard_sources(request)
        prepare(request)  # Re-read terminal P3 and P1 original bytes at actual release.
        return request


def adapt_portfolio(request, state):
    x, _, _, _ = prepare(request)
    x = deepcopy(x)
    decision = utc(x["context"]["decision_time"])
    c = account(state)
    if c["cash_alloc"] < 0 or c["equity_alloc"] <= 0:
        raise ContractError("INFEASIBLE_P4_BUDGET_PROJECTION")
    if any(o["status"] in ("ACCEPTED", "PARTIALLY_FILLED") for o in state["orders"].values()):
        raise ContractError("REBALANCE_PENDING_ORDERS")
    for name in ("prices", "status", "exposures", "permissions"):
        e = x["inputs"][name]
        times = []
        for row in e["data"]:
            a = state["assets"][row["security_id"]]
            if a["mark_ref"] is None or utc(a["mark_ref"]["available_at"]) > decision:
                raise ContractError("NO_VISIBLE_DECISION_MARK")
            r = a["mark_ref"]
            times.append(r["available_at"])
            row.update(
                event_time=r["event_time"],
                available_at=r["available_at"],
                as_of=x["context"]["decision_time"],
            )
            if name == "prices":
                row.update(price=p4_input(a["mark"]), lot=p4_input(a["lot"]))
            elif name == "status":
                row.update(tradable=a["tradable"], in_universe=a["in_universe"])
            elif name == "exposures":
                row.update(industry=a["industry"], beta=p4_input(a["beta"]))
            else:
                row.update(
                    short_permission=a["short_permission"],
                    borrow_limit_total=p4_input(a["borrow_limit"]),
                    sellable_qty=p4_input(sellable(a, state["session"])),
                )
        e.update(
            event_time=max(times, key=utc),
            available_at=max(times, key=utc),
            as_of=x["context"]["decision_time"],
        )
    e = x["inputs"]["account"]
    e.update(
        event_time=x["context"]["decision_time"],
        available_at=x["context"]["decision_time"],
        as_of=x["context"]["decision_time"],
    )
    e["data"].update(
        equity=p4_input(c["equity_alloc"]),
        total_cash=p4_input(c["cash_alloc"]),
        restricted_cash=p4_input(c["short_value"] + c["P4_nonshort"]),
        short_restriction=p4_input(c["short_value"]),
        nonshort_restriction=p4_input(c["P4_nonshort"]),
        positions=[
            {"security_id": k, "quantity": p4_input(a["quantity"])}
            for k, a in sorted(state["assets"].items())
        ],
        valuation_time=x["context"]["decision_time"],
        price_ref=x["inputs"]["prices"]["ref"],
    )
    x["profile"]["fee_reserve"] = "0"
    entries = [v for k, v in x["inputs"].items() if k != "scores"] + x["inputs"]["scores"]
    for e in entries:
        e["content_sha256"] = digest({k: v for k, v in e.items() if k != "content_sha256"})
    x["source"]["fixture_manifest"] = {e["ref"]: e["content_sha256"] for e in entries}
    out = PortfolioRequest(canonical(x))
    prepare(out)
    return out, c


def signal_identity(request):
    x = load(request.raw)
    return [
        {
            "factor_ref": e["data"]["factor_ref"],
            "params_hash": e["data"]["params_hash"],
            "stage": e["data"]["stage"],
            "content_sha256": e["content_sha256"],
        }
        for e in x["inputs"]["scores"]
    ]


def verify_portfolio_result(request, returned, root):
    import hashlib

    guard_sources(request)
    ledger = ExperimentLedger(guard_path(root))
    run = returned["run_id"]
    manifest = ledger.verify(run)

    def read(name):
        rows = [e for e in manifest["files"] if e["path"] == name]
        if len(rows) != 1:
            raise ContractError("P4_ARTIFACT_NOT_TERMINAL_MANIFESTED")
        path = guard_path(ledger.path(run) / name)
        raw = path.read_bytes()
        if path.is_symlink() or hashlib.sha256(raw).hexdigest() != rows[0]["sha256"]:
            raise ContractError("P4_TERMINAL_BYTES_CHANGED")
        return raw

    original = read("result.json")
    if (
        canonical({k: v for k, v in returned.items() if k != "manifest"}) != original
        or returned["manifest"] != manifest
    ):
        raise ContractError("P4_RETURN_TERMINAL_BINDING_MISMATCH")
    if returned["status"] == "SUCCEEDED":
        candidate = build_candidate(request)
        if candidate.raw != read("candidate.json") or load(read("risk.json")) != returned["risk"]:
            raise ContractError("P4_CANDIDATE_RISK_BYTES_CHANGED")
        audit = audit_published(original, request, candidate)
        if load(read("published-byte-audit.json")) != audit:
            raise ContractError("P4_PUBLISHED_AUDIT_CHANGED")
