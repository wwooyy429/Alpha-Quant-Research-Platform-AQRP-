"""Developer independent read-side oracle: standard library only, no AQRP imports.

Raw executed Fill/Market/action/settlement/borrow/flow records are the inputs.
Production account states are comparisons only, never generated expected answers.
This is developer validation, not a substitute for independent GPT Work G2.
"""

import hashlib
import json
import sys
from datetime import datetime
from fractions import Fraction as Q
from pathlib import Path


def decode(v):
    if isinstance(v, dict):
        if "$fraction" in v:
            return Q(*map(int, v["$fraction"]))
        if set(v) == {"numerator", "denominator", "display"}:
            return Q(int(v["numerator"]), int(v["denominator"]))
        return {k: decode(x) for k, x in v.items()}
    if isinstance(v, list):
        return [decode(x) for x in v]
    return v


def cent(v):
    v = abs(v) * 100
    return Q((2 * v.numerator + v.denominator) // (2 * v.denominator), 100)


def verify_run(request, result, transactions):
    config = json.loads(request)
    result = decode(result)
    cash = Q(config["initial_cash"])
    names = [a["security_id"] for a in config["assets"]]
    qty, cost, mark = ({k: Q(0) for k in names} for _ in range(3))
    lots = {k: [] for k in names}
    sale_cash = []
    rights = {}
    close_qty = qty.copy()
    session = -1
    fees = borrow_cost = dividend = external = Q(0)
    fragments = []
    capacity = {}
    journal_balances = {"cash_set": cash, "U_free": Q(0), "U_short": Q(0)}
    journal_quantities = {k: Q(0) for k in names}
    journal_seen = 0
    assertions = 0
    previous_commit = None
    last_dispatch = None

    def same(actual, expected, field):
        nonlocal assertions
        assert actual == expected, (field, actual, expected)
        assertions += 1

    def historical_capacity(sid, clock):
        if "liquidity" not in config:
            return Q(10)  # Explicit pre-ADV development evidence, never current-profile execution.
        as_of = datetime.fromisoformat(clock)
        n = config["liquidity"]["lookback_sessions"]
        days = [
            s["session_id"]
            for s in config["sessions"]
            if datetime.fromisoformat(s["close"].replace("Z", "+00:00")) <= as_of
        ][-n:]
        known = {}
        for r in config["sidecar"]["volume_history"]:
            if (
                r["security_id"] == sid
                and datetime.fromisoformat(r["available_at"].replace("Z", "+00:00")) <= as_of
            ):
                day = r["session_id"]
                if day not in known or (r["available_at"], r["revision_id"]) > (
                    known[day]["available_at"],
                    known[day]["revision_id"],
                ):
                    known[day] = r
        if len(days) < n or any(day not in known or known[day]["shares"] is None for day in days):
            return Q(0)
        average = sum((Q(known[day]["shares"]) for day in days), Q(0)) / n
        return min(Q(10), average) if average >= Q(config["liquidity"]["minimum_adv"]) else Q(0)

    def fill(fill, order_id=None, recovery=False):
        nonlocal cash, fees
        sid = fill["security_id"]
        signed, p, fee = (Q(fill[k]) for k in ("signed_qty", "price", "fee"))
        n = abs(signed)
        if not recovery:
            same(fee, cent(max(Q(1), n * p / 1000)), "independent commission")
            raw = Q(fill["raw_price"])
            ratio = raw * (Q(1001, 1000) if signed > 0 else Q(999, 1000)) * 100
            actual = Q(
                -(-ratio.numerator // ratio.denominator)
                if signed > 0
                else ratio.numerator // ratio.denominator,
                100,
            )
            same(p, actual, "independent slippage tick")
            order = result["orders"][order_id]
            submitted = datetime.fromisoformat(order["submitted_at"])
            eligible = datetime.fromisoformat(order["eligible_at"])
            same(
                submitted < eligible <= datetime.fromisoformat(fill["at"]),
                True,
                "strict future order eligibility",
            )
            same(
                datetime.fromisoformat(fill["at"]),
                datetime.fromisoformat(tx["payload"]["slice"]["event_time"]),
                "opening slice time",
            )
            same(
                datetime.fromisoformat(tx["payload"]["slice"]["available_at"]),
                datetime.fromisoformat(fill["at"]),
                "no late slice backfill",
            )
            low, high = Q(order["low"]), Q(order["high"])
            same(
                low <= raw <= high and low <= p <= high,
                True,
                "both raw and actual prices inside frozen band",
            )
        old = qty[sid]
        closing = min(abs(old), n) if old * signed < 0 else Q(0)
        opening = n - closing
        expected_legs = []
        if closing:
            expected_legs.append(
                {
                    "effect": "CLOSE",
                    "direction": "LONG" if old > 0 else "SHORT",
                    "quantity": closing,
                    "signed_qty": closing if signed > 0 else -closing,
                    "fee": fee * closing / n,
                    "realized_gross": closing * (1 if old > 0 else -1) * (p - cost[sid]),
                }
            )
        if opening:
            expected_legs.append(
                {
                    "effect": "OPEN",
                    "direction": "LONG" if signed > 0 else "SHORT",
                    "quantity": opening,
                    "signed_qty": opening if signed > 0 else -opening,
                    "fee": fee * opening / n,
                    "realized_gross": Q(0),
                }
            )
        same(fill["execution_side"], "BUY" if signed > 0 else "SELL", "execution side")
        same(fill["position_before"], old, "pre-fill position")
        same(fill["position_after"], old + signed, "post-fill position")
        same(fill["position_legs"], expected_legs, "independent exposure-leg quantity/fee/gross")
        same(
            fill["direction"],
            expected_legs[0]["direction"] if len(expected_legs) == 1 else "MIXED",
            "unambiguous fill exposure direction",
        )
        cash -= fee
        fees += fee
        if signed > 0:
            cash -= n * p
        else:
            if closing:
                sale_cash.append(
                    {
                        "entry": None,
                        "amount": closing * p,
                        "due": session + 1,
                        "settled": False,
                        "kind": "FREE",
                    }
                )
            if opening:
                sale_cash.append(
                    {
                        "entry": fill["fill_id"],
                        "amount": opening * p,
                        "due": session + 1,
                        "settled": False,
                        "kind": "SHORT",
                    }
                )
        needed = closing
        for lot in lots[sid]:
            if needed <= 0 or not lot["remaining"] or lot["direction"] * signed > 0:
                continue
            taken = min(needed, lot["remaining"])
            share = taken / lot["remaining"]
            pools = {k: lot[k] * share for k in ("fee", "borrow", "dividend")}
            for k in pools:
                lot[k] -= pools[k]
            fragments.append(
                {
                    "entry": lot["entry"],
                    "exit": fill["fill_id"],
                    "net": lot["direction"] * taken * (p - lot["price"])
                    - pools["fee"]
                    - fee * taken / n
                    - pools["borrow"]
                    + pools["dividend"],
                }
            )
            if lot["direction"] < 0:
                for entry in list(sale_cash):
                    if entry["kind"] == "SHORT" and entry["entry"] == lot["entry"]:
                        released = entry["amount"] * share
                        entry["amount"] -= released
                        if not entry["settled"]:
                            sale_cash.append(
                                {**entry, "amount": released, "entry": None, "kind": "FREE"}
                            )
            lot["remaining"] -= taken
            needed -= taken
        same(needed, 0, "FIFO close quantity coverage")
        if opening:
            lots[sid].append(
                {
                    "entry": fill["fill_id"],
                    "remaining": opening,
                    "direction": 1 if signed > 0 else -1,
                    "price": p,
                    "fee": fee * opening / n,
                    "borrow": Q(0),
                    "dividend": Q(0),
                }
            )
        if old == 0 or old * (old + signed) < 0:
            cost[sid] = p
        elif old * signed > 0:
            cost[sid] = (abs(old) * cost[sid] + n * p) / abs(old + signed)
        qty[sid] += signed
        if qty[sid] == 0:
            cost[sid] = Q(0)

    for index, encoded in enumerate(transactions):
        body = {k: v for k, v in encoded.items() if k != "sha256"}
        wire = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        same(hashlib.sha256(wire).hexdigest(), encoded["sha256"], "transaction content hash")
        if previous_commit is not None:
            same(encoded["previous"], previous_commit, "commit hash chain")
        previous_commit = encoded["sha256"]
        tx = decode(encoded)
        same(tx["commit_seq"], index + 1, "ordered committed transaction")
        state = tx["post_state"]
        payload = tx["payload"]
        child_kinds = [c["kind"] for c in tx["children"]]
        dispatch = (datetime.fromisoformat(tx["dispatch_key"][0]), *tx["dispatch_key"][1:])
        if last_dispatch is not None:
            same(last_dispatch < dispatch, True, "outer envelope total order")
        last_dispatch = dispatch
        for child in tx["children"]:
            kind = child["kind"]
            if kind == "AccountUpdated" and tx["dispatch_key"][1] == 10:
                session = payload["session"]
                for item in sale_cash:
                    if item["due"] <= session and not item["settled"]:
                        item["settled"] = True
                        cash += item["amount"]
            elif kind == "MarketConfirmed":
                for row in payload["rows"]:
                    if row["price"] is not None:
                        mark[row["security_id"]] = Q(row["price"])
                    if payload["kind"] == "OPEN":
                        capacity[row["slice_id"]] = historical_capacity(
                            row["security_id"], tx["dispatch_key"][0]
                        )
            elif kind == "Fill":
                same(child["local_stage"], 80, "Fill is local child of70")
                same(tx["dispatch_key"][1], 70, "Fill parent phase70")
                same(child_kinds, ["Fill", "AccountUpdated"], "atomic Fill/account pair")
                record = child["fill"]
                fill(record, payload["order_id"])
                capacity[payload["slice"]["slice_id"]] -= abs(record["signed_qty"])
                assert capacity[payload["slice"]["slice_id"]] >= 0
            elif kind == "SPLIT":
                sid, ratio = payload["security_id"], Q(payload["value"])
                qty[sid] *= ratio
                cost[sid] /= ratio
                mark[sid] /= ratio
                for lot in lots[sid]:
                    lot["remaining"] *= ratio
                    lot["price"] /= ratio
            elif kind == "DIVIDEND":
                sid = payload["security_id"]
                eligible = close_qty[sid] if payload["unit"] == "PER_OLD_SHARE" else qty[sid]
                amount = eligible * Q(payload["value"])
                rights[payload["action_id"]] = amount
                dividend += amount
                if qty[sid]:
                    for lot in lots[sid]:
                        lot["dividend"] += amount * lot["remaining"] / abs(qty[sid])
            elif kind == "DIVIDEND_PAY":
                cash += rights.pop(payload["action_id"])
            elif kind == "DELIST":
                sid = payload["security_id"]
                if qty[sid]:
                    fill(
                        {
                            "fill_id": payload["action_id"],
                            "security_id": sid,
                            "signed_qty": -qty[sid],
                            "price": Q(payload["value"]),
                            "fee": Q(0),
                        },
                        recovery=True,
                    )
            elif kind == "Borrow":
                total = Q(0)
                for sid in names:
                    amount = cent(max(-qty[sid], 0) * mark[sid] / 25200)
                    total += amount
                    if qty[sid] < 0:
                        for lot in lots[sid]:
                            lot["borrow"] += amount * lot["remaining"] / -qty[sid]
                same(child["fee"], total, "independent borrow fee")
                cash -= total
                borrow_cost += total
            elif kind == "ExternalFlow":
                cash += Q(payload["amount"])
                external += Q(payload["amount"])
            elif kind == "Valuation":
                close_qty = qty.copy()
        uf = sum((c["amount"] for c in sale_cash if not c["settled"] and c["kind"] == "FREE"), Q(0))
        us = sum(
            (c["amount"] for c in sale_cash if not c["settled"] and c["kind"] == "SHORT"), Q(0)
        )
        restricted = sum(
            (c["amount"] for c in sale_cash if c["settled"] and c["kind"] == "SHORT"), Q(0)
        )
        receivable = sum((max(r, 0) for r in rights.values()), Q(0))
        payable = -sum((min(r, 0) for r in rights.values()), Q(0))
        total_cash = cash + uf + us
        total_equity = (
            total_cash + sum((qty[k] * mark[k] for k in names), Q(0)) + sum(rights.values(), Q(0))
        )
        same(state["cash_set"], cash, "cash settled reconstructed from raw events")
        same(state["capacity"], capacity, "shared capacity consumed only by committed fills")
        for order in state["orders"].values():
            same(
                order["original_qty"]
                - order["filled_qty"]
                - order["cancelled_qty"]
                - order["expired_remaining"],
                order["remaining"],
                "full order quantity conservation",
            )
        same(state["fees"], fees, "fees paid exactly once")
        same(state["borrow"], borrow_cost, "borrow costs accrued once")
        same(state["dividends"], dividend, "dividend accrual/pay separation")
        for k in names:
            same(state["assets"][k]["quantity"], qty[k], "signed share conservation")
            same(state["assets"][k]["cost"], cost[k], "moving average exact cost")
        same(
            sum((r["amount"] for r in state["rights"].values()), Q(0)),
            sum(rights.values(), Q(0)),
            "receivable/payable net",
        )
        same(
            sum((max(r["amount"], 0) for r in state["rights"].values()), Q(0)),
            receivable,
            "separate receivable",
        )
        same(
            -sum((min(r["amount"], 0) for r in state["rights"].values()), Q(0)),
            payable,
            "separate payable",
        )
        for row in state["journal"][journal_seen:]:
            if row["kind"] == "SETTLEMENT":
                same(
                    row["settlement_session"],
                    session,
                    "durable settlement session from raw dispatch",
                )
            balances = {}
            for e in row["entries"]:
                balances[e["unit"]] = balances.get(e["unit"], Q(0)) + e["amount"]
                if e["unit"] == "CCY":
                    journal_balances[e["account"]] = (
                        journal_balances.get(e["account"], Q(0)) + e["amount"]
                    )
                elif e["account"] == "position_quantity":
                    journal_quantities[e["unit"]] += e["amount"]
            same(set(balances.values()) <= {Q(0)}, True, "double entry every event/unit")
        journal_seen = len(state["journal"])
        same(journal_balances["cash_set"], cash, "raw journal cash independently reconciled")
        same(journal_balances["U_free"], uf, "raw journal U_free")
        same(journal_balances["U_short"], us, "raw journal U_short")
        same(journal_balances.get("receivable", Q(0)), receivable, "raw journal receivable")
        same(journal_balances.get("payable", Q(0)), -payable, "raw journal payable sign")
        same(journal_quantities, qty, "raw journal shares")
        for c in tx["children"]:
            if "account" in c:
                same(c["account"]["cash_total"], total_cash, "actual committed account cash")
                same(c["account"]["equity"], total_equity, "actual committed account equity")
                for key, value in {
                    "cash_set": cash,
                    "U_free": uf,
                    "U_short": us,
                    "S_set": restricted,
                    "receivable": receivable,
                    "payable": payable,
                }.items():
                    same(c["account"][key], value, "actual committed individual bucket " + key)
    same(Q(result["account"]["cash_total"]), total_cash, "serialized final cash")
    same(Q(result["account"]["equity"]), total_equity, "serialized final equity")
    same(
        Q(result["performance"]["net_pnl"]),
        total_equity - Q(config["initial_cash"]) - external,
        "serialized net pnl excludes flows",
    )
    same(len(result["fragments"]), len(fragments), "closed FIFO fragment count")
    for actual, expected in zip(result["fragments"], fragments):
        same(actual["entry_fill_id"], expected["entry"], "historical FIFO entry identity")
        same(
            Q(actual["net"]) if isinstance(actual["net"], str) else actual["net"],
            expected["net"],
            "exact closed fragment attributed net",
        )
    return {
        "result": "PASS",
        "assertions": assertions,
        "committed_transactions": len(transactions),
        "scope": "Developer independent stdlib raw-event/journal reconstruction; not independent GPT Work G2",
    }


def main():
    root = Path(sys.argv[1])
    outcomes = {}
    for name in ("momentum", "reversal"):
        result = json.loads((root / (name + "-result.json")).read_bytes())
        transactions = json.loads(
            (root / (name + "-runs") / result["run_id"] / "transactions.json").read_bytes()
        )
        outcomes[name] = verify_run(
            (root / (name + "-request.json")).read_bytes(), result, transactions
        )
    (root / "independent-reference.json").write_text(
        json.dumps(outcomes, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(outcomes))


if __name__ == "__main__":
    main()
