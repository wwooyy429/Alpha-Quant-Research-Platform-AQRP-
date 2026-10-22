"""Input-only engineering generators; none of these functions creates test answers."""

import uuid
from datetime import date, timedelta

from aqrp.core.canonical import canonical, digest
from aqrp.portfolio.contracts import load

from .contracts import EngineeringBacktestRequest, timestamp

NAMESPACE = uuid.UUID("11bd7bd0-e45d-49ed-bd40-62d76c02bf43")


def portfolio_template(assets, context, *, factor_key="fixture", scores=None):
    names = [a["security_id"] for a in assets]
    now = context["decision_time"]
    clock = {"event_time": now, "available_at": now, "as_of": now}
    data = {
        "securities": [
            {
                "security_id": a["security_id"],
                "symbol": a["security_id"],
                "market_id": context["market_id"],
                "currency": context["currency"],
                **clock,
            }
            for a in assets
        ],
        "prices": [
            {"security_id": a["security_id"], "price": "100", "lot": a["lot"], **clock}
            for a in assets
        ],
        "status": [
            {"security_id": sid, "tradable": True, "in_universe": True, **clock} for sid in names
        ],
        "exposures": [
            {"security_id": a["security_id"], "industry": a["industry"], "beta": a["beta"], **clock}
            for a in assets
        ],
        "permissions": [
            {
                "security_id": a["security_id"],
                "short_permission": a["short_permission"],
                "borrow_limit_total": a["borrow_limit"],
                "sellable_qty": "0",
                **clock,
            }
            for a in assets
        ],
        "account": {
            "equity": "1000",
            "total_cash": "1000",
            "restricted_cash": "0",
            "short_restriction": "0",
            "nonshort_restriction": "0",
            "positions": [{"security_id": sid, "quantity": "0"} for sid in names],
            "valuation_time": now,
            "price_ref": "fixture-prices",
        },
    }
    envelopes = {
        name: {
            "schema_version": "portfolio-input/1.0.0",
            "kind": name,
            "ref": "fixture-" + name,
            "context": context,
            **clock,
            "data": rows,
        }
        for name, rows in data.items()
    }
    values = scores or {sid: str(len(names) - i) for i, sid in enumerate(names)}
    envelope = {
        "schema_version": "portfolio-input/1.0.0",
        "kind": "scores",
        "ref": "fixture-scores",
        "context": context,
        **clock,
        "data": {
            "factor_key": factor_key,
            "factor_ref": {
                "factor_id": "declared-fixture",
                "factor_version": "1.0.0",
                "implementation_hash": digest({"fixture": True}),
            },
            "params_hash": digest({}),
            "stage": "final",
            "rows": [
                {
                    "security_id": sid,
                    "score": values[sid],
                    "valid": True,
                    "signal_time": now,
                    "session_index": context["session_index"],
                    **clock,
                }
                for sid in names
            ],
        },
    }
    for e in [*envelopes.values(), envelope]:
        e["content_sha256"] = digest(e)
    return {
        "schema_version": "portfolio-request/1.0.0",
        "context": context,
        "profile": {
            "profile_id": "SYNTHETIC_PORTFOLIO_1",
            "max_age_sessions": 0,
            "allow_full_close_odd_lot": True,
            "fee_reserve": "0",
        },
        "policy": {
            "mode": "LONG_ONLY",
            "weighting": "equal",
            "top_k": 1,
            "long_k": 1,
            "short_k": 1,
            "gross": "1",
            "net": "1",
            "factor_weights": {factor_key: "1"},
        },
        "constraints": {
            "per_asset": {sid: "1" for sid in names},
            "gross_max": "2",
            "net_min": "-2",
            "net_max": "2",
            "leverage_max": "2",
            "turnover_max": "4",
            "beta_min": "-3",
            "beta_max": "3",
            "industries": {
                a["industry"]: {"net_min": "-2", "net_max": "2", "gross_max": "2"} for a in assets
            },
            "allow_cash_only": True,
        },
        "source": {
            "kind": "DECLARED_FIXTURE",
            "scope": "ENGINEERING_TEST_ONLY",
            "dataset_kind": "SYNTHETIC",
            "financial_approval": "NONE",
            "fixture_manifest": {
                e["ref"]: e["content_sha256"] for e in [*envelopes.values(), envelope]
            },
        },
        "inputs": {**envelopes, "scores": [envelope]},
    }


def seal_sidecar(value):
    sidecar = value["sidecar"]
    sidecar["content_sha256"] = digest({k: v for k, v in sidecar.items() if k != "content_sha256"})
    return EngineeringBacktestRequest.create(value)


def fixture_request(*, sessions=4, assets=2):
    securities = [
        {
            "security_id": f"SYNTH:{i}",
            "market_id": "SYNTH",
            "lot": "1",
            "industry": "I",
            "beta": "1",
            "short_permission": True,
            "borrow_limit": "1000",
        }
        for i in range(assets)
    ]
    calendar = [
        {
            "session_id": str(date(2024, 2, 1) + timedelta(days=i)),
            "open": str(date(2024, 2, 1) + timedelta(days=i)) + "T09:00:00Z",
            "close": str(date(2024, 2, 1) + timedelta(days=i)) + "T16:00:00Z",
        }
        for i in range(sessions)
    ]
    parent_id, parent_hash = "declared-P5-fixture", digest({"declared_engineering": True})
    context = {
        "decision_time": calendar[0]["close"],
        "currency": "CCY",
        "market_id": "SYNTH",
        "calendar_id": "SYNTHETIC_V1",
        "snapshot_id": parent_id,
        "snapshot_sha256": parent_hash,
        "session_index": 0,
    }
    p = portfolio_template(securities, context)
    rows = []
    for s in calendar:
        for a in securities:
            for kind in ("OPEN", "CLOSE"):
                t = s[kind.lower()]
                rows.append(
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
    return seal_sidecar(
        {
            "schema_version": "simulation-request/1.0.0",
            "request_id": str(NAMESPACE),
            "scope": "ENGINEERING_TEST_ONLY",
            "financial_approval": "NONE",
            "currency": "CCY",
            "calendar_id": "SYNTHETIC_V1",
            "initial_cash": "1000",
            "fee_budget": "10",
            "liquidity": {"lookback_sessions": 1, "minimum_adv": "10"},
            "assets": securities,
            "sessions": calendar,
            "sidecar": {
                "schema_version": "execution-sidecar/1.0.0",
                "snapshot_id": parent_id,
                "snapshot_sha256": parent_hash,
                "rows": rows,
                "volume_history": [
                    {
                        "security_id": a["security_id"],
                        "session_id": s["session_id"],
                        "shares": "100",
                        "event_time": s["close"],
                        "available_at": s["close"],
                        "revision_id": 1,
                    }
                    for s in calendar
                    for a in securities
                ],
            },
            "decisions": [
                {
                    "portfolio_request_utf8": canonical(p).decode(),
                    "order_type": "MARKET",
                    "limit_prices": {},
                    "time_in_force": "DAY",
                    "expires_session": calendar[-1]["session_id"],
                }
            ],
            "actions": [],
            "cashflows": [],
            "cancellations": [],
        }
    )


def research_backtests(destination, code_commit):
    """One real P1/P3 run, two preregistered exact Refs, identical execution/core inputs."""
    from aqrp.data.snapshot import verify_snapshot
    from aqrp.portfolio.research_input import bind_research
    from aqrp.research.synthetic import synthetic_research
    from aqrp.services.research import ResearchRequest, research

    c, ref, exposures, coverage = synthetic_research(
        destination / "inputs", sessions=24, assets=6, factor_ids=("momentum", "reversal")
    )
    ledger_root = destination / "research-runs"
    r = research(ResearchRequest.create(c, ref, exposures, coverage, code_commit), ledger_root)
    if r["manifest"]["status"] != "SUCCEEDED":
        raise RuntimeError("Synthetic P3 preparation failed")
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
    decision_window = c["decisions"][2:5]
    first = next(
        i for i, s in enumerate(sessions) if s["session_id"] == decision_window[0]["session"]
    )
    sessions = sessions[first - 1 : first + 5]
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
    for factor in ("momentum", "reversal"):
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
    (destination / "research-request.json").write_bytes(
        canonical(
            {
                "config": c,
                "snapshot_id": ref.snapshot_id,
                "snapshot_hash": ref.manifest_hash,
                "research_run_id": r["run_id"],
                "sidecar_price_source": "Independent declared constant100 synthetic engineering input; not historical P1 OHLCV relabelled as available at open",
            }
        )
    )
    return output
