"""Six thin local engineering views over the shared application service."""

import json
import math
import os
import uuid
from decimal import Decimal, InvalidOperation

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import load
from aqrp.services.task_requests import catalogue
from aqrp.services.task_worker import start_worker
from aqrp.services.tasks import TaskService
from aqrp.ui.numbers import fixed_view

PAGES = [
    "Dashboard",
    "Factor Library",
    "Alpha Research",
    "Strategy Backtest",
    "Experiment Manager",
    "Settings",
]


def table(value):
    if isinstance(value, list) and value and isinstance(value[0], dict):
        frame = pd.json_normalize(value)
        st.dataframe(
            frame.map(
                lambda x: "N/A" if x is None or (isinstance(x, float) and math.isnan(x)) else str(x)
            ),
            width="stretch",
        )
    else:
        st.json(value)


def chart(xs, ys, title):
    values = []
    for x in ys:
        if x is None:
            values.append(None)
            continue
        try:
            d = Decimal(str(x))
            f = float(d)
            if not d.is_finite() or d.copy_abs() > 2**53 or (d and not f):
                st.warning("Chart precision unavailable; use the exact raw table/download.")
                return
            values.append(f)
        except (ValueError, InvalidOperation, OverflowError):
            st.warning("Chart precision unavailable; use the exact raw table/download.")
            return
    fig = go.Figure(
        go.Scatter(
            x=xs,
            y=values,
            mode="lines+markers",
            customdata=[
                [str(x), "N/A" if y is None else str(y)] for x, y in zip(xs, ys, strict=True)
            ],
            hovertemplate="%{customdata[0]}<br>raw=%{customdata[1]}<extra></extra>",
        )
    )
    fig.update_layout(title=title, height=300, margin=dict(l=12, r=12, t=45, b=12))
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Charts use approximate browser numbers. Raw tables and downloads retain original values; N/A retains its reason."
    )


def picker(service, key, *, success=False, rows=None):
    rows = service.list() if rows is None else rows
    if success:
        rows = [r for r in rows if r["status"] == "SUCCEEDED"]
    if not rows:
        st.info("No matching tasks yet.")
        return None
    labels = {r["task_id"]: r for r in rows}
    task = st.selectbox(
        "Task", list(labels), format_func=lambda t: t + " · " + labels[t]["status"], key=key
    )
    return labels[task]


def inspect_task(service, row, key):
    st.write("Task status: " + row["status"])
    st.code(row["task_id"], language=None)
    if row.get("error"):
        st.error(str(row["error"]))
    if row["status"] == "INTEGRITY_ERROR":
        st.error("Task integrity failed; verified results and downloads are unavailable.")
        return
    if st.button("Refresh task", key=key + "refresh"):
        st.rerun()
    if row["status"] in ("QUEUED", "RUNNING") and st.button("Cancel safely", key=key + "cancel"):
        st.info(service.cancel(row["task_id"]))
        st.rerun()
    st.caption("Cancellation is acknowledged at safe stage or atomic-transaction boundaries.")
    slots = row.get("slots", {})
    try:
        raw_log = service.worker_log(row["task_id"])
        st.download_button(
            "Download worker log prefix",
            raw_log,
            file_name="worker.log",
            mime="text/plain",
            key=key + "worker-download",
        )
    except FileNotFoundError:
        st.caption(
            "No subprocess worker log for this task; persistent task events remain available."
        )
    if not slots:
        return
    slot = st.selectbox("Child stage", list(slots), key=key + "slot")
    try:
        m = service.artifact_catalogue(row["task_id"], slot)
        name = st.selectbox(
            "Manifest artifact", [e["path"] for e in m["files"]], key=key + "artifact"
        )
        raw = service.artifact(row["task_id"], slot, name)
        st.download_button(
            "Download verified original",
            raw,
            file_name=slot.replace(":", "-") + "-" + name,
            mime="text/html" if name.endswith(".html") else "application/json",
            key=key + "download",
        )
        with st.expander("Verified original artifact"):
            if name.endswith(".json"):
                st.json(json.loads(raw))
            else:
                st.code(raw.decode(), language="html")
    except (ContractError, OSError, ValueError) as exc:
        st.info("Child artifact unavailable: " + getattr(exc, "code", type(exc).__name__))
    events = service.logs(row["task_id"])
    with st.expander("Task events (persistent)"):
        table(events)
    st.download_button(
        "Download task event prefix",
        json.dumps(events).encode(),
        file_name="task-events.json",
        mime="application/json",
        key=key + "event-download",
    )
    st.caption("Event download is a persistent log prefix, not a terminal financial result.")


def research_view(service, row):
    if row["status"] == "INTEGRITY_ERROR":
        return
    if "R" not in row.get("slots", {}):
        return
    try:
        metrics = json.loads(service.artifact(row["task_id"], "R", "metrics.json"))
        st.subheader("IC, Rank IC, ICIR and stratified returns")
        table(metrics["summaries"])
        daily = metrics["daily"]
        if daily:
            chart(
                [r["session"] for r in daily],
                [r["ic"]["value"] for r in daily],
                "Pearson IC by session / stage",
            )
        with st.expander("Rank IC and group returns by session"):
            table(daily)
        st.subheader("Horizon decay")
        table(metrics["decay"])
        for name, label in [
            ("oos.json", "Out-of-sample / walk-forward"),
            ("multiplicity.json", "Trials and multiple testing"),
            ("approvals.json", "Approval proposals — no financial approval"),
        ]:
            st.subheader(label)
            st.json(json.loads(service.artifact(row["task_id"], "R", name)))
        with st.expander("Raw / clean / standardized / neutralized / final"):
            stage = st.selectbox(
                "Research stage", ["raw", "clean", "standardized", "neutralized", "final"]
            )
            table(json.loads(service.artifact(row["task_id"], "R", stage + ".json")))
    except (ContractError, OSError, ValueError) as exc:
        st.info("Research results pending or invalid: " + getattr(exc, "code", type(exc).__name__))


def backtest_view(service, row):
    if "B" not in row.get("slots", {}):
        return
    if row["status"] == "INTEGRITY_ERROR":
        st.error("No trusted financial results for an invalid task.")
        return
    try:
        result = service.financial_result(row["task_id"])
        if result["status"] != "SUCCEEDED":
            st.error(
                "No verified complete financial result. "
                + str(result.get("committed_state_verification", {}))
            )
            st.json(
                {
                    k: v
                    for k, v in result.items()
                    if k not in ("account", "performance", "positions", "last_committed_account")
                }
            )
            return
        st.subheader("Verified account buckets")
        st.json(result["account"])
        performance = result["performance"]
        drawdown = performance["maximum_drawdown"]
        st.metric(
            "Maximum drawdown (core result)",
            fixed_view(str(drawdown["value"]), 4, multiply=100) + "%"
            if drawdown["value"] is not None
            else "N/A",
        )
        if drawdown["reason"]:
            st.caption(drawdown["reason"])
        nav = performance["flow_adjusted_nav"]
        chart(list(range(len(nav))), nav, "Flow-adjusted NAV · core result")
        for key in [
            "performance",
            "orders",
            "fills",
            "positions",
            "journal",
            "valuations",
            "reconciliation",
        ]:
            with st.expander(key.title()):
                table(result[key])
        with st.expander("Actual P4 source, target, risk and request lineage"):
            st.json(json.loads(service.artifact(row["task_id"], "B", "portfolio-lineage.json")))
    except (ContractError, OSError, ValueError, KeyError) as exc:
        st.error("Financial result unavailable: " + getattr(exc, "code", type(exc).__name__))


def submit_page(service, cat, pipeline):
    kind = "engineering_pipeline" if pipeline else "research"
    st.caption(
        "Synthetic engineering data · UTC decision timestamps and split/fit rules are preserved."
    )
    config = cat["config"]
    st.caption(
        "Select a trusted synthetic historical universe. Snapshot, membership and availability identities enter the immutable request. Parameters must belong to a preregistered campaign; all campaigns share the same data budget of 12 hypotheses. Failed and cancelled attempts consume budget."
    )
    defaults = json.loads(service.defaults()["payload"])
    selection = st.session_state.get("selected_factors", defaults.get("factor_ids", ["momentum"]))
    with st.form(kind + "-form"):
        factors = st.multiselect(
            "Factors", ["momentum", "reversal", "volume", "price_volume"], default=selection
        )
        start = st.text_input(
            "First decision session (YYYY-MM-DD)",
            value=defaults.get("start", config["decisions"][2]["session"]),
        )
        end = st.text_input(
            "Last decision session (YYYY-MM-DD)",
            value=defaults.get("end", config["decisions"][2]["session"]),
        )
        lookback = st.number_input(
            "Lookback sessions",
            min_value=1,
            max_value=20,
            value=defaults.get("lookback", 2),
            step=1,
        )
        horizons = st.text_input(
            "Prediction horizons (session counts)",
            value=",".join(map(str, defaults.get("horizons", [1, 2]))),
        )
        direction = st.selectbox(
            "Factor direction", [1, -1], index=0 if defaults.get("direction", 1) == 1 else 1
        )
        neutralize = st.checkbox(
            "Industry / size neutralization", value=defaults.get("neutralize", True)
        )
        universes = list(cat["universes"])
        universe = st.selectbox(
            "Stock universe",
            universes,
            index=universes.index(defaults.get("universe_id", "SYN_U")),
            key=kind + "-universe",
        )
        campaign_ids = ["engineering-default"] + [
            x["id"] for x in service.campaigns() if x["id"] != "engineering-default"
        ]
        campaign = st.selectbox(
            "Preregistered research campaign",
            campaign_ids,
            index=campaign_ids.index(defaults.get("campaign_id", "engineering-default")),
            key=kind + "-campaign",
        )
        weights = st.text_area(
            "Factor weights in percent — JSON decimal strings",
            value=json.dumps(defaults.get("weights_percent", {n: "100" for n in selection})),
        )
        if pipeline:
            cash = st.text_input(
                "Initial cash (exact decimal)", value=defaults.get("initial_cash", "1000")
            )
            budget = st.text_input(
                "Fee budget (exact decimal)", value=defaults.get("fee_budget", "10")
            )
            policy = st.text_area(
                "Portfolio policy overrides (existing schema)",
                value=json.dumps(defaults.get("policy", {"top_k": 1})),
            )
            constraints = st.text_area(
                "Risk overrides (existing schema)",
                value=json.dumps(defaults.get("constraints", {})),
            )
            st.caption(
                "Existing SYNTHETIC_EXECUTION_1 fees and event economics remain fixed. Empty decisions are refused; trades need not occur."
            )
        submit = st.form_submit_button(
            "Submit engineering pipeline" if pipeline else "Submit research"
        )
    if st.button("New experiment key", key=kind + "newkey"):
        st.session_state[kind + "key"] = str(uuid.uuid4())
    if submit:
        draft = {
            "kind": kind,
            "factor_ids": factors,
            "universe_id": universe,
            "campaign_id": campaign,
            "start": start,
            "end": end,
            "lookback": lookback,
            "horizons": [int(h.strip()) for h in horizons.split(",")],
            "neutralize": neutralize,
            "weights_percent": load(weights.encode()),
        }
        if direction != 1 or "direction" in defaults:
            draft["direction"] = direction
        if pipeline:
            draft.update(
                initial_cash=cash,
                fee_budget=budget,
                policy=load(policy.encode()),
                constraints=load(constraints.encode()),
            )
        frozen = service.freeze(draft)
        key = st.session_state.setdefault(kind + "key", str(uuid.uuid4()))
        receipt = service.submit(frozen, key)
        st.session_state[kind + "task"] = receipt["task_id"]
        worker = start_worker(service, receipt["task_id"])
        st.success("Task submitted: " + receipt["task_id"])
        st.caption(
            "Request hash: " + receipt["config_hash"] + " · " + worker["status"]
            if "status" in worker
            else "Request hash: " + receipt["config_hash"]
        )
    task = st.session_state.get(kind + "task")
    row = service.status(task) if task else picker(service, kind + "pick")
    if row:
        inspect_task(service, row, kind)
        research_view(service, row)
        if pipeline:
            backtest_view(service, row)


def main():
    st.set_page_config(page_title="AQRP Research", layout="wide")
    st.sidebar.title("AQRP")
    page = st.sidebar.radio("Workspace", PAGES, key="workspace-page")
    st.sidebar.caption("ENGINEERING TEST ONLY\nFinancial approval: NONE")
    st.title(page)
    st.caption("Alpha Quant Research Platform · local engineering workspace")
    service = TaskService(os.environ["AQRP_WORKSPACE"])
    try:
        cat = catalogue(service.root)
        if page == "Dashboard":
            rows = service.list()
            a, b, c = st.columns(3)
            a.metric("Engineering built-in factors", len(cat["factor_specs"]))
            b.metric("Tasks", len(rows))
            c.metric("Verified successful tasks", sum(r["status"] == "SUCCEEDED" for r in rows))
            table(
                [{k: r.get(k) for k in ("task_id", "status", "error", "config_hash")} for r in rows]
            )
            st.subheader("Recent actual runs")

            def open_run(task, pipeline):
                kind = "engineering_pipeline" if pipeline else "research"
                st.session_state[kind + "task"] = task
                st.session_state["workspace-page"] = (
                    "Strategy Backtest" if pipeline else "Alpha Research"
                )

            for row in rows[:10]:
                slots = row.get("slots", {})
                if "R" in slots:
                    st.button(
                        "Open research run " + slots["R"]["binding"]["child_run_id"],
                        key="open-R-" + row["task_id"],
                        on_click=open_run,
                        args=(row["task_id"], False),
                    )
                if "B" in slots:
                    st.button(
                        "Open backtest run " + slots["B"]["binding"]["child_run_id"],
                        key="open-B-" + row["task_id"],
                        on_click=open_run,
                        args=(row["task_id"], True),
                    )
            st.button("Refresh dashboard")
        elif page == "Factor Library":
            table(cat["factor_specs"])
            chosen = st.multiselect(
                "Selected factors",
                ["momentum", "reversal", "volume", "price_volume"],
                default=st.session_state.get("selected_factors", ["momentum"]),
            )
            if st.button("Apply selection to new forms"):
                st.session_state["selected_factors"] = chosen
                st.success("Selection saved for new drafts")
            st.caption(
                "Exact Ref and parameter identities remain pinned. Historical runs retain their original versions; configuration rollback does not approve code."
            )
            defaults = service.defaults()
            notice = st.session_state.pop("factor-defaults-notice", None)
            if notice:
                st.success(notice)
            if st.button("Save factor selection as a defaults revision"):
                patch = {
                    **load(defaults["payload"]),
                    "factor_ids": chosen,
                    "weights_percent": {n: "100" for n in chosen},
                }
                revision = service.save_defaults(defaults["revision"], patch)
                st.session_state["selected_factors"] = chosen
                st.session_state["factor-defaults-notice"] = (
                    "New defaults revision " + str(revision) + " saved"
                )
                st.rerun()
            if defaults["revision"]:
                revision = st.selectbox(
                    "Factor configuration rollback revision",
                    list(range(1, defaults["revision"] + 1)),
                )
                if st.button("Rollback factor configuration"):
                    new_revision = service.rollback_defaults(defaults["revision"], revision)
                    restored = load(service.defaults(new_revision)["payload"])
                    st.session_state["selected_factors"] = restored.get("factor_ids", ["momentum"])
                    st.session_state["factor-defaults-notice"] = "New revision " + str(new_revision)
                    st.rerun()
            rows = service.list()
            if len(rows) > 1:
                first = st.selectbox("Compare version / parameters A", [r["task_id"] for r in rows])
                second = st.selectbox(
                    "Compare version / parameters B", [r["task_id"] for r in rows], index=1
                )
                if st.button("Compare frozen factor configurations"):
                    st.json(
                        {
                            "A": service.request(first),
                            "B": service.request(second),
                        }
                    )
            if rows:
                row = picker(service, "factorhistory")
                if row:
                    st.json(service.request(row["task_id"])["payload"])
            if (service.root / "history.json").exists():
                from aqrp.services.task_history import history_catalogue

                history = history_catalogue(service.root)
                st.subheader("Registered historical factor artifacts")
                st.caption(history["scope"] + " · full historical host NOT VERIFIED")
                publication = __import__("pathlib").Path(history["publication_root"])
                old = [
                    json.loads(p.read_bytes())["spec"]
                    for p in sorted((publication / "sdk/factor-runs").glob("*/config.json"))
                ]
                table(old)
        elif page == "Alpha Research":
            submit_page(service, cat, False)
        elif page == "Strategy Backtest":
            st.info(
                "Engineering simulation only. Formal strategy approval and formal Test remain unavailable."
            )
            if st.button("Check formal-entry gate"):
                try:
                    service.freeze({"kind": "formal"})
                except ContractError as exc:
                    st.error(exc.code)
            submit_page(service, cat, True)
        elif page == "Experiment Manager":
            st.subheader("Preregister research variants before observing results")
            st.caption(
                "A plan freezes its complete variant set and multiplicity definitions. New plans retain prior data access and share budget12; creating a new name cannot reset the budget. The first-use default freezes current parameters, four single factors, horizons1/1,2 and the three synthetic pools once. Later edits outside that set are refused."
            )
            with st.form("campaign-registration"):
                campaign_name = st.text_input(
                    "New immutable campaign ID", value="engineering-study"
                )
                variants = st.text_area(
                    "Preregistered variant drafts (JSON list)",
                    value='[{"factor_ids":["momentum"],"lookback":2,"horizons":[1]}]',
                )
                register = st.form_submit_button("Freeze research campaign")
            if register:
                plan = service.register_campaign(campaign_name, load(variants.encode()))
                st.success("Campaign frozen: " + plan["id"] + " · " + plan["campaign_hash"])
            with st.expander("Immutable campaigns / variants / prior data access"):
                st.json(service.campaigns())
            if (service.root / "history.json").exists() and st.button(
                "Replay registered original factor artifacts"
            ):
                receipt = service.submit(
                    service.freeze(
                        {
                            "kind": "replay",
                            "profile": "PUBLISHED_REF_PROJECTION",
                            "source_task": "published-original",
                        }
                    ),
                    "old-ref-" + str(uuid.uuid4()),
                )
                start_worker(service, receipt["task_id"])
                st.success("Historical replay task: " + receipt["task_id"])
            query = st.text_input("Task / run ID contains")
            statuses = st.multiselect(
                "Task states",
                ["QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "INTEGRITY_ERROR"],
            )
            rows = [
                r
                for r in service.list()
                if (not statuses or r["status"] in statuses)
                and (
                    not query
                    or query in r["task_id"]
                    or any(
                        query in x["binding"]["child_run_id"] for x in r.get("slots", {}).values()
                    )
                )
            ]
            row = picker(service, "experiments", rows=rows)
            if row:
                inspect_task(service, row, "exp")
                if row["status"] == "SUCCEEDED":
                    other = st.selectbox(
                        "Compare with task",
                        [r["task_id"] for r in service.list() if r["status"] == "SUCCEEDED"],
                    )
                    if st.button("Compare declared results"):
                        st.json(service.compare(row["task_id"], other))
                    if "backtest_run_id" in row.get("result", {}) and st.button(
                        "Replay verified P5 result"
                    ):
                        replay = service.submit(
                            service.freeze({"kind": "replay", "source_task": row["task_id"]}),
                            "ui-replay-" + str(uuid.uuid4()),
                        )
                        start_worker(service, replay["task_id"])
                        st.success("Replay task: " + replay["task_id"])
                with st.expander("Immutable effective request / versions / parameters"):
                    st.json(service.request(row["task_id"]))
        else:
            st.subheader("Default configuration revisions")
            defaults = service.defaults()
            editor_key = "settings-defaults-editor"
            base_key = "settings-defaults-editor-base"
            pending = st.session_state.pop("settings-defaults-pending", None)
            if pending is not None or base_key not in st.session_state:
                snapshot = pending if pending is not None else defaults
                st.session_state[base_key] = snapshot["revision"]
                st.session_state[editor_key] = snapshot["payload"]
            if st.button("Reload latest defaults"):
                st.session_state[base_key] = defaults["revision"]
                st.session_state[editor_key] = defaults["payload"]
            base = st.session_state[base_key]
            st.write("Current revision", defaults["revision"])
            st.write("Editor base revision", base)
            notice = st.session_state.pop("settings-defaults-notice", None)
            if notice:
                st.success(notice)
            if base != defaults["revision"]:
                st.warning(
                    "Defaults changed after this editor was loaded. Reload latest defaults before saving; unsaved text is retained."
                )
            payload = st.text_area("Defaults JSON (new requests only)", key=editor_key)
            if st.button("Save defaults revision"):
                revision = service.save_defaults(base, load(payload.encode()))
                st.session_state["settings-defaults-pending"] = service.defaults(revision)
                st.session_state["settings-defaults-notice"] = "Saved revision " + str(revision)
                st.rerun()
            if defaults["revision"]:
                target = st.selectbox(
                    "Rollback target revision", list(range(1, defaults["revision"] + 1))
                )
                if st.button("Rollback by adding a revision"):
                    revision = service.rollback_defaults(base, target)
                    st.session_state["settings-defaults-pending"] = service.defaults(revision)
                    st.session_state["settings-defaults-notice"] = "New revision " + str(revision)
                    st.rerun()
            with st.expander("Synthetic input catalogue / core and UI environment"):
                st.json(
                    {
                        k: cat[k]
                        for k in [
                            "revision",
                            "scope",
                            "financial_approval",
                            "snapshot",
                            "exposures",
                            "core_environment",
                            "ui_environment",
                        ]
                    }
                )
            st.caption("No credentials or account/ACL/service/scheduler settings are stored here.")
    except (ContractError, OSError, ValueError, TypeError, KeyError) as exc:
        st.error(getattr(exc, "code", type(exc).__name__))


main()
