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

    def path(self, run_id):
        try:
            key = str(uuid.UUID(run_id))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ContractError("INVALID_RUN_ID") from exc
        return self.root / key

    def start(self, config, lineage):
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
        metadata = canonical(lineage)
        run_id = str(uuid.uuid4())
        root = self.path(run_id)
        root.mkdir(exist_ok=False)
        immutable_write(root / "config.json", content)
        immutable_write(root / "lineage.json", metadata)
        append_chain(
            root / "events.jsonl",
            "RUNNING",
            {"config_hash": digest(config), "lineage_hash": digest(lineage)},
        )
        return run_id

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

    def register_trial(self, run_id, family, hypothesis, *, budget, hypothesis_spec=None):
        if not family or not hypothesis or type(budget) is not int or budget < 1:
            raise ContractError("INVALID_EXPERIMENT_FAMILY")
        root = self.path(run_id)
        config = json.loads((root / "config.json").read_bytes())
        lineage = json.loads((root / "lineage.json").read_bytes())
        fingerprint_config = {k: v for k, v in config.items() if k not in ("family", "candidates")}
        if "candidates" in config:
            fingerprint_config["candidates"] = [
                {k: v for k, v in c.items() if k != "hypothesis"} for c in config["candidates"]
            ]
        fingerprint = digest(
            {
                "config": fingerprint_config,
                "lineage": {
                    k: v for k, v in lineage.items() if k not in ("protocol_hash", "code_commit")
                },
                "hypothesis_spec": {
                    k: v
                    for k, v in (hypothesis_spec or {}).items()
                    if k not in ("hypothesis", "score_key")
                },
            }
        )
        with mutex(self.root / ".trials-lock"):
            past = read_chain(self.root / "trials.jsonl")
            peers = [x for x in past if x["payload"]["family"] == family]
            repeated = [
                x["payload"]["run_id"] for x in past if x["payload"]["fingerprint"] == fingerprint
            ]
            item = {
                "run_id": run_id,
                "family": family,
                "hypothesis": hypothesis,
                "fingerprint": fingerprint,
                "repeat_of": repeated,
                "over_budget": len(peers) >= budget,
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
