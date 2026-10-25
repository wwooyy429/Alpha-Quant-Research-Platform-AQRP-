"""SQLite task allocation/claims. Engineering integrity, not OS isolation."""

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import immutable_write, mutex, read_chain

SETUP_TIMEOUT_SECONDS = 30.0

TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED"}


class TaskState:
    def __init__(self, root):
        self.root = guard_path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        control = guard_path(self.root / "task-control")
        control.mkdir(exist_ok=True)
        self.db = control / "tasks.sqlite"
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

    def submit(self, raw, key, *, campaign=None):
        if not isinstance(key, str) or not 1 <= len(key) <= 128:
            raise ContractError("INVALID_IDEMPOTENCY_KEY")
        request = json.loads(raw)
        with self.transaction() as c:
            prior = c.execute("SELECT * FROM tasks WHERE key=?", (key,)).fetchone()
            if prior:
                if prior["hash"] != digest(request):
                    raise ContractError("IDEMPOTENCY_CONFIG_CONFLICT")
                return prior["id"]
            task = str(uuid.uuid4())
            directory = guard_path(self.root / "tasks" / task)
            directory.mkdir(parents=True)
            immutable_write(directory / "request.json", raw)
            c.execute(
                "INSERT INTO tasks(id,key,raw,hash,status,epoch) VALUES (?,?,?,?,?,0)",
                (task, key, raw.decode(), digest(request), "QUEUED"),
            )
            control = None
            if campaign is not None:
                control = self._reserve_campaign(c, task, request, campaign, directory)
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

    def _checked_campaign_record(self, c, row):
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
        return item

    def _reserve_campaign(self, c, task, request, campaign, directory):
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
        verified = [self._checked_campaign_record(c, r) for r in rows]
        own_runs = {
            json.loads(r[0])["child_run_id"]
            for r in c.execute(
                "SELECT binding FROM slots JOIN campaign_attempts ON slots.task=campaign_attempts.task WHERE slot='R'"
            )
        }
        trial_root = guard_path(self.root / "research-runs")
        trial_root.mkdir(exist_ok=True)
        with mutex(trial_root / ".trials-lock"):
            legacy = [
                r["payload"]
                for r in read_chain(trial_root / "trials.jsonl")
                if r["payload"].get("data_hash") == campaign["data_hash"]
                and r["payload"]["run_id"] not in own_runs
            ]
        peers = [x for x in verified if x["campaign"]["data_hash"] == campaign["data_hash"]]
        units = [h["hypothesis"] for h in hypotheses(request["payload"]["research"])]
        used = sum(x["units"] for x in peers) + len(legacy)
        record = {
            "campaign": campaign,
            "task_id": task,
            "task_config_hash": digest(request),
            "hypothesis_ids": units,
            "units": len(units),
            "prior_reserved_units": used,
            "prior_legacy_trials": len(legacy),
            "prior_other_campaign_attempts": sum(
                x["campaign"]["campaign_hash"] != campaign["campaign_hash"] for x in peers
            ),
            "prior_other_family_legacy_trials": sum(
                x["family"] != request["payload"]["research"]["family"]["id"] for x in legacy
            ),
            "over_budget": used + len(units) > 12,
            "reservation_policy": "Shared data budget12, atomic with Task; all failures/cancellations retained, no refunds; idempotent retries reuse original reservation",
        }
        immutable_write(directory / "campaign-attempt.json", canonical(record))
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
        with self.transaction() as c:
            row = c.execute("SELECT * FROM campaign_attempts WHERE task=?", (task,)).fetchone()
            if row is None:
                raise ContractError("CAMPAIGN_ATTEMPT_REQUIRED")
            return self._checked_campaign_record(c, row)

    def claim(self, task, *, recover=False):
        owner = str(uuid.uuid4())
        with self.transaction() as c:
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

    def cancel(self, task):
        with self.transaction() as c:
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
