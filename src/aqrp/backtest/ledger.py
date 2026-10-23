"""BT-005–008: exact double-entry cash, average cost, FIFO and corporate actions."""

from copy import deepcopy

from aqrp.core.errors import ContractError
from aqrp.execution.model import LIVE, fee_upper, transition

from .exact import F, money, round_cent, thaw


def initial_state(cash, assets):
    return {
        "initial_cash": cash,
        "cash_set": cash,
        "cashlots": [],
        "rights": {},
        "external_flows": F(0),
        "fees": F(0),
        "borrow": F(0),
        "dividends": F(0),
        "realized_long": F(0),
        "realized_short": F(0),
        "other_restriction": F(0),
        "assets": {
            a["security_id"]: {
                "quantity": F(0),
                "cost": F(0),
                "mark": F(0),
                "last_mark_session": -1,
                "lot": money(a["lot"]),
                "industry": a["industry"],
                "beta": money(a["beta"]),
                "short_permission": a["short_permission"],
                "borrow_limit": money(a["borrow_limit"]),
                "tradable": False,
                "in_universe": False,
                "lots": [],
                "mark_ref": None,
                "valuation_adjustment": F(0),
                "delisted": False,
            }
            for a in assets
        },
        "orders": {},
        "budgets": {},
        "current_budget": None,
        "capacity": {},
        "fills": [],
        "liquidations": [],
        "fragments": [],
        "journal": [],
        "valuations": [],
        "close_quantities": {},
        "session": -1,
        "last_key": None,
    }


def cash_values(s):
    free = sum(
        (c["amount"] for c in s["cashlots"] if not c["settled"] and c["kind"] == "FREE"), F(0)
    )
    short = sum(
        (c["amount"] for c in s["cashlots"] if not c["settled"] and c["kind"] == "SHORT"), F(0)
    )
    restricted = sum(
        (c["amount"] for c in s["cashlots"] if c["settled"] and c["kind"] == "SHORT"), F(0)
    )
    return {
        "cash_set": s["cash_set"],
        "U_free": free,
        "U_short": short,
        "S_set": restricted,
        "cash_total": s["cash_set"] + free + short,
    }


def verify_cash_structure(s, cash):
    """Check internal lot relations; original executions require a separate proof.

    Settlement uses the durable Journal's completed session, not a mutable lot flag
    or the scheduler's current session. Negative available cash alone is not an
    inconsistency: a correctly recorded margin breach must keep its actual loss.
    """
    sessions = []
    for event in s["journal"]:
        if event["kind"] == "SETTLEMENT":
            value = event.get("settlement_session")
            if type(value) is not int or value < 0 or (sessions and value < sessions[-1]):
                raise ContractError("UNVERIFIED_SETTLEMENT_SESSION")
            sessions.append(value)
    settled_through = sessions[-1] if sessions else -1
    backing = {}
    for asset in s["assets"].values():
        for lot in asset["lots"]:
            if lot["direction"] == -1:
                if lot["id"] in backing or lot["remaining"] < 0 or lot["price"] < 0:
                    raise ContractError("INVALID_SHORT_PROCEEDS_BACKING")
                backing[lot["id"]] = lot
    ids, bound = set(), set()
    for lot in s["cashlots"]:
        if (
            set(lot) != {"id", "entry_id", "kind", "amount", "settled", "due"}
            or not isinstance(lot["id"], str)
            or not lot["id"]
            or lot["id"] in ids
            or lot["kind"] not in {"FREE", "SHORT"}
            or lot["amount"] < 0
            or type(lot["settled"]) is not bool
            or type(lot["due"]) is not int
            or lot["due"] < 0
            or lot["settled"] != (lot["due"] <= settled_through)
        ):
            raise ContractError("INVALID_CASH_LOT_CLASSIFICATION")
        ids.add(lot["id"])
        if lot["kind"] == "FREE":
            if lot["entry_id"] is not None:
                raise ContractError("INVALID_FREE_CASH_BACKING")
        else:
            entry = lot["entry_id"]
            if entry not in backing or entry in bound:
                raise ContractError("INVALID_SHORT_PROCEEDS_BACKING")
            position_lot = backing[entry]
            if (
                lot["amount"] != position_lot["remaining"] * position_lot["price"]
                or lot["due"] != position_lot["settles"]
            ):
                raise ContractError("SHORT_PROCEEDS_OR_SETTLEMENT_MISMATCH")
            bound.add(entry)
    if bound != set(backing):
        raise ContractError("MISSING_SHORT_PROCEEDS_BACKING")
    if any(cash[k] < 0 for k in ("U_free", "U_short", "S_set")) or cash["S_set"] > cash["cash_set"]:
        raise ContractError("RESTRICTED_CASH_SUBSET_FAILED")
    return {
        "status": "INTERNAL_LOT_STRUCTURE_CHECKED_EXECUTION_PROOF_REQUIRED",
        "cash_lots": len(ids),
        "short_entries": len(bound),
        "settled_through_session": settled_through,
    }


def verify_execution_backing(s, records):
    """BT-005/007/008: rebuild lots from verified durable children/payloads.

    Never use post_state, cached fills or cached lot prices as reconstruction
    inputs. The caller supplies the prefix read under TransactionStore's lock.
    Hash-chain validity is necessary but is not financial or OS authorization.
    """
    if records is None:
        raise ContractError("DURABLE_EXECUTION_PROVENANCE_REQUIRED")
    positions = {sid: [] for sid in s["assets"]}
    costs = {sid: F(0) for sid in positions}
    marks = costs.copy()
    cashlots, fills, recoveries, sessions = [], [], [], []
    session = -1
    seen = set()

    def execute(f):
        sid, entry = f["security_id"], f["fill_id"]
        q, p = f["signed_qty"], f["price"]
        if (
            sid not in positions
            or entry in seen
            or not q
            or q.denominator != 1
            or p < 0
            or session < 0
        ):
            raise ContractError("INVALID_DURABLE_EXECUTION")
        seen.add(entry)
        lots = positions[sid]
        old = sum((item["direction"] * item["remaining"] for item in lots), F(0))
        closed = min(abs(old), abs(q)) if old * q < 0 else F(0)
        opened = abs(q) - closed
        new = old + q
        if not new:
            costs[sid] = F(0)
        elif not old or old * new < 0:
            costs[sid] = p
        elif old * q > 0:
            costs[sid] = (abs(old) * costs[sid] + abs(q) * p) / abs(new)
        if q < 0:
            for kind, n, suffix in (("FREE", closed, ":long-sale"), ("SHORT", opened, ":short")):
                if n:
                    cashlots.append(
                        {
                            "id": entry + suffix,
                            "entry_id": entry if kind == "SHORT" else None,
                            "kind": kind,
                            "amount": n * p,
                            "settled": False,
                            "due": session + 1,
                        }
                    )
        needed = closed
        for lot in lots:
            if not needed or not lot["remaining"] or lot["direction"] * q > 0:
                continue
            taken = min(needed, lot["remaining"])
            if lot["direction"] == -1:
                cash = next(
                    c for c in cashlots if c["kind"] == "SHORT" and c["entry_id"] == lot["id"]
                )
                # Original gross per remaining share, derived from the raw Fill.
                released = taken * lot["price"]
                cash["amount"] -= released
                if not cash["settled"]:
                    cashlots.append(
                        {
                            **cash,
                            "id": cash["id"] + ":released:" + str(len(cashlots)),
                            "entry_id": None,
                            "kind": "FREE",
                            "amount": released,
                        }
                    )
            lot["remaining"] -= taken
            needed -= taken
        if needed:
            raise ContractError("DURABLE_FIFO_CLOSE_NOT_COVERED")
        if opened:
            lots.append(
                {
                    "id": entry,
                    "direction": 1 if q > 0 else -1,
                    "remaining": opened,
                    "price": p,
                    "settles": session + 1,
                    "at": f["at"],
                }
            )

    for encoded in records:
        record = thaw(encoded)
        payload, children = record["payload"], record["children"]
        kinds = [c["kind"] for c in children]
        if (
            record["dispatch_key"][1] == 10
            and kinds == ["AccountUpdated"]
            and set(payload) == {"session"}
        ):
            value = payload["session"]
            if type(value) is not int or value < 0 or value < session:
                raise ContractError("INVALID_DURABLE_SETTLEMENT_ORDER")
            session = value
            sessions.append(value)
            for c in cashlots:
                if c["due"] <= value:
                    c["settled"] = True
        elif "MarketConfirmed" in kinds:
            for row in payload["rows"]:
                if row["price"] is not None:
                    marks[row["security_id"]] = money(row["price"])
        elif "SPLIT" in kinds:
            ratio = money(payload["value"])
            if ratio <= 0:
                raise ContractError("INVALID_DURABLE_SPLIT")
            for lot in positions[payload["security_id"]]:
                lot["remaining"] *= ratio
                lot["price"] /= ratio
            costs[payload["security_id"]] /= ratio
            marks[payload["security_id"]] /= ratio
        elif "DELIST" in kinds:
            sid = payload["security_id"]
            q = -sum((item["direction"] * item["remaining"] for item in positions[sid]), F(0))
            if q:
                f = {
                    "fill_id": payload["action_id"],
                    "security_id": sid,
                    "signed_qty": q,
                    "price": money(payload["value"]),
                    "fee": F(0),
                    "at": record["dispatch_key"][0],
                }
                execute(f)
                recoveries.append(f)
        for child in children:
            if child["kind"] == "Fill":
                execute(child["fill"])
                fills.append(child["fill"])
    if s["fills"] != fills or len(s["liquidations"]) != len(recoveries):
        raise ContractError("DURABLE_EXECUTION_COPY_MISMATCH")
    for actual, expected in zip(s["liquidations"], recoveries):
        if any(actual[k] != v for k, v in expected.items()):
            raise ContractError("DURABLE_RECOVERY_EXECUTION_MISMATCH")
    for sid, expected in positions.items():
        actual = s["assets"][sid]
        if (
            len(actual["lots"]) != len(expected)
            or any(any(a[k] != v for k, v in e.items()) for a, e in zip(actual["lots"], expected))
            or actual["quantity"]
            != sum((item["direction"] * item["remaining"] for item in expected), F(0))
            or actual["cost"] != costs[sid]
            or actual["mark"] != marks[sid]
            or actual["valuation_adjustment"] != actual["quantity"] * (marks[sid] - costs[sid])
        ):
            raise ContractError("DURABLE_POSITION_LOT_BACKING_MISMATCH", sid)
    if (
        s["cashlots"] != cashlots
        or s["session"] != session
        or [e["settlement_session"] for e in s["journal"] if e["kind"] == "SETTLEMENT"] != sessions
    ):
        raise ContractError("DURABLE_CASH_PROCEEDS_OR_SETTLEMENT_MISMATCH")
    return {
        "status": "RAW_COMMITTED_EXECUTIONS_FIFO_AND_SETTLEMENT_VERIFIED",
        "fills": len(fills),
        "recoveries": len(recoveries),
        "prefix_commits": len(records),
        "S_set": sum(
            (c["amount"] for c in cashlots if c["kind"] == "SHORT" and c["settled"]), F(0)
        ),
    }


def reserves(s):
    notional = sum(
        (o["reserve_notional"] for o in s["orders"].values() if o["status"] in LIVE), F(0)
    )
    fee = sum(
        (fee_upper(o["remaining"], o["high"]) for o in s["orders"].values() if o["status"] in LIVE),
        F(0),
    )
    payable = -sum((min(r["amount"], 0) for r in s["rights"].values()), F(0))
    return notional, fee, payable


def account(s):
    c = cash_values(s)
    marked = sum((a["quantity"] * a["mark"] for a in s["assets"].values()), F(0))
    short = sum((max(-a["quantity"] * a["mark"], 0) for a in s["assets"].values()), F(0))
    receivable = sum((max(r["amount"], 0) for r in s["rights"].values()), F(0))
    on, of, payable = reserves(s)
    available = c["cash_set"] - c["S_set"] - short - on - of - payable - s["other_restriction"]
    unused = F(0)
    if s["current_budget"] is not None:
        b = s["budgets"][s["current_budget"]]
        unused = b["total"] - b["paid"] - of
    h = max(short - c["S_set"], F(0))
    cash_alloc = c["cash_total"] - c["U_free"] - c["U_short"] - on - of - payable - unused
    return {
        **c,
        "marked_value": marked,
        "short_value": short,
        "receivable": receivable,
        "payable": payable,
        "O_N": on,
        "O_F": of,
        "F_unused": unused,
        "P_res": payable,
        "Z": s["other_restriction"],
        "available": available,
        "equity": c["cash_total"] + marked + receivable - payable,
        "H": h,
        "cash_alloc": cash_alloc,
        "equity_alloc": cash_alloc + marked,
        "P4_nonshort": s["other_restriction"] + max(c["S_set"] - short, 0),
        "P4_free": available - unused - h,
    }


def sellable(a, session):
    return sum(
        (
            lot["remaining"]
            for lot in a["lots"]
            if lot["direction"] == 1 and lot["settles"] <= session
        ),
        F(0),
    )


def _post(s, event_id, kind, lines, quantities=None):
    entries = [{"account": k, "unit": "CCY", "amount": v} for k, v in lines.items() if v]
    if sum((x["amount"] for x in entries), F(0)):
        raise ContractError("UNBALANCED_FINANCIAL_JOURNAL")
    for sid, q in (quantities or {}).items():
        entries += [
            {"account": "position_quantity", "unit": sid, "amount": q},
            {"account": "quantity_control", "unit": sid, "amount": -q},
        ]
    s["journal"].append({"event_id": event_id, "kind": kind, "entries": entries})


def _cash_delta(before, after):
    return {k: after[k] - before[k] for k in ("cash_set", "U_free", "U_short")}


def record_valuation(s, sid, event_id):
    a = s["assets"][sid]
    value = a["quantity"] * (a["mark"] - a["cost"])
    delta = value - a["valuation_adjustment"]
    a["valuation_adjustment"] = value
    if delta:
        _post(
            s, event_id, "MARK_TO_MARKET", {"positions_valuation": delta, "unrealized_pnl": -delta}
        )


def _release_short(s, lot_id, qty, before_qty):
    for c in list(s["cashlots"]):
        if c["entry_id"] != lot_id or c["kind"] != "SHORT":
            continue
        released = c["amount"] * qty / before_qty
        c["amount"] -= released
        if not c["settled"]:
            s["cashlots"].append(
                {
                    **c,
                    "id": c["id"] + ":released:" + str(len(s["cashlots"])),
                    "kind": "FREE",
                    "amount": released,
                    "entry_id": None,
                }
            )


def trade(s, *, fill_id, sid, signed_qty, p, fee, session, at, raw_price=None, recovery=False):
    """Pure candidate mutation; caller commits only after full post-risk checks."""
    a = s["assets"][sid]
    oldq, oldcost = a["quantity"], a["cost"]
    before = cash_values(s)
    qty = abs(signed_qty)
    if qty <= 0 or qty.denominator != 1 or p < 0 or (p == 0 and not recovery) or fee < 0:
        raise ContractError("INVALID_FILL_DOMAIN")
    closed = min(abs(oldq), qty) if oldq * signed_qty < 0 else F(0)
    opened = qty - closed
    realized = closed * (1 if oldq > 0 else -1) * (p - oldcost)
    direction = 1 if signed_qty > 0 else -1
    if signed_qty > 0:
        s["cash_set"] -= qty * p + fee
    else:
        s["cash_set"] -= fee
        if closed:
            s["cashlots"].append(
                {
                    "id": fill_id + ":long-sale",
                    "entry_id": None,
                    "kind": "FREE",
                    "amount": closed * p,
                    "settled": False,
                    "due": session + 1,
                }
            )
        if opened:
            s["cashlots"].append(
                {
                    "id": fill_id + ":short",
                    "entry_id": fill_id,
                    "kind": "SHORT",
                    "amount": opened * p,
                    "settled": False,
                    "due": session + 1,
                }
            )
    remaining = closed
    for lot in a["lots"]:
        if not remaining or lot["direction"] == direction or not lot["remaining"]:
            continue
        n = min(remaining, lot["remaining"])
        prior = lot["remaining"]
        allocated = {
            k: lot[k] * n / prior
            for k in ("entry_fee", "borrow", "long_dividend", "short_dividend")
        }
        for k, v in allocated.items():
            lot[k] -= v
        exit_fee = fee * n / qty
        net = (
            lot["direction"] * n * (p - lot["price"])
            - allocated["entry_fee"]
            - exit_fee
            - allocated["borrow"]
            + allocated["long_dividend"]
            - allocated["short_dividend"]
        )
        s["fragments"].append(
            {
                "entry_fill_id": lot["id"],
                "close_fill_id": fill_id,
                "security_id": sid,
                "quantity": n,
                "direction": lot["direction"],
                "entry_price": lot["price"],
                "exit_price": p,
                "entry_fee": allocated["entry_fee"],
                "exit_fee": exit_fee,
                "borrow": allocated["borrow"],
                "long_dividend": allocated["long_dividend"],
                "short_dividend": allocated["short_dividend"],
                "net": net,
            }
        )
        if lot["direction"] == -1:
            _release_short(s, lot["id"], n, prior)
        lot["remaining"] -= n
        remaining -= n
    if remaining:
        raise ContractError("FIFO_POSITION_MISMATCH")
    if opened:
        a["lots"].append(
            {
                "id": fill_id,
                "direction": direction,
                "remaining": opened,
                "price": p,
                "entry_fee": fee * opened / qty,
                "borrow": F(0),
                "long_dividend": F(0),
                "short_dividend": F(0),
                "at": at,
                "settles": session + 1,
            }
        )
    newq = oldq + signed_qty
    if not newq:
        newcost = F(0)
    elif not oldq or oldq * newq < 0:
        newcost = p
    elif oldq * signed_qty > 0:
        newcost = (abs(oldq) * oldcost + qty * p) / abs(newq)
    else:
        newcost = oldcost
    a.update(quantity=newq, cost=newcost)
    s["fees"] += fee
    key = "realized_long" if oldq > 0 else "realized_short"
    s[key] += realized
    lines = _cash_delta(before, cash_values(s))
    lines.update(
        positions_cost=newq * newcost - oldq * oldcost, **{key: -realized}, commission_expense=fee
    )
    _post(s, fill_id, "FILL", lines, {sid: signed_qty})
    record_valuation(s, sid, fill_id + ":valuation")
    legs = []
    for effect, quantity, exposure in (
        ("CLOSE", closed, "LONG" if oldq > 0 else "SHORT"),
        ("OPEN", opened, "LONG" if signed_qty > 0 else "SHORT"),
    ):
        if quantity:
            legs.append(
                {
                    "effect": effect,
                    "direction": exposure,
                    "quantity": quantity,
                    "signed_qty": direction * quantity,
                    "fee": fee * quantity / qty,
                    "realized_gross": realized if effect == "CLOSE" else F(0),
                }
            )
    fill = {
        "fill_id": fill_id,
        "security_id": sid,
        "signed_qty": signed_qty,
        "price": p,
        "fee": fee,
        "at": at,
        "raw_price": p if raw_price is None else raw_price,
        "slippage_cost": signed_qty * (p - (p if raw_price is None else raw_price)),
        "realized_gross": realized,
        "direction": legs[0]["direction"] if len(legs) == 1 else "MIXED",
        "execution_side": "BUY" if signed_qty > 0 else "SELL",
        "position_before": oldq,
        "position_after": newq,
        "position_legs": legs,
    }
    s["fills"].append(fill)
    return fill


def liquidate(s, *, event_id, sid, recovery_price, session, at):
    q = s["assets"][sid]["quantity"]
    if q:
        record = trade(
            s,
            fill_id=event_id,
            sid=sid,
            signed_qty=-q,
            p=recovery_price,
            fee=F(0),
            session=session,
            at=at,
            recovery=True,
        )
        s["fills"].pop()
        s["liquidations"].append({**record, "kind": "DECLARED_CORPORATE_CASH_RECOVERY"})
    s["assets"][sid].update(delisted=True, tradable=False, in_universe=False)


def settle(s, session, event_id):
    before = cash_values(s)
    for c in s["cashlots"]:
        if not c["settled"] and c["due"] <= session:
            c["settled"] = True
            s["cash_set"] += c["amount"]
    _post(s, event_id, "SETTLEMENT", _cash_delta(before, cash_values(s)))
    s["journal"][-1]["settlement_session"] = session


def accrue(s, event_id, sid, amount, *, kind, pay_at=None):
    a = s["assets"][sid]
    qty = abs(a["quantity"])
    if kind == "BORROW":
        s["cash_set"] -= amount
        s["borrow"] += amount
        pool = "borrow"
        _post(s, event_id, kind, {"cash_set": -amount, "borrow_expense": amount})
    else:
        if event_id in s["rights"]:
            raise ContractError("DUPLICATE_DIVIDEND")
        s["rights"][event_id] = {"amount": amount, "pay_at": pay_at, "security_id": sid}
        s["dividends"] += amount
        pool = "long_dividend" if amount >= 0 else "short_dividend"
        _post(
            s,
            event_id,
            kind,
            {"receivable" if amount >= 0 else "payable": amount, "dividend_income": -amount},
        )
    if qty:
        for lot in a["lots"]:
            if lot["remaining"]:
                lot[pool] += abs(amount) * lot["remaining"] / qty


def pay(s, action_id, event_id):
    if action_id not in s["rights"]:
        raise ContractError("DIVIDEND_RIGHT_NOT_FOUND")
    r = s["rights"].pop(action_id)
    s["cash_set"] += r["amount"]
    _post(
        s,
        event_id,
        "DIVIDEND_PAY",
        {"cash_set": r["amount"], "receivable" if r["amount"] >= 0 else "payable": -r["amount"]},
    )


def split(s, event_id, sid, ratio):
    a = s["assets"][sid]
    if (a["quantity"] * ratio).denominator != 1 or any(
        (lot["remaining"] * ratio).denominator != 1 for lot in a["lots"]
    ):
        raise ContractError("UNDEFINED_FRACTIONAL_SPLIT")
    old = a["quantity"]
    for o in s["orders"].values():
        if o["security_id"] == sid and o["status"] in LIVE:
            cancel(o, "CANCELLED", "CORPORATE_ACTION_REPLACE_REQUIRED")
    a["quantity"] *= ratio
    a["cost"] /= ratio
    a["mark"] /= ratio
    for lot in a["lots"]:
        lot["remaining"] *= ratio
        lot["price"] /= ratio
    _post(s, event_id, "SPLIT", {}, {sid: a["quantity"] - old})


def cancel(o, status, reason):
    remaining = o["remaining"]
    o["cancelled_qty" if status == "CANCELLED" else "expired_remaining"] += remaining
    o["remaining"] = F(0)
    o["signed_remaining"] = F(0)
    o["reserve_notional"] = F(0)
    transition(o, status, reason)


def borrow(s, event_id, sid):
    a = s["assets"][sid]
    amount = round_cent(max(-a["quantity"], 0) * a["mark"] / 25200)
    if amount:
        accrue(s, event_id, sid, amount, kind="BORROW")
    return amount


def assert_economic_identity(s):
    c = account(s)
    unrealized = sum((a["quantity"] * (a["mark"] - a["cost"]) for a in s["assets"].values()), F(0))
    pnl = (
        s["realized_long"]
        + s["realized_short"]
        + unrealized
        - s["fees"]
        - s["borrow"]
        + s["dividends"]
    )
    if c["equity"] - s["initial_cash"] - s["external_flows"] != pnl:
        raise ContractError("ECONOMIC_EQUITY_IDENTITY_FAILED")
    for sid, a in s["assets"].items():
        if a["quantity"] != sum((lot["direction"] * lot["remaining"] for lot in a["lots"]), F(0)):
            raise ContractError("LOT_QUANTITY_IDENTITY_FAILED", sid)
    return {"equity": c["equity"], "pnl": pnl, "unrealized": unrealized}


def reconcile(initial_cash, journal, assets):
    """Independent read side: raw debit/credit/quantity entries, never AccountState."""
    balances = {
        "cash_set": initial_cash,
        "U_free": F(0),
        "U_short": F(0),
        "receivable": F(0),
        "payable": F(0),
    }
    quantities = {sid: F(0) for sid in assets}
    for event in journal:
        totals = {}
        for e in event["entries"]:
            totals[e["unit"]] = totals.get(e["unit"], F(0)) + e["amount"]
            if e["unit"] == "CCY":
                balances[e["account"]] = balances.get(e["account"], F(0)) + e["amount"]
            elif e["account"] == "position_quantity":
                quantities[e["unit"]] += e["amount"]
        if any(totals.values()):
            raise ContractError("RAW_JOURNAL_UNBALANCED")
    return {
        "balances": balances,
        "quantities": quantities,
        "cash_total": sum(balances[k] for k in ("cash_set", "U_free", "U_short")),
    }


def readonly_snapshot(s):
    return deepcopy(
        {"account": account(s), "positions": s["assets"], "economic": assert_economic_identity(s)}
    )
