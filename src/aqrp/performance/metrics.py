"""BT-008/009: flow-adjusted TWR, ddof1, A252 and CLOSED_FIFO_FRAGMENT statistics."""

import math

from aqrp.backtest.exact import F
from aqrp.backtest.ledger import account
from aqrp.core.errors import ContractError


def undefined(reason):
    return {"value": None, "reason": reason}


def measured(value):
    return {"value": value, "reason": None}


def finite_stat(fn):
    try:
        value = fn()
        if not math.isfinite(value):
            return undefined("NUMERIC_RANGE")
        return measured(value)
    except (ArithmeticError, ValueError):
        return undefined("NUMERIC_RANGE")


def summary(returns, nav, *, rf_daily=F(0)):
    if not returns or any(n <= 0 for n in nav):
        return {
            k: undefined(
                "NONPOSITIVE_EQUITY" if any(n <= 0 for n in nav) else "NO_SESSION_INTERVALS"
            )
            for k in (
                "cumulative_return",
                "annual_return",
                "volatility",
                "sharpe",
                "maximum_drawdown",
            )
        }
    total = F(1)
    for r in returns:
        total *= 1 + r
    peak = nav[0]
    mdd = F(0)
    for n in nav:
        peak = max(peak, n)
        mdd = max(mdd, 1 - n / peak)
    result = {
        "cumulative_return": measured(total - 1),
        "maximum_drawdown": measured(mdd),
        "annual_return": finite_stat(
            lambda: math.expm1(math.log(float(total)) * 252 / len(returns))
        )
        if total > 0
        else undefined("NONPOSITIVE_GROWTH"),
    }
    if len(returns) < 2:
        result.update(
            volatility=undefined("INSUFFICIENT_INTERVALS"),
            sharpe=undefined("INSUFFICIENT_INTERVALS"),
        )
    else:
        mean = sum(returns, F(0)) / len(returns)
        variance = sum(((r - mean) ** 2 for r in returns), F(0)) / (len(returns) - 1)
        result["sample_variance"] = measured(variance)
        result["volatility"] = finite_stat(lambda: math.sqrt(float(variance) * 252))
        result["sharpe"] = (
            finite_stat(
                lambda: float(mean - rf_daily) / math.sqrt(float(variance)) * math.sqrt(252)
            )
            if variance
            else undefined("ZERO_VARIANCE")
        )
    return result


def fifo_statistics(fragments):
    values = [f["net"] for f in fragments]
    winners, losers = [v for v in values if v > 0], [v for v in values if v < 0]
    rate = measured(F(len(winners), len(values))) if values else undefined("NO_CLOSED_FRAGMENTS")
    reason = (
        "NO_CLOSED_FRAGMENTS"
        if not values
        else "NO_NONZERO_OUTCOMES"
        if not winners and not losers
        else "NO_WINNERS"
        if not winners
        else "NO_LOSERS"
        if not losers
        else None
    )
    ratio = (
        undefined(reason)
        if reason
        else measured((sum(winners, F(0)) / len(winners)) / -(sum(losers, F(0)) / len(losers)))
    )
    return {
        "convention": "CLOSED_FIFO_FRAGMENT",
        "count": len(values),
        "winners": len(winners),
        "losers": len(losers),
        "zero": sum(v == 0 for v in values),
        "win_rate": rate,
        "profit_loss_ratio": ratio,
    }


def performance(s):
    anchor = s["initial_cash"]
    nav = [F(1)]
    factor = F(1)
    cumulative = F(1)
    returns = []
    invalid = anchor <= 0
    for v in s["valuations"]:
        if v["kind"] == "EXTERNAL_FLOW":
            before = v["before_equity"]
            invalid |= before <= 0 or v["account"]["equity"] <= 0
            if anchor > 0:
                factor *= before / anchor
            anchor = v["account"]["equity"]
            nav.append(cumulative * factor)
        else:
            equity = v["account"]["equity"]
            invalid |= equity <= 0
            if anchor > 0:
                factor *= equity / anchor
            returns.append(factor - 1)
            cumulative *= factor
            nav.append(cumulative)
            anchor = equity
            factor = F(1)
    stats = summary(returns, [F(0)] if invalid else nav)
    contribution = {"LONG": F(0), "SHORT": F(0)}
    for f in s["fragments"]:
        contribution["LONG" if f["direction"] == 1 else "SHORT"] += f["net"]
    open_pools = []
    for sid, a in s["assets"].items():
        for lot in a["lots"]:
            if lot["remaining"]:
                net = (
                    lot["direction"] * lot["remaining"] * (a["mark"] - lot["price"])
                    - lot["entry_fee"]
                    - lot["borrow"]
                    + lot["long_dividend"]
                    - lot["short_dividend"]
                )
                contribution["LONG" if lot["direction"] == 1 else "SHORT"] += net
                open_pools.append(
                    {
                        "security_id": sid,
                        "entry_fill_id": lot["id"],
                        "remaining": lot["remaining"],
                        "net_contribution": net,
                        "entry_fee": lot["entry_fee"],
                        "borrow": lot["borrow"],
                        "long_dividend": lot["long_dividend"],
                        "short_dividend": lot["short_dividend"],
                    }
                )
    net_pnl = account(s)["equity"] - s["initial_cash"] - s["external_flows"]
    if sum(contribution.values(), F(0)) != net_pnl:
        raise ContractError("LONG_SHORT_ATTRIBUTION_MISMATCH")
    turnover = sum(
        (b["turnover_notional"] / b["decision_equity"] for b in s["budgets"].values()), F(0)
    )
    return {
        "schema_version": "performance/1.0.0",
        "annualization": 252,
        "ddof": 1,
        "rf_daily": F(0),
        "session_intervals": len(returns),
        "returns": returns,
        "flow_adjusted_nav": nav,
        **stats,
        "fifo": fifo_statistics(s["fragments"]),
        "turnover_full": turnover,
        "turnover_half": turnover / 2,
        "net_pnl": net_pnl,
        "commission": s["fees"],
        "borrow": s["borrow"],
        "dividends": s["dividends"],
        "slippage_cost_already_in_prices": sum((f["slippage_cost"] for f in s["fills"]), F(0)),
        "contribution": contribution,
        "open_lot_pools": open_pools,
    }
