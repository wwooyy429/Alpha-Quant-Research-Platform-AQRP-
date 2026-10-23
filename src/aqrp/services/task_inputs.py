"""Shared P1/P3-source-bound execution INPUT assembly; no financial calculations."""

import uuid

from aqrp.backtest.contracts import timestamp
from aqrp.backtest.synthetic import NAMESPACE, fixture_request, portfolio_template, seal_sidecar
from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.data.snapshot import verify_snapshot
from aqrp.portfolio.contracts import load
from aqrp.portfolio.research_input import bind_research


def execution_requests(c, ref, ledger_root, r):
    _, tables = verify_snapshot(ref)
    cal = sorted(
        [row for row in tables["calendar"].to_pylist() if row["calendar_id"] == c["calendar_id"]],
        key=lambda row: row["open_at"],
    )
    sessions = [
        {
            "session_id": str(row["session_date"]),
            "open": timestamp(row["open_at"]),
            "close": timestamp(row["close_at"]),
        }
        for row in cal
    ]
    # Retain all24 P1/P3 sessions; the execution fixture freezes six sessions and
    # three decisions, sufficient for replacement + settlement + final lifecycle.
    decision_window = c["decisions"]
    if not decision_window:
        raise ContractError("NO_REQUIRED_DECISIONS")
    first = next(
        i for i, s in enumerate(sessions) if s["session_id"] == decision_window[0]["session"]
    )
    last = next(
        i for i, s in enumerate(sessions) if s["session_id"] == decision_window[-1]["session"]
    )
    sessions = sessions[max(0, first - 1) : min(len(sessions), last + 3)]
    assets = [
        {
            "security_id": f"SYN_A:{i:03d}",
            "market_id": "SYN_A",
            "lot": "1",
            "industry": "I",
            "beta": "1",
            "short_permission": True,
            "borrow_limit": "1000",
        }
        for i in range(1, 7)
    ]
    base = load(fixture_request().raw)
    base.update(assets=assets, currency=c["currency"], sessions=sessions)
    base["sidecar"].update(snapshot_id=ref.snapshot_id, snapshot_sha256=ref.manifest_hash, rows=[])
    base["sidecar"]["volume_history"] = [
        {
            "security_id": row["security_id"],
            "session_id": str(row["session_date"]),
            "shares": str(row["volume"]) if row["volume"] is not None else None,
            "event_time": timestamp(row["event_time"]),
            "available_at": timestamp(row["available_at"]),
            "revision_id": row["revision_id"],
        }
        for row in tables["bars_daily"].to_pylist()
        if row["security_id"] in {a["security_id"] for a in assets}
        and str(row["session_date"]) in {s["session_id"] for s in sessions}
    ]
    # Independently declared synthetic opening/mark input; never exposes P1 daily OHLCV at open.
    for s in sessions:
        for a in assets:
            for kind in ("OPEN", "CLOSE"):
                t = s[kind.lower()]
                base["sidecar"]["rows"].append(
                    {
                        "slice_id": str(
                            uuid.uuid5(NAMESPACE, s["session_id"] + a["security_id"] + kind)
                        ),
                        "security_id": a["security_id"],
                        "session_id": s["session_id"],
                        "kind": kind,
                        "event_time": t,
                        "available_at": t,
                        "known_at": t,
                        "price": "100",
                        "tradable": True,
                        "in_universe": True,
                        "short_permission": True,
                        "borrow_limit": "1000",
                        "industry": "I",
                        "beta": "1",
                        "status": "ACTIVE",
                    }
                )
    output = {}
    for factor in [candidate["hypothesis"] for candidate in c["candidates"]]:
        x = load(canonical(base))
        x["decisions"] = []
        for d in decision_window:
            index = next(i for i, s in enumerate(sessions) if s["session_id"] == d["session"])
            context = {
                "decision_time": d["decision_time"],
                "currency": c["currency"],
                "market_id": c["market_id"],
                "calendar_id": "SYNTHETIC_V1",
                "snapshot_id": ref.snapshot_id,
                "snapshot_sha256": ref.manifest_hash,
                "session_index": index,
            }
            p = portfolio_template(assets, context, factor_key=factor)
            req = bind_research(p, ledger_root, r["run_id"], source_snapshot=ref)
            x["decisions"].append(
                {
                    "portfolio_request_utf8": req.raw.decode(),
                    "order_type": "MARKET",
                    "limit_prices": {},
                    "time_in_force": "DAY",
                    "expires_session": sessions[-1]["session_id"],
                }
            )
        output[factor] = seal_sidecar(x)
    return output
