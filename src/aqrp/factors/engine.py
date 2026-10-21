"""Trusted host queries P1 per decision; only admitted builtins receive DataView."""

import hashlib
import json
import platform
import uuid
from dataclasses import asdict
from pathlib import Path

from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.pit import visible_rows
from aqrp.data.query import query
from aqrp.data.store import read_snapshot

from .admission import LOCK_HASH, validate_admission
from .contracts import FactorContext, SignalBatch, freeze_parameters, uuid_value
from .registry import FactorRegistry


class FactorEngine:
    def __init__(self, registry: FactorRegistry):
        self.registry = registry

    def run(self, ref, query_spec, decision_time, snapshot_ref, **options):
        return self.run_pinned(
            self.registry.resolve(ref), query_spec, decision_time, snapshot_ref, **options
        )

    def run_pinned(
        self,
        pin,
        query_spec,
        decision_time,
        snapshot_ref,
        *,
        parameters=None,
        run_id=None,
        computation_id=None,
        seed=0,
        mode="test",
        requested_weight=None,
    ):
        if mode != "test":
            raise ContractError("STRATEGY_OR_EXTERNAL_EXECUTION_UNSUPPORTED", "mode")
        spec = self.registry.check_pin(pin)
        validate_admission(spec)
        if (
            not isinstance(query_spec, QuerySpec)
            or query_spec.price_basis != spec.price_basis
            or not set(spec.required_fields) <= set(query_spec.fields)
        ):
            raise ContractError("FACTOR_QUERY_MISMATCH", "QuerySpec")
        params, params_hash = freeze_parameters(spec, parameters)
        cutoff = utc(decision_time, field="decision_time")
        view = query(query_spec, cutoff, snapshot_ref)
        _, tables = read_snapshot(snapshot_ref)
        schedule = tuple(
            sorted(
                (r["session_date"], r["close_at"])
                for r in visible_rows("calendar", tables["calendar"].to_pylist(), cutoff)
                if r["calendar_id"] == query_spec.calendar_id
                and r["market_id"] == query_spec.market_id
                and query_spec.session_range[0] <= r["session_date"] <= query_spec.session_range[1]
            )
        )
        aliases = visible_rows("symbol_alias", tables["symbol_alias"].to_pylist(), cutoff)
        symbols = tuple(
            (
                sid,
                next(
                    (
                        r["symbol"]
                        for r in aliases
                        if r["security_id"] == sid and r["market_id"] == query_spec.market_id
                    ),
                    None,
                ),
            )
            for sid in query_spec.security_ids
        )
        context = FactorContext(
            spec,
            str(uuid.uuid4()) if run_id is None else run_id,
            str(uuid.uuid4()) if computation_id is None else computation_id,
            cutoff,
            query_spec.session_range[1],
            snapshot_ref.snapshot_id,
            snapshot_ref.manifest_hash,
            view.query_hash,
            query_spec.calendar_id,
            view.metadata["calendar_version"],
            schedule,
            symbols,
            query_spec.market_id,
            tuple(query_spec.security_ids),
            params,
            params_hash,
            seed,
            requested_weight,
        )
        # No dynamic module name, path, expression or caller-provided factory is accepted.
        from .builtins import BuiltinFactor

        return BuiltinFactor().compute(view, context)


def write_run(batch, output_root, registry):
    if not isinstance(batch, SignalBatch):
        raise ContractError("SIGNAL_BATCH_REQUIRED", "batch")
    config = json.loads(batch.config_snapshot)
    run_id = uuid_value(config["run_id"])
    root = Path(output_root) / run_id
    root.mkdir(parents=True, exist_ok=False)
    payloads = {
        "config.json": batch.config_snapshot,
        "signals.json": canonical([asdict(r) for r in batch.rows]),
        "registry-events.json": canonical([asdict(e) for e in registry.events]),
    }
    for name, data in payloads.items():
        (root / name).write_bytes(data)
    manifest = {
        "run_id": config["run_id"],
        "status": "SUCCEEDED",
        "mode": "TEST_ONLY",
        "financial_approval": "NONE",
        "runtime": {
            "python": platform.python_version(),
            "os": platform.platform(),
            "dependency_lock_sha256": LOCK_HASH,
        },
        "content_hash": batch.content_hash,
        "logical_hash": batch.logical_hash,
        "artifacts": [
            {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}
            for name, data in sorted(payloads.items())
        ],
    }
    # Artifact hashes bind actual persisted bytes; logical projections are separate.
    (root / "manifest.json").write_bytes(canonical(manifest))
    return root


def write_failure(output_root, run_id, error):
    root = Path(output_root) / uuid_value(run_id)
    root.mkdir(parents=True, exist_ok=False)
    (root / "manifest.json").write_bytes(
        canonical(
            {
                "run_id": run_id,
                "status": "FAILED",
                "error_type": type(error).__name__,
                "code": getattr(error, "code", "EXECUTION_ERROR"),
            }
        )
    )
    return root
