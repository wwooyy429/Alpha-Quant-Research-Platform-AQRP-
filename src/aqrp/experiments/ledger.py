"""Durable append-only hash chains, UUID runs and whole-config artifact integrity."""

import hashlib
import json
import os
import re
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.data.snapshot import safe_path

IS_WINDOWS = os.name == "nt"


@contextmanager
def mutex(path, timeout=5):
    f = Path(path).open("a+b")
    if f.tell() == 0:
        f.write(b"0")
        f.flush()
    start = time.monotonic()
    while True:
        try:
            f.seek(0)
            if IS_WINDOWS:
                import msvcrt

                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except OSError as exc:
            if time.monotonic() - start >= timeout:
                f.close()
                raise ContractError("LEDGER_LOCK_TIMEOUT") from exc
            time.sleep(0.01)
    try:
        yield
    finally:
        f.seek(0)
        if IS_WINDOWS:
            import msvcrt

            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()


def read_chain(path):
    if not Path(path).exists():
        return []
    previous = "0" * 64
    records = []
    for index, line in enumerate(Path(path).read_bytes().splitlines()):
        item = json.loads(line)
        value = {k: v for k, v in item.items() if k != "hash"}
        if value["seq"] != index or value["previous"] != previous or digest(value) != item["hash"]:
            raise ContractError("LEDGER_CHAIN_CORRUPTED")
        previous = item["hash"]
        records.append(item)
    return records


def append_chain(path, kind, payload):
    records = read_chain(path)
    item = {
        "seq": len(records),
        "recorded_at": datetime.now(UTC).isoformat(timespec="microseconds"),
        "previous": records[-1]["hash"] if records else "0" * 64,
        "kind": kind,
        "payload": payload,
    }
    item["hash"] = digest(item)
    with Path(path).open("ab") as f:
        f.write(canonical(item) + b"\n")
        f.flush()
        os.fsync(f.fileno())
    return item


def immutable_write(path, content):
    with Path(path).open("xb") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())


class ExperimentLedger:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._prepared_research = None

    @staticmethod
    def _research_units(config, lineage=None):
        """Freeze every candidate × horizon before any managed result is observed."""
        from aqrp.services.research import hypotheses, hypothesis_definition

        try:
            units = hypotheses(config)
            family = config["family"]
            aliases = [u["hypothesis"] for u in units]
            definitions = family["definitions"]
            if (
                not aliases
                or len(set(aliases)) != len(aliases)
                or not set(aliases) <= set(family["hypotheses"])
                or set(definitions) != set(family["hypotheses"])
                or type(family["budget"]) is not int
                or family["budget"] < 1
                or any(not re.fullmatch("[0-9a-f]{64}", definitions[a]) for a in aliases)
            ):
                raise ContractError("ADMISSION_SCHEMA_ERROR")
            if lineage is not None and any(
                definitions[u["hypothesis"]]
                != hypothesis_definition(
                    u,
                    config,
                    lineage["data_hash"],
                    lineage.get("exposure_hash"),
                    lineage["coverage_hash"],
                )
                for u in units
            ):
                raise ContractError("HYPOTHESIS_CHANGED_AFTER_PREREGISTRATION")
            return [
                {"hypothesis_alias": alias, "definition_hash": definitions[alias]}
                for alias in aliases
            ]
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ContractError):
                raise
            raise ContractError("ADMISSION_SCHEMA_ERROR") from exc

    def prepare_research(self, config, lineage, *, snapshot_ref=None, exposure_ref=None):
        """Mandatory managed legacy admission; standalone P3 retains its original API."""
        from aqrp.experiments.admission import resolve_admission_domain

        budget = resolve_admission_domain(
            self.root,
            config=config,
            lineage=lineage,
            snapshot_ref=snapshot_ref,
            exposure_ref=exposure_ref,
        )
        if budget is None:
            return None
        source = json.loads((budget.root / "catalog.json").read_bytes())
        input_binding = {
            "snapshot_root": str(Path(source["snapshot"]["root"]).resolve()),
            "exposure_root": str(Path(source["exposures"]["root"]).resolve()),
            "data_hash": source["snapshot"]["manifest_hash"],
        }
        prior_binding = lineage.get("admission_inputs", {})
        if not isinstance(prior_binding, dict) or any(
            input_binding.get(k) != v for k, v in prior_binding.items()
        ):
            raise ContractError("ADMISSION_DOMAIN_CONFLICT")
        # Direct public ledger calls get the original physical source binding too;
        # copying their run files elsewhere cannot erase its managed provenance.
        lineage["admission_inputs"] = input_binding
        units = self._research_units(config, lineage)
        budget.materialize()
        with budget.transaction() as c:
            budget.verify(c)
            binding = budget.lookup_legacy_actor(c, digest(config), self.root)
            run_id = (binding or {}).get("owner_id") or str(uuid.uuid4())
            admission = budget.reserve(
                c,
                data_hash=lineage["data_hash"],
                owner_kind="LEGACY",
                owner_id=run_id,
                key=binding["client_key"]
                if binding
                else digest({"ledger_root": str(self.root.resolve()), "run_id": run_id}),
                request_hash=digest(config),
                units=units,
                family_id=config["family"]["id"],
                family_limit=config["family"]["budget"],
                service_kind="LEGACY",
                output_root=self.root,
            )
            budget.queue_projection(
                c,
                budget.root / "task-control" / "admissions" / (admission["admission_id"] + ".json"),
                canonical(admission),
                admission["admission_id"],
                kind="SIDECAR",
            )
        budget.materialize()
        if admission["decision"] != "ADMITTED":
            raise ContractError(admission.get("code") or "EXPERIMENT_BUDGET_EXCEEDED")
        with budget.transaction() as c:
            budget.verify_admission_projections(c, admission["admission_id"])
        self._prepared_research = (run_id, digest(config), digest(lineage))
        return admission

    def path(self, run_id):
        try:
            key = str(uuid.UUID(run_id))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ContractError("INVALID_RUN_ID") from exc
        return self.root / key

    def start(self, config, lineage, *, task_context=None):
        required = {
            "code_commit",
            "code_bundle",
            "data_hash",
            "environment",
            "protocol_hash",
            "permission_domain",
            "seed",
        }
        if not required <= set(lineage) or not re.fullmatch("[0-9a-f]{40}", lineage["code_commit"]):
            raise ContractError("INCOMPLETE_RUN_LINEAGE")
        content = canonical(config)
        managed_run = False
        if task_context is not None:
            from aqrp.services.task_context import require_context

            run_id, lineage = require_context(task_context).start(self.root, config, lineage)
        else:
            if self._prepared_research is None and (
                "candidates" in config or self.root.name == "research-runs"
            ):
                from aqrp.experiments.admission import resolve_admission_domain

                managed = resolve_admission_domain(self.root, config=config, lineage=lineage)
                if managed is not None:
                    self.prepare_research(config, lineage)
            if self._prepared_research is None:
                run_id = str(uuid.uuid4())
            else:
                run_id, expected_config, expected_lineage = self._prepared_research
                managed_run = True
                if (expected_config, expected_lineage) != (digest(config), digest(lineage)):
                    raise ContractError("ADMISSION_IDEMPOTENCY_CONFLICT")
                self._prepared_research = None
        metadata = canonical(lineage)
        root = self.path(run_id)
        if root.exists() and managed_run:
            raise ContractError("ADMISSION_LEGACY_ALREADY_STARTED")
        running = None
        if "candidates" in config and self.root.name == "research-runs":
            running = self._freeze_running_event(run_id, config, lineage, task_context)
        root.mkdir(exist_ok=False)
        immutable_write(root / "config.json", content)
        immutable_write(root / "lineage.json", metadata)
        if running is None:
            append_chain(
                root / "events.jsonl",
                "RUNNING",
                {"config_hash": digest(config), "lineage_hash": digest(lineage)},
            )
        else:
            immutable_write(root / "events.jsonl", canonical(running) + b"\n")
        return run_id

    def _freeze_running_event(self, run_id, config, lineage, task_context):
        from aqrp.experiments.admission import resolve_admission_domain

        authority = resolve_admission_domain(self.root, config=config, lineage=lineage)
        if authority is None:
            return None
        context = None
        if task_context is not None:
            from aqrp.services.task_context import require_context

            context = require_context(task_context)
        authority.materialize()
        payload = {"config_hash": digest(config), "lineage_hash": digest(lineage)}
        path = authority.root / "task-control/start-events" / (run_id + ".json")
        with authority.transaction() as c:
            authority.verify(c)
            if context is not None:
                context.authority.check(connection=c)
                admission = authority.lookup_owner(c, "TASK", context.authority.task)
                if context.slot != "R" or lineage["task_binding"]["child_run_id"] != run_id:
                    raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            else:
                admission = authority.lookup_owner(c, "LEGACY", run_id)
            if admission is None or admission["decision"] != "ADMITTED":
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            old = c.execute(
                "SELECT content FROM admission_outbox WHERE path=?", (str(path),)
            ).fetchone()
            running = (
                json.loads(bytes(old[0]))
                if old is not None
                else {
                    "seq": 0,
                    "recorded_at": datetime.now(UTC).isoformat(timespec="microseconds"),
                    "previous": "0" * 64,
                    "kind": "RUNNING",
                    "payload": payload,
                }
            )
            if old is None:
                running["hash"] = digest(running)
            if (
                running["seq"] != 0
                or running["previous"] != "0" * 64
                or running["kind"] != "RUNNING"
                or running["payload"] != payload
                or digest({k: v for k, v in running.items() if k != "hash"}) != running["hash"]
            ):
                raise ContractError("ADMISSION_INTEGRITY_ERROR")
            authority.queue_projection(
                c, path, canonical(running), admission["admission_id"], kind="SIDECAR"
            )
        authority.materialize()
        return running

    def event(self, run_id, kind, payload):
        root = self.path(run_id)
        with mutex(root / ".lock"):
            events = read_chain(root / "events.jsonl")
            if not events or events[-1]["kind"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
                raise ContractError("IMMUTABLE_TERMINAL_RUN")
            return append_chain(root / "events.jsonl", kind, payload)

    def artifact(self, run_id, name, payload):
        if not re.fullmatch(r"[a-z0-9_-]+\.(json|html)", name) or name in (
            "config.json",
            "lineage.json",
            "manifest.json",
        ):
            raise ContractError("INVALID_RUN_ARTIFACT")
        root = self.path(run_id)
        with mutex(root / ".lock"):
            if read_chain(root / "events.jsonl")[-1]["kind"] in (
                "SUCCEEDED",
                "FAILED",
                "CANCELLED",
            ):
                raise ContractError("IMMUTABLE_TERMINAL_RUN")
            immutable_write(
                root / name,
                payload.encode("utf-8") if name.endswith(".html") else canonical(payload),
            )

    def finish(self, run_id, status):
        if status not in ("SUCCEEDED", "FAILED", "CANCELLED"):
            raise ContractError("INVALID_TERMINAL_STATUS")
        root = self.path(run_id)
        with mutex(root / ".lock"):
            events = read_chain(root / "events.jsonl")
            if events[-1]["kind"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
                raise ContractError("IMMUTABLE_TERMINAL_RUN")
            manifest = {
                "run_id": run_id,
                "status": status,
                "event_prefix_hash": events[-1]["hash"],
                "files": [
                    {"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                    for p in sorted(root.iterdir())
                    if p.suffix in (".json", ".html")
                ],
            }
            immutable_write(root / "manifest.json", canonical(manifest))
            append_chain(
                root / "events.jsonl",
                status,
                {
                    "manifest_sha256": hashlib.sha256(
                        (root / "manifest.json").read_bytes()
                    ).hexdigest()
                },
            )
        return self.verify(run_id)

    def verify(self, run_id):
        root = self.path(run_id)
        events = read_chain(root / "events.jsonl")
        if not events or events[-1]["kind"] not in ("SUCCEEDED", "FAILED", "CANCELLED"):
            raise ContractError("NONTERMINAL_RUN")
        raw = (root / "manifest.json").read_bytes()
        m = json.loads(raw)
        if (
            hashlib.sha256(raw).hexdigest() != events[-1]["payload"]["manifest_sha256"]
            or m["event_prefix_hash"] != events[-2]["hash"]
            or m["status"] != events[-1]["kind"]
            or m["run_id"] != run_id
        ):
            raise ContractError("RUN_MANIFEST_MISMATCH")
        for entry in m["files"]:
            p = safe_path(root, entry["path"])
            if (root / entry["path"]).is_symlink() or hashlib.sha256(
                p.read_bytes()
            ).hexdigest() != entry["sha256"]:
                raise ContractError("RUN_ARTIFACT_HASH_MISMATCH")
        return m

    def decision(self, run_id, record):
        """Post-run decisions never mutate terminal research artifacts."""
        manifest = self.verify(run_id)
        with mutex(self.root / ".decision-lock"):
            return append_chain(
                self.root / "decisions.jsonl",
                "HUMAN_RESEARCH_DECISION",
                {"run_id": run_id, "manifest_hash": digest(manifest), "record": record},
            )

    def register_trial(
        self, run_id, family, hypothesis, *, budget, hypothesis_spec=None, task_context=None
    ):
        if not family or not hypothesis or type(budget) is not int or budget < 1:
            raise ContractError("INVALID_EXPERIMENT_FAMILY")
        root = self.path(run_id)
        config_raw, lineage_raw = (
            (root / "config.json").read_bytes(),
            (root / "lineage.json").read_bytes(),
        )
        config, lineage = json.loads(config_raw), json.loads(lineage_raw)
        with mutex(root / ".lock"):
            initial = read_chain(root / "events.jsonl")
            initial_bytes = (root / "events.jsonl").read_bytes()
        if (
            not initial
            or initial[0]["kind"] != "RUNNING"
            or initial[0]["payload"]
            != {"config_hash": digest(config), "lineage_hash": digest(lineage)}
            or canonical(config) != config_raw
            or canonical(lineage) != lineage_raw
        ):
            raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
        fingerprint_config = {k: v for k, v in config.items() if k not in ("family", "candidates")}
        if "candidates" in config:
            fingerprint_config["candidates"] = [
                {k: v for k, v in c.items() if k != "hypothesis"} for c in config["candidates"]
            ]
        fingerprint = digest(
            {
                "config": fingerprint_config,
                "lineage": {
                    k: v
                    for k, v in lineage.items()
                    if k
                    not in (
                        "protocol_hash",
                        "code_commit",
                        "task_binding",
                        "task_binding_hash",
                        "campaign_control",
                    )
                },
                "hypothesis_spec": {
                    k: v
                    for k, v in (hypothesis_spec or {}).items()
                    if k not in ("hypothesis", "score_key")
                },
            }
        )
        from aqrp.experiments.admission import resolve_admission_domain

        authority = resolve_admission_domain(self.root, config=config, lineage=lineage)
        if authority is not None:
            if b"".join(canonical(event) + b"\n" for event in initial) != initial_bytes:
                raise ContractError("ADMISSION_HISTORY_UNVERIFIED")
            if initial[-1]["kind"] in ("SUCCEEDED", "FAILED", "CANCELLED") and not any(
                event["kind"] == "TRIAL_REGISTERED"
                and event["payload"].get("hypothesis") == hypothesis
                for event in initial
            ):
                raise ContractError("IMMUTABLE_TERMINAL_RUN")
            return self._register_managed_trial(
                authority,
                run_id,
                family,
                hypothesis,
                budget,
                hypothesis_spec,
                config,
                lineage,
                fingerprint,
                task_context,
            )
        with mutex(self.root / ".trials-lock"):
            past = read_chain(self.root / "trials.jsonl")
            peers = [x for x in past if x["payload"]["family"] == family]
            repeated = [
                x["payload"]["run_id"] for x in past if x["payload"]["fingerprint"] == fingerprint
            ]
            campaign = config.get("family", {}).get("campaign")
            control = lineage.get("campaign_control", {})
            item = {
                "cross_campaign_data_access": bool(campaign)
                and (
                    campaign["registration_history"]["contaminated_before_registration"]
                    or any(
                        x["payload"].get("data_hash") == lineage["data_hash"]
                        and x["payload"]["family"] != family
                        for x in past
                    )
                    or control.get("prior_other_campaign_attempts", 0) > 0
                    or control.get("prior_other_family_legacy_trials", 0) > 0
                ),
                "campaign_control": control,
                "run_id": run_id,
                "family": family,
                "hypothesis": hypothesis,
                "fingerprint": fingerprint,
                "repeat_of": repeated,
                "over_budget": len(peers) >= budget
                or (
                    bool(campaign)
                    and sum(x["payload"].get("data_hash") == lineage["data_hash"] for x in past)
                    >= budget
                ),
                "prior_data_attempts": sum(
                    r["payload"].get("data_hash") == lineage["data_hash"] for r in past
                ),
                "data_hash": lineage["data_hash"],
                "first_validation_access_at": min(
                    (
                        r["recorded_at"]
                        for r in past
                        if r["payload"].get("data_hash") == lineage["data_hash"]
                    ),
                    default=read_chain(root / "events.jsonl")[0]["recorded_at"],
                ),
            }
            append_chain(self.root / "trials.jsonl", "TRIAL_ATTEMPT", item)
        self.event(run_id, "TRIAL_REGISTERED", item)
        if item["over_budget"]:
            raise ContractError("EXPERIMENT_BUDGET_EXCEEDED")
        return item

    def _register_managed_trial(
        self,
        authority,
        run_id,
        family,
        hypothesis,
        budget,
        hypothesis_spec,
        config,
        lineage,
        fingerprint,
        task_context,
    ):
        """Claim an already debited unit; publish the exact authoritative outbox."""
        units = self._research_units(config, lineage)
        matches = [i for i, u in enumerate(units) if u["hypothesis_alias"] == hypothesis]
        if (
            len(matches) != 1
            or family != config["family"]["id"]
            or budget != config["family"]["budget"]
        ):
            raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
        context = None
        if lineage.get("task_binding") is not None:
            if task_context is None:
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            from aqrp.services.task_context import require_context

            context = require_context(task_context)
        authority.materialize()
        if context is None:
            with authority.transaction() as c:
                authority.verify(c)
                admission = authority.lookup_owner(c, "LEGACY", run_id)
                if admission is None:
                    binding = authority.lookup_legacy_actor(c, digest(config), self.root)
                    if binding and binding.get("owner_id") not in (None, run_id):
                        raise ContractError("EXECUTION_PLAN_SLOT_EXHAUSTED")
                    admission = authority.reserve(
                        c,
                        data_hash=lineage["data_hash"],
                        owner_kind="LEGACY",
                        owner_id=run_id,
                        key=binding["client_key"]
                        if binding
                        else digest({"ledger_root": str(self.root.resolve()), "run_id": run_id}),
                        request_hash=digest(config),
                        units=units,
                        family_id=family,
                        family_limit=budget,
                        service_kind="LEGACY",
                        output_root=self.root,
                    )
                    authority.queue_projection(
                        c,
                        authority.root
                        / "task-control"
                        / "admissions"
                        / (admission["admission_id"] + ".json"),
                        canonical(admission),
                        admission["admission_id"],
                        kind="SIDECAR",
                    )
            authority.materialize()
            if admission["decision"] != "ADMITTED":
                raise ContractError(admission.get("code") or "EXPERIMENT_BUDGET_EXCEEDED")
        with authority.transaction() as c:
            authority.verify(c)
            task_binding = lineage.get("task_binding")
            if task_binding is not None:
                context.authority.check(connection=c)
                if context.slot != "R":
                    raise ContractError("RESEARCH_CAMPAIGN_CONTEXT_REQUIRED")
                slot = c.execute(
                    "SELECT binding FROM slots WHERE task=? AND slot='R'",
                    (context.authority.task,),
                ).fetchone()
                task = c.execute(
                    "SELECT raw,hash FROM tasks WHERE id=?", (context.authority.task,)
                ).fetchone()
                if (
                    slot is None
                    or json.loads(slot[0]) != task_binding
                    or lineage.get("task_binding_hash") != digest(task_binding)
                    or task_binding["child_run_id"] != run_id
                    or task_binding["physical_ledger_root"] != str(self.root.resolve())
                    or task_binding["core_config_hash"] != digest(config)
                    or json.loads(task[0])["payload"]["research"] != config
                    or task_binding["plan_hash"] != task[1]
                ):
                    raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
                admission = authority.lookup_owner(c, "TASK", context.authority.task)
            else:
                admission = authority.lookup_owner(c, "LEGACY", run_id)
            if admission is None or admission["units"] != units:
                raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
            if admission["decision"] != "ADMITTED":
                raise ContractError(admission.get("code") or "EXPERIMENT_BUDGET_EXCEEDED")
            access = authority.research_access_before(c, admission["admission_id"])
            claim = authority.claim(
                c,
                admission["admission_id"],
                matches[0],
                self.root,
                run_id,
                digest(config),
                digest(lineage),
                {"hypothesis": hypothesis, "definition_hash": units[matches[0]]["definition_hash"]},
            )
            projected = [
                json.loads(bytes(row[0]))
                for row in c.execute(
                    "SELECT content FROM admission_outbox WHERE kind='TRIAL' ORDER BY seq"
                )
            ]
            existing = [
                row
                for row in projected
                if row["payload"]["run_id"] == run_id and row["payload"]["hypothesis"] == hypothesis
            ]
            if existing:
                if len(existing) != 1 or existing[0]["payload"]["fingerprint"] != fingerprint:
                    raise ContractError("ADMISSION_OWNERSHIP_CONFLICT")
                item = existing[0]["payload"]
            else:
                campaign = config.get("family", {}).get("campaign")
                control = lineage.get("campaign_control", {})
                item = {
                    "admission_history": access,
                    "cross_campaign_data_access": access["prior_other_family_admitted_units"] > 0
                    or bool(campaign)
                    and (
                        campaign["registration_history"]["contaminated_before_registration"]
                        or any(
                            r["payload"].get("data_hash") == lineage["data_hash"]
                            and r["payload"]["family"] != family
                            for r in projected
                        )
                        or control.get("prior_other_campaign_attempts", 0) > 0
                        or control.get("prior_other_family_legacy_trials", 0) > 0
                    ),
                    "campaign_control": control,
                    "run_id": run_id,
                    "family": family,
                    "hypothesis": hypothesis,
                    "fingerprint": fingerprint,
                    "repeat_of": [
                        r["payload"]["run_id"]
                        for r in projected
                        if r["payload"]["fingerprint"] == fingerprint
                    ],
                    "over_budget": False,
                    "prior_data_attempts": sum(
                        r["payload"].get("data_hash") == lineage["data_hash"] for r in projected
                    ),
                    "data_hash": lineage["data_hash"],
                    "first_validation_access_at": min(
                        (
                            r["recorded_at"]
                            for r in projected
                            if r["payload"].get("data_hash") == lineage["data_hash"]
                        ),
                        default=read_chain(self.path(run_id) / "events.jsonl")[0]["recorded_at"],
                    ),
                }
                authority.project_trial(c, admission["admission_id"], claim, item)
            self._freeze_trial_event(c, authority, admission, matches[0], run_id, item)
        authority.materialize()
        self._publish_trial_events(authority, run_id)
        return item

    def _freeze_trial_event(self, c, authority, admission, ordinal, run_id, item):
        """Freeze the complete run-event wrapper before its authoritative commit."""
        path = self.path(run_id) / f"admission-trial-event-{ordinal}.json"
        old = c.execute(
            "SELECT content FROM admission_outbox WHERE path=?", (str(path),)
        ).fetchone()
        if old is not None:
            frozen = json.loads(bytes(old[0]))
            if frozen["kind"] != "TRIAL_REGISTERED" or frozen["payload"] != item:
                raise ContractError("ADMISSION_INTEGRITY_ERROR")
            return
        with mutex(self.path(run_id) / ".lock"):
            events = read_chain(self.path(run_id) / "events.jsonl")
        matching = [
            e
            for e in events
            if e["kind"] == "TRIAL_REGISTERED"
            and e["payload"].get("hypothesis") == item["hypothesis"]
        ]
        if matching:
            if len(matching) != 1 or matching[0]["payload"] != item:
                raise ContractError("ADMISSION_INTEGRITY_ERROR")
            if admission.get("migrated"):
                # Migration freezes the original entire run/event files. Do not
                # add a new sidecar to an already immutable historical terminal.
                return
            frozen = matching[0]
        else:
            if events[-1]["kind"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
                raise ContractError("IMMUTABLE_TERMINAL_RUN")
            queued = [
                json.loads(bytes(row[1]))
                for row in c.execute(
                    "SELECT path,content FROM admission_outbox WHERE kind='SIDECAR'"
                )
                if Path(row[0]).parent == self.path(run_id)
                and Path(row[0]).name.startswith("admission-trial-event-")
            ]
            tip = max([events[-1], *queued], key=lambda e: e["seq"])
            frozen = {
                "seq": tip["seq"] + 1,
                "recorded_at": datetime.now(UTC).isoformat(timespec="microseconds"),
                "previous": tip["hash"],
                "kind": "TRIAL_REGISTERED",
                "payload": item,
            }
            frozen["hash"] = digest(frozen)
        authority.queue_projection(
            c, path, canonical(frozen), admission["admission_id"], kind="SIDECAR"
        )

    def _publish_trial_events(self, authority, run_id):
        """Append only committed wrappers, including crash-left predecessors."""
        with authority.transaction() as c:
            authority.verify(c)
            queued = [
                json.loads(bytes(row[1]))
                for row in c.execute(
                    "SELECT path,content FROM admission_outbox WHERE kind='SIDECAR'"
                )
                if Path(row[0]).parent == self.path(run_id)
                and Path(row[0]).name.startswith("admission-trial-event-")
            ]
        with mutex(self.path(run_id) / ".lock"):
            path = self.path(run_id) / "events.jsonl"
            events = read_chain(path)
            if b"".join(canonical(event) + b"\n" for event in events) != path.read_bytes():
                raise ContractError("ADMISSION_INTEGRITY_ERROR")
            for frozen in sorted(queued, key=lambda e: e["seq"]):
                seq = frozen["seq"]
                if seq < len(events):
                    if events[seq] != frozen:
                        raise ContractError("ADMISSION_INTEGRITY_ERROR")
                    continue
                if (
                    seq != len(events)
                    or frozen["previous"] != events[-1]["hash"]
                    or events[-1]["kind"] in ("SUCCEEDED", "FAILED", "CANCELLED")
                    or digest({k: v for k, v in frozen.items() if k != "hash"}) != frozen["hash"]
                ):
                    raise ContractError("ADMISSION_INTEGRITY_ERROR")
                with path.open("ab") as stream:
                    stream.write(canonical(frozen) + b"\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                events.append(frozen)

    def cache_get(self, key):
        path = self.root / ("cache-" + digest(key) + ".json")
        if not path.exists():
            return None
        item = json.loads(path.read_bytes())
        if item["key"] != key or item["checksum"] != digest(item["payload"]):
            raise ContractError("CACHE_CORRUPTION")
        return item["payload"]

    def cache_put(self, key, payload):
        data = canonical({"key": key, "payload": payload, "checksum": digest(payload)})
        path = self.root / ("cache-" + digest(key) + ".json")
        with mutex(self.root / ".cache-lock"):
            if path.exists():
                if path.read_bytes() != data:
                    raise ContractError("NONDETERMINISTIC_CACHE_RESULT")
            else:
                immutable_write(path, data)

    def catalogue(self):
        rows = []
        for p in self.root.glob("*/manifest.json"):
            m = self.verify(p.parent.name)
            rows.append({"run_id": m["run_id"], "status": m["status"]})
        if not rows:
            return []
        import pandas as pd

        with duckdb.connect(":memory:") as db:
            db.register("runs", pd.DataFrame(rows))
            return db.sql("SELECT * FROM runs ORDER BY run_id").df().to_dict("records")

    def compare(self, a, b):
        ma, mb = self.verify(a), self.verify(b)
        return {
            "a": a,
            "b": b,
            "status_equal": ma["status"] == mb["status"],
            "artifact_differences": sorted(
                set((r["path"], r["sha256"]) for r in ma["files"])
                ^ set((r["path"], r["sha256"]) for r in mb["files"])
            ),
        }

    def family(self, family, declarations, results=None, *, definitions=None):
        if not declarations or len(set(declarations)) != len(declarations):
            raise ContractError("INVALID_FAMILY_DECLARATIONS")
        with mutex(self.root / ".family-lock"):
            path = self.root / ("family-" + digest(family) + ".jsonl")
            rows = read_chain(path)
            if not rows:
                append_chain(path, "DECLARED", {"ids": declarations, "definitions": definitions})
                rows = read_chain(path)
            if rows[0]["payload"] != {"ids": declarations, "definitions": definitions}:
                raise ContractError("FAMILY_REDEFINED_AFTER_REGISTRATION")
            if results is not None:
                if not set(results) <= set(declarations):
                    raise ContractError("UNREGISTERED_HYPOTHESIS")
                append_chain(path, "RESULTS", results)
                rows = read_chain(path)
            latest = {}
            duplicates = set()
            for row in rows[1:]:
                for k, v in row["payload"].items():
                    if k in latest:
                        duplicates.add(k)
                    latest[k] = v
            return {
                "ids": declarations,
                "results": latest,
                "duplicate_hypotheses": sorted(duplicates),
            }
