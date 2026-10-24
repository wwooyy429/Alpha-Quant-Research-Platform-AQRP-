"""SQLite task allocation/claims. Engineering integrity, not OS isolation."""

import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import BudgetAuthority
from aqrp.experiments.ledger import immutable_write, read_chain

SETUP_TIMEOUT_SECONDS = 30.0

TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED"}


class TaskState:
    def __init__(self, root):
        self.root = guard_path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        control = guard_path(self.root / "task-control")
        control.mkdir(exist_ok=True)
        self.db = control / "tasks.sqlite"
        self.budget = BudgetAuthority(self.root)
        self.managed = (self.root / "catalog.json").exists() or self.budget.anchor.exists()
        if not self.managed:
            from aqrp.experiments.admission import resolve_admission_domain

            # An empty child queue cannot masquerade as another authority under W.
            resolve_admission_domain(self.root / "research-runs")
        if self.budget.anchor.exists():
            with self.budget.transaction() as connection:
                self.budget.verify(connection)
        with self.transaction() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS workspace (id TEXT PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS tasks (
                  id TEXT PRIMARY KEY, key TEXT UNIQUE, raw TEXT, hash TEXT,
                  status TEXT, owner TEXT, epoch INTEGER, cancel INTEGER DEFAULT 0,
                  completion TEXT, error TEXT);
                CREATE TABLE IF NOT EXISTS slots (
                  task TEXT, slot TEXT, binding TEXT, state TEXT,
                  PRIMARY KEY(task,slot));
                CREATE TABLE IF NOT EXISTS adapted_requests (
                  task TEXT, slot TEXT, raw TEXT, hash TEXT,
                  PRIMARY KEY(task,slot));
                CREATE TABLE IF NOT EXISTS events (
                  seq INTEGER PRIMARY KEY, task TEXT, kind TEXT, payload TEXT);
                CREATE TABLE IF NOT EXISTS campaign_attempts (
                  task TEXT PRIMARY KEY, campaign TEXT, plan_hash TEXT, data_hash TEXT,
                  units INTEGER, payload TEXT, hash TEXT);
                CREATE TABLE IF NOT EXISTS defaults (
                  revision INTEGER PRIMARY KEY, payload TEXT, hash TEXT);
            """)
            c.execute("BEGIN IMMEDIATE")
            if not c.execute("SELECT id FROM workspace").fetchone():
                c.execute("INSERT INTO workspace VALUES (?)", (str(uuid.uuid4()),))
            self.workspace_id = c.execute("SELECT id FROM workspace").fetchone()[0]
            if self.managed:
                self.budget.initialize(
                    c, self.workspace_id, history_verifier=self._migration_history
                )
        if self.managed:
            self.budget.materialize()

    @contextmanager
    def transaction(self):
        guard_path(self.db)
        c = sqlite3.connect(self.db, timeout=0, isolation_level=None)
        try:
            c.row_factory = sqlite3.Row
            # journal_mode can return SQLITE_BUSY immediately during a first-open
            # race. Wait only before a transaction exists; never rerun its body.
            deadline = time.monotonic() + SETUP_TIMEOUT_SECONDS
            while True:
                try:
                    row = c.execute("PRAGMA journal_mode=WAL").fetchone()
                    if row is None or row[0] != "wal":
                        raise ContractError("TASK_JOURNAL_MODE_UNVERIFIED")
                    break
                except sqlite3.OperationalError as exc:
                    code = getattr(exc, "sqlite_errorcode", None)
                    if code is None or code & 0xFF not in (
                        sqlite3.SQLITE_BUSY,
                        sqlite3.SQLITE_LOCKED,
                    ):
                        raise
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise
                    time.sleep(min(0.01, remaining))
            c.execute("PRAGMA synchronous=FULL")
            remaining_ms = max(0, int(1000 * (deadline - time.monotonic())))
            c.execute("PRAGMA busy_timeout=" + str(remaining_ms))
            c.execute("BEGIN IMMEDIATE")
            try:
                yield c
                c.commit()
            except BaseException:
                c.rollback()
                raise

        finally:
            c.close()

    @staticmethod
    def event(c, task, kind, payload):
        c.execute(
            "INSERT INTO events(task,kind,payload) VALUES (?,?,?)",
            (task, kind, canonical(payload).decode()),
        )

    def get(self, task):
        with self.transaction() as c:
            row = c.execute("SELECT * FROM tasks WHERE id=?", (task,)).fetchone()
            if row is None:
                raise ContractError("UNKNOWN_TASK")
            return dict(row)

    def submit(self, raw, key, *, campaign=None, activation=None):
        if not self.managed:
            return self._submit_standalone(raw, key, campaign=campaign)
        for _ in range(128):
            try:
                self.budget.materialize()
            except ContractError as exc:
                if (
                    exc.code == "ADMISSION_HISTORY_UNVERIFIED"
                    and type(exc.__cause__) is ValueError
                    and exc.__cause__.args == ("campaign admission set",)
                ):
                    raise ContractError("CAMPAIGN_ATTEMPT_HISTORY_INCOMPLETE") from exc
                raise
            task = self._submit_once(raw, key, campaign=campaign, activation=activation)
            if task is not None:
                self.budget.materialize()
                return task
            # Only a pre-admission empty transaction may ask for projection drain.
            # No reservation, Task insertion or caller business body is retried.
        raise ContractError("ADMISSION_PUBLICATION_BUSY", retryable=True)

    def _submit_standalone(self, raw, key, *, campaign=None):
        """Original data-free SQLite queue; it cannot execute a frozen research request."""
        from aqrp.experiments.admission import resolve_admission_domain

        resolve_admission_domain(self.root / "research-runs")
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ContractError("INVALID_IDEMPOTENCY_KEY")
        request = json.loads(raw)
        if (
            campaign is not None
            or request.get("schema") == "task-request/1"
            or "payload" in request
        ):
            raise ContractError("ADMISSION_DOMAIN_CONFLICT")
        if (self.root / "catalog.json").exists() or self.budget.anchor.exists():
            raise ContractError("ADMISSION_DOMAIN_CONFLICT")
        with self.transaction() as c:
            prior = c.execute("SELECT * FROM tasks WHERE key=?", (key,)).fetchone()
            if prior is not None:
                if prior["hash"] != digest(request):
                    raise ContractError("IDEMPOTENCY_CONFIG_CONFLICT")
                return prior["id"]
            task = str(uuid.uuid4())
            directory = guard_path(self.root / "tasks" / task)
            directory.mkdir(parents=True)
            immutable_write(directory / "request.json", raw)
            self._insert_task(c, task, key, raw, request)
            self.event(
                c,
                task,
                "SUBMITTED",
                {"config_hash": digest(request), "campaign_attempt_sha256": None},
            )
        return task

    def _submit_once(self, raw, key, *, campaign=None, activation=None):
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ContractError("INVALID_IDEMPOTENCY_KEY")
        request = json.loads(raw)
        with self.transaction() as c:
            if c.execute("SELECT count(*) FROM admission_outbox WHERE materialized=0").fetchone()[
                0
            ]:
                return None
            prior = c.execute("SELECT * FROM tasks WHERE key=?", (key,)).fetchone()
            if prior:
                if prior["hash"] != digest(request):
                    raise ContractError("ADMISSION_IDEMPOTENCY_CONFLICT")
                self.budget.verify(c)
                return prior["id"]
            task = str(uuid.uuid4())
            directory = guard_path(self.root / "tasks" / task)
            control = None
            if campaign is not None:
                control = self._reserve_campaign(
                    c, task, request, campaign, directory, raw=raw, key=key, activation=activation
                )
                admission = control["admission"]
            else:
                from aqrp.services.task_requests import catalogue

                cat = catalogue(self.root)
                self._insert_task(c, task, key, raw, request)
                admission = self.budget.reserve(
                    c,
                    data_hash=cat["snapshot"]["manifest_hash"],
                    owner_kind="TASK",
                    owner_id=task,
                    key=key,
                    request_hash=digest(request),
                    units=[],
                    service_kind="TASK_REPLAY",
                    output_root=self.root / "replay-runs",
                    activation=activation,
                )
            self.budget.queue_projection(
                c,
                directory / "request.json",
                raw,
                admission["admission_id"],
                kind="SIDECAR",
            )
            self.event(
                c,
                task,
                "SUBMITTED",
                {
                    "config_hash": digest(request),
                    "campaign_attempt_sha256": None if control is None else digest(control),
                },
            )
            if control is not None:
                self.event(c, task, "CAMPAIGN_ATTEMPT_RESERVED", control)
            if control is not None and control["over_budget"]:
                c.execute(
                    "UPDATE tasks SET status='FAILED',error=? WHERE id=?",
                    ("EXPERIMENT_BUDGET_EXCEEDED", task),
                )
                self.event(
                    c,
                    task,
                    "FAILED",
                    {"code": "EXPERIMENT_BUDGET_EXCEEDED", "campaign_attempt": control},
                )
        return task

    @staticmethod
    def _insert_task(c, task, key, raw, request):
        c.execute(
            "INSERT INTO tasks(id,key,raw,hash,status,epoch) VALUES (?,?,?,?,?,0)",
            (task, key, raw.decode(), digest(request), "QUEUED"),
        )

    def _checked_campaign_record(self, c, row, *, legacy=False, authority_verified=False):
        from aqrp.services.research import hypotheses

        raw = guard_path(self.root / "tasks" / row["task"] / "campaign-attempt.json").read_bytes()
        item = json.loads(raw)
        reqrow = c.execute("SELECT raw,hash FROM tasks WHERE id=?", (row["task"],)).fetchone()
        if reqrow is None:
            raise ContractError("CAMPAIGN_ATTEMPT_HISTORY_INCOMPLETE")
        req = json.loads(reqrow["raw"])
        actual_raw = guard_path(self.root / "tasks" / row["task"] / "request.json").read_bytes()
        if (
            canonical(item) != raw
            or raw.decode() != row["payload"]
            or digest(item) != row["hash"]
            or actual_raw.decode() != reqrow["raw"]
            or digest(req) != reqrow["hash"]
            or item["task_config_hash"] != reqrow["hash"]
            or item["campaign"] != req["payload"]["campaign"]
            or item["hypothesis_ids"]
            != [h["hypothesis"] for h in hypotheses(req["payload"]["research"])]
            or item["units"] != row["units"]
            or item["units"] != len(item["hypothesis_ids"])
            or row["data_hash"] != item["campaign"]["data_hash"]
            or row["plan_hash"] != item["campaign"]["campaign_hash"]
            or row["campaign"] != item["campaign"]["id"]
            or item["campaign"]["budget"] != 12
        ):
            raise ContractError("CAMPAIGN_ATTEMPT_IDENTITY_CHANGED")
        if not legacy:
            admitted = self.budget.lookup_owner(c, "TASK", row["task"])
            if item.get("admission") != admitted and not (
                admitted is not None
                and admitted.get("migrated") is True
                and admitted["request_hash"] == reqrow["hash"]
                and admitted["units"]
                == [
                    {
                        "hypothesis_alias": alias,
                        "definition_hash": req["payload"]["research"]["family"]["definitions"][
                            alias
                        ],
                    }
                    for alias in item["hypothesis_ids"]
                ]
            ):
                raise ContractError("CAMPAIGN_ATTEMPT_IDENTITY_CHANGED")
            if not authority_verified:
                self.budget.verify_admission_projections(c, admitted["admission_id"])
        return item

    def _migration_history(self, c):
        try:
            return self._verified_legacy_history(c)
        except (ContractError, OSError, ValueError, TypeError, KeyError, IndexError) as exc:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED") from exc

    def _verified_legacy_history(self, c):
        """Complete, same-package legacy import; no old bundle or partial-history fallback."""
        import hashlib

        from aqrp.experiments.ledger import ExperimentLedger
        from aqrp.services.task_campaigns import campaigns, variant_key
        from aqrp.services.task_requests import catalogue, freeze_request
        from aqrp.services.tasks import TaskService, read_core, verify_core_proofs

        cat = catalogue(self.root)  # Preserves exact bundle, environment and P1 identities.
        task_rows = list(c.execute("SELECT * FROM tasks ORDER BY rowid"))
        campaign_rows = {r["task"]: r for r in c.execute("SELECT * FROM campaign_attempts")}
        task_ids = {r["id"] for r in task_rows}
        task_directory = guard_path(self.root / "tasks")
        if task_directory.exists() and {p.name for p in task_directory.iterdir()} != task_ids:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        records, projections, claims, files = [], [], [], {}
        run_owners = {}

        def remember(path):
            path = guard_path(path)
            raw = path.read_bytes()
            files[str(path)] = {
                "path": str(path),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
            return raw

        def projection(path, raw, owner_kind, owner_id, kind="SIDECAR"):
            projections.append(
                {
                    "path": str(path),
                    "content_hex": raw.hex(),
                    "kind": kind,
                    "owner_kind": owner_kind,
                    "owner_id": owner_id,
                }
            )

        remember(self.root / "catalog.json")
        registered = {record["id"]: record for record in campaigns(self.root, cat)}
        if registered:
            remember(self.root / "research-campaigns/index.jsonl")
            for name in registered:
                remember(self.root / "research-campaigns" / (digest(name) + ".json"))
        expected_campaigns = set()
        for row in task_rows:
            raw = remember(self.root / "tasks" / row["id"] / "request.json")
            req = json.loads(raw)
            if canonical(req) != raw or row["raw"] != raw.decode() or row["hash"] != digest(req):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            revision = req["defaults_revision"]
            defaults = c.execute(
                "SELECT payload,hash FROM defaults WHERE revision=?", (revision,)
            ).fetchone()
            if revision != 0 and (
                defaults is None or digest(json.loads(defaults[0])) != defaults[1]
            ):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            draft = (
                {
                    "kind": "replay",
                    **{k: v for k, v in req["payload"].items() if k in ("source_task", "profile")},
                }
                if req["kind"] == "replay"
                else req["payload"]["raw_draft"]
            )
            if freeze_request(self.root, draft, revision).raw != raw:
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            events = list(
                c.execute("SELECT kind,payload FROM events WHERE task=? ORDER BY seq", (row["id"],))
            )
            if any(canonical(json.loads(e[1])).decode() != e[1] for e in events):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            submissions = [json.loads(e[1]) for e in events if e[0] == "SUBMITTED"]
            task_claims = [json.loads(e[1]) for e in events if e[0] == "CLAIMED"]
            if (
                len(submissions) != 1
                or submissions[0]["config_hash"] != row["hash"]
                or row["status"] == "RUNNING"
                or row["status"] not in TERMINAL | {"QUEUED"}
                or type(row["epoch"]) is not int
                or row["epoch"] < 0
                or row["cancel"] not in (0, 1)
                or row["owner"] is not None
            ):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            if any(
                type(claim["epoch"]) is not int or type(claim["owner"]) is not str
                for claim in task_claims
            ):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            if [claim["epoch"] for claim in task_claims] != list(range(1, row["epoch"] + 1)):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            for claim in task_claims:
                if str(uuid.UUID(claim["owner"])) != claim["owner"]:
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            campaign = req.get("payload", {}).get("campaign")
            if campaign is not None:
                expected_campaigns.add(row["id"])
                if row["id"] not in campaign_rows:
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                item = self._checked_campaign_record(c, campaign_rows[row["id"]], legacy=True)
                config = req["payload"]["research"]
                registered_campaign = registered.get(campaign["id"])
                if (
                    registered_campaign is None
                    or registered_campaign["campaign_hash"] != campaign["campaign_hash"]
                    or registered_campaign["variants"].get(variant_key(config)) != config
                ):
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                units = ExperimentLedger._research_units(config)
                if item["units"] != len(units):
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                projection(
                    self.root / "tasks" / row["id"] / "campaign-attempt.json",
                    remember(self.root / "tasks" / row["id"] / "campaign-attempt.json"),
                    "TASK",
                    row["id"],
                )
            else:
                if req["kind"] != "replay":
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                config, units = None, []
            records.append(
                {
                    "data_hash": cat["snapshot"]["manifest_hash"],
                    "owner_kind": "TASK",
                    "owner_id": row["id"],
                    "key": row["key"],
                    "request_hash": row["hash"],
                    "units": units,
                    "family_id": config["family"]["id"] if config else None,
                    "family_limit": config["family"]["budget"] if config else None,
                    "service_kind": "TASK" if config else "TASK_REPLAY",
                    "output_root": str(self.root / ("research-runs" if config else "replay-runs")),
                    "_migration_decision": "REJECTED"
                    if campaign and item["over_budget"]
                    else "ADMITTED",
                }
            )
            projection(self.root / "tasks" / row["id"] / "request.json", raw, "TASK", row["id"])
            slot_rows = list(c.execute("SELECT * FROM slots WHERE task=?", (row["id"],)))
            slot_states = {r["slot"]: r["state"] for r in slot_rows}
            slots = {r["slot"]: json.loads(r["binding"]) for r in slot_rows}
            if row["status"] == "QUEUED" and slots:
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            for name, binding in slots.items():
                if (
                    binding["task_id"] != row["id"]
                    or binding["plan_hash"] != row["hash"]
                    or binding["workspace_id"] != self.workspace_id
                ):
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                root = guard_path(binding["physical_ledger_root"]) / binding["child_run_id"]
                if not root.exists():
                    starts = [json.loads(e[1]) for e in events if e[0] == "CORE_START_INTENT"]
                    if (
                        row["status"] == "SUCCEEDED"
                        or slot_states[name] not in ("ALLOCATED", "BOUND")
                        or row["status"] == "CANCELLED"
                        and slot_states[name] != "ALLOCATED"
                        or any(e.get("slot_id") == name for e in starts)
                    ):
                        raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                    continue
                manifest, _ = read_core(binding)
                for path in root.iterdir():
                    if path.is_file() and path.suffix in (".json", ".jsonl", ".html"):
                        remember(path)
                if row["status"] == "SUCCEEDED" and manifest["status"] != "SUCCEEDED":
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                if name == "R":
                    run_owners[binding["child_run_id"]] = ("TASK", row["id"], units)
                if row["status"] == "CANCELLED" and binding["service_kind"] in ("P5", "P5_REPLAY"):
                    TaskService._verified_financial_prefix(binding)
                    if binding["service_kind"] == "P5_REPLAY":
                        source = c.execute(
                            "SELECT binding FROM slots WHERE task=? AND slot='B'",
                            (req["payload"]["source_task"],),
                        ).fetchone()
                        if source is None:
                            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                        TaskService._verified_financial_prefix(json.loads(source[0]))
                    for path in (root / "transactions").iterdir():
                        if path.name != ".lock":
                            remember(path)
            if row["status"] == "SUCCEEDED":
                pointer = json.loads(row["completion"])
                if (
                    canonical(pointer).decode() != row["completion"]
                    or set(pointer) != {"file", "sha256"}
                    or type(pointer["file"]) is not str
                    or re.fullmatch(r"completion(?:-[0-9]+)?\.json", pointer["file"]) is None
                ):
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                completion_raw = remember(self.root / "tasks" / row["id"] / pointer["file"])
                completion = json.loads(completion_raw)
                terminals = [json.loads(e[1]) for e in events if e[0] == "SUCCEEDED"]
                proofs = verify_core_proofs(
                    self.root,
                    self.workspace_id,
                    row["id"],
                    row,
                    {
                        name: {"binding": binding, "state": slot_states[name]}
                        for name, binding in slots.items()
                    },
                    lambda name: c.execute(
                        "SELECT raw,hash FROM adapted_requests WHERE task=? AND slot=?",
                        (row["id"], name),
                    ).fetchone(),
                )
                plan_path = self.root / "tasks" / row["id"] / "resolved-plan.json"
                plan_raw = remember(plan_path) if plan_path.exists() else None
                if (
                    canonical(completion) != completion_raw
                    or hashlib.sha256(completion_raw).hexdigest() != pointer["sha256"]
                    or completion["config_hash"] != row["hash"]
                    or completion["task_id"] != row["id"]
                    or completion["kind"] != req["kind"]
                    or completion["scope"] != "ENGINEERING_TEST_ONLY"
                    or completion["financial_approval"] != "NONE"
                    or completion["claim_epoch"] != row["epoch"]
                    or terminals != [{"completion": pointer, "claim_epoch": row["epoch"]}]
                    or completion["core_proofs"] != proofs
                    or completion["resolved_plan_sha256"]
                    != (hashlib.sha256(plan_raw).hexdigest() if plan_raw is not None else None)
                ):
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                for binding in slots.values():
                    if binding["service_kind"] in ("P5", "P5_REPLAY"):
                        transactions = (
                            guard_path(binding["physical_ledger_root"])
                            / binding["child_run_id"]
                            / "transactions"
                        )
                        for path in transactions.iterdir():
                            if path.name != ".lock":
                                remember(path)
        if expected_campaigns != set(campaign_rows):
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        ledger = ExperimentLedger(self.root / "research-runs")
        trial_path = self.root / "research-runs/trials.jsonl"
        trial_rows = read_chain(trial_path)
        if trial_path.exists():
            remember(trial_path)
        trial_keys = set()
        for trial in trial_rows:
            payload = trial["payload"]
            run = payload["run_id"]
            root = ledger.path(run)
            cfg_raw, line_raw = remember(root / "config.json"), remember(root / "lineage.json")
            cfg, lineage = json.loads(cfg_raw), json.loads(line_raw)
            if (
                lineage["data_hash"] != cat["snapshot"]["manifest_hash"]
                or lineage["code_bundle"] != cat["code_bundle"]
            ):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            ledger.verify(run)
            registered = [
                e
                for e in read_chain(root / "events.jsonl")
                if e["kind"] == "TRIAL_REGISTERED" and e["payload"] == payload
            ]
            if len(registered) != 1 or (run, payload["hypothesis"]) in trial_keys:
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            trial_keys.add((run, payload["hypothesis"]))
            if run not in run_owners:
                if lineage.get("task_binding") is not None:
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                units = ExperimentLedger._research_units(cfg)
                run_trials = [r for r in trial_rows if r["payload"]["run_id"] == run]
                if {r["payload"]["hypothesis"] for r in run_trials} != {
                    u["hypothesis_alias"] for u in units
                }:
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                decisions = {bool(r["payload"]["over_budget"]) for r in run_trials}
                if len(decisions) != 1:
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                records.append(
                    {
                        "data_hash": lineage["data_hash"],
                        "owner_kind": "LEGACY",
                        "owner_id": run,
                        "key": digest({"ledger_root": str(ledger.root.resolve()), "run_id": run}),
                        "request_hash": digest(cfg),
                        "units": units,
                        "family_id": cfg["family"]["id"],
                        "family_limit": cfg["family"]["budget"],
                        "service_kind": "LEGACY",
                        "output_root": str(ledger.root),
                        "_migration_decision": "REJECTED" if next(iter(decisions)) else "ADMITTED",
                    }
                )
                run_owners[run] = ("LEGACY", run, units)
            owner_kind, owner_id, units = run_owners[run]
            ordinals = [
                i for i, u in enumerate(units) if u["hypothesis_alias"] == payload["hypothesis"]
            ]
            if len(ordinals) != 1 or cfg["family"]["id"] != payload["family"]:
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            claims.append(
                {
                    "owner_kind": owner_kind,
                    "owner_id": owner_id,
                    "ordinal": ordinals[0],
                    "ledger_root": str(ledger.root),
                    "run_id": run,
                    "config_hash": digest(cfg),
                    "lineage_hash": digest(lineage),
                    "claim_payload": {
                        "hypothesis": payload["hypothesis"],
                        "definition_hash": units[ordinals[0]]["definition_hash"],
                    },
                }
            )
            projection(trial_path, canonical(trial) + b"\n", owner_kind, owner_id, "TRIAL")
        # Orphan/nonterminal research directories cannot be ignored by an empty trial scan.
        actual_runs = {p.name for p in ledger.root.iterdir() if p.is_dir()}
        if actual_runs != set(run_owners):
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        for run in run_owners:
            registered = [
                e["payload"]
                for e in read_chain(ledger.path(run) / "events.jsonl")
                if e["kind"] == "TRIAL_REGISTERED"
            ]
            original_trials = [r["payload"] for r in trial_rows if r["payload"]["run_id"] == run]
            if registered != original_trials:
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            for path in ledger.path(run).iterdir():
                if path.is_file() and path.suffix in (".json", ".jsonl", ".html"):
                    remember(path)
        return {
            "complete": True,
            "records": records,
            "projections": projections,
            "claims": claims,
            "evidence": {
                "schema": "complete-same-bundle-budget-migration/1",
                "catalogue_hash": digest(cat),
                "files": list(files.values()),
                "task_ids": sorted(task_ids),
                "trial_keys": sorted(trial_keys),
                "source_rows_hash": digest([{k: row[k] for k in row.keys()} for row in task_rows]),
            },
        }

    def _reserve_campaign(
        self, c, task, request, campaign, directory, *, raw, key, activation=None
    ):
        from aqrp.services.research import hypotheses

        if campaign != request["payload"]["campaign"] or campaign["budget"] != 12:
            raise ContractError("CAMPAIGN_ATTEMPT_IDENTITY_CHANGED")
        rows = list(c.execute("SELECT * FROM campaign_attempts"))
        expected = {
            r["id"]
            for r in c.execute("SELECT id,raw FROM tasks WHERE id!=?", (task,))
            if "campaign" in json.loads(r["raw"]).get("payload", {})
        }
        if expected != {r["task"] for r in rows}:
            raise ContractError("CAMPAIGN_ATTEMPT_HISTORY_INCOMPLETE")
        verified = [self._checked_campaign_record(c, r, authority_verified=True) for r in rows]
        # This transaction entered only after all projections were published.
        # Verify the complete immutable authority once, rather than once per peer.
        self.budget.verify(c, require_projections=True)
        own_runs = {
            json.loads(r[0])["child_run_id"]
            for r in c.execute(
                "SELECT binding FROM slots JOIN campaign_attempts ON slots.task=campaign_attempts.task WHERE slot='R'"
            )
        }
        trial_root = guard_path(self.root / "research-runs")
        trial_root.mkdir(exist_ok=True)
        legacy = [
            r["payload"]
            for r in (
                json.loads(bytes(row[0]))
                for row in c.execute(
                    "SELECT content FROM admission_outbox WHERE kind='TRIAL' ORDER BY seq"
                )
            )
            if r["payload"].get("data_hash") == campaign["data_hash"]
            and r["payload"]["run_id"] not in own_runs
        ]
        peers = [x for x in verified if x["campaign"]["data_hash"] == campaign["data_hash"]]
        units = [h["hypothesis"] for h in hypotheses(request["payload"]["research"])]
        legacy_admissions = [
            json.loads(row[0])
            for row in c.execute(
                "SELECT payload FROM admissions WHERE data_hash=? AND owner_kind='LEGACY'",
                (campaign["data_hash"],),
            )
        ]
        # Retain the original requested-attempt literal, including refusals.
        # Actual debits and refused units are separate immutable authority fields.
        used = sum(x["units"] for x in peers) + sum(len(a["units"]) for a in legacy_admissions)
        config = request["payload"]["research"]
        self._insert_task(c, task, key, raw, request)
        admission = self.budget.reserve(
            c,
            data_hash=campaign["data_hash"],
            owner_kind="TASK",
            owner_id=task,
            key=key,
            request_hash=digest(request),
            units=[
                {
                    "hypothesis_alias": alias,
                    "definition_hash": config["family"]["definitions"][alias],
                }
                for alias in units
            ],
            family_id=config["family"]["id"],
            family_limit=config["family"]["budget"],
            service_kind="TASK",
            output_root=self.root / "research-runs",
            activation=activation,
        )
        record = {
            "campaign": campaign,
            "task_id": task,
            "task_config_hash": digest(request),
            "hypothesis_ids": units,
            "units": len(units),
            "prior_reserved_units": used,
            "prior_legacy_trials": len(legacy),
            "prior_legacy_admission_units": sum(len(a["units"]) for a in legacy_admissions),
            "prior_other_campaign_attempts": sum(
                x["campaign"]["campaign_hash"] != campaign["campaign_hash"] for x in peers
            ),
            "prior_other_family_legacy_trials": sum(
                x["family"] != request["payload"]["research"]["family"]["id"] for x in legacy
            ),
            "over_budget": admission["decision"] != "ADMITTED",
            "admission": admission,
            "reservation_policy": "Shared data budget12, atomic with Task; all failures/cancellations retained, no refunds; idempotent retries reuse original reservation",
        }
        self.budget.queue_projection(
            c,
            directory / "campaign-attempt.json",
            canonical(record),
            admission["admission_id"],
            kind="SIDECAR",
        )
        c.execute(
            "INSERT INTO campaign_attempts VALUES (?,?,?,?,?,?,?)",
            (
                task,
                campaign["id"],
                campaign["campaign_hash"],
                campaign["data_hash"],
                len(units),
                canonical(record).decode(),
                digest(record),
            ),
        )
        return record

    def research_attempt(self, task):
        if not self.managed:
            raise ContractError("CAMPAIGN_ATTEMPT_REQUIRED")
        self.budget.materialize()
        with self.transaction() as c:
            self.budget.verify(c)
            row = c.execute("SELECT * FROM campaign_attempts WHERE task=?", (task,)).fetchone()
            if row is None:
                raise ContractError("CAMPAIGN_ATTEMPT_REQUIRED")
            return self._checked_campaign_record(c, row)

    def claim(self, task, *, recover=False):
        owner = str(uuid.uuid4())
        if self.managed:
            self.budget.materialize()
        with self.transaction() as c:
            if self.managed:
                self.budget.verify(c)
            row = c.execute("SELECT * FROM tasks WHERE id=?", (task,)).fetchone()
            if row is None or row["status"] in TERMINAL:
                raise ContractError("TASK_NOT_CLAIMABLE")
            if row["owner"]:
                raise ContractError("TASK_ALREADY_CLAIMED")
            if row["status"] != "QUEUED" and not recover:
                raise ContractError("TASK_RECOVERY_REQUIRED")
            epoch = row["epoch"] + 1
            c.execute(
                "UPDATE tasks SET owner=?,epoch=?,status='RUNNING' WHERE id=?", (owner, epoch, task)
            )
            self.event(c, task, "CLAIMED", {"owner": owner, "epoch": epoch, "recovery": recover})
        return owner, epoch

    def abandon(self, task, owner, epoch):
        """Explicit owner release; no PID/mtime takeover and no automatic duplicate worker."""
        with self.transaction() as c:
            row = c.execute("SELECT owner,epoch FROM tasks WHERE id=?", (task,)).fetchone()
            if row is None or (row[0], row[1]) != (owner, epoch):
                raise ContractError("STALE_TASK_CLAIM")
            c.execute("UPDATE tasks SET owner=NULL WHERE id=?", (task,))
            self.event(c, task, "CLAIM_RELEASED", {"epoch": epoch})

    def cancel(self, task, *, activation=None):
        with self.transaction() as c:
            current = (
                c.execute(
                    "SELECT payload FROM execution_plan_activations ORDER BY seq DESC LIMIT 1"
                ).fetchone()
                if self.managed
                else None
            )
            if activation is not None and (current is None or json.loads(current[0]) != activation):
                raise ContractError("EXECUTION_PLAN_ACTIVATION_STALE")
            if current is not None:
                admission = self.budget.lookup_owner(c, "TASK", task)
                if admission is None or admission.get("actor", {}).get("activation") != json.loads(
                    current[0]
                ):
                    raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
            row = c.execute("SELECT status FROM tasks WHERE id=?", (task,)).fetchone()
            if row is None:
                raise ContractError("UNKNOWN_TASK")
            if row[0] in TERMINAL:
                return "TOO_LATE"
            c.execute("UPDATE tasks SET cancel=1 WHERE id=?", (task,))
            if row[0] == "QUEUED":
                c.execute("UPDATE tasks SET status='CANCELLED' WHERE id=?", (task,))
            self.event(c, task, "CANCEL_REQUESTED", {})
            return "CANCELLED" if row[0] == "QUEUED" else "CANCEL_REQUESTED"

    def slots(self, task):
        with self.transaction() as c:
            return {
                r["slot"]: {"binding": json.loads(r["binding"]), "state": r["state"]}
                for r in c.execute("SELECT * FROM slots WHERE task=? ORDER BY slot", (task,))
            }

    def defaults(self, revision=None):
        if revision is not None and (type(revision) is not int or revision < 0):
            raise ContractError("UNKNOWN_DEFAULTS_REVISION")
        empty = {"revision": 0, "payload": "{}", "hash": digest({})}
        if revision == 0:
            return empty
        with self.transaction() as c:
            row = (
                c.execute("SELECT * FROM defaults ORDER BY revision DESC LIMIT 1").fetchone()
                if revision is None
                else c.execute("SELECT * FROM defaults WHERE revision=?", (revision,)).fetchone()
            )
            if row is None:
                if revision is None:
                    return empty
                raise ContractError("UNKNOWN_DEFAULTS_REVISION")
            if digest(json.loads(row["payload"])) != row["hash"]:
                raise ContractError("DEFAULTS_REVISION_IDENTITY_CHANGED")
            return dict(row)

    def save_defaults(self, expected, payload):
        with self.transaction() as c:
            row = c.execute("SELECT max(revision) FROM defaults").fetchone()[0] or 0
            if row != expected:
                raise ContractError("DEFAULTS_REVISION_CONFLICT")
            c.execute(
                "INSERT INTO defaults VALUES (?,?,?)",
                (row + 1, canonical(payload).decode(), digest(payload)),
            )
        return row + 1

    def rollback_defaults(self, expected, target):
        if type(target) is not int or target < 1:
            raise ContractError("UNKNOWN_DEFAULTS_REVISION")
        payload = json.loads(self.defaults(target)["payload"])
        return self.save_defaults(expected, payload)
