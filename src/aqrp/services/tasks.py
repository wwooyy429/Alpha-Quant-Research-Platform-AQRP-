"""Restricted real-core task orchestration shared by SDK, task CLI and Streamlit."""

import hashlib
import json
import re
from copy import deepcopy

from aqrp.backtest.contracts import EngineeringBacktestRequest, validate
from aqrp.backtest.synthetic import seal_sidecar
from aqrp.backtest.transactions import TransactionStore, guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.experiments.ledger import ExperimentLedger, immutable_write, read_chain
from aqrp.portfolio.contracts import load
from aqrp.portfolio.research_input import bind_research
from aqrp.services.backtest import (
    projection,
    replay_engineering,
    result_engineering,
    resume_engineering,
    simulate_engineering,
)
from aqrp.services.research import research
from aqrp.services.task_context import authority
from aqrp.services.task_inputs import execution_requests
from aqrp.services.task_requests import (
    EffectiveRequest,
    build_research_config,
    catalogue,
    execution_selection,
    freeze_request,
    references,
    research_request,
    validate_defaults,
    validate_draft,
)
from aqrp.services.task_state import TERMINAL, TaskState


def read_core(binding):
    """Read-only terminal proof including original bytes and pre-call initial binding."""
    root = guard_path(binding["physical_ledger_root"])
    run = binding["child_run_id"]
    ledger = ExperimentLedger(root)
    m = ledger.verify(run)
    directory = guard_path(ledger.path(run))
    entries = {e["path"]: e for e in m["files"]}
    if len(entries) != len(m["files"]):
        raise ContractError("TASK_DUPLICATE_MANIFEST_MEMBER")
    required = {"config.json", "lineage.json"}
    if m["status"] == "SUCCEEDED":
        required |= {
            "P3": {
                "engine.json",
                "raw.json",
                "clean.json",
                "standardized.json",
                "neutralized.json",
                "final.json",
                "labels.json",
                "metrics.json",
                "oos.json",
                "inference.json",
                "multiplicity.json",
                "approvals.json",
                "report.json",
                "report.html",
                "report-html.json",
            },
            "P4": {"candidate.json", "risk.json", "result.json", "published-byte-audit.json"},
            "P5": {
                "state.json",
                "transactions.json",
                "transaction-files.json",
                "portfolio-lineage.json",
                "trace.json",
                "result.json",
                "published-byte-audit.json",
            },
            "P5_REPLAY": {
                "result.json",
                "comparison.json",
                "portfolio-lineage.json",
                "transaction-files.json",
            },
            "PUBLISHED_REF_PROJECTION": {"result.json", "source-registration.json"},
        }[binding["service_kind"]]
    if not required <= set(entries):
        raise ContractError("TASK_REQUIRED_ARTIFACT_MISSING")
    contents = {}
    for name, e in entries.items():
        p = guard_path(directory / name)
        if (
            not re.fullmatch(r"[a-z0-9_-]+\.(json|html)", name)
            or not p.is_relative_to(directory)
            or p.parent != directory
        ):
            raise ContractError("TASK_ARTIFACT_BOUNDARY")
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != e["sha256"]:
            raise ContractError("TASK_CORE_ARTIFACT_CHANGED")
        contents[name] = raw
    lineage = load(contents["lineage.json"])
    config = load(contents["config.json"])
    initial = read_chain(directory / "events.jsonl")[0]["payload"]
    if initial["config_hash"] != digest(config) or initial["lineage_hash"] != digest(lineage):
        raise ContractError("TASK_INITIAL_RECORD_CHANGED")
    if m["status"] == "SUCCEEDED" and binding["service_kind"] == "P3":
        report = load(contents["report.json"])
        if (
            report.get("schema") != "research-report/1"
            or report.get("run_id") != run
            or report.get("purpose") != "ENGINEERING_DEMO"
            or report.get("financial_approval") != "NONE"
            or report.get("independence_verified") is not False
        ):
            raise ContractError("TASK_RESEARCH_REPORT_IDENTITY_CHANGED")
    if (
        lineage.get("task_binding") != binding
        or lineage.get("task_binding_hash") != digest(binding)
        or digest(config) != binding["core_config_hash"]
    ):
        raise ContractError("TASK_INITIAL_BINDING_MISMATCH")
    return m, contents


class TaskService:
    def __init__(self, root, *, fault=None):
        self.state = TaskState(root)
        self.root = self.state.root
        self.fault = fault
        from aqrp.experiments.admission import capture_activation

        self._activation = capture_activation(self.root) if self.state.managed else None

    def checkpoint(self, name):
        if self.fault is not None:
            self.fault(name)

    def freeze(self, draft):
        d = self.state.defaults()
        return freeze_request(self.root, draft, d["revision"], json.loads(d["payload"]))

    def campaigns(self):
        from aqrp.services.task_campaigns import campaigns

        return campaigns(self.root, catalogue(self.root))

    def register_campaign(self, name, variants):
        from aqrp.services.task_campaigns import register

        if not isinstance(variants, list) or not variants or len(variants) > 64:
            raise ContractError("INVALID_CAMPAIGN_VARIANTS")
        cat = catalogue(self.root)
        configs = []
        for draft in variants:
            validate_draft(draft)
            if set(draft) & {"campaign_id", "source_task", "profile"} or draft.get(
                "kind", "research"
            ) not in ("research", "engineering_pipeline"):
                raise ContractError("INVALID_CAMPAIGN_VARIANT_KIND")
            configs.append(build_research_config(cat, draft))
        return register(self.root, name, configs, cat)

    def validate_effective(self, raw):
        x = load(raw)
        with self.state.transaction() as c:
            row = c.execute(
                "SELECT * FROM defaults WHERE revision=?", (x["defaults_revision"],)
            ).fetchone()
            if x["defaults_revision"] != 0 and (
                row is None or digest(load(row["payload"])) != row["hash"]
            ):
                raise ContractError("DEFAULTS_REVISION_IDENTITY_CHANGED")
        if x["kind"] == "replay":
            draft = {
                "kind": "replay",
                **{k: v for k, v in x["payload"].items() if k in ("source_task", "profile")},
            }
        else:
            draft = x["payload"]["raw_draft"]
        expected = freeze_request(self.root, draft, x["defaults_revision"])
        if expected.raw != raw:
            raise ContractError("EFFECTIVE_REQUEST_CHANGED")
        return x

    def submit(self, effective, idempotency_key):
        from aqrp.experiments.admission import verify_activation

        if self.state.managed:
            verify_activation(self.root, self._activation)
        if type(effective) is not EffectiveRequest:
            raise ContractError("FROZEN_TASK_REQUEST_REQUIRED")
        x = self.validate_effective(effective.raw)
        return self.status(
            self.state.submit(
                effective.raw,
                idempotency_key,
                campaign=x["payload"].get("campaign"),
                activation=self._activation
                if self._activation is not None
                else {"inactive_service": True},
            )
        )

    def cancel(self, task):
        from aqrp.experiments.admission import verify_activation

        if self.state.managed:
            verify_activation(self.root, self._activation)
            self._verify_planned_replay_source(task)
        return self.state.cancel(task, activation=self._activation)

    def save_defaults(self, expected, patch):
        validate_draft(patch)
        if patch.get("kind") == "replay":
            raise ContractError("REPLAY_REQUIRES_EXPLICIT_SOURCE")
        validate_defaults(self.root, patch)
        return self.state.save_defaults(expected, patch)

    def _snapshot(self, task):
        row = self.state.get(task)
        raw = guard_path(self.root / "tasks" / task / "request.json").read_bytes()
        if raw.decode() != row["raw"] or digest(load(raw)) != row["hash"]:
            raise ContractError("TASK_REQUEST_IDENTITY_CHANGED")
        if self.state.managed:
            with self.state.transaction() as c:
                self.state.budget.verify(c)
        return row

    def status(self, task):
        row = self._snapshot(task)
        public = {
            "task_id": task,
            "config_hash": row["hash"],
            "status": row["status"],
            "cancel_requested": bool(row["cancel"]),
            "error": row["error"],
            "slots": self.state.slots(task),
            "scope": "ENGINEERING_TEST_ONLY",
            "financial_approval": "NONE",
        }
        if "campaign" in load(row["raw"].encode()).get("payload", {}):
            public["research_control"] = self.state.research_attempt(task)
        if row["status"] == "CANCELLED":
            try:
                self._verify_cancelled_finances(task)
            except (Exception, KeyboardInterrupt) as exc:
                public.update(
                    status="INTEGRITY_ERROR",
                    usable=False,
                    error="COMMITTED_STATE_UNVERIFIED",
                    financial_verification_error=getattr(exc, "code", type(exc).__name__),
                    original_terminal_status="CANCELLED",
                )
        if row["status"] == "SUCCEEDED":
            try:
                self.validate_effective(row["raw"].encode())
                pointer = load(row["completion"])
                if set(pointer) != {"file", "sha256"} or not re.fullmatch(
                    r"completion(?:-[0-9]+)?\.json", pointer["file"]
                ):
                    raise ContractError("TASK_COMPLETION_CHANGED")
                raw = guard_path(self.root / "tasks" / task / pointer["file"]).read_bytes()
                receipt = load(raw)
                plan_path = guard_path(self.root / "tasks" / task / "resolved-plan.json")
                plan_hash = (
                    hashlib.sha256(plan_path.read_bytes()).hexdigest()
                    if plan_path.exists()
                    else None
                )
                if (
                    hashlib.sha256(raw).hexdigest() != pointer["sha256"]
                    or canonical(receipt) != raw
                    or receipt["claim_epoch"] != row["epoch"]
                    or receipt["config_hash"] != row["hash"]
                    or receipt["core_proofs"] != self._proofs(task)
                    or receipt["resolved_plan_sha256"] != plan_hash
                ):
                    raise ContractError("TASK_COMPLETION_CHANGED")
                public["result"] = receipt["result"]
            except (ContractError, OSError, KeyError, ValueError, TypeError, IndexError) as exc:
                public.update(
                    status="INTEGRITY_ERROR",
                    error=getattr(exc, "code", type(exc).__name__),
                    usable=False,
                )
        return public

    def list(self):
        with self.state.transaction() as c:
            ids = [r[0] for r in c.execute("SELECT id FROM tasks ORDER BY rowid DESC")]
        rows = []
        for task in ids:
            try:
                rows.append(self.status(task))
            except (ContractError, OSError, ValueError) as exc:
                rows.append(
                    {
                        "task_id": task,
                        "status": "INTEGRITY_ERROR",
                        "error": getattr(exc, "code", type(exc).__name__),
                    }
                )
        return rows

    def logs(self, task):
        self._snapshot(task)
        with self.state.transaction() as c:
            return [
                {"seq": r["seq"], "kind": r["kind"], "payload": json.loads(r["payload"])}
                for r in c.execute("SELECT * FROM events WHERE task=? ORDER BY seq", (task,))
            ]

    def request(self, task):
        return load(self._snapshot(task)["raw"])

    def defaults(self, revision=None):
        return self.state.defaults(revision)

    def rollback_defaults(self, expected, target):
        return self.state.rollback_defaults(expected, target)

    def artifact_catalogue(self, task, slot):
        self._snapshot(task)
        slots = self.state.slots(task)
        if slot not in slots:
            raise ContractError("UNKNOWN_TASK_SLOT")
        manifest, _ = read_core(slots[slot]["binding"])
        return manifest

    def worker_log(self, task):
        self._snapshot(task)
        # Only this fixed log name; it is a captured diagnostic prefix, never a financial proof.
        return guard_path(self.root / "tasks" / task / "worker.log").read_bytes()

    def _proofs(self, task):
        row = self._snapshot(task)
        slots = self.state.slots(task)

        def read_adapted(name):
            with self.state.transaction() as c:
                return c.execute(
                    "SELECT raw,hash FROM adapted_requests WHERE task=? AND slot=?",
                    (task, name),
                ).fetchone()

        return verify_core_proofs(
            self.root, self.state.workspace_id, task, row, slots, read_adapted
        )

    def artifact(self, task, slot, name):
        self._snapshot(task)
        if not re.fullmatch(r"[a-z0-9_-]+\.(json|html)", name):
            raise ContractError("INVALID_TASK_ARTIFACT")
        entries = self.state.slots(task)
        if slot not in entries:
            raise ContractError("UNKNOWN_TASK_SLOT")
        _, contents = read_core(entries[slot]["binding"])
        if name not in contents:
            raise ContractError("TASK_ARTIFACT_NOT_MANIFESTED")
        return contents[name]

    @staticmethod
    def _verified_financial_prefix(binding):
        """Current physical financial authority, also for already successful children."""
        _, contents = read_core(binding)
        result = load(contents["result.json"])
        evidence = result.get("committed_state_verification", {})
        if evidence.get("financial_state_known") is False:
            raise ContractError("TASK_FINANCIAL_RESULT_UNKNOWN")
        root = guard_path(binding["physical_ledger_root"]) / binding["child_run_id"]
        # Never let TransactionStore create a missing directory and call it an empty prefix.
        if (
            not guard_path(root / "transactions").is_dir()
            or not guard_path(root / "transactions/initial.json").is_file()
        ):
            raise ContractError("TASK_TRANSACTION_FILES_MISSING")
        state, records, files = TransactionStore(root / "transactions").verified_snapshot()
        computed = projection(state, records)
        if files != load(contents["transaction-files.json"]):
            raise ContractError("TASK_FINANCIAL_RESULT_CHANGED")
        if binding["service_kind"] == "P5_REPLAY":
            comparison = load(contents["comparison.json"])
            if (
                result["status"] != "NUMERICAL_REPLAY_VERIFIED"
                or comparison != {"expected": computed, "actual": computed, "equal": True}
                or result["state_sha256"] != computed["state_sha256"]
            ):
                raise ContractError("TASK_FINANCIAL_RESULT_CHANGED")
        elif result["status"] == "SUCCEEDED":
            if any(result[k] != v for k, v in computed.items()):
                raise ContractError("TASK_FINANCIAL_RESULT_CHANGED")
        elif (
            evidence.get("financial_state_known") is not True
            or result.get("last_committed_account") != computed["account"]
            or evidence.get("state_sha256") != computed["state_sha256"]
            or evidence.get("financial_proof_sha256") != digest(computed["reconciliation"])
            or evidence.get("commit_count") != len(records)
            or evidence.get("prefix_sha256")
            != (records[-1]["sha256"] if records else computed["state_sha256"])
        ):
            raise ContractError("TASK_FINANCIAL_RESULT_CHANGED")
        return result

    def _verify_cancelled_finances(self, task):
        """No safe cancellation certificate may rely on a cached known-state flag."""
        self._verify_planned_replay_source(task)
        for slot in self.state.slots(task).values():
            binding = slot["binding"]
            if binding["service_kind"] not in ("P5", "P5_REPLAY"):
                continue
            root = guard_path(binding["physical_ledger_root"]) / binding["child_run_id"]
            if slot["state"] == "ALLOCATED" and not root.exists():
                continue
            self._verified_financial_prefix(binding)
            if binding["service_kind"] == "P5_REPLAY":
                x = load(self._snapshot(task)["raw"].encode())
                source = self.state.slots(x["payload"]["source_task"])["B"]["binding"]
                self._verified_financial_prefix(source)

    def _verify_planned_replay_source(self, task):
        """A zero-research planned cancellation still retains a real source proof."""
        if not self.state.managed:
            return
        source_task = None
        with self.state.transaction() as c:
            self.state.budget.verify(c)
            actor = c.execute(
                "SELECT payload,binding FROM execution_plan_slots WHERE owner_id=?", (task,)
            ).fetchone()
            if actor is None:
                return
            spec, binding = load(actor[0]), load(actor[1])
            if spec["service_kind"] != "TASK_REPLAY" or "source_slot" not in spec:
                return
            source = c.execute(
                "SELECT payload,binding FROM execution_plan_slots WHERE slot=?",
                (spec["source_slot"],),
            ).fetchone()
            if source is None or source[1] is None:
                raise ContractError("TASK_CANCEL_SOURCE_UNVERIFIED")
            original, owner = load(source[0]), load(source[1])
            row = c.execute("SELECT raw,hash FROM tasks WHERE id=?", (task,)).fetchone()
            if (
                row is None
                or binding["owner_id"] != task
                or original["service_kind"] != "TASK"
                or original["request_hash"] != spec["originalsource_request_hash"]
                or load(row[0])["payload"]
                != {"source_task": owner["owner_id"], "profile": "P5_NUMERICAL"}
            ):
                raise ContractError("TASK_CANCEL_SOURCE_UNVERIFIED")
            source_task = owner["owner_id"]
        # The existing status/proof gate opens its own transaction and reconciles
        # the physical source ledger. Never call it under an authority lock.
        source = self.status(source_task)
        if source["status"] != "SUCCEEDED" or source.get("usable") is False:
            raise ContractError("TASK_CANCEL_SOURCE_UNVERIFIED")

    def financial_result(self, task):
        row = self._snapshot(task)
        self.validate_effective(row["raw"].encode())
        slots = self.state.slots(task)
        if "B" not in slots:
            raise ContractError("NO_BACKTEST_STAGE")
        _, contents = read_core(slots["B"]["binding"])
        original = load(contents["result.json"])
        # Preserve the original opaque failure report for diagnosis; this never
        # certifies cash, and cancellation always calls the strict prefix gate.
        if (
            original["status"] != "SUCCEEDED"
            and original.get("committed_state_verification", {}).get("financial_state_known")
            is False
        ):
            if "account" in original or "last_committed_account" in original:
                raise ContractError("TASK_FINANCIAL_RESULT_UNKNOWN")
            return original
        return self._verified_financial_prefix(slots["B"]["binding"])

    def _pipeline_request(self, x, r):
        cat = catalogue(self.root)
        ref, _, _ = references(self.root, cat)
        options = x["payload"]["execution"]
        selection = execution_selection(x["payload"])
        selected_research = deepcopy(x["payload"]["research"])
        selected_research["decisions"] = [
            selected_research["decisions"][entry["research_ordinal"]]
            for entry in selection["resolved"]
        ]
        requests = execution_requests(selected_research, ref, self.root / "research-runs", r)
        values = [load(req.raw) for req in requests.values()]
        combined = deepcopy(values[0])
        combined.update(initial_cash=options["initial_cash"], fee_budget=options["fee_budget"])
        for i, decision in enumerate(combined["decisions"]):
            portfolios = [load(v["decisions"][i]["portfolio_request_utf8"]) for v in values]
            p = portfolios[0]
            p["policy"].update(options["policy"])
            p["policy"]["factor_weights"] = options["factor_weights"]
            p["constraints"].update(options["constraints"])
            # Existing bind_research owns score/source construction and validation.
            p = bind_research(p, self.root / "research-runs", r["run_id"], source_snapshot=ref)
            decision["portfolio_request_utf8"] = p.raw.decode()
        return seal_sidecar(combined)

    def _plan(self, auth, parent, request):
        x = validate(request)
        slots = {parent.slot: parent.binding()["child_run_id"]}
        if parent.slot == "B":
            slots["R"] = auth.context("R").binding()["child_run_id"]
        for index, d in enumerate(x["decisions"]):
            p = load(d["portfolio_request_utf8"])
            child = auth.allocate(
                f"P:{index}",
                "P4",
                guard_path(parent.binding()["physical_ledger_root"])
                / parent.binding()["child_run_id"]
                / "portfolio-runs",
                parent=parent,
                index=index,
                time=utc(p["context"]["decision_time"]).isoformat(),
                source=hashlib.sha256(d["portfolio_request_utf8"].encode()).hexdigest(),
            )
            slots[child.slot] = child.binding()["child_run_id"]
        if parent.slot == "B" and not x["decisions"]:
            raise ContractError("NO_REQUIRED_DECISIONS")
        plan = {
            "task_config_hash": auth.check()["hash"],
            "request_sha256": request.content_hash,
            "request_utf8": request.raw.decode(),
            "decision_count": len(x["decisions"]),
            "slots": slots,
        }
        effective = load(auth.check()["raw"])
        if parent.slot == "B":
            selected = execution_selection(effective["payload"])
        else:
            source = effective["payload"]["source_task"]
            original_plan = load(
                guard_path(self.root / "tasks" / source / "resolved-plan.json").read_bytes()
            )
            selected = original_plan["execution_selection"]
            if original_plan["request_sha256"] != request.content_hash:
                raise ContractError("TASK_REPLAY_SELECTION_CHANGED")
        if len(selected["resolved"]) != len(x["decisions"]):
            raise ContractError("TASK_EXECUTION_SELECTION_CHANGED")
        for entry, decision in zip(selected["resolved"], x["decisions"], strict=True):
            portfolio = load(decision["portfolio_request_utf8"])
            if utc(portfolio["context"]["decision_time"]) != utc(entry["decision_time"]):
                raise ContractError("TASK_EXECUTION_SELECTION_CHANGED")
        plan["execution_selection"] = selected
        path = guard_path(self.root / "tasks" / auth.task / "resolved-plan.json")
        if path.exists():
            if path.read_bytes() != canonical(plan):
                raise ContractError("TASK_RESOLVED_PLAN_CHANGED")
        else:
            immutable_write(path, canonical(plan))

    def work(self, task, *, recover=False):
        if self.state.get(task)["status"] in TERMINAL:
            return self.status(task)
        owner, epoch = self.state.claim(task, recover=recover)
        auth = authority(self.state, task, owner, epoch)
        try:
            x = self.validate_effective(auth.check()["raw"].encode())
            auth.check(cancel=True)
            if x["kind"] == "replay":
                result = self._replay(auth, x)
            else:
                ctx = auth.allocate("R", "P3", self.root / "research-runs")
                r = ctx.existing()
                if r is None:
                    r = research(
                        research_request(self.root, x),
                        self.root / "research-runs",
                        task_context=ctx,
                    )
                ctx.verify(self.root / "research-runs", r["run_id"])
                if r["manifest"]["status"] != "SUCCEEDED":
                    raise ContractError("REQUIRED_STAGE_REJECTED")
                self.checkpoint("R_TERMINAL_BEFORE_MAPPING")
                ctx.mark_verified(r["manifest"])
                auth.check(cancel=True)
                result = {"research_run_id": r["run_id"]}
                if x["kind"] == "engineering_pipeline":
                    b = auth.allocate("B", "P5", self.root / "backtest-runs")
                    req = self._pipeline_request(x, r)
                    self._plan(auth, b, req)
                    self.checkpoint("PLAN_FROZEN_BEFORE_B")
                    try:
                        bt = b.existing()
                    except ContractError as exc:
                        if exc.code != "NONTERMINAL_RUN":
                            raise
                        bt = resume_engineering(
                            self.root / "backtest-runs", b.binding()["child_run_id"], task_context=b
                        ).read()
                    if bt is None:
                        bt = simulate_engineering(
                            req, self.root / "backtest-runs", x["code_commit"], task_context=b
                        ).read()
                    if (
                        bt.get("committed_state_verification", {}).get("financial_state_known")
                        is False
                    ):
                        raise ContractError("COMMITTED_STATE_UNVERIFIED")
                    if bt["status"] == "CANCELLED":
                        raise KeyboardInterrupt("TASK_SAFE_CANCEL_CHECKPOINT")
                    if bt["status"] != "SUCCEEDED":
                        raise ContractError("TASK_BACKTEST_FAILED")
                    self.checkpoint("B_TERMINAL_BEFORE_MAPPING")
                    b.mark_verified(bt["manifest"])
                    result["backtest_run_id"] = bt["run_id"]
            proofs = self._proofs(task)
            auth.check(cancel=True)
            completion = {
                "task_id": task,
                "kind": x["kind"],
                "config_hash": digest(x),
                "core_proofs": proofs,
                "result": result,
                "scope": "ENGINEERING_TEST_ONLY",
                "financial_approval": "NONE",
                "claim_epoch": epoch,
                "resolved_plan_sha256": hashlib.sha256(
                    (self.root / "tasks" / task / "resolved-plan.json").read_bytes()
                ).hexdigest()
                if x["kind"] != "research"
                else None,
                "validation_steps": {
                    "research": ["RV"],
                    "engineering_pipeline": ["PLAN", "RV", "BV"],
                    "replay": ["SV", "CV"],
                }[x["kind"]],
            }
            path = guard_path(self.root / "tasks" / task / "completion.json")
            self.checkpoint("BEFORE_COMPLETION")
            if path.exists():
                old = load(path.read_bytes())
                if {k: v for k, v in old.items() if k != "claim_epoch"} != {
                    k: v for k, v in completion.items() if k != "claim_epoch"
                }:
                    raise ContractError("TASK_COMPLETION_CHANGED")
                if old["claim_epoch"] != epoch:
                    completion["previous_completion_sha256"] = hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    path = path.with_name(f"completion-{epoch}.json")
            if path.exists():
                if path.read_bytes() != canonical(completion):
                    raise ContractError("TASK_COMPLETION_CHANGED")
            else:
                immutable_write(path, canonical(completion))
            pointer = {"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            self.checkpoint("COMPLETION_BEFORE_SQL")
            with self.state.transaction() as c:
                row = c.execute("SELECT * FROM tasks WHERE id=?", (task,)).fetchone()
                if (row["owner"], row["epoch"], row["status"]) != (owner, epoch, "RUNNING"):
                    raise ContractError("STALE_TASK_CLAIM")
                if row["cancel"]:
                    raise KeyboardInterrupt("TASK_SAFE_CANCEL_CHECKPOINT")
                c.execute(
                    "UPDATE tasks SET status='SUCCEEDED',completion=?,owner=NULL WHERE id=?",
                    (canonical(pointer).decode(), task),
                )
                self.state.event(
                    c, task, "SUCCEEDED", {"completion": pointer, "claim_epoch": epoch}
                )
        except (Exception, KeyboardInterrupt) as exc:
            cancelled = isinstance(exc, KeyboardInterrupt)
            unknown = False
            verification_error = None
            if cancelled:
                try:
                    self._verify_cancelled_finances(task)
                except (Exception, KeyboardInterrupt) as financial_error:
                    unknown = True
                    verification_error = getattr(
                        financial_error, "code", type(financial_error).__name__
                    )
            with self.state.transaction() as c:
                final = "CANCELLED" if cancelled and not unknown else "FAILED"
                code = (
                    "COMMITTED_STATE_UNVERIFIED"
                    if unknown
                    else getattr(exc, "code", type(exc).__name__)
                )
                updated = c.execute(
                    "UPDATE tasks SET status=?,error=?,owner=NULL WHERE id=? AND owner=? AND epoch=? AND status='RUNNING'",
                    (final, code, task, owner, epoch),
                )
                if updated.rowcount:
                    self.state.event(
                        c,
                        task,
                        final,
                        {
                            "code": code,
                            "original_error": getattr(exc, "code", type(exc).__name__),
                            "cancellation_intent": cancelled,
                            "financial_verification_error": verification_error,
                        },
                    )
        return self.status(task)

    def compare(self, left, right):
        a, b = self.status(left), self.status(right)
        if a["status"] != "SUCCEEDED" or b["status"] != "SUCCEEDED":
            raise ContractError("VERIFIED_SUCCESS_REQUIRED")

        def projection(row):
            result = row["result"]
            if "backtest_run_id" in result:
                x = result_engineering(self.root / "backtest-runs", result["backtest_run_id"])
                return {
                    k: x[k] for k in ["account", "positions", "fills", "performance", "valuations"]
                }
            if "replay" in result:
                values = load(self.artifact(row["task_id"], "E", "comparison.json"))["actual"]
                return {
                    k: values[k]
                    for k in ["account", "positions", "fills", "performance", "valuations"]
                }
            if "historical_replay" in result:
                return {"historical_runs": result["historical_replay"]["runs"]}
            return {
                name: load(self.artifact(row["task_id"], "R", name + ".json"))
                for name in ("metrics", "oos")
            }

        pa, pb = projection(a), projection(b)
        return {
            "left": left,
            "right": right,
            "config_equal": a["config_hash"] == b["config_hash"],
            "numeric_equal": pa == pb,
            "left_projection": pa,
            "right_projection": pb,
            "scope": "DECLARED_RESULT_PROJECTION",
            "projection_fields": {
                "research": ["metrics", "oos"],
                "historical_replay": ["historical_runs"],
                "backtest": ["account", "positions", "fills", "performance", "valuations"],
            },
            "excluded_metadata": [
                "task_id",
                "run_id",
                "wallclock_events",
                "file_roots",
                "task_ownership",
                "trial_history_and_approval_proposals_retained_separately",
            ],
        }

    def _replay(self, auth, x):
        if x["payload"]["profile"] == "PUBLISHED_REF_PROJECTION":
            from aqrp.services.task_history import execute_history

            return execute_history(self, auth, x)
        source = self.status(x["payload"]["source_task"])
        if source["status"] != "SUCCEEDED" or "backtest_run_id" not in source["result"]:
            raise ContractError("VERIFIED_PIPELINE_SOURCE_REQUIRED")
        run = source["result"]["backtest_run_id"]
        ledger = ExperimentLedger(self.root / "backtest-runs")
        ledger.verify(run)
        config = load((ledger.path(run) / "config.json").read_bytes())
        req = EngineeringBacktestRequest(bytes.fromhex(config["raw_request_hex"]))
        e = auth.allocate("E", "P5_REPLAY", self.root / "replay-runs")
        self._plan(auth, e, req)
        prior = e.existing()
        if prior is None:
            prior = replay_engineering(
                self.root / "backtest-runs", run, self.root / "replay-runs", task_context=e
            )
        e.mark_verified(prior["manifest"])
        return {
            "source_task": source["task_id"],
            "replay": {k: v for k, v in prior.items() if k != "manifest"},
        }


def verify_core_proofs(workspace_root, workspace_id, task, row, slots, read_adapted):
    """One complete original-byte proof contract for live tasks and history import."""
    x = load(row["raw"])
    expected = {"R"} if x["kind"] == "research" else {"R", "B"}
    if x["kind"] == "replay":
        expected = {"E"}
    plan_path = guard_path(workspace_root / "tasks" / task / "resolved-plan.json")
    if x["kind"] != "research":
        plan = load(plan_path.read_bytes())
        if x["kind"] == "engineering_pipeline":
            selected = execution_selection(x["payload"])
        elif x["payload"]["profile"] != "PUBLISHED_REF_PROJECTION":
            source = x["payload"]["source_task"]
            source_plan = load(
                guard_path(workspace_root / "tasks" / source / "resolved-plan.json").read_bytes()
            )
            selected = source_plan["execution_selection"]
            if source_plan["request_sha256"] != plan["request_sha256"]:
                raise ContractError("TASK_REPLAY_SELECTION_CHANGED")
        else:
            selected = {"resolved": []}
        if x["payload"].get("profile") != "PUBLISHED_REF_PROJECTION" and (
            plan.get("execution_selection") != selected
            or plan["decision_count"] != len(selected["resolved"])
        ):
            raise ContractError("TASK_EXECUTION_SELECTION_CHANGED")
        expected |= {f"P:{i}" for i in range(plan["decision_count"])}
        if (
            plan["task_config_hash"] != row["hash"]
            or set(plan["slots"]) != expected
            or plan["slots"] != {n: s["binding"]["child_run_id"] for n, s in slots.items()}
            or hashlib.sha256(plan["request_utf8"].encode()).hexdigest() != plan["request_sha256"]
        ):
            raise ContractError("TASK_RESOLVED_PLAN_CHANGED")
    if set(slots) != expected:
        raise ContractError("TASK_REQUIRED_SLOT_SET_MISMATCH")
    proofs = {}
    for name, slot in slots.items():
        b = slot["binding"]
        if (
            b["task_id"] != task
            or b["workspace_id"] != workspace_id
            or b["plan_hash"] != row["hash"]
        ):
            raise ContractError("TASK_SLOT_PARENT_CHANGED")
        m, contents = read_core(b)
        if m["status"] != "SUCCEEDED":
            raise ContractError("REQUIRED_STAGE_REJECTED")
        if name.startswith("P:"):
            parent = slots["B" if x["kind"] == "engineering_pipeline" else "E"]["binding"]
            decision = load(plan["request_utf8"])["decisions"][b["decision_index"]]
            original = load(decision["portfolio_request_utf8"])
            selected_decision = selected["resolved"][b["decision_index"]]
            if (
                b["parent_slot_id"] != parent["slot_id"]
                or b["parent_execution_run_id"] != parent["child_run_id"]
                or b["physical_ledger_root"]
                != str(
                    guard_path(parent["physical_ledger_root"])
                    / parent["child_run_id"]
                    / "portfolio-runs"
                )
                or b["source_request_hash"]
                != hashlib.sha256(decision["portfolio_request_utf8"].encode()).hexdigest()
                or b["decision_time_UTC"] != utc(original["context"]["decision_time"]).isoformat()
                or b["decision_time_UTC"] != utc(selected_decision["decision_time"]).isoformat()
            ):
                raise ContractError("TASK_NESTED_P4_BINDING_MISMATCH")
            adapted = read_adapted(name)
            if (
                adapted is None
                or adapted[1] != b["adapted_request_hash"]
                or hashlib.sha256(adapted[0].encode()).hexdigest() != adapted[1]
                or load(contents["config.json"])["raw_request_hex"] != adapted[0].encode().hex()
            ):
                raise ContractError("TASK_ADAPTED_REQUEST_CHANGED")
        if b["service_kind"] == "PUBLISHED_REF_PROJECTION":
            from aqrp.services.task_history import history_catalogue

            if digest(history_catalogue(workspace_root)) != x["payload"]["history_sha256"]:
                raise ContractError("HISTORICAL_CATALOG_CHANGED")
            result = load(contents["result.json"])
            registration = load(contents["source-registration.json"])
            if (
                digest(registration) != x["payload"]["history_sha256"]
                or result["status"] != "ALL_ORIGINAL_BYTES_VERIFIED_AND_THREE_RUNS_REPLAYED"
                or len(result["runs"]) != 3
                or any(v["status"] != "DECLARED_PROJECTION_MATCH" for v in result["runs"])
            ):
                raise ContractError("TASK_HISTORICAL_REPLAY_UNVERIFIED")
        elif name in ("B", "E"):
            root = guard_path(b["physical_ledger_root"]) / b["child_run_id"]
            if (
                not (root / "transactions").is_dir()
                or not (root / "transactions/initial.json").is_file()
            ):
                raise ContractError("TASK_TRANSACTION_FILES_MISSING")
            state, records, transaction_files = TransactionStore(
                root / "transactions"
            ).verified_snapshot()
            if transaction_files != load(contents["transaction-files.json"]):
                raise ContractError("TASK_TRANSACTION_FILES_CHANGED")
            current = projection(state, records)
            if name == "E":
                comparison = load(contents["comparison.json"])
                if (
                    not comparison["equal"]
                    or comparison["actual"] != current
                    or comparison["expected"] != current
                ):
                    raise ContractError("TASK_REPLAY_COMPARISON_CHANGED")
            children = guard_path(root / "portfolio-runs")
            actual = {p.name for p in children.iterdir()} if children.exists() else set()
            intended = {
                s["binding"]["child_run_id"] for n, s in slots.items() if n.startswith("P:")
            }
            if actual != intended:
                raise ContractError("TASK_NESTED_CHILD_SET_MISMATCH")
            for p in children.iterdir() if children.exists() else []:
                guard_path(p)
            if name == "B":
                result = result_engineering(b["physical_ledger_root"], b["child_run_id"])
                if (
                    result["status"] != "SUCCEEDED"
                    or result.get("committed_state_verification", {}).get("financial_state_known")
                    is False
                ):
                    raise ContractError("TASK_FINANCIAL_RESULT_UNKNOWN")
                if any(result[k] != v for k, v in current.items()):
                    raise ContractError("TASK_FINANCIAL_RESULT_CHANGED")
                config = load(contents["config.json"])
                if config["raw_request_hex"] != plan["request_utf8"].encode().hex():
                    raise ContractError("TASK_EXECUTION_PLAN_REQUEST_CHANGED")
                actual_lineage = load(contents["portfolio-lineage.json"])
                if len(actual_lineage) != plan["decision_count"]:
                    raise ContractError("TASK_PORTFOLIO_LINEAGE_MISSING")
                for p in actual_lineage:
                    child = slots[f"P:{p['index']}"]["binding"]
                    if (
                        p["result"]["run_id"] != child["child_run_id"]
                        or hashlib.sha256(p["request_utf8"].encode()).hexdigest()
                        != child["adapted_request_hash"]
                    ):
                        raise ContractError("TASK_PORTFOLIO_LINEAGE_CHANGED")
        proofs[name] = {
            "binding_hash": digest(b),
            "manifest_hash": digest(m),
            "status": m["status"],
        }
    return proofs
