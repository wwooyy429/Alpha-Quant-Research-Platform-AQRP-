"""One SQLite research budget for every managed engineering entry point.

The authority is an engineering integrity control, not a host permission boundary.
Callers which already own a TaskState transaction pass that exact connection.  No
method below commits a caller's transaction, and no file lock is held while an
authority transaction is acquired.
"""

import hashlib
import inspect
import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError

SCHEMA = "common-research-admission/1"
SHARED_LIMIT = 12
_PLAN_SEAL = object()


def _guard(path):
    # Kept here rather than importing transactions -> ledger -> admission.
    path = Path(path).absolute()
    for candidate in (path, *path.parents):
        if (
            candidate.is_symlink()
            or candidate.is_junction()
            or (candidate.is_file() and candidate.stat().st_nlink > 1)
        ):
            raise ContractError("SIMULATION_LINK_PATH_FORBIDDEN")
    return path


def _json(raw):
    try:
        value = json.loads(raw)
        if not isinstance(value, dict) or canonical(value) != (
            raw.encode() if isinstance(raw, str) else raw
        ):
            raise ValueError("noncanonical")
        return value
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ContractError("ADMISSION_HISTORY_UNVERIFIED") from exc


def _read(path):
    try:
        return _json(_guard(path).read_bytes())
    except OSError as exc:
        raise ContractError("ADMISSION_HISTORY_UNVERIFIED") from exc


def _immutable(path, raw):
    path = _guard(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        return
    try:
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        if path.read_bytes() != raw:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")


def _table(c, name):
    return c.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()


def _projection_bytes(path, kind):
    """Read a complete publication, never a writer's partial OS write.

    The reader already owns the authority transaction and may then take the
    file lock. Publishers release the file lock before opening any transaction;
    the reverse acquisition is forbidden throughout this module.
    """
    from aqrp.experiments.ledger import mutex

    path = _guard(path)
    if not path.parent.exists():
        return b""
    lock = path.parent / (".trials-lock" if kind == "TRIAL" else ".admission-projection-lock")
    with mutex(lock, timeout=30):
        return path.read_bytes() if path.exists() else b""


def _catalogue(root):
    from aqrp.factors.admission import bundle_hash

    cat = _read(root / "catalog.json")
    if (
        cat.get("schema") != "task-catalog/2"
        or digest({k: v for k, v in cat.items() if k != "revision"}) != cat.get("revision")
        or cat.get("scope") != "ENGINEERING_TEST_ONLY"
        or cat.get("financial_approval") != "NONE"
        or cat.get("code_bundle") != bundle_hash()
    ):
        raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    for field in ("snapshot", "exposures"):
        if not _guard(cat[field]["root"]).is_relative_to(root):
            raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    return cat


def _task_terminal(c, budget, task_id, request_hash):
    """Read original terminal proofs without opening another DB transaction."""
    task = c.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if task is None:
        raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
    task = dict(task)
    raw = _guard(budget.root / "tasks" / task_id / "request.json").read_bytes()
    request = _json(raw)
    if (
        task["raw"] != raw.decode()
        or task["hash"] != request_hash
        or digest(request) != request_hash
    ):
        raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
    if task["status"] == "SUCCEEDED":
        from aqrp.services.tasks import read_core

        pointer = _json(task["completion"])
        name = pointer.get("file")
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or not name.startswith("completion")
            or not name.endswith(".json")
        ):
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        proof_raw = _guard(budget.root / "tasks" / task_id / name).read_bytes()
        proof = _json(proof_raw)
        if (
            hashlib.sha256(proof_raw).hexdigest() != pointer.get("sha256")
            or proof.get("config_hash") != request_hash
            or proof.get("claim_epoch") != task["epoch"]
        ):
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        actual = {}
        actual_runs = {}
        for row in c.execute("SELECT slot,binding FROM slots WHERE task=?", (task_id,)):
            binding = _json(row[1])
            manifest, _ = read_core(binding)
            actual[row[0]] = {
                "binding_hash": digest(binding),
                "manifest_hash": digest(manifest),
                "status": manifest["status"],
            }
            actual_runs[row[0]] = binding["child_run_id"]
            if manifest["status"] != "SUCCEEDED":
                raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        if actual != proof.get("core_proofs"):
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        plan = budget.root / "tasks" / task_id / "resolved-plan.json"
        plan_hash = hashlib.sha256(plan.read_bytes()).hexdigest() if plan.exists() else None
        if proof.get("resolved_plan_sha256") != plan_hash:
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        if request["kind"] == "research":
            expected = {"R"}
        else:
            resolved = _read(plan)
            if (
                resolved.get("task_config_hash") != request_hash
                or resolved.get("slots") != actual_runs
            ):
                raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
            count = resolved.get("decision_count")
            if type(count) is not int or count < (
                1 if request["kind"] == "engineering_pipeline" else 0
            ):
                raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
            expected = ({"R", "B"} if request["kind"] == "engineering_pipeline" else {"E"}) | {
                f"P:{i}" for i in range(count)
            }
        if set(actual) != expected:
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
    return task


def _resolved_slot_request(c, budget, slot, owner_id):
    if "source_slot" not in slot:
        return slot["request_hash"]
    source = c.execute(
        "SELECT payload,binding FROM execution_plan_slots WHERE slot=?", (slot["source_slot"],)
    ).fetchone()
    if source is None or source[1] is None:
        raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
    original = _json(source[0])
    binding = _json(source[1])
    if (
        original["request_hash"] != slot["originalsource_request_hash"]
        or original["service_kind"] != "TASK"
    ):
        raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
    source_task = _task_terminal(c, budget, binding["owner_id"], original["request_hash"])
    if source_task["status"] != "SUCCEEDED":
        raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
    template = json.loads(canonical(slot["request_template"]))
    if template.get("kind") != "replay" or template.get("payload") != {
        "source_task": "$SOURCE_TASK",
        "profile": slot["profile"],
    }:
        raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
    template["payload"]["source_task"] = binding["owner_id"]
    if owner_id is not None:
        request = c.execute("SELECT raw,hash FROM tasks WHERE id=?", (owner_id,)).fetchone()
        if request is None or _json(request[0]) != template or request[1] != digest(template):
            raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
    return digest(template)


def _ancestors(path):
    roots = []
    for candidate in (_guard(path), *_guard(path).parents):
        if (
            (candidate / "catalog.json").exists()
            or (candidate / "task-control/admission-anchor.json").exists()
            or _managed_remnant(candidate)
        ):
            roots.append(candidate)
    if len(roots) > 1:
        raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    return roots


def _managed_remnant(root):
    """Deleting discoverable metadata must not turn a managed W into standalone."""
    control = _guard(root / "task-control")
    if not control.exists():
        return False
    if (control / "execution-plan.json").exists() or (control / "admissions").is_dir():
        return True
    db = _guard(control / "tasks.sqlite")
    if db.exists():
        c = None
        try:
            c = sqlite3.connect("file:" + db.as_posix() + "?mode=ro", uri=True)
            if _table(c, "admission_meta"):
                return True
            if _table(c, "tasks"):
                fields = {r[1] for r in c.execute("PRAGMA table_info(tasks)")}
                if "raw" in fields:
                    for row in c.execute("SELECT raw FROM tasks"):
                        value = _json(row[0])
                        if value.get("schema") == "task-request/1" or "code_bundle" in value:
                            return True
            if (root / "research-runs/trials.jsonl").exists():
                return True
        except (sqlite3.DatabaseError, OSError) as exc:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED") from exc
        finally:
            if c is not None:
                c.close()
    tasks = _guard(root / "tasks")
    if tasks.is_dir():
        for directory in tasks.iterdir():
            path = _guard(directory / "request.json")
            if path.exists() and _read(path).get("schema") == "task-request/1":
                return True
    return False


def resolve_admission_domain(
    output_root, config=None, lineage=None, snapshot_ref=None, exposure_ref=None
):
    """Return the one physical managed domain, or a genuine standalone None.

    A managed input never permits an unmanaged/alternate output.  A managed
    output must be precisely W/research-runs, and original source identities must
    agree with its catalogue.  No receipt/purpose/campaign token chooses scope.
    """
    output = _guard(output_root)
    paths = [output]
    for ref in (snapshot_ref, exposure_ref):
        if ref is not None:
            paths.append(_guard(ref.root if hasattr(ref, "root") else ref["root"]))
    # Direct-ledger verification uses immutable source roots in admission sidecar.
    for obj in (lineage or {}, config or {}):
        source = obj.get("admission_inputs", obj.get("admission_source"))
        if source is not None:
            if not isinstance(source, dict):
                raise ContractError("ADMISSION_DOMAIN_CONFLICT")
            paths.extend(
                _guard(source[k]) for k in ("snapshot_root", "exposure_root") if source.get(k)
            )
    discovered = [_ancestors(p) for p in paths]
    domains = {str(item) for roots in discovered for item in roots}
    if not domains:
        return None
    if len(domains) != 1:
        raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    root = _guard(next(iter(domains)))
    if output != root / "research-runs" or any(not p.is_relative_to(root) for p in paths):
        raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    cat = _catalogue(root)
    authority = BudgetAuthority(root)
    if not authority.db.is_file() or not authority.anchor.is_file():
        raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
    for ref, field in ((snapshot_ref, "snapshot"), (exposure_ref, "exposures")):
        if ref is not None:
            expected = cat[field]
            actual_root = _guard(ref.root if hasattr(ref, "root") else ref["root"])
            actual_hash = (
                ref.manifest_hash if hasattr(ref, "manifest_hash") else ref["manifest_hash"]
            )
            if actual_root != _guard(expected["root"]) or actual_hash != expected["manifest_hash"]:
                raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    if lineage and lineage.get("data_hash") != cat["snapshot"]["manifest_hash"]:
        raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    if lineage and lineage.get("code_bundle") != cat["code_bundle"]:
        raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    if lineage and (
        lineage.get("exposure_hash") != cat["exposures"]["manifest_hash"]
        or lineage.get("coverage_hash") != cat.get("coverage", {}).get("checksum")
    ):
        raise ContractError("ADMISSION_DOMAIN_CONFLICT")
    with authority.transaction() as c:
        authority.verify(c)
    return authority


class BudgetAuthority:
    def __init__(self, workspace_root):
        self.root = _guard(workspace_root)
        self.db = _guard(self.root / "task-control/tasks.sqlite")
        self.anchor = _guard(self.root / "task-control/admission-anchor.json")

    @contextmanager
    def transaction(self):
        if not self.db.is_file():
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        c = None
        try:
            c = sqlite3.connect(self.db, timeout=0, isolation_level=None)
            c.row_factory = sqlite3.Row
            deadline = time.monotonic() + 30
            while True:
                try:
                    c.execute("PRAGMA synchronous=FULL")
                    c.execute("BEGIN IMMEDIATE")
                    break
                except sqlite3.OperationalError as exc:
                    code = getattr(exc, "sqlite_errorcode", None)
                    if code is None or code & 0xFF not in (
                        sqlite3.SQLITE_BUSY,
                        sqlite3.SQLITE_LOCKED,
                    ):
                        raise
                    if time.monotonic() >= deadline:
                        raise ContractError("ADMISSION_BUSY", retryable=True) from exc
                    time.sleep(0.01)
            try:
                yield c
                c.commit()
            except BaseException:
                c.rollback()
                raise
        except sqlite3.DatabaseError as exc:
            code = getattr(exc, "sqlite_errorcode", None)
            if code is not None and code & 0xFF in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                raise ContractError("ADMISSION_BUSY", retryable=True) from exc
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED") from exc
        finally:
            if c is not None:
                c.close()

    connection = transaction

    def initialize(self, c, workspace_id, history_verifier=None):
        """Initialize a fresh authority, or verify an existing immutable anchor.

        A nonempty pre-schema history requires a complete trusted import; the
        verifier is supplied by TaskState, which owns its original task schema.
        It cannot silently turn an unreadable history into zero debits.
        """
        if not c.in_transaction:
            raise ContractError("ADMISSION_TRANSACTION_REQUIRED")
        existing = bool(_table(c, "admission_meta"))
        if self.anchor.exists() and not existing:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        migration = None
        if not existing:
            has_history = (
                any(
                    _table(c, name) and c.execute("SELECT count(*) FROM " + name).fetchone()[0]
                    for name in ("tasks", "campaign_attempts")
                )
                or (self.root / "research-runs/trials.jsonl").exists()
            )
            if has_history:
                if history_verifier is None:
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                migration = history_verifier(c)
                if (
                    not isinstance(migration, dict)
                    or migration.get("complete") is not True
                    or not isinstance(migration.get("records"), list)
                    or not migration.get("evidence")
                ):
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                for item in migration["evidence"].get("files", []):
                    path = _guard(item["path"])
                    if (
                        not path.is_relative_to(self.root)
                        or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]
                        or item.get("bytes", path.stat().st_size) != path.stat().st_size
                    ):
                        raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            statements = [
                "CREATE TABLE admission_meta (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL, hash TEXT NOT NULL)",
                "CREATE TABLE budget_domains (data_hash TEXT PRIMARY KEY, payload TEXT NOT NULL, hash TEXT NOT NULL)",
                "CREATE TABLE admissions (id TEXT PRIMARY KEY, owner_kind TEXT NOT NULL, owner_id TEXT NOT NULL, key TEXT NOT NULL, data_hash TEXT NOT NULL, family TEXT, decision TEXT NOT NULL, debit INTEGER NOT NULL CHECK(debit>=0), payload TEXT NOT NULL, hash TEXT NOT NULL, UNIQUE(owner_kind,key), UNIQUE(owner_kind,owner_id))",
                "CREATE TABLE admission_units (admission_id TEXT, ordinal INTEGER, payload TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(admission_id,ordinal))",
                "CREATE TABLE trial_claims (admission_id TEXT, ordinal INTEGER, ledger_root TEXT NOT NULL, run_id TEXT NOT NULL, payload TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(admission_id,ordinal), UNIQUE(ledger_root,run_id,ordinal))",
                "CREATE TABLE admission_outbox (seq INTEGER PRIMARY KEY, admission_id TEXT NOT NULL, kind TEXT NOT NULL, path TEXT NOT NULL, content BLOB NOT NULL, hash TEXT NOT NULL, materialized INTEGER NOT NULL DEFAULT 0)",
                "CREATE TABLE admission_events (seq INTEGER PRIMARY KEY, previous_hash TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, hash TEXT NOT NULL)",
                "CREATE TABLE execution_plans (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL, hash TEXT NOT NULL)",
                "CREATE TABLE execution_plan_slots (slot TEXT PRIMARY KEY, ordinal INTEGER UNIQUE, payload TEXT NOT NULL, hash TEXT NOT NULL, client_key TEXT, owner_id TEXT, binding TEXT, binding_hash TEXT)",
                "CREATE TABLE execution_plan_activations (seq INTEGER PRIMARY KEY, payload TEXT NOT NULL, hash TEXT NOT NULL, completion TEXT, completion_hash TEXT)",
                "CREATE TABLE legacy_execution_owners (admission_id TEXT PRIMARY KEY, token TEXT NOT NULL, pid INTEGER NOT NULL, epoch INTEGER NOT NULL, released INTEGER NOT NULL DEFAULT 0)",
            ]
            for statement in statements:
                c.execute(statement)
            meta = {
                "schema": SCHEMA,
                "workspace_id": workspace_id,
                "physical_root": str(self.root),
                "shared_limit": SHARED_LIMIT,
                "migration_evidence_hash": digest(migration) if migration else None,
            }
            raw = canonical(meta)
            c.execute("INSERT INTO admission_meta VALUES (1,?,?)", (raw.decode(), digest(meta)))
            _immutable(self.anchor, raw)
            self._event(c, "INITIALIZED", meta)
            if migration:
                imported = {}
                for record in migration["records"]:
                    admitted = self.reserve(c, **record, _migrating=True)
                    imported[(admitted["owner_kind"], admitted["owner_id"])] = admitted
                for claim in migration.get("claims", []):
                    item = dict(claim)
                    admitted = imported[(item.pop("owner_kind"), item.pop("owner_id"))]
                    self.claim(c, admitted["admission_id"], **item, _migrating=True)
                for projection in migration.get("projections", []):
                    admitted = imported[(projection["owner_kind"], projection["owner_id"])]
                    seq = self.queue_projection(
                        c,
                        projection["path"],
                        bytes.fromhex(projection["content_hex"]),
                        admitted["admission_id"],
                        projection["kind"],
                    )
                    c.execute("UPDATE admission_outbox SET materialized=1 WHERE seq=?", (seq,))
                for item in migration["evidence"].get("files", []):
                    path = _guard(item["path"])
                    if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                        raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                self._event(c, "MIGRATED", migration)
        self.verify(c)
        meta = _json(c.execute("SELECT payload FROM admission_meta WHERE id=1").fetchone()[0])
        if meta["workspace_id"] != workspace_id:
            raise ContractError("ADMISSION_DOMAIN_CONFLICT")
        return meta

    def _event(self, c, kind, payload):
        prior = c.execute(
            "SELECT seq,hash FROM admission_events ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        seq = 0 if prior is None else prior[0] + 1
        previous = "0" * 64 if prior is None else prior[1]
        body = {"seq": seq, "previous_hash": previous, "kind": kind, "payload": payload}
        c.execute(
            "INSERT INTO admission_events VALUES (?,?,?,?,?)",
            (seq, previous, kind, canonical(payload).decode(), digest(body)),
        )
        return body

    def verify(self, c, require_projections=False, pending_task=None):
        """Check the complete authority and every already published projection."""
        try:
            row = c.execute("SELECT * FROM admission_meta WHERE id=1").fetchone()
            if row is None:
                raise ValueError("missing meta")
            meta = _json(row[1])
            if (
                digest(meta) != row[2]
                or meta["schema"] != SCHEMA
                or meta["physical_root"] != str(self.root)
                or meta["shared_limit"] != SHARED_LIMIT
                or self.anchor.read_bytes() != canonical(meta)
                or not _table(c, "workspace")
                or [r[0] for r in c.execute("SELECT id FROM workspace")] != [meta["workspace_id"]]
            ):
                raise ValueError("anchor")
            events = list(c.execute("SELECT * FROM admission_events ORDER BY seq"))
            previous = "0" * 64
            admitted_events, claim_events, outbox_events = {}, {}, {}
            for seq, item in enumerate(events):
                payload = _json(item[3])
                body = {"seq": seq, "previous_hash": previous, "kind": item[2], "payload": payload}
                if item[0] != seq or item[1] != previous or digest(body) != item[4]:
                    raise ValueError("event chain")
                previous = item[4]
                if item[2] == "ADMISSION":
                    admitted_events[payload["admission_id"]] = digest(payload)
                elif item[2] == "CLAIM":
                    claim_events[(payload["admission_id"], payload["ordinal"])] = digest(payload)
                elif item[2] == "OUTBOX":
                    outbox_events[payload["seq"]] = payload
            admissions = list(c.execute("SELECT * FROM admissions"))
            actual_admissions = {}
            units_expected = {}
            for item in admissions:
                body = _json(item[8])
                if digest(body) != item[9] or (
                    body["admission_id"],
                    body["owner_kind"],
                    body["owner_id"],
                    body["key"],
                    body["data_hash"],
                    body["family_id"],
                    body["decision"],
                    body["debit"],
                ) != tuple(item[:8]):
                    raise ValueError("admission identity")
                if body["debit"] != (len(body["units"]) if body["decision"] == "ADMITTED" else 0):
                    raise ValueError("debit")
                actual_admissions[item[0]] = item[9]
                for ordinal, unit in enumerate(body["units"]):
                    units_expected[(item[0], ordinal)] = unit
            if admitted_events != actual_admissions:
                raise ValueError("admission set")
            if _table(c, "tasks"):
                task_rows = {r["id"]: dict(r) for r in c.execute("SELECT * FROM tasks")}
                task_admissions = {
                    _json(a[8])["owner_id"]: _json(a[8]) for a in admissions if a[1] == "TASK"
                }
                prospective = set()
                if pending_task is not None and pending_task not in task_admissions:
                    new = task_rows.get(pending_task)
                    if (
                        new is None
                        or new.get("status") != "QUEUED"
                        or new.get("owner") is not None
                        or new.get("epoch") != 0
                        or digest(_json(new["raw"])) != new["hash"]
                    ):
                        raise ValueError("invalid prospective task")
                    prospective.add(pending_task)
                if set(task_rows) - prospective != set(task_admissions):
                    raise ValueError("task admission set")
                for owner, admission in task_admissions.items():
                    row = task_rows[owner]
                    if (
                        row["hash"] != admission["request_hash"]
                        or digest(_json(row["raw"])) != row["hash"]
                        or row["key"] != admission["key"]
                    ):
                        raise ValueError("task request changed")
                directory = self.root / "tasks"
                if directory.exists() and any(
                    not _guard(p).is_dir() or p.name not in task_rows for p in directory.iterdir()
                ):
                    raise ValueError("foreign task directory")
                expected_campaigns = {
                    owner
                    for owner, r in task_rows.items()
                    if owner not in prospective and "campaign" in _json(r["raw"]).get("payload", {})
                }
                campaign_rows = (
                    list(c.execute("SELECT * FROM campaign_attempts"))
                    if _table(c, "campaign_attempts")
                    else []
                )
                if {r["task"] for r in campaign_rows} != expected_campaigns:
                    raise ValueError("campaign admission set")
                for row in campaign_rows:
                    item = _json(row["payload"])
                    admission = task_admissions[row["task"]]
                    if (
                        digest(item) != row["hash"]
                        or item.get("task_id") != row["task"]
                        or item.get("task_config_hash") != admission["request_hash"]
                        or item.get("units") != len(admission["units"])
                        or item.get("admission") != admission
                        and not admission["migrated"]
                    ):
                        raise ValueError("campaign record changed")
            actual_units = {}
            for item in c.execute("SELECT * FROM admission_units"):
                unit = _json(item[2])
                if digest(unit) != item[3]:
                    raise ValueError("unit hash")
                actual_units[(item[0], item[1])] = unit
            if actual_units != units_expected:
                raise ValueError("unit set")
            actual_claims = {}
            claimed_trials = set()
            for item in c.execute("SELECT * FROM trial_claims"):
                body = _json(item[4])
                if (
                    digest(body) != item[5]
                    or (body["admission_id"], body["ordinal"], body["ledger_root"], body["run_id"])
                    != tuple(item[:4])
                    or body["admission_id"] not in actual_admissions
                    or (body["admission_id"], body["ordinal"]) not in actual_units
                ):
                    raise ValueError("claim identity")
                actual_claims[(item[0], item[1])] = item[5]
                key = (body["run_id"], body["unit"]["hypothesis_alias"])
                if key in claimed_trials:
                    raise ValueError("duplicate trial claim")
                claimed_trials.add(key)
            if actual_claims != claim_events:
                raise ValueError("claim set")
            domains = list(c.execute("SELECT * FROM budget_domains"))
            if {a[4] for a in admissions} != {d[0] for d in domains}:
                raise ValueError("domain set")
            for item in domains:
                domain = _json(item[1])
                if (
                    digest(domain) != item[2]
                    or domain["data_hash"] != item[0]
                    or domain["limit"] != SHARED_LIMIT
                ):
                    raise ValueError("domain")
                if sum(a[7] for a in admissions if a[4] == item[0]) > SHARED_LIMIT:
                    raise ValueError("over limit")
            outbox = list(c.execute("SELECT * FROM admission_outbox ORDER BY seq"))
            if {x[0] for x in outbox} != set(outbox_events):
                raise ValueError("outbox set")
            by_path = {}
            for item in outbox:
                seq, aid, kind, path, content, checksum, materialized = tuple(item)
                content = bytes(content)
                if (
                    aid not in actual_admissions
                    or hashlib.sha256(content).hexdigest() != checksum
                    or outbox_events[seq]
                    != {
                        "seq": seq,
                        "admission_id": aid,
                        "kind": kind,
                        "path": path,
                        "sha256": checksum,
                    }
                    or materialized not in (0, 1)
                    or require_projections
                    and not materialized
                ):
                    raise ValueError("outbox identity")
                target = _guard(path)
                if not target.is_relative_to(self.root):
                    raise ValueError("projection boundary")
                by_path.setdefault(path, []).append((kind, content, materialized))
            projected_trials = set()
            for path, items in by_path.items():
                target = _guard(path)
                wanted = b"".join(x[1] for x in items) if items[0][0] == "TRIAL" else items[0][1]
                if (
                    any(x[0] != items[0][0] for x in items)
                    or items[0][0] != "TRIAL"
                    and len(items) != 1
                ):
                    raise ValueError("projection kind")
                if items[0][0] == "TRIAL":
                    previous = "0" * 64
                    for ordinal, (_, raw, _) in enumerate(items):
                        record = _json(raw.rstrip(b"\n"))
                        body = {k: v for k, v in record.items() if k != "hash"}
                        key = (record["payload"]["run_id"], record["payload"]["hypothesis"])
                        if (
                            canonical(record) + b"\n" != raw
                            or record["seq"] != ordinal
                            or record["previous"] != previous
                            or digest(body) != record["hash"]
                            or record["kind"] != "TRIAL_ATTEMPT"
                            or key in projected_trials
                        ):
                            raise ValueError("frozen trial chain")
                        projected_trials.add(key)
                        previous = record["hash"]
                actual = _projection_bytes(target, items[0][0])
                # Only a prefix consisting of complete frozen records may await recovery.
                allowed = {b""}
                prefix = b""
                for _, raw, _ in items:
                    prefix += raw
                    allowed.add(prefix)
                materialized_length = 0
                prefix_length = 0
                for _, raw, materialized in items:
                    prefix_length += len(raw)
                    if materialized:
                        materialized_length = prefix_length
                if actual not in allowed or len(actual) < materialized_length:
                    raise ValueError("projection changed or truncated")
                if require_projections and actual != wanted:
                    raise ValueError("projection incomplete")
            trials = self.root / "research-runs/trials.jsonl"
            if claimed_trials != projected_trials:
                raise ValueError("claim projection set")
            if trials.exists() and str(trials) not in by_path and trials.read_bytes():
                raise ValueError("foreign trials")
            self._verify_plan(c)
            return meta
        except (sqlite3.DatabaseError, OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED") from exc

    def get(self, c, admission_id):
        row = c.execute("SELECT payload FROM admissions WHERE id=?", (admission_id,)).fetchone()
        if row is None:
            raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        return _json(row[0])

    def verify_admission_projections(self, c, admission_id):
        """Require this owner's publications without blocking unrelated pending work."""
        self.verify(c)
        self.get(c, admission_id)
        for row in c.execute(
            "SELECT seq,kind,path,content,materialized FROM admission_outbox WHERE admission_id=? ORDER BY seq",
            (admission_id,),
        ):
            path = _guard(row[2])
            if not row[4] or not path.is_file():
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            actual = path.read_bytes()
            if row[1] == "TRIAL":
                prefix = b"".join(
                    bytes(r[0])
                    for r in c.execute(
                        "SELECT content FROM admission_outbox WHERE path=? AND seq<=? ORDER BY seq",
                        (row[2], row[0]),
                    )
                )
                if not actual.startswith(prefix):
                    raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            elif actual != bytes(row[3]):
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        return True

    def lookup_owner(self, c, owner_kind, owner_id):
        row = c.execute(
            "SELECT payload FROM admissions WHERE owner_kind=? AND owner_id=?",
            (owner_kind, owner_id),
        ).fetchone()
        return None if row is None else _json(row[0])

    def find_run(self, c, ledger_root, run_id):
        rows = list(
            c.execute(
                "SELECT DISTINCT admission_id FROM trial_claims WHERE ledger_root=? AND run_id=?",
                (str(_guard(ledger_root)), run_id),
            )
        )
        if len(rows) > 1:
            raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        if rows:
            return self.get(c, rows[0][0])
        return self.lookup_owner(c, "LEGACY", run_id)

    def lookup_legacy_actor(self, c, request_hash, output_root, activation=None):
        return lookup_legacy_actor(c, self.root, request_hash, output_root, activation)

    def history(self, c, data_hash=None, pending_task=None):
        self.verify(c, pending_task=pending_task)
        rows = [_json(r[0]) for r in c.execute("SELECT payload FROM admissions")]
        rows = [r for r in rows if data_hash is None or r["data_hash"] == data_hash]
        return {
            "requested_units": sum(len(x["units"]) for x in rows),
            "admitted_units": sum(x["debit"] for x in rows),
            "rejected_units": sum(len(x["units"]) for x in rows if x["decision"] == "REJECTED"),
            "admissions": rows,
            "registered_trials": c.execute("SELECT count(*) FROM trial_claims").fetchone()[0],
        }

    def reserve(
        self,
        c,
        data_hash,
        owner_kind,
        owner_id,
        key,
        request_hash,
        units,
        family_id=None,
        family_limit=None,
        service_kind=None,
        output_root=None,
        activation=None,
        _migrating=False,
        _migration_decision=None,
    ):
        """Reserve the complete candidate×horizon set, once, inside the caller c."""
        if not c.in_transaction:
            raise ContractError("ADMISSION_TRANSACTION_REQUIRED")
        if _migration_decision is not None and (
            not _migrating or _migration_decision not in ("ADMITTED", "REJECTED")
        ):
            raise ContractError("ADMISSION_INTEGRITY_ERROR")
        if not _migrating:
            self.verify(c, pending_task=owner_id if owner_kind == "TASK" else None)
        has_plan = bool(c.execute("SELECT 1 FROM execution_plans").fetchone())
        if activation == {"inactive_service": True} and not has_plan:
            activation = None
        if activation is not None:
            current = c.execute(
                "SELECT payload FROM execution_plan_activations ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            if current is None or _json(current[0]) != activation:
                raise ContractError("EXECUTION_PLAN_ACTIVATION_STALE")
        if (
            owner_kind not in ("TASK", "LEGACY")
            or not owner_id
            or not isinstance(key, str)
            or not key
            or not isinstance(units, list)
            or any(
                not isinstance(u, dict)
                or set(u) != {"hypothesis_alias", "definition_hash"}
                or not all(isinstance(v, str) and v for v in u.values())
                for u in units
            )
            or len({u["hypothesis_alias"] for u in units}) != len(units)
            or family_limit is not None
            and (type(family_limit) is not int or family_limit < 1)
        ):
            raise ContractError("ADMISSION_INTEGRITY_ERROR")
        if not units and not (owner_kind == "TASK" and service_kind == "TASK_REPLAY"):
            raise ContractError("ADMISSION_INTEGRITY_ERROR")
        if owner_kind == "TASK" and _table(c, "tasks"):
            task = c.execute("SELECT raw,hash FROM tasks WHERE id=?", (owner_id,)).fetchone()
            if task is None or task[1] != request_hash or digest(_json(task[0])) != request_hash:
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            if not units and _json(task[0]).get("kind") != "replay":
                raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
        prior = c.execute(
            "SELECT payload FROM admissions WHERE owner_kind=? AND (key=? OR owner_id=?)",
            (owner_kind, key, owner_id),
        ).fetchall()
        if prior:
            if len(prior) != 1:
                raise ContractError("ADMISSION_IDEMPOTENCY_CONFLICT")
            body = _json(prior[0][0])
            if any(
                body[k] != v
                for k, v in {
                    "owner_id": owner_id,
                    "key": key,
                    "data_hash": data_hash,
                    "request_hash": request_hash,
                    "units": units,
                    "family_id": family_id,
                    "family_limit": family_limit,
                }.items()
            ):
                raise ContractError("ADMISSION_IDEMPOTENCY_CONFLICT")
            return body
        binding = None
        if _table(c, "execution_plans") and c.execute("SELECT 1 FROM execution_plans").fetchone():
            binding = bind_current_actor(
                self.root,
                service_kind or owner_kind,
                request_hash,
                output_root or self.root / "research-runs",
                client_key=key,
                owner_id=owner_id,
                units_count=len(units),
                activation=activation,
                connection=c,
                _bind=False,
            )
        if family_id is not None:
            family_history = [
                _json(r[0])
                for r in c.execute(
                    "SELECT payload FROM admissions WHERE data_hash=? AND family=?",
                    (data_hash, family_id),
                )
            ]
            if any(item["family_limit"] != family_limit for item in family_history):
                raise ContractError("ADMISSION_FAMILY_CONFLICT")
        cat = _catalogue(self.root) if (self.root / "catalog.json").exists() else None
        if cat is not None and data_hash != cat["snapshot"]["manifest_hash"]:
            raise ContractError("ADMISSION_DOMAIN_CONFLICT")
        domain = {
            "schema": SCHEMA,
            "workspace_id": _read(self.anchor)["workspace_id"],
            "workspace_anchor_sha256": hashlib.sha256(self.anchor.read_bytes()).hexdigest(),
            "data_hash": data_hash,
            "limit": SHARED_LIMIT,
            "catalogue_hash": digest(cat) if cat else None,
            "migration_saturated": False,
        }
        old_domain = c.execute(
            "SELECT payload FROM budget_domains WHERE data_hash=?", (data_hash,)
        ).fetchone()
        if old_domain is not None:
            old = _json(old_domain[0])
            if {**old, "migration_saturated": False} != domain:
                raise ContractError("ADMISSION_DOMAIN_CONFLICT")
            domain = old
        used = c.execute(
            "SELECT coalesce(sum(debit),0) FROM admissions WHERE data_hash=?", (data_hash,)
        ).fetchone()[0]
        family_used = (
            c.execute(
                "SELECT coalesce(sum(debit),0) FROM admissions WHERE data_hash=? AND family=?",
                (data_hash, family_id),
            ).fetchone()[0]
            if family_id
            else 0
        )
        code = None
        if (
            used + len(units) > SHARED_LIMIT
            or family_limit is not None
            and family_used + len(units) > family_limit
            or domain["migration_saturated"]
            and units
        ):
            code = "EXPERIMENT_BUDGET_EXCEEDED"
        elif binding and (
            len(units) > binding["grant_capacity"] or binding["max_admitted_owners"] < 1
        ):
            raise ContractError("EXECUTION_PLAN_SLOT_EXHAUSTED")
        if _migration_decision == "ADMITTED" and code:
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        if _migration_decision == "REJECTED":
            code = "EXPERIMENT_BUDGET_EXCEEDED"
            domain["migration_saturated"] = True
        if old_domain is None:
            c.execute(
                "INSERT INTO budget_domains VALUES (?,?,?)",
                (data_hash, canonical(domain).decode(), digest(domain)),
            )
        elif _migration_decision == "REJECTED":
            c.execute(
                "UPDATE budget_domains SET payload=?,hash=? WHERE data_hash=?",
                (canonical(domain).decode(), digest(domain), data_hash),
            )
        body = {
            "schema": SCHEMA,
            "admission_id": str(uuid.uuid4()),
            "owner_kind": owner_kind,
            "owner_id": owner_id,
            "key": key,
            "request_hash": request_hash,
            "data_hash": data_hash,
            "units": units,
            "family_id": family_id,
            "family_limit": family_limit,
            "decision": "REJECTED" if code else "ADMITTED",
            "code": code,
            "prior_debit": used,
            "prior_family_debit": family_used,
            "debit": 0 if code else len(units),
            "actor": binding,
            "migrated": _migrating,
            "original_migration_decision": _migration_decision,
        }
        c.execute(
            "INSERT INTO admissions VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                body["admission_id"],
                owner_kind,
                owner_id,
                key,
                data_hash,
                family_id,
                body["decision"],
                body["debit"],
                canonical(body).decode(),
                digest(body),
            ),
        )
        for ordinal, unit in enumerate(units):
            c.execute(
                "INSERT INTO admission_units VALUES (?,?,?,?)",
                (body["admission_id"], ordinal, canonical(unit).decode(), digest(unit)),
            )
        self._event(c, "ADMISSION", body)
        if binding:
            bind_current_actor(
                self.root,
                service_kind or owner_kind,
                request_hash,
                output_root or self.root / "research-runs",
                client_key=key,
                owner_id=owner_id,
                units_count=len(units),
                activation=activation,
                connection=c,
            )
        return body

    def claim(
        self,
        c,
        admission_id,
        ordinal,
        ledger_root,
        run_id,
        config_hash,
        lineage_hash,
        claim_payload=None,
        _migrating=False,
    ):
        if not _migrating:
            self.verify(c)
        admission = self.get(c, admission_id)
        historical_rejected = (
            _migrating
            and admission["migrated"]
            and admission["original_migration_decision"] == "REJECTED"
        )
        if (
            admission["decision"] != "ADMITTED"
            and not historical_rejected
            or type(ordinal) is not int
            or not 0 <= ordinal < len(admission["units"])
            or _guard(ledger_root) != self.root / "research-runs"
        ):
            raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        if not _migrating and admission["owner_kind"] == "TASK":
            if not _table(c, "slots") or not _table(c, "tasks"):
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            slot = c.execute(
                "SELECT binding FROM slots WHERE task=? AND slot='R'", (admission["owner_id"],)
            ).fetchone()
            task = c.execute(
                "SELECT raw,hash,status,owner FROM tasks WHERE id=?", (admission["owner_id"],)
            ).fetchone()
            if slot is None or task is None:
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            binding = _json(slot[0])
            if (
                binding.get("child_run_id") != run_id
                or binding.get("physical_ledger_root") != str(_guard(ledger_root))
                or binding.get("core_config_hash") != config_hash
                or task[1] != admission["request_hash"]
                or task[2] != "RUNNING"
                or not task[3]
            ):
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        elif admission["owner_kind"] == "LEGACY" and (
            admission["owner_id"] != run_id or admission["request_hash"] != config_hash
        ):
            raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        body = {
            "admission_id": admission_id,
            "ordinal": ordinal,
            "ledger_root": str(_guard(ledger_root)),
            "run_id": run_id,
            "config_hash": config_hash,
            "lineage_hash": lineage_hash,
            "unit": admission["units"][ordinal],
            "evidence": claim_payload or {},
            "historical_rejected_attempt": historical_rejected,
        }
        prior = c.execute(
            "SELECT payload FROM trial_claims WHERE admission_id=? AND ordinal=?",
            (admission_id, ordinal),
        ).fetchone()
        if prior:
            if _json(prior[0]) != body:
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            return body
        c.execute(
            "INSERT INTO trial_claims VALUES (?,?,?,?,?,?)",
            (
                admission_id,
                ordinal,
                body["ledger_root"],
                run_id,
                canonical(body).decode(),
                digest(body),
            ),
        )
        self._event(c, "CLAIM", body)
        return body

    def queue_projection(self, c, path, content, admission_id, kind="SIDECAR"):
        path = str(_guard(path))
        if (
            not Path(path).is_relative_to(self.root)
            or kind not in ("SIDECAR", "TRIAL")
            or not isinstance(content, bytes)
        ):
            raise ContractError("ADMISSION_INTEGRITY_ERROR")
        self.get(c, admission_id)
        old = list(c.execute("SELECT * FROM admission_outbox WHERE path=? ORDER BY seq", (path,)))
        if kind != "TRIAL" and old:
            if len(old) != 1 or bytes(old[0][4]) != content or old[0][1] != admission_id:
                raise ContractError("ADMISSION_INTEGRITY_ERROR")
            return old[0][0]
        seq = c.execute("SELECT coalesce(max(seq),-1)+1 FROM admission_outbox").fetchone()[0]
        checksum = hashlib.sha256(content).hexdigest()
        c.execute(
            "INSERT INTO admission_outbox VALUES (?,?,?,?,?,?,0)",
            (seq, admission_id, kind, path, content, checksum),
        )
        self._event(
            c,
            "OUTBOX",
            {
                "seq": seq,
                "admission_id": admission_id,
                "kind": kind,
                "path": path,
                "sha256": checksum,
            },
        )
        return seq

    def project_trial(self, c, admission_id, claim, payload):
        """Freeze JSONL sequence and previous hash before committing any writer."""
        if claim["admission_id"] != admission_id:
            raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        path = str(self.root / "research-runs/trials.jsonl")
        rows = list(
            c.execute("SELECT content FROM admission_outbox WHERE path=? ORDER BY seq", (path,))
        )
        for row in rows:
            item = _json(bytes(row[0]).rstrip(b"\n"))
            if (
                item["payload"].get("run_id") == claim["run_id"]
                and item["payload"].get("hypothesis") == claim["unit"]["hypothesis_alias"]
            ):
                if item["payload"] != payload:
                    raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
                return item
        previous = _json(bytes(rows[-1][0]).rstrip(b"\n"))["hash"] if rows else "0" * 64
        item = {
            "seq": len(rows),
            "recorded_at": datetime.now(UTC).isoformat(timespec="microseconds"),
            "previous": previous,
            "kind": "TRIAL_ATTEMPT",
            "payload": payload,
        }
        item["hash"] = digest(item)
        self.queue_projection(c, path, canonical(item) + b"\n", admission_id, kind="TRIAL")
        return item

    def materialize(self):
        """Publish every frozen prefix in authority order, regardless lock arrival."""
        from aqrp.experiments.ledger import mutex

        for _ in range(100):
            with self.transaction() as c:
                self.verify(c)
                rows = [tuple(r) for r in c.execute("SELECT * FROM admission_outbox ORDER BY seq")]
                if all(row[6] for row in rows):
                    # verify already required every materialized immutable byte;
                    # a complete authority needs no repeated file publication.
                    return
            grouped = {}
            for row in rows:
                grouped.setdefault(row[3], []).append(row)
            completed = []
            for name, items in grouped.items():
                path = _guard(name)
                path.parent.mkdir(parents=True, exist_ok=True)
                lock = path.parent / (
                    ".trials-lock" if items[0][2] == "TRIAL" else ".admission-projection-lock"
                )
                with mutex(lock, timeout=30):
                    wanted = (
                        b"".join(bytes(x[4]) for x in items)
                        if items[0][2] == "TRIAL"
                        else bytes(items[0][4])
                    )
                    actual = path.read_bytes() if path.exists() else b""
                    if actual == wanted:
                        pass
                    elif items[0][2] == "TRIAL":
                        prefixes = {b""}
                        prefix = b""
                        for row in items:
                            prefix += bytes(row[4])
                            prefixes.add(prefix)
                        if actual not in prefixes:
                            # Another publisher can already have a newer complete
                            # prefix. Consult the authority only after unlocking.
                            if not actual.startswith(wanted):
                                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
                        else:
                            with path.open("ab") as stream:
                                stream.write(wanted[len(actual) :])
                                stream.flush()
                                os.fsync(stream.fileno())
                    else:
                        _immutable(path, wanted)
                    completed.extend(x[0] for x in items)
            with self.transaction() as c:
                self.verify(c)
                for seq in completed:
                    c.execute("UPDATE admission_outbox SET materialized=1 WHERE seq=?", (seq,))
                if (
                    c.execute(
                        "SELECT count(*) FROM admission_outbox WHERE materialized=0"
                    ).fetchone()[0]
                    == 0
                ):
                    self.verify(c, require_projections=True)
                    return
                # A distinct writer committed new frozen outbox rows while files
                # were being published. Drain them next, without rerunning any
                # reservation/claim transaction or declaring corruption.
        raise ContractError("ADMISSION_PUBLICATION_BUSY", retryable=True)

    @contextmanager
    def legacy_execution(self, admission_id):
        """A live owner holds a real kernel file lock; crash recovery is fenced."""
        from aqrp.experiments.ledger import mutex

        lock = self.root / "task-control" / ("legacy-" + admission_id + ".lock")
        try:
            with mutex(lock, timeout=0):
                token = str(uuid.uuid4())
                with self.transaction() as c:
                    self.verify_admission_projections(c, admission_id)
                    admission = self.get(c, admission_id)
                    if admission["owner_kind"] != "LEGACY" or admission["decision"] != "ADMITTED":
                        raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
                    prior = c.execute(
                        "SELECT epoch FROM legacy_execution_owners WHERE admission_id=?",
                        (admission_id,),
                    ).fetchone()
                    epoch = 0 if prior is None else prior[0] + 1
                    c.execute(
                        "INSERT OR REPLACE INTO legacy_execution_owners VALUES (?,?,?,?,0)",
                        (admission_id, token, os.getpid(), epoch),
                    )
                    self._event(
                        c,
                        "LEGACY_EXECUTION_CLAIM",
                        {
                            "admission_id": admission_id,
                            "token": token,
                            "pid": os.getpid(),
                            "epoch": epoch,
                        },
                    )
                try:
                    yield {
                        "admission_id": admission_id,
                        "token": token,
                        "pid": os.getpid(),
                        "epoch": epoch,
                    }
                finally:
                    with self.transaction() as c:
                        c.execute(
                            "UPDATE legacy_execution_owners SET released=1 WHERE admission_id=? AND token=? AND epoch=?",
                            (admission_id, token, epoch),
                        )
        except ContractError as exc:
            if exc.code == "LEDGER_LOCK_TIMEOUT":
                raise ContractError("ADMISSION_LEGACY_OWNER_ACTIVE") from exc
            raise

    def _verify_plan(self, c):
        event_rows = list(
            c.execute(
                "SELECT kind,payload FROM admission_events WHERE kind IN ('PLAN_INSTALLED','ACTOR_BOUND','ACTOR_ACTIVATED','ACTOR_COMPLETED') ORDER BY seq"
            )
        )
        row = c.execute("SELECT payload,hash FROM execution_plans WHERE id=1").fetchone()
        if row is None:
            if (
                (self.root / "task-control/execution-plan.json").exists()
                or event_rows
                or c.execute("SELECT count(*) FROM execution_plan_slots").fetchone()[0]
                or c.execute("SELECT count(*) FROM execution_plan_activations").fetchone()[0]
            ):
                raise ValueError("orphan plan")
            return
        plan = _json(row[0])
        if digest(plan) != row[1] or _read(self.root / "task-control/execution-plan.json") != plan:
            raise ValueError("plan changed")
        installed = [_json(x[1]) for x in event_rows if x[0] == "PLAN_INSTALLED"]
        if installed != [{"plan_hash": row[1]}]:
            raise ValueError("plan installation history")
        event_bindings = {
            _json(x[1])["slot_id"]: _json(x[1]) for x in event_rows if x[0] == "ACTOR_BOUND"
        }
        actual_bindings = {}
        slots = list(c.execute("SELECT * FROM execution_plan_slots ORDER BY ordinal"))
        if len(slots) != len(plan["slots"]):
            raise ValueError("slot set")
        for ordinal, slot in enumerate(slots):
            if (
                slot[0] != plan["slots"][ordinal]["slot_id"]
                or slot[1] != ordinal
                or _json(slot[2]) != plan["slots"][ordinal]
                or digest(_json(slot[2])) != slot[3]
            ):
                raise ValueError("slot changed")
            if slot[6] is not None:
                binding = _json(slot[6])
                if (
                    digest(binding) != slot[7]
                    or binding["client_key"] != slot[4]
                    or binding["owner_id"] != slot[5]
                ):
                    raise ValueError("binding changed")
                actual_bindings[slot[0]] = binding
        if actual_bindings != event_bindings:
            raise ValueError("binding event set")
        event_activations = [_json(x[1]) for x in event_rows if x[0] == "ACTOR_ACTIVATED"]
        event_completed = {
            _json(x[1])["activation"]["activation_seq"]: _json(x[1])["receipt"]
            for x in event_rows
            if x[0] == "ACTOR_COMPLETED"
        }
        actual_activations, actual_completed = [], {}
        for ordinal, act in enumerate(
            c.execute("SELECT * FROM execution_plan_activations ORDER BY seq")
        ):
            body = _json(act[1])
            if (
                act[0] != ordinal
                or body["activation_seq"] != ordinal
                or digest(body) != act[2]
                or body["plan_hash"] != row[1]
            ):
                raise ValueError("activation changed")
            if act[3] is not None and digest(_json(act[3])) != act[4]:
                raise ValueError("completion changed")
            actual_activations.append(body)
            if act[3] is not None:
                actual_completed[ordinal] = _json(act[3])
        if actual_activations != event_activations or actual_completed != event_completed:
            raise ValueError("activation event set")


class PlanAuthority:
    def __init__(self, budget, plan_hash, execution_identity, *, seal):
        if seal is not _PLAN_SEAL:
            raise ContractError("TRUSTED_PROTOCOL_DRIVER_REQUIRED")
        self.budget, self.plan_hash, self.execution_identity = budget, plan_hash, execution_identity

    def __reduce__(self):
        raise TypeError("PlanAuthority is process-local and cannot be serialized")


def _driver_identity(plan, execution_identity):
    expected = {k: plan[k] for k in ("runner_path", "runner_sha256", "code_bundle", "code_commit")}
    if execution_identity != expected:
        raise ContractError("TRUSTED_PROTOCOL_DRIVER_REQUIRED")
    module_path = _guard(__file__)
    caller = None
    for frame in inspect.stack()[1:]:
        candidate = _guard(frame.filename)
        if candidate.is_file() and os.path.samefile(candidate, module_path):
            continue
        caller = candidate
        break
    runner = _guard(plan["runner_path"])
    if (
        caller is None
        or not caller.is_file()
        or not os.path.samefile(caller, runner)
        or hashlib.sha256(runner.read_bytes()).hexdigest() != plan["runner_sha256"]
    ):
        raise ContractError("TRUSTED_PROTOCOL_DRIVER_REQUIRED")


def install_execution_plan(workspace_root, plan, execution_identity):
    """Called only by the frozen local engineering runner before any result."""
    _driver_identity(plan, execution_identity)
    budget = BudgetAuthority(workspace_root)
    cat = _catalogue(budget.root)
    if (
        plan.get("schema") != "p7-execution-plan/1"
        or plan.get("data_hash") != cat["snapshot"]["manifest_hash"]
        or plan.get("catalogue_hash") != digest(cat)
        or plan.get("code_bundle") != cat["code_bundle"]
        or plan.get("code_commit") != cat["code_commit"]
        or not plan.get("purpose")
        or not isinstance(plan.get("slots"), list)
        or not plan["slots"]
    ):
        raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
    seen = set()
    for slot in plan["slots"]:
        required = {
            "slot_id",
            "service_kind",
            "request_hash",
            "output_root",
            "requested_units",
            "grant_capacity",
            "max_admitted_owners",
            "expected_status",
        }
        if (
            not required <= set(slot)
            or slot["slot_id"] in seen
            or slot["service_kind"] not in ("TASK", "TASK_REPLAY", "LEGACY")
            or any(
                type(slot[k]) is not int or slot[k] < 0
                for k in ("requested_units", "grant_capacity", "max_admitted_owners")
            )
            or slot["max_admitted_owners"] > 1
            or _guard(slot["output_root"])
            != budget.root
            / ("replay-runs" if slot["service_kind"] == "TASK_REPLAY" else "research-runs")
            or slot["expected_status"] not in ("SUCCEEDED", "FAILED", "CANCELLED", "REJECTED")
        ):
            raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
        if "source_slot" in slot:
            source = next((s for s in plan["slots"] if s["slot_id"] == slot["source_slot"]), None)
            if (
                source is None
                or slot["source_slot"] not in seen
                or source["service_kind"] != "TASK"
                or source["request_hash"] != slot.get("originalsource_request_hash")
                or slot["service_kind"] != "TASK_REPLAY"
                or slot["requested_units"] != 0
                or slot["grant_capacity"] != 0
                or slot.get("request_hash") is not None
                or slot.get("profile") != "P5_NUMERICAL"
                or slot.get("request_template", {}).get("payload")
                != {"source_task": "$SOURCE_TASK", "profile": "P5_NUMERICAL"}
            ):
                raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
        seen.add(slot["slot_id"])
    with budget.transaction() as c:
        budget.verify(c)
        old = c.execute("SELECT hash FROM execution_plans WHERE id=1").fetchone()
        if old:
            if old[0] != digest(plan):
                raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
            return old[0]
        if c.execute("SELECT count(*) FROM admissions").fetchone()[0]:
            raise ContractError("EXECUTION_PLAN_PREREGISTRATION_REQUIRED")
        c.execute(
            "INSERT INTO execution_plans VALUES (1,?,?)", (canonical(plan).decode(), digest(plan))
        )
        for ordinal, slot in enumerate(plan["slots"]):
            c.execute(
                "INSERT INTO execution_plan_slots(slot,ordinal,payload,hash) VALUES (?,?,?,?)",
                (slot["slot_id"], ordinal, canonical(slot).decode(), digest(slot)),
            )
        _immutable(budget.root / "task-control/execution-plan.json", canonical(plan))
        budget._event(c, "PLAN_INSTALLED", {"plan_hash": digest(plan)})
    return digest(plan)


def open_protocol_driver(workspace_root, expected_plan_hash, execution_identity):
    budget = BudgetAuthority(workspace_root)
    cat = _catalogue(budget.root)
    with budget.transaction() as c:
        budget.verify(c)
        row = c.execute("SELECT payload,hash FROM execution_plans WHERE id=1").fetchone()
        if row is None or row[1] != expected_plan_hash:
            raise ContractError("TRUSTED_PROTOCOL_DRIVER_REQUIRED")
        plan = _json(row[0])
        if (
            plan["code_bundle"] != cat["code_bundle"]
            or plan["code_commit"] != cat["code_commit"]
            or plan["catalogue_hash"] != digest(cat)
        ):
            raise ContractError("TRUSTED_PROTOCOL_DRIVER_REQUIRED")
        _driver_identity(plan, execution_identity)
    return PlanAuthority(budget, expected_plan_hash, execution_identity, seal=_PLAN_SEAL)


def capture_activation(workspace_root):
    budget = BudgetAuthority(workspace_root)
    with budget.transaction() as c:
        budget.verify(c)
        row = c.execute(
            "SELECT payload FROM execution_plan_activations ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        return None if row is None else _json(row[0])


def verify_activation(workspace_root, captured):
    current = capture_activation(workspace_root)
    if current != captured:
        raise ContractError("EXECUTION_PLAN_ACTIVATION_STALE")
    return current


def advance_actor(plan_authority, expected_activation_seq):
    if type(plan_authority) is not PlanAuthority:
        raise ContractError("TRUSTED_PROTOCOL_DRIVER_REQUIRED")
    budget = plan_authority.budget
    with budget.transaction() as c:
        budget.verify(c)
        row = c.execute(
            "SELECT * FROM execution_plan_activations ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        seq = -1 if row is None else row[0]
        if seq != expected_activation_seq:
            raise ContractError("EXECUTION_PLAN_ACTIVATION_STALE")
        if row is not None and row[3] is None:
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        plan = _json(c.execute("SELECT payload FROM execution_plans WHERE id=1").fetchone()[0])
        if seq + 1 >= len(plan["slots"]):
            raise ContractError("EXECUTION_PLAN_SLOT_UNAUTHORIZED")
        slot = plan["slots"][seq + 1]
        receipt = {
            "plan_hash": plan_authority.plan_hash,
            "activation_seq": seq + 1,
            "activation_id": str(uuid.uuid4()),
            "epoch": seq + 1,
            "slot_id": slot["slot_id"],
            "execution_identity": plan_authority.execution_identity,
        }
        c.execute(
            "INSERT INTO execution_plan_activations(seq,payload,hash) VALUES (?,?,?)",
            (seq + 1, canonical(receipt).decode(), digest(receipt)),
        )
        budget._event(c, "ACTOR_ACTIVATED", receipt)
        return receipt


def bind_current_actor(
    workspace_root,
    service_kind,
    canonical_request_hash,
    physical_output_root,
    client_key=None,
    owner_id=None,
    units_count=None,
    activation=None,
    connection=None,
    _bind=True,
):
    budget = BudgetAuthority(workspace_root)
    if connection is None:
        with budget.transaction() as c:
            return bind_current_actor(
                workspace_root,
                service_kind,
                canonical_request_hash,
                physical_output_root,
                client_key,
                owner_id,
                units_count,
                activation,
                c,
                _bind,
            )
    c = connection
    row = c.execute("SELECT payload,hash FROM execution_plans WHERE id=1").fetchone()
    if row is None:
        return None
    current = c.execute(
        "SELECT payload,completion FROM execution_plan_activations ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    if activation is not None and (current is None or _json(current[0]) != activation):
        raise ContractError("EXECUTION_PLAN_ACTIVATION_STALE")
    # A key already bound to an older actor never binds a later equal request.
    old = (
        c.execute(
            "SELECT binding FROM execution_plan_slots WHERE client_key=?", (client_key,)
        ).fetchone()
        if client_key
        else None
    )
    if old is not None:
        prior = _json(old[0])
        if (
            prior["request_hash"] != canonical_request_hash
            or prior["service_kind"] != service_kind
            or prior["output_root"] != str(_guard(physical_output_root))
        ):
            raise ContractError("ADMISSION_IDEMPOTENCY_CONFLICT")
        if owner_id is not None and owner_id != prior["owner_id"]:
            raise ContractError("ADMISSION_IDEMPOTENCY_CONFLICT")
        return prior
    if current is None or current[1] is not None:
        raise ContractError("EXECUTION_PLAN_SLOT_UNAUTHORIZED")
    active = _json(current[0])
    if activation is not None and activation != active:
        raise ContractError("EXECUTION_PLAN_ACTIVATION_STALE")
    slot_row = c.execute(
        "SELECT * FROM execution_plan_slots WHERE slot=?", (active["slot_id"],)
    ).fetchone()
    slot = _json(slot_row[2])
    expected_request_hash = _resolved_slot_request(c, budget, slot, owner_id)
    if (
        slot["service_kind"] != service_kind
        or expected_request_hash != canonical_request_hash
        or _guard(slot["output_root"]) != _guard(physical_output_root)
        or units_count is not None
        and slot["requested_units"] != units_count
        or slot.get("client_key") is not None
        and slot["client_key"] != client_key
    ):
        raise ContractError("EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT")
    internal_key = (
        digest({"plan_hash": row[1], "slot_id": slot["slot_id"]})
        if service_kind == "LEGACY"
        else client_key
    )
    if service_kind == "LEGACY":
        client_key = internal_key
    if slot_row[6] is not None:
        prior = _json(slot_row[6])
        if (
            service_kind == "LEGACY"
            and prior["client_key"] == client_key
            and (owner_id is None or owner_id == prior["owner_id"])
        ):
            return prior
        raise ContractError("EXECUTION_PLAN_SLOT_EXHAUSTED")
    if not client_key:
        raise ContractError("ADMISSION_IDEMPOTENCY_CONFLICT")
    binding = {
        **slot,
        "plan_hash": row[1],
        "activation": active,
        "client_key": client_key,
        "owner_id": owner_id,
        "request_hash": canonical_request_hash,
    }
    if _bind:
        if not owner_id:
            raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        c.execute(
            "UPDATE execution_plan_slots SET client_key=?,owner_id=?,binding=?,binding_hash=? WHERE slot=? AND binding IS NULL",
            (client_key, owner_id, canonical(binding).decode(), digest(binding), slot["slot_id"]),
        )
        budget._event(c, "ACTOR_BOUND", binding)
    return binding


def lookup_legacy_actor(connection, workspace_root, request_hash, output_root, activation=None):
    """Resolve a stable plan owner/key before a legacy caller allocates a UUID."""
    return bind_current_actor(
        workspace_root,
        "LEGACY",
        request_hash,
        output_root,
        activation=activation,
        connection=connection,
        _bind=False,
    )


def complete_actor(plan_authority, receipt):
    """Verify a real bound terminal before permitting the next frozen actor."""
    if type(plan_authority) is not PlanAuthority:
        raise ContractError("TRUSTED_PROTOCOL_DRIVER_REQUIRED")
    budget = plan_authority.budget
    # The existing public status gate includes exact financial reconciliation on
    # cancellation and the complete P3/P4/P5 proofs on success. Run it without an
    # authority transaction: it legitimately opens TaskState's own connection.
    with budget.transaction() as c:
        budget.verify(c, require_projections=True)
        active_row = c.execute(
            "SELECT payload FROM execution_plan_activations ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        if active_row is None:
            raise ContractError("EXECUTION_PLAN_SLOT_UNAUTHORIZED")
        active_before = _json(active_row[0])
        slot_before = c.execute(
            "SELECT payload,binding FROM execution_plan_slots WHERE slot=?",
            (active_before["slot_id"],),
        ).fetchone()
        spec_before = _json(slot_before[0])
        binding_before = _json(slot_before[1]) if slot_before[1] else None
    if binding_before is None:
        raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
    if (
        spec_before["service_kind"] in ("TASK", "TASK_REPLAY")
        and spec_before["expected_status"] != "REJECTED"
    ):
        from aqrp.services.tasks import TaskService

        public = TaskService(budget.root).status(binding_before["owner_id"])
        if (
            public["status"] != spec_before["expected_status"]
            or public["status"] == "INTEGRITY_ERROR"
        ):
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
    with budget.transaction() as c:
        budget.verify(c, require_projections=True)
        row = c.execute(
            "SELECT * FROM execution_plan_activations ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        if row is None:
            raise ContractError("EXECUTION_PLAN_SLOT_UNAUTHORIZED")
        activation = _json(row[1])
        if activation != active_before:
            raise ContractError("EXECUTION_PLAN_ACTIVATION_STALE")
        slot = c.execute(
            "SELECT payload,binding FROM execution_plan_slots WHERE slot=?",
            (activation["slot_id"],),
        ).fetchone()
        spec = _json(slot[0])
        binding = _json(slot[1]) if slot[1] else None
        if binding is None or receipt.get("owner_id") != binding["owner_id"]:
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        kind = "TASK" if spec["service_kind"] == "TASK_REPLAY" else spec["service_kind"]
        admission = budget.lookup_owner(c, kind, binding["owner_id"])
        expected = spec["expected_status"]
        if expected == "REJECTED":
            status = admission["decision"]
            code = admission["code"]
        elif spec["service_kind"] in ("TASK", "TASK_REPLAY"):
            task = _task_terminal(c, budget, binding["owner_id"], binding["request_hash"])
            status, code = task["status"], task["error"]
        else:
            from aqrp.experiments.ledger import ExperimentLedger

            manifest = ExperimentLedger(budget.root / "research-runs").verify(binding["owner_id"])
            status, code = manifest["status"], None
        evidence = receipt.get("evidence")
        if (
            status != expected
            or spec.get("expected_code") not in (None, code)
            or receipt.get("status") != status
            or not isinstance(evidence, list)
            or not evidence
        ):
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        for item in evidence:
            path = _guard(item["path"])
            if (
                not path.is_relative_to(budget.root)
                or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]
            ):
                raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        raw = canonical(receipt).decode()
        if row[3] is not None and row[3] != raw:
            raise ContractError("EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED")
        if row[3] == raw:
            return receipt
        c.execute(
            "UPDATE execution_plan_activations SET completion=?,completion_hash=? WHERE seq=?",
            (raw, digest(receipt), row[0]),
        )
        budget._event(c, "ACTOR_COMPLETED", {"activation": activation, "receipt": receipt})
        return receipt
