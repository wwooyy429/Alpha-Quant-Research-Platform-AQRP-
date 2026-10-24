"""Explicit per-instance preallocated ownership. No global current-task state."""

import hashlib
import json
import re
import uuid

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger, read_chain

_SEAL = object()


class TaskAuthority:
    def __init__(self, state, task, owner, epoch, *, seal):
        if seal is not _SEAL:
            raise ContractError("TRUSTED_TASK_LAUNCHER_REQUIRED")
        self.state, self.task, self.owner, self.epoch = state, task, owner, epoch

    def check(self, *, cancel=False, connection=None):
        row = (
            self.state.get(self.task)
            if connection is None
            else connection.execute("SELECT * FROM tasks WHERE id=?", (self.task,)).fetchone()
        )
        if (row["owner"], row["epoch"], row["status"]) != (self.owner, self.epoch, "RUNNING"):
            raise ContractError("STALE_TASK_CLAIM")
        raw = guard_path(self.state.root / "tasks" / self.task / "request.json").read_bytes()
        if raw.decode() != row["raw"] or digest(json.loads(raw)) != row["hash"]:
            raise ContractError("TASK_REQUEST_IDENTITY_CHANGED")
        if cancel and row["cancel"]:
            raise KeyboardInterrupt("TASK_SAFE_CANCEL_CHECKPOINT")
        return row

    def allocate(self, slot, service, root, *, parent=None, index=None, time=None, source=None):
        row = self.check()
        req = json.loads(row["raw"])
        root = guard_path(root)
        expected_root = {
            "R": self.state.root / "research-runs",
            "B": self.state.root / "backtest-runs",
            "E": self.state.root / "replay-runs",
        }
        if service == "P4":
            if (
                parent is None
                or slot != f"P:{index}"
                or type(index) is not int
                or index < 0
                or parent.authority is not self
            ):
                raise ContractError("TASK_SLOT_SCHEMA_MISMATCH")
            if parent.binding()["service_kind"] not in ("P5", "P5_REPLAY"):
                raise ContractError("TASK_SLOT_SCHEMA_MISMATCH")
            expected_root[slot] = (
                guard_path(parent.binding()["physical_ledger_root"])
                / parent.binding()["child_run_id"]
                / "portfolio-runs"
            )
        elif (slot, service) not in {
            ("R", "P3"),
            ("B", "P5"),
            ("E", "P5_REPLAY"),
            ("E", "PUBLISHED_REF_PROJECTION"),
        }:
            raise ContractError("TASK_SLOT_SCHEMA_MISMATCH")
        if (
            (req["kind"] == "research" and slot != "R")
            or (req["kind"] == "engineering_pipeline" and slot == "E")
            or (req["kind"] == "replay" and slot in ("R", "B"))
            or root != expected_root[slot]
        ):
            raise ContractError("TASK_SLOT_ROOT_OR_KIND_MISMATCH")
        if not root.is_relative_to(self.state.root):
            raise ContractError("TASK_ROOT_OUTSIDE_WORKSPACE")
        binding = {
            "workspace_id": self.state.workspace_id,
            "task_id": self.task,
            "task_kind": req["kind"],
            "plan_hash": row["hash"],
            "slot_id": slot,
            "service_kind": service,
            "decision_index": index,
            "decision_time_UTC": time,
            "source_request_hash": source,
            "adapted_request_hash": None,
            "parent_slot_id": parent.slot if parent else None,
            "parent_execution_run_id": parent.binding()["child_run_id"] if parent else None,
            "child_run_id": str(uuid.uuid4()),
            "physical_ledger_root": str(root),
            "core_config_hash": None,
            "code_sha": req["code_commit"],
            "code_bundle": req["code_bundle"],
            "core_lock_hash": req["core_lock_hash"],
            "ui_lock_hash": req["ui_lock_hash"],
        }
        with self.state.transaction() as c:
            self.check(connection=c)
            existing = c.execute(
                "SELECT binding FROM slots WHERE task=? AND slot=?", (self.task, slot)
            ).fetchone()
            if existing:
                old = json.loads(existing[0])
                for key in binding:
                    if (
                        key not in ("child_run_id", "core_config_hash", "adapted_request_hash")
                        and old[key] != binding[key]
                    ):
                        raise ContractError("TASK_SLOT_BINDING_CONFLICT", key)
            else:
                c.execute(
                    "INSERT INTO slots VALUES (?,?,?,'ALLOCATED')",
                    (self.task, slot, canonical(binding).decode()),
                )
                self.state.event(c, self.task, "SLOT_ALLOCATED", binding)
        return TaskRunContext(self, slot, seal=_SEAL)

    def context(self, slot):
        if slot not in self.state.slots(self.task):
            raise ContractError("UNREGISTERED_TASK_SLOT")
        return TaskRunContext(self, slot, seal=_SEAL)


def authority(state, task, owner, epoch):
    return TaskAuthority(state, task, owner, epoch, seal=_SEAL)


def require_context(context):
    if type(context) is not TaskRunContext or type(context.authority) is not TaskAuthority:
        raise ContractError("TRUSTED_TASK_CONTEXT_REQUIRED")
    context.authority.check()
    return context


class TaskRunContext:
    def __init__(self, auth, slot, *, seal):
        if seal is not _SEAL:
            raise ContractError("TRUSTED_TASK_CONTEXT_REQUIRED")
        self.authority, self.slot = auth, slot

    def binding(self):
        self.authority.check()
        return self.authority.state.slots(self.authority.task)[self.slot]["binding"]

    def checkpoint(self):
        self.authority.check(cancel=True)

    def research_attempt(self):
        require_context(self)
        if self.slot != "R":
            raise ContractError("RESEARCH_CAMPAIGN_CONTEXT_REQUIRED")
        return self.authority.state.research_attempt(self.authority.task)

    def mark_verified(self, manifest):
        binding = self.binding()
        with self.authority.state.transaction() as c:
            self.authority.check(connection=c)
            state = "VERIFIED_SUCCESS" if manifest["status"] == "SUCCEEDED" else "VERIFIED_FAILURE"
            c.execute(
                "UPDATE slots SET state=? WHERE task=? AND slot=?",
                (state, binding["task_id"], self.slot),
            )
            self.authority.state.event(
                c,
                binding["task_id"],
                "SLOT_TERMINAL_VERIFIED",
                {
                    "slot": self.slot,
                    "manifest_hash": digest(manifest),
                    "binding_hash": digest(binding),
                    "state": state,
                },
            )

    def start(self, root, config, lineage):
        self.checkpoint()
        b = self.binding()
        planned = json.loads(self.authority.check()["raw"])
        if (
            b["service_kind"] == "PUBLISHED_REF_PROJECTION"
            and config.get("registered_history_sha256") != planned["payload"]["history_sha256"]
        ):
            raise ContractError("TASK_PLANNED_REPLAY_CHANGED")
        if b["service_kind"] == "P3" and config != planned["payload"]["research"]:
            raise ContractError("TASK_PLANNED_RESEARCH_CHANGED")
        if b["service_kind"] in ("P5", "P5_REPLAY"):
            plan = json.loads(
                guard_path(
                    self.authority.state.root / "tasks" / b["task_id"] / "resolved-plan.json"
                ).read_bytes()
            )
            if (
                b["service_kind"] == "P5"
                and config.get("raw_request_hex") != plan["request_utf8"].encode().hex()
            ):
                raise ContractError("TASK_PLANNED_SIMULATION_CHANGED")
            if (
                b["service_kind"] == "P5_REPLAY"
                and config.get("request_sha256") != plan["request_sha256"]
            ):
                raise ContractError("TASK_PLANNED_REPLAY_CHANGED")
        if b["service_kind"] == "P4" and (
            config.get("request_sha256") != b["adapted_request_hash"]
            or hashlib.sha256(bytes.fromhex(config["raw_request_hex"])).hexdigest()
            != b["adapted_request_hash"]
        ):
            raise ContractError("TASK_PLANNED_PORTFOLIO_CHANGED")
        if (
            str(guard_path(root)) != b["physical_ledger_root"]
            or lineage["code_commit"] != b["code_sha"]
            or lineage["code_bundle"] != b["code_bundle"]
        ):
            raise ContractError("TASK_CORE_IDENTITY_MISMATCH")
        h = digest(config)
        with self.authority.state.transaction() as c:
            self.authority.check(connection=c)
            row = c.execute(
                "SELECT * FROM slots WHERE task=? AND slot=?", (b["task_id"], self.slot)
            ).fetchone()
            if row["state"] not in ("ALLOCATED", "BOUND") or b["core_config_hash"] not in (None, h):
                raise ContractError("TASK_SLOT_ALREADY_STARTED")
            b["core_config_hash"] = h
            c.execute(
                "UPDATE slots SET binding=?,state='START_INTENT' WHERE task=? AND slot=?",
                (canonical(b).decode(), b["task_id"], self.slot),
            )
            self.authority.state.event(c, b["task_id"], "CORE_START_INTENT", b)
        return b["child_run_id"], {**lineage, "task_binding": b, "task_binding_hash": digest(b)}

    def verify(self, root, run, config=None, *, terminal=True):
        b = self.binding()
        if str(guard_path(root)) != b["physical_ledger_root"] or run != b["child_run_id"]:
            raise ContractError("TASK_CORE_OWNERSHIP_MISMATCH")
        ledger = ExperimentLedger(root)
        m = ledger.verify(run) if terminal else {"files": []}
        lineage = json.loads((ledger.path(run) / "lineage.json").read_bytes())
        actual = json.loads((ledger.path(run) / "config.json").read_bytes())
        if (
            lineage.get("task_binding") != b
            or lineage.get("task_binding_hash") != digest(b)
            or digest(actual) != b["core_config_hash"]
            or (config is not None and actual != config)
        ):
            raise ContractError("TASK_INITIAL_BINDING_MISMATCH")
        if len({e["path"] for e in m["files"]}) != len(m["files"]):
            raise ContractError("TASK_DUPLICATE_MANIFEST_MEMBER")
        if any(not re.fullmatch(r"[a-z0-9_-]+\.(json|html)", e["path"]) for e in m["files"]):
            raise ContractError("TASK_ARTIFACT_BOUNDARY")
        initial = read_chain(ledger.path(run) / "events.jsonl")[0]["payload"]
        if initial["config_hash"] != digest(actual) or initial["lineage_hash"] != digest(lineage):
            raise ContractError("TASK_INITIAL_RECORD_CHANGED")
        return m

    def existing(self):
        b = self.binding()
        root = guard_path(b["physical_ledger_root"]) / b["child_run_id"]
        slot = self.authority.state.slots(self.authority.task)[self.slot]
        if slot["state"] in ("ALLOCATED", "BOUND"):
            if root.exists():
                raise ContractError("TASK_UNREGISTERED_CORE_DIRECTORY")
            return None
        if not root.exists():
            raise ContractError("RECOVERY_REQUIRED")
        try:
            m = self.verify(root.parent, root.name)
        except ContractError as exc:
            if exc.code == "NONTERMINAL_RUN" and b["service_kind"] == "P4":
                raise ContractError("RECOVERY_REQUIRED") from exc
            raise
        name = "report.json" if b["service_kind"] == "P3" else "result.json"
        raw = guard_path(root / name).read_bytes()
        matches = [e for e in m["files"] if e["path"] == name]
        if len(matches) != 1 or hashlib.sha256(raw).hexdigest() != matches[0]["sha256"]:
            raise ContractError("TASK_RESULT_NOT_MANIFESTED")
        result = json.loads(raw)
        if b["service_kind"] == "P3":
            return {"run_id": root.name, "manifest": m, "report": result}
        return {**result, "manifest": m}

    def child(self, index, request, root):
        self.checkpoint()
        parent = self.binding()
        self.verify(parent["physical_ledger_root"], parent["child_run_id"], terminal=False)
        child = self.authority.context(f"P:{index}")
        b = child.binding()
        from aqrp.core.time import utc
        from aqrp.portfolio.contracts import load

        x = load(request.raw)
        if (
            b["parent_execution_run_id"] != self.binding()["child_run_id"]
            or str(guard_path(root)) != b["physical_ledger_root"]
            or utc(x["context"]["decision_time"]).isoformat() != b["decision_time_UTC"]
        ):
            raise ContractError("TASK_NESTED_P4_BINDING_MISMATCH")
        with self.authority.state.transaction() as c:
            self.authority.check(connection=c)
            if b["adapted_request_hash"] not in (None, request.content_hash):
                raise ContractError("TASK_ADAPTED_REQUEST_CHANGED")
            b["adapted_request_hash"] = request.content_hash
            raw = c.execute(
                "SELECT raw,hash FROM adapted_requests WHERE task=? AND slot=?",
                (b["task_id"], child.slot),
            ).fetchone()
            if raw is not None and (
                raw[0] != request.raw.decode() or raw[1] != request.content_hash
            ):
                raise ContractError("TASK_ADAPTED_REQUEST_CHANGED")
            if raw is None:
                c.execute(
                    "INSERT INTO adapted_requests VALUES (?,?,?,?)",
                    (b["task_id"], child.slot, request.raw.decode(), request.content_hash),
                )
            c.execute(
                "UPDATE slots SET binding=?,state=CASE WHEN state='ALLOCATED' THEN 'BOUND' ELSE state END WHERE task=? AND slot=?",
                (canonical(b).decode(), b["task_id"], child.slot),
            )
        return child
