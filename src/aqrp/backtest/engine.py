"""BT-001–010: deterministic envelope scheduler and atomic per-order matching."""

import heapq
import uuid
from copy import deepcopy
from datetime import timedelta

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.execution.liquidity import visible_adv
from aqrp.execution.model import (
    LIVE,
    bounds,
    commission,
    execute_price,
    fee_upper,
    fill_quantity,
    transition,
)
from aqrp.portfolio.construct import build_candidate
from aqrp.portfolio.contracts import PortfolioRequest, load, prepare, serialized_number
from aqrp.portfolio.service import construct_engineering
from aqrp.risk.checks import assess as p4_assess

from .contracts import timestamp
from .exact import F, freeze, money, p4_input, thaw
from .ledger import (
    _post,
    account,
    accrue,
    assert_economic_identity,
    borrow,
    cancel,
    initial_state,
    liquidate,
    pay,
    readonly_snapshot,
    record_valuation,
    sellable,
    settle,
    split,
    trade,
)
from .provider import SignalProvider, adapt_portfolio, signal_identity, verify_portfolio_result
from .risk import assess
from .transactions import TransactionStore


class Simulator:
    def __init__(self, config, root, code_commit, *, fault=None):
        self.config = config
        self.namespace = uuid.UUID(config["request_id"])
        self.root = root
        self.code_commit = code_commit
        self.fault = fault
        self.store = TransactionStore(
            root / "transactions", initial_state(money(config["initial_cash"]), config["assets"])
        )
        # Recover by deterministic re-execution against immutable committed prefixes.
        # Existing commands are compared, not applied a second time or recomputed from the final state.
        self.store.state = deepcopy(self.store.initial)
        self.logical_version = 0
        self.provider = SignalProvider(config["decisions"])
        self.queue = []
        self.seq = 0
        self.trace = []
        self.portfolios = []
        self.decisions = {}
        self.current_key = None
        self.session_ids = {s["session_id"]: i for i, s in enumerate(config["sessions"])}
        self._schedule()

    def uid(self, text):
        return str(uuid.uuid5(self.namespace, text))

    def enqueue(self, at, phase, kind, data):
        at = utc(at)
        if self.current_key is not None and (at, phase) < self.current_key[:2]:
            raise ContractError("EVENT_INSERTION_BEFORE_CURRENT_PHASE")
        self.seq += 1
        heapq.heappush(self.queue, (at, phase, self.seq, kind, data))

    def _schedule(self):
        for i, s in enumerate(self.config["sessions"]):
            self.enqueue(s["open"], 10, "SETTLEMENT", {"session": i})
            for kind in ("OPEN", "CLOSE"):
                rows = [
                    r
                    for r in self.config["sidecar"]["rows"]
                    if r["session_id"] == s["session_id"] and r["kind"] == kind
                ]
                on_time = [
                    r
                    for r in rows
                    if utc(r["available_at"]) == utc(r["event_time"])
                    and utc(r["known_at"]) <= utc(r["event_time"])
                ]
                self.enqueue(
                    s[kind.lower()], 20, "MARKET", {"session": i, "kind": kind, "rows": on_time}
                )
                for r in rows:
                    if r not in on_time:
                        self.enqueue(
                            max(utc(r["available_at"]), utc(r["known_at"])), 20, "LATE_SLICE", r
                        )
            self.enqueue(s["close"], 65, "EXPIRY", {"session": i})
            self.enqueue(s["close"], 95, "BORROW", {"session": i})
            self.enqueue(s["close"], 100, "VALUATION", {"session": i})
            self.enqueue(s["open"], 100, "OPEN_VALUATION", {"session": i})
        for index, d in enumerate(self.config["decisions"]):
            at = load(d["portfolio_request_utf8"])["context"]["decision_time"]
            self.enqueue(at, 30, "SIGNAL", {"index": index, "decision": d})
        scheduled_actions = []
        priorities = {"SPLIT": 1, "DIVIDEND": 2, "DELIST": 4}
        end = utc(self.config["sessions"][-1]["close"])
        for a in self.config["actions"]:
            if utc(a["available_at"]) > utc(a["effective_at"]):
                scheduled_actions.append((utc(a["available_at"]), 0, "LATE_ACTION", a))
            else:
                scheduled_actions.append(
                    (utc(a["effective_at"]), priorities[a["kind"]], a["kind"], a)
                )
                if a["kind"] == "DIVIDEND":
                    scheduled_actions.append((utc(a["pay_at"]), 3, "DIVIDEND_PAY", a))
        for at, _, kind, a in sorted(
            scheduled_actions, key=lambda v: (v[0], v[1], v[3]["action_id"])
        ):
            if at <= end:
                self.enqueue(at, 10, kind, a)
        for f in self.config["cashflows"]:
            self.enqueue(f["at"], 10, "CASHFLOW", f)
        for c in self.config["cancellations"]:
            received = utc(c["received_at"])
            # A control delivered during70 cannot back-insert65; acknowledgement next UTCus.
            during_match = c["received_phase"] > 65
            ack = received + timedelta(microseconds=1) if during_match else received
            self.enqueue(
                ack,
                65,
                "CANCELLATION",
                {**c, "ack_at": timestamp(ack), "deferred_during_match": during_match},
            )

    def _observe(self, kind, payload):
        self.trace.append(
            {
                "dispatch_key": [timestamp(self.current_key[0]), *self.current_key[1:]],
                "kind": kind,
                "read_version": self.logical_version,
                "payload": freeze(payload),
            }
        )

    def _commit(self, kind, payload, operation, *, key=None):
        expected_hash = digest(freeze(self.store.state))
        post = deepcopy(self.store.state)
        children = operation(post)
        assert_economic_identity(post)
        if post == self.store.state:
            self._observe(kind, {"unchanged": True, "children": children})
            return None

        def apply(s):
            if digest(freeze(s)) != expected_hash:
                raise ContractError("STALE_TRANSACTION_PRESTATE")
            s.clear()
            s.update(deepcopy(post))
            return children

        event_key = key or self.uid(kind + ":" + str(self.current_key))
        dispatch = [timestamp(self.current_key[0]), *self.current_key[1:]]
        item = self.store.commit(event_key, payload, dispatch, apply, fault=self.fault)
        if (
            item["pre_hash"] != expected_hash
            or item["post_hash"] != digest(freeze(post))
            or item["children"] != [{"child_seq": i, **freeze(v)} for i, v in enumerate(children)]
            or item["commit_seq"] != self.logical_version + 1
        ):
            raise ContractError("RECOVERY_NONDETERMINISTIC_TRANSACTION")
        self.logical_version += 1
        self.store.state = thaw(item["post_state"])
        self._observe(kind, {"commit_seq": item["commit_seq"], "sha256": item["sha256"]})
        return item

    def run(self):
        while self.queue:
            at, phase, seq, kind, payload = heapq.heappop(self.queue)
            self.current_key = (at, phase, seq)
            self._dispatch(kind, payload)
        return self.store.state

    def _dispatch(self, kind, d):
        if kind == "SETTLEMENT":

            def apply(s):
                s["session"] = d["session"]
                settle(s, d["session"], self.uid("settle:" + str(d["session"])))
                return [{"kind": "AccountUpdated", "local_stage": 90}]

            self._commit(kind, d, apply)
        elif kind == "MARKET":
            self._market(d)
        elif kind == "LATE_SLICE":
            self._observe(kind, d)
        elif kind == "RISK":
            self._risk_portfolio(d["index"])
        elif kind == "LATE_ACTION":
            raise ContractError("DATA_REVISION_REQUIRES_RERUN")
        elif kind == "SIGNAL":
            request = self.provider.release(self.current_key[0])
            self.decisions[d["index"]] = {"original": request, "configuration": d["decision"]}
            self._observe(
                kind,
                {
                    "request_sha256": request.content_hash,
                    "signal_identity": signal_identity(request),
                },
            )
            self.enqueue(self.current_key[0], 40, "PORTFOLIO", {"index": d["index"]})
        elif kind == "PORTFOLIO":
            self._portfolio(d["index"])
        elif kind == "SUBMISSION":
            self._submit(d["index"])
        elif kind == "MATCH":
            self._match(d)
        elif kind in ("EXPIRY", "CANCELLATION"):
            self._cancel(kind, d)
        elif kind == "BORROW":
            self._borrow(d)
        elif kind == "VALUATION":
            self._valuation(d)
        elif kind == "OPEN_VALUATION":
            self._observe(kind, readonly_snapshot(self.store.state))
        elif kind == "CASHFLOW":
            self._flow(d)
        else:
            self._action(kind, d)

    def _market(self, d):
        def apply(s):
            for r in d["rows"]:
                a = s["assets"][r["security_id"]]
                if a["delisted"] and r["tradable"]:
                    raise ContractError("DELISTED_SECURITY_REACTIVATION")
                if r["status"] == "DELISTED" and a["quantity"]:
                    raise ContractError("UNRESOLVED_DELISTING")
                a.update(
                    tradable=r["tradable"],
                    in_universe=r["in_universe"],
                    short_permission=r["short_permission"],
                    borrow_limit=money(r["borrow_limit"]),
                    industry=r["industry"],
                    beta=money(r["beta"]),
                )
                if r["price"] is not None:
                    a.update(
                        mark=money(r["price"]), last_mark_session=d["session"], mark_ref=deepcopy(r)
                    )
                    record_valuation(s, r["security_id"], r["slice_id"] + ":valuation")
                if d["kind"] == "OPEN":
                    history = visible_adv(self.config, r["security_id"], self.current_key[0])
                    s["capacity"][r["slice_id"]] = (
                        min(F(10), history["average"]) if history["passed"] else F(0)
                    )
            return [{"kind": "MarketConfirmed", "local_stage": 20}]

        self._commit("MARKET", d, apply)
        if account(self.store.state)["available"] < 0:
            raise ContractError("MARGIN_BREACH")
        if d["kind"] == "OPEN":
            rows = {r["security_id"]: r for r in d["rows"]}
            orders = sorted(
                self.store.state["orders"].values(),
                key=lambda o: (utc(o["submitted_at"]), o["order_id"]),
            )
            for o in orders:
                if (
                    o["status"] in LIVE
                    and utc(o["eligible_at"]) <= self.current_key[0]
                    and o["security_id"] in rows
                ):
                    self.enqueue(
                        self.current_key[0],
                        70,
                        "MATCH",
                        {"order_id": o["order_id"], "slice": rows[o["security_id"]]},
                    )

    def _portfolio(self, index):
        dec = self.decisions[index]
        budget_id = self.uid("decision:" + str(index))

        def apply(s):
            if any(o["status"] in LIVE for o in s["orders"].values()):
                raise ContractError("REBALANCE_PENDING_ORDERS")
            s["budgets"][budget_id] = {
                "total": money(self.config["fee_budget"]),
                "paid": F(0),
                "turnover_notional": F(0),
                "decision_equity": account(s)["equity"],
            }
            s["current_budget"] = budget_id
            return [{"kind": "CommissionBudgetRegistered", "local_stage": 40}]

        self._commit("BUDGET", {"index": index}, apply)
        request, projection = adapt_portfolio(dec["original"], self.store.state)
        candidate = build_candidate(request)
        dec.update(request=request, budget_id=budget_id, projection=projection)
        self._observe(
            "PORTFOLIO_DECISION",
            {
                "index": index,
                "request_hash": request.content_hash,
                "candidate": load(candidate.raw),
                "projection": projection,
            },
        )
        self.enqueue(self.current_key[0], 50, "RISK", {"index": index})

    def _risk_portfolio(self, index):
        dec = self.decisions[index]
        request, projection = dec["request"], dec["projection"]
        result = construct_engineering(
            request, self.root / "portfolio-runs", self.code_commit
        ).read()
        verify_portfolio_result(request, result, self.root / "portfolio-runs")
        dec["result"] = result
        self.portfolios.append(
            {
                "index": index,
                "request_utf8": request.raw.decode("utf-8"),
                "projection": freeze(projection),
                "result": result,
            }
        )
        self._observe(
            "RISK",
            {
                "index": index,
                "status": result["status"],
                "actual_P4_run_id": result["run_id"],
                "projection": projection,
            },
        )
        if result["status"] == "SUCCEEDED":
            self.enqueue(self.current_key[0], 60, "SUBMISSION", {"index": index})

    def _submit(self, index):
        dec = self.decisions[index]
        cfg = dec["configuration"]
        verify_portfolio_result(dec["request"], dec["result"], self.root / "portfolio-runs")
        submitted = self.current_key[0]
        eligible = next(
            (i for i, v in enumerate(self.config["sessions"]) if utc(v["open"]) > submitted), None
        )
        if eligible is None:
            self._observe(
                "SUBMISSION_REJECTED", {"reason": "NO_FUTURE_EXECUTION_SESSION", "index": index}
            )
            return
        expires = (
            eligible if cfg["time_in_force"] == "DAY" else self.session_ids[cfg["expires_session"]]
        )
        if expires < eligible:
            raise ContractError("EXPIRY_BEFORE_ELIGIBILITY")
        request_x = load(dec["request"].raw)

        def apply(s):
            orders = []
            for sid, delta in sorted(dec["result"]["target"]["deltas"].items()):
                signed = serialized_number(delta)
                if not signed:
                    continue
                a = s["assets"][sid]
                oid = self.uid(f"order:{index}:{sid}")
                low, high = bounds(
                    a["mark"],
                    "BUY" if signed > 0 else "SELL",
                    cfg["order_type"],
                    money(cfg["limit_prices"][sid]) if cfg["order_type"] == "LIMIT" else None,
                )
                q = abs(signed)
                short_increase = max(-(a["quantity"] + signed), 0) - max(-a["quantity"], 0)
                reserve = q * high if signed > 0 else max(short_increase, 0) * high
                o = {
                    "order_id": oid,
                    "security_id": sid,
                    "original_qty": q,
                    "filled_qty": F(0),
                    "cancelled_qty": F(0),
                    "expired_remaining": F(0),
                    "remaining": q,
                    "signed_remaining": signed,
                    "side": "BUY" if signed > 0 else "SELL",
                    "kind": cfg["order_type"],
                    "time_in_force": cfg["time_in_force"],
                    "submitted_at": timestamp(submitted),
                    "eligible_at": timestamp(self.config["sessions"][eligible]["open"]),
                    "expires_session": expires,
                    "low": low,
                    "high": high,
                    "lot": a["lot"],
                    "reserve_notional": reserve,
                    "budget_id": dec["budget_id"],
                    "constraints": request_x["constraints"],
                    "P4_request_utf8": dec["request"].raw.decode("utf-8"),
                    "P4_request_sha256": dec["request"].content_hash,
                    "P4_risk_sha256": dec["result"]["risk"]["content_sha256"],
                    "P4_target_sha256": dec["result"]["target"]["content_sha256"],
                    "decision_time": request_x["context"]["decision_time"],
                    "reference_price": a["mark"],
                    "submission_liquidity": visible_adv(self.config, sid, submitted),
                    "limit_price": money(cfg["limit_prices"][sid])
                    if cfg["order_type"] == "LIMIT"
                    else None,
                    "status": "CREATED",
                    "history": [{"status": "CREATED", "reason": None}],
                }
                if (signed / a["lot"]).denominator != 1 and signed != -a["quantity"]:
                    raise ContractError("DELTA_LOT_MISMATCH")
                transition(o, "SUBMITTED")
                s["orders"][oid] = o
                orders.append(oid)
            c = account(s)
            new_n = sum((s["orders"][oid]["reserve_notional"] for oid in orders), F(0))
            new_f = sum(
                (
                    fee_upper(s["orders"][oid]["remaining"], s["orders"][oid]["high"])
                    for oid in orders
                ),
                F(0),
            )
            liquidity_passed = all(
                s["orders"][oid]["submission_liquidity"]["passed"] for oid in orders
            )
            accepted = (
                liquidity_passed and c["F_unused"] >= new_f and c["available"] >= new_n + new_f
            )
            for oid in orders:
                transition(
                    s["orders"][oid],
                    "ACCEPTED" if accepted else "REJECTED",
                    None
                    if accepted
                    else "ADV_HISTORY_OR_THRESHOLD_REJECTED"
                    if not liquidity_passed
                    else "ORDER_BASKET_BUDGET_OR_CASH_EXCEEDED",
                )
                if not accepted:
                    s["orders"][oid]["reserve_notional"] = F(0)
            return [
                {
                    "kind": "OrdersAccepted" if accepted else "OrdersRejected",
                    "local_stage": 60,
                    "order_ids": orders,
                }
            ]

        self._commit(
            "SUBMISSION", {"index": index, "P4_request_hash": dec["request"].content_hash}, apply
        )

    def _p4_post(self, post, before, order):
        x, maps, _, _ = prepare(PortfolioRequest(order["P4_request_utf8"].encode()))
        x = deepcopy(x)
        c = account(post)
        x["inputs"]["account"]["data"].update(
            equity=p4_input(c["equity_alloc"]),
            total_cash=p4_input(c["cash_alloc"]),
            nonshort_restriction=p4_input(c["P4_nonshort"]),
        )
        for sid, a in post["assets"].items():
            maps["prices"][sid].update(price=p4_input(a["mark"]), lot=p4_input(a["lot"]))
            maps["status"][sid].update(tradable=a["tradable"], in_universe=a["in_universe"])
            maps["exposures"][sid].update(industry=a["industry"], beta=p4_input(a["beta"]))
            maps["permissions"][sid].update(
                short_permission=a["short_permission"],
                borrow_limit_total=p4_input(a["borrow_limit"]),
                sellable_qty=p4_input(sellable(before["assets"][sid], post["session"])),
            )
        if c["equity_alloc"] <= 0 or c["cash_alloc"] < 0:
            return {"passed": False, "reason": "INFEASIBLE_P4_BUDGET_PROJECTION"}
        return p4_assess(
            x,
            maps,
            {k: a["quantity"] for k, a in before["assets"].items()},
            {k: a["quantity"] for k, a in post["assets"].items()},
            post=True,
        )

    def _match(self, d):
        before = self.store.state
        order = before["orders"][d["order_id"]]
        r = d["slice"]
        if order["status"] not in LIVE:
            self._observe("MATCH_TERMINAL_ORDER_REFUSED", d)
            return
        for decision in self.decisions.values():
            if (
                decision.get("request") is not None
                and decision["request"].raw.decode("utf-8") == order["P4_request_utf8"]
            ):
                verify_portfolio_result(
                    decision["request"], decision["result"], self.root / "portfolio-runs"
                )
        if r["price"] is None or not r["tradable"]:
            self._observe("MATCH_NOT_TRADABLE", d)
            return
        liquidity = visible_adv(self.config, order["security_id"], self.current_key[0])
        if not liquidity["passed"]:
            self._observe("MATCH_SKIPPED_LIQUIDITY", liquidity)
            return
        actual = execute_price(order, money(r["price"]))
        if actual is None:
            self._observe("MATCH_SKIPPED_PRICE_DOMAIN", d)
            return
        n = fill_quantity(
            order, before["capacity"][r["slice_id"]], before["assets"][r["security_id"]]["quantity"]
        )
        if not n:
            self._observe("MATCH_NO_CAPACITY_LOT", d)
            return
        signed = n if order["side"] == "BUY" else -n
        fee = commission(n, actual)
        fill_id = self.uid("fill:" + order["order_id"] + ":" + r["slice_id"])
        post = deepcopy(before)
        o = post["orders"][order["order_id"]]
        old_remaining = o["remaining"]
        o["remaining"] -= n
        o["signed_remaining"] -= signed
        o["filled_qty"] += n
        o["reserve_notional"] *= o["remaining"] / old_remaining
        transition(o, "FILLED" if o["remaining"] == 0 else "PARTIALLY_FILLED")
        b = post["budgets"][o["budget_id"]]
        b["paid"] += fee
        b["turnover_notional"] += n * actual
        fill = trade(
            post,
            fill_id=fill_id,
            sid=o["security_id"],
            signed_qty=signed,
            p=actual,
            fee=fee,
            session=post["session"],
            at=timestamp(self.current_key[0]),
            raw_price=money(r["price"]),
        )
        post["capacity"][r["slice_id"]] -= n
        financial = assess(
            post,
            o["constraints"],
            sid=o["security_id"],
            signed_qty=signed,
            before=before,
            turnover=b["turnover_notional"] / b["decision_equity"],
        )
        conservative = self._p4_post(post, before, o)
        if not financial["passed"] or not conservative["passed"]:

            def reject(s):
                cancel(s["orders"][order["order_id"]], "CANCELLED", "RISK_RECHECK_FAILED")
                return [
                    {
                        "kind": "RiskRejected",
                        "local_stage": 70,
                        "actual": financial,
                        "P4_budget": conservative,
                    }
                ]

            self._commit("MATCH_RISK_CANCELLED", d, reject)
            return

        def apply(s):
            s.clear()
            s.update(post)
            return [
                {"kind": "Fill", "local_stage": 80, "fill": fill},
                {
                    "kind": "AccountUpdated",
                    "local_stage": 90,
                    "account": account(s),
                    "actual_risk": financial,
                    "P4_budget_risk": conservative,
                },
            ]

        self._commit("MATCH", d, apply, key=fill_id)

    def _cancel(self, kind, d):
        if kind == "CANCELLATION" and utc(d["available_at"]) < utc(d["received_at"]):
            raise ContractError("STALE_CANCELLATION_TIME")

        def apply(s):
            if kind == "CANCELLATION":
                if d["order_id"] not in s["orders"]:
                    raise ContractError("UNKNOWN_CANCELLATION_ORDER")
                orders = [s["orders"][d["order_id"]]]
            else:
                orders = [o for o in s["orders"].values() if o["expires_session"] <= d["session"]]
            changed = []
            for o in orders:
                if o["status"] in LIVE:
                    cancel(o, "CANCELLED" if kind == "CANCELLATION" else "EXPIRED", kind)
                    changed.append(o["order_id"])
            return [{"kind": kind, "local_stage": 65, "order_ids": changed, "control": d}]

        self._commit(kind, d, apply)

    def _borrow(self, d):
        def apply(s):
            total = F(0)
            for sid in s["assets"]:
                total += borrow(s, self.uid(f"borrow:{d['session']}:{sid}"), sid)
            return [{"kind": "Borrow", "local_stage": 95, "fee": total}]

        self._commit("BORROW", d, apply)
        if account(self.store.state)["available"] < 0:
            raise ContractError("BORROW_OR_MARGIN_BREACH")

    def _valuation(self, d):
        for a in self.store.state["assets"].values():
            if a["quantity"] and (not a["mark"] or d["session"] - a["last_mark_session"] > 1):
                raise ContractError("STALE_POSITION_MARK")

        def apply(s):
            s["close_quantities"] = {sid: a["quantity"] for sid, a in s["assets"].items()}
            s["valuations"].append(
                {
                    "kind": "SESSION_CLOSE",
                    "session": d["session"],
                    "at": timestamp(self.current_key[0]),
                    **readonly_snapshot(s),
                }
            )
            return [{"kind": "Valuation", "local_stage": 100, "account": account(s)}]

        self._commit("VALUATION", d, apply)

    def _flow(self, d):
        def apply(s):
            before = account(s)["equity"]
            amount = money(d["amount"])
            s["cash_set"] += amount
            s["external_flows"] += amount
            _post(
                s, d["flow_id"], "EXTERNAL_FLOW", {"cash_set": amount, "external_capital": -amount}
            )
            s["valuations"].append(
                {
                    "kind": "EXTERNAL_FLOW",
                    "at": timestamp(self.current_key[0]),
                    "before_equity": before,
                    "amount": amount,
                    **readonly_snapshot(s),
                }
            )
            return [{"kind": "ExternalFlow", "local_stage": 10}]

        self._commit("CASHFLOW", d, apply, key=d["flow_id"])
        if account(self.store.state)["available"] < 0:
            raise ContractError("EXTERNAL_WITHDRAWAL_EXCEEDS_AVAILABLE")

    def _action(self, kind, d):
        sid = d["security_id"]

        def apply(s):
            if kind == "SPLIT":
                split(s, d["action_id"], sid, money(d["value"]))
            elif kind == "DIVIDEND":
                q = (
                    s["close_quantities"].get(sid, F(0))
                    if d["unit"] == "PER_OLD_SHARE"
                    else s["assets"][sid]["quantity"]
                )
                accrue(
                    s,
                    d["action_id"],
                    sid,
                    q * money(d["value"]),
                    kind="DIVIDEND_EX",
                    pay_at=d["pay_at"],
                )
            elif kind == "DIVIDEND_PAY":
                pay(s, d["action_id"], self.uid("pay:" + d["action_id"]))
            elif kind == "DELIST":
                for o in s["orders"].values():
                    if o["security_id"] == sid and o["status"] in LIVE:
                        cancel(o, "CANCELLED", "DELIST_LIQUIDATION")
                liquidate(
                    s,
                    event_id=d["action_id"],
                    sid=sid,
                    recovery_price=money(d["value"]),
                    session=s["session"],
                    at=timestamp(self.current_key[0]),
                )
            else:
                raise ContractError("UNKNOWN_SIMULATION_EVENT")
            return [{"kind": kind, "local_stage": 10, "action_id": d["action_id"]}]

        self._commit(kind, d, apply)
        if account(self.store.state)["available"] < 0:
            raise ContractError("ACTION_OR_MARGIN_BREACH")
