"""Latest-state P5 checks use true equity/cash; P4's budget checks remain independent."""

from aqrp.backtest.exact import F, money
from aqrp.backtest.ledger import account, sellable


def assess(s, limits, *, sid=None, signed_qty=F(0), before=None, turnover=F(0)):
    c = account(s)
    equity = c["equity"]
    checks = []

    def check(code, actual, low=None, high=None):
        checks.append(
            {
                "code": code,
                "actual": actual,
                "low": low,
                "high": high,
                "passed": (low is None or actual >= low) and (high is None or actual <= high),
            }
        )

    check("POSITIVE_EQUITY", equity, low=F(1, 10**100))
    check("ACTUAL_FREE_CASH", c["available"], low=F(0))
    check("COMMISSION_BUDGET", c["F_unused"], low=F(0))
    check("SETTLED_SHORT_SUBSET", c["cash_set"] - c["S_set"], low=F(0))
    if equity <= 0:
        return {"passed": False, "account": c, "checks": checks}
    weights = {k: a["quantity"] * a["mark"] / equity for k, a in s["assets"].items()}
    gross = sum((abs(w) for w in weights.values()), F(0))
    net = sum(weights.values(), F(0))
    beta = sum((weights[k] * a["beta"] for k, a in s["assets"].items()), F(0))
    for k, w in weights.items():
        check("ASSET:" + k, abs(w), high=money(limits["per_asset"][k]))
    check("GROSS", gross, high=money(limits["gross_max"]))
    check("LEVERAGE", gross, high=money(limits["leverage_max"]))
    check("NET", net, low=money(limits["net_min"]), high=money(limits["net_max"]))
    check("BETA", beta, low=money(limits["beta_min"]), high=money(limits["beta_max"]))
    check("TURNOVER", turnover, high=money(limits["turnover_max"]))
    if not limits["allow_cash_only"]:
        check("CASH_ONLY_FORBIDDEN", gross, low=F(1, 10**12))
    sectors = {}
    for k, a in s["assets"].items():
        sector = sectors.setdefault(a["industry"], {"net": F(0), "gross": F(0)})
        sector["net"] += weights[k]
        sector["gross"] += abs(weights[k])
        if a["quantity"] < 0:
            check("SHORT_PERMISSION:" + k, F(a["short_permission"]), low=F(1))
            check("BORROW:" + k, -a["quantity"], high=a["borrow_limit"])
    for sector, v in sectors.items():
        lim = limits["industries"].get(sector)
        if lim is None:
            check("INDUSTRY_UNKNOWN:" + sector, F(1), high=F(0))
        else:
            check(
                "INDUSTRY_NET:" + sector,
                v["net"],
                low=money(lim["net_min"]),
                high=money(lim["net_max"]),
            )
            check("INDUSTRY_GROSS:" + sector, v["gross"], high=money(lim["gross_max"]))
    if sid is not None:
        a = s["assets"][sid]
        old = before["assets"][sid]
        check("TRADABLE", F(a["tradable"]), low=F(1))
        if abs(a["quantity"]) > abs(old["quantity"]):
            check("IN_UNIVERSE", F(a["in_universe"]), low=F(1))
        if signed_qty < 0:
            check(
                "SELLABLE",
                min(-signed_qty, max(old["quantity"], 0)),
                high=sellable(old, s["session"]),
            )
        full_close = a["quantity"] == 0 and signed_qty == -old["quantity"]
        check(
            "DELTA_LOT",
            F((abs(signed_qty) / a["lot"]).denominator != 1 and not full_close),
            high=F(0),
        )
    return {
        "passed": all(v["passed"] for v in checks),
        "account": c,
        "checks": checks,
        "metrics": {
            "weights": weights,
            "gross": gross,
            "net": net,
            "beta": beta,
            "turnover": turnover,
            "industries": sectors,
        },
    }
