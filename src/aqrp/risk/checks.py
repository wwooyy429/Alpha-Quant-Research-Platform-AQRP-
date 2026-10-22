"""Reconstruct and check every constraint before and after target quantization."""

from aqrp.core.canonical import digest
from aqrp.portfolio.construct import build_candidate, compute
from aqrp.portfolio.contracts import CASH_TOL, RATIO_TOL, F, TargetCandidate, fail, number, project


def assess(x, maps, positions, quantities, *, post):
    account = x["inputs"]["account"]["data"]
    equity = number(account["equity"])
    weights = {s: q * number(maps["prices"][s]["price"]) / equity for s, q in quantities.items()}
    delta = {s: q - positions[s] for s, q in quantities.items()}
    gross, net = sum(abs(v) for v in weights.values()), sum(weights.values())
    turnover = sum(abs(delta[s] * number(maps["prices"][s]["price"])) for s in delta) / equity
    short_value = sum(
        max(-q * number(maps["prices"][s]["price"]), 0) for s, q in quantities.items()
    )
    cash = equity - sum(q * number(maps["prices"][s]["price"]) for s, q in quantities.items())
    nonshort = number(account["nonshort_restriction"])
    restricted = short_value + nonshort
    reserve = number(x["profile"]["fee_reserve"])
    free = cash - restricted - short_value - reserve
    beta = sum(weights[s] * number(maps["exposures"][s]["beta"]) for s in weights)
    industries = {}
    for sid, w in weights.items():
        sector = maps["exposures"][sid]["industry"]
        industries.setdefault(sector, {"net": F(0), "gross": F(0)})
        industries[sector]["net"] += w
        industries[sector]["gross"] += abs(w)
    checks = []

    def check(code, actual, *, low=None, high=None, tol=RATIO_TOL, security_id=None):
        passed = (low is None or actual >= low - tol) and (high is None or actual <= high + tol)
        checks.append(
            {
                "code": code,
                "security_id": security_id,
                "actual": actual,
                "low": low,
                "high": high,
                "tolerance": tol,
                "passed": passed,
            }
        )

    limits = x["constraints"]
    for sid, w in weights.items():
        check("ASSET_WEIGHT", abs(w), high=number(limits["per_asset"][sid]), security_id=sid)
    check("GROSS", gross, high=number(limits["gross_max"]))
    check("NET", net, low=number(limits["net_min"]), high=number(limits["net_max"]))
    check("LEVERAGE", gross, high=number(limits["leverage_max"]))
    check("TURNOVER", turnover, high=number(limits["turnover_max"]))
    check("BETA", beta, low=number(limits["beta_min"]), high=number(limits["beta_max"]))
    check("FREE_CASH", free, low=F(0), tol=CASH_TOL)
    if not limits["allow_cash_only"]:
        check("CASH_ONLY_FORBIDDEN", gross, low=RATIO_TOL, tol=F(0))
    for sector, values in industries.items():
        config = limits["industries"][sector]
        check(
            "INDUSTRY_NET",
            values["net"],
            low=number(config["net_min"]),
            high=number(config["net_max"]),
            security_id=sector,
        )
        check(
            "INDUSTRY_GROSS", values["gross"], high=number(config["gross_max"]), security_id=sector
        )
    exemptions = []
    for sid, dq in delta.items():
        permission = maps["permissions"][sid]
        q = quantities[sid]
        if post and dq:
            lot = number(maps["prices"][sid]["lot"])
            check(
                "TARGET_LOT_MISMATCH",
                F((q / lot).denominator != 1),
                high=F(0),
                tol=F(0),
                security_id=sid,
            )
            full_close = (
                q == 0
                and positions[sid] != 0
                and dq == -positions[sid]
                and x["profile"]["allow_full_close_odd_lot"]
            )
            bad_delta = (dq / lot).denominator != 1
            if full_close and bad_delta:
                exemptions.append(sid)
            check(
                "DELTA_LOT_MISMATCH",
                F(bad_delta and not full_close),
                high=F(0),
                tol=F(0),
                security_id=sid,
            )
        if dq:
            check(
                "NOT_TRADABLE",
                F(not maps["status"][sid]["tradable"]),
                high=F(0),
                tol=F(0),
                security_id=sid,
            )
            long_sale = min(max(-dq, 0), max(positions[sid], 0))
            check(
                "SELLABLE",
                long_sale,
                high=number(permission["sellable_qty"]),
                tol=F(0),
                security_id=sid,
            )
        if q < 0:
            check(
                "SHORT_PERMISSION",
                F(not permission["short_permission"]),
                high=F(0),
                tol=F(0),
                security_id=sid,
            )
            check(
                "BORROW_TOTAL",
                -q,
                high=number(permission["borrow_limit_total"]),
                tol=F(0),
                security_id=sid,
            )
    return {
        "phase": "POST" if post else "PRE",
        "passed": all(c["passed"] for c in checks),
        "checks": checks,
        "metrics": {
            "weights": weights,
            "quantities": quantities,
            "deltas": delta,
            "cash": cash,
            "restricted_cash": restricted,
            "margin_requirement": short_value,
            "fee_reserve": reserve,
            "free_cash": free,
            "gross": gross,
            "net": net,
            "cash_weight": 1 - net,
            "leverage": gross,
            "turnover": turnover,
            "half_turnover": turnover / 2,
            "beta": beta,
            "industries": industries,
        },
        "full_close_lot_exemptions": exemptions,
    }


def check_target(candidate, request):
    if not isinstance(candidate, TargetCandidate) or candidate.request_hash != request.content_hash:
        fail("CANDIDATE_REQUEST_MISMATCH")
    expected = build_candidate(request)
    if candidate.raw != expected.raw:
        fail("CANDIDATE_TAMPERED")
    x, maps, positions, ideal, rounded, _, _ = compute(request)
    pre, post = (
        assess(x, maps, positions, ideal, post=False),
        assess(x, maps, positions, rounded, post=True),
    )
    result = project(
        {
            "schema_version": "risk-decision/1.0.0",
            "passed": pre["passed"] and post["passed"],
            "request_hash": request.content_hash,
            "candidate_hash": digest({"raw": candidate.raw.decode()}),
            "pre": pre,
            "post": post,
        }
    )
    result["content_sha256"] = digest(result)
    return result
