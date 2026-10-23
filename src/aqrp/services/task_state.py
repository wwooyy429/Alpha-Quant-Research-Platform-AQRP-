"""SQLite task allocation/claims. Engineering integrity, not OS isolation."""

import json
import sqlite3
import uuid
from contextlib import contextmanager

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import immutable_write

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
        c = sqlite3.connect(self.db, timeout=30, isolation_level=None)
        try:
            c.row_factory = sqlite3.Row
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("PRAGMA synchronous=FULL")
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

    def submit(self, raw, key):
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
            self.event(c, task, "SUBMITTED", {"config_hash": digest(request)})
            return task

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

    def defaults(self):
        with self.transaction() as c:
            row = c.execute("SELECT * FROM defaults ORDER BY revision DESC LIMIT 1").fetchone()
            return dict(row) if row else {"revision": 0, "payload": "{}", "hash": digest({})}

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
        with self.transaction() as c:
            row = c.execute("SELECT payload FROM defaults WHERE revision=?", (target,)).fetchone()
            if row is None:
                raise ContractError("UNKNOWN_DEFAULTS_REVISION")
            payload = json.loads(row[0])
        return self.save_defaults(expected, payload)
