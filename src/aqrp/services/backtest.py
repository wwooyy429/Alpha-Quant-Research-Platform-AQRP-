"""Immutable engineering simulation service, formal refusal and numerical replay."""

import hashlib
import uuid
from pathlib import Path

from aqrp.backtest.contracts import BacktestResult, EngineeringBacktestRequest, validate
from aqrp.backtest.engine import Simulator
from aqrp.backtest.exact import freeze, present, thaw
from aqrp.backtest.ledger import account, assert_economic_identity, reconcile
from aqrp.backtest.transactions import TransactionStore, guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.environment import runtime_manifest, verify_runtime
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger, read_chain
from aqrp.factors.admission import reviewed_policy
from aqrp.performance.metrics import performance
from aqrp.portfolio.contracts import load

PROTOCOL = {
    "profile": "SYNTHETIC_EXECUTION_1",
    "schema": "simulation/1.0.0",
    "G1_sha": "5262032bee4f631f68763e57510e1878945f6b8c",
    "scope": "ENGINEERING_TEST_ONLY",
    "financial_approval": "NONE",
}


def _bound_read(ledger, run_id, name, manifest):
    entries = [e for e in manifest["files"] if e["path"] == name]
    if len(entries) != 1:
        raise ContractError("SIMULATION_ARTIFACT_NOT_TERMINAL_MANIFESTED", name)
    p = guard_path(ledger.path(run_id) / name)
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != entries[0]["sha256"]:
        raise ContractError("SIMULATION_ARTIFACT_BYTES_CHANGED", name)
    return raw


def _reconciled_account(state):
    c = account(state)
    rebuilt = reconcile(state["initial_cash"], state["journal"], state["assets"])
    if (
        rebuilt["cash_total"] != c["cash_total"]
        or any(rebuilt["quantities"][k] != a["quantity"] for k, a in state["assets"].items())
        or rebuilt["balances"]["receivable"] + rebuilt["balances"]["payable"]
        != c["receivable"] - c["payable"]
    ):
        raise ContractError("RAW_JOURNAL_ACCOUNT_RECONCILIATION_FAILED")
    return c, rebuilt


def projection(state):
    c, rebuilt = _reconciled_account(state)
    return {
        "state_sha256": digest(freeze(state)),
        "account": present(c),
        "positions": present(state["assets"]),
        "orders": present(state["orders"]),
        "fills": present(state["fills"]),
        "journal": present(state["journal"]),
        "liquidations": present(state["liquidations"]),
        "valuations": present(state["valuations"]),
        "fragments": present(state["fragments"]),
        "reconciliation": present(rebuilt),
        "performance": present(performance(state)),
    }


def audit_bytes(raw, expected):
    if raw != canonical(expected) or load(raw) != expected:
        raise ContractError("SIMULATION_PUBLISHED_BYTES_CHANGED")
    return {
        "scope": "ACTUAL_SERIALIZED_FINANCIAL_OUTPUT",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "result_and_expected_projection_exact": True,
    }


def _failure_snapshot(ledger, run, simulator, result):
    """Never publish a cached account as a durable one after a captured interruption."""
    root = guard_path(ledger.path(run))
    if not (root / "transactions").exists():
        result["committed_state_verification"] = {"status": "NOT_STARTED"}
        return
    try:
        state, records, files = TransactionStore(root / "transactions").verified_snapshot()
        current, _ = _reconciled_account(state)
        assert_economic_identity(state)
    except (Exception, KeyboardInterrupt) as recovery_error:
        evidence = {
            "status": "UNVERIFIED_COMMITTED_STATE",
            "financial_state_known": False,
            "error": getattr(recovery_error, "code", type(recovery_error).__name__),
            "message": str(recovery_error),
            "original_status": result["status"],
            "original_transaction_files_preserved": True,
        }
        result["status"] = "FAILED"
        result["reasons"].append("COMMITTED_STATE_UNVERIFIED")
    else:
        evidence = {
            "status": "VERIFIED_COMMITTED_PREFIX",
            "financial_state_known": True,
            "commit_count": len(records),
            "state_sha256": digest(freeze(state)),
            "prefix_sha256": records[-1]["sha256"] if records else digest(freeze(state)),
            "trace_scope": "Observed scheduler trace may stop before a published commit; committed-trace and transactions are the durable authority",
        }
        payloads = {
            "failed-state.json": freeze(state),
            "transactions.json": records,
            "transaction-files.json": files,
            "committed-trace.json": [
                {
                    "commit_seq": r["commit_seq"],
                    "sha256": r["sha256"],
                    "dispatch_key": r["dispatch_key"],
                    "children": r["children"],
                }
                for r in records
            ],
        }
        if simulator is not None:
            payloads["trace.json"] = simulator.trace
        for name, payload in payloads.items():
            path = root / name
            if path.exists():
                if guard_path(path).read_bytes() != canonical(payload):
                    raise ContractError("FAILURE_PUBLICATION_CONFLICT", name)
            else:
                ledger.artifact(run, name, payload)
        result["last_committed_account"] = present(current)
    result["committed_state_verification"] = evidence
    ledger.artifact(run, "failure-recovery.json", evidence)


def simulate_engineering(request, ledger_root, code_commit):
    if not isinstance(request, EngineeringBacktestRequest):
        raise ContractError("FROZEN_SIMULATION_REQUEST_REQUIRED")
    policy = reviewed_policy()
    environment = runtime_manifest()
    verify_runtime(environment)
    ledger = ExperimentLedger(guard_path(ledger_root))
    lineage = {
        "code_commit": code_commit,
        "code_bundle": policy["bundle_sha256"],
        "data_hash": request.content_hash,
        "environment": environment,
        "environment_hash": digest(environment),
        "protocol_hash": digest(PROTOCOL),
        "permission_domain": "ENGINEERING_TEST_ONLY",
        "seed": 0,
        "code_commit_binding": "Caller-declared; clean SDK binds actual source, wheel and full commit",
    }
    config = {
        "schema_version": "simulation-run/1.0.0",
        "raw_request_hex": request.raw.hex(),
        "request_sha256": request.content_hash,
        "protocol": PROTOCOL,
    }
    run = ledger.start(config, lineage)
    return _execute_engineering(request, ledger, run, code_commit, policy)


def _execute_engineering(request, ledger, run, code_commit, policy):
    result = {
        "schema_version": "simulation-result/1.0.0",
        "run_id": run,
        "status": "FAILED",
        "scope": "ENGINEERING_TEST_ONLY",
        "financial_approval": "NONE",
        "executable": False,
        "request_sha256": request.content_hash,
        "code_bundle": policy["bundle_sha256"],
    }
    base_result = result.copy()
    simulator = None
    try:
        x = validate(request)
        simulator = Simulator(x, ledger.path(run), code_commit)
        state = simulator.run()
        computed = projection(state)
        ledger.artifact(run, "state.json", freeze(state))
        ledger.artifact(run, "trace.json", simulator.trace)
        ledger.artifact(run, "portfolio-lineage.json", simulator.portfolios)
        ledger.artifact(run, "transactions.json", simulator.store.records)
        transaction_files = [
            {
                "path": p.relative_to(ledger.path(run)).as_posix(),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
            for p in sorted((ledger.path(run) / "transactions").iterdir())
            if p.name != ".lock"
        ]
        ledger.artifact(run, "transaction-files.json", transaction_files)
        result.update(status="SUCCEEDED", **computed)
        wire = canonical(result)
        audit_bytes(wire, result)
        ledger.artifact(run, "result.json", result)
        audit = audit_bytes((ledger.path(run) / "result.json").read_bytes(), result)
        ledger.artifact(run, "published-byte-audit.json", audit)
        ledger.finish(run, "SUCCEEDED")
    except (Exception, KeyboardInterrupt) as exc:
        if (ledger.path(run) / "result.json").exists():
            ledger.artifact(
                run,
                "publication-failure.json",
                {"code": getattr(exc, "code", type(exc).__name__), "not_published": True},
            )
            ledger.finish(run, "FAILED")
            raise
        cancelled = isinstance(exc, KeyboardInterrupt)
        result = base_result.copy()
        result["status"] = "CANCELLED" if cancelled else "FAILED"
        result["reasons"] = [getattr(exc, "code", type(exc).__name__)]
        result["error"] = {
            "type": type(exc).__name__,
            "field": getattr(exc, "field", ""),
            "message": str(exc),
        }
        _failure_snapshot(ledger, run, simulator, result)
        ledger.artifact(run, "result.json", result)
        ledger.finish(run, result["status"])
        if not isinstance(exc, (ContractError, KeyboardInterrupt)):
            raise
    manifest = ledger.verify(run)
    result["manifest"] = manifest
    wire = canonical(result)
    returned = load(wire)
    returned.pop("manifest")
    if canonical(returned) != _bound_read(ledger, run, "result.json", manifest):
        raise ContractError("SIMULATION_RETURN_BYTES_CHANGED")
    return BacktestResult(wire)


def resume_engineering(ledger_root, run_id):
    """Resume an interrupted unfinished engineering run with its exact original config/code."""
    policy = reviewed_policy()
    verify_runtime(runtime_manifest())
    ledger = ExperimentLedger(guard_path(ledger_root))
    root = guard_path(ledger.path(run_id))
    events = read_chain(guard_path(root / "events.jsonl"))
    if not events or events[-1]["kind"] in ("SUCCEEDED", "FAILED", "CANCELLED"):
        raise ContractError("NONRUNNING_SIMULATION_CANNOT_RESUME")
    config = load(guard_path(root / "config.json").read_bytes())
    lineage = load(guard_path(root / "lineage.json").read_bytes())
    if (
        digest(config) != events[0]["payload"]["config_hash"]
        or digest(lineage) != events[0]["payload"]["lineage_hash"]
    ):
        raise ContractError("RESUME_CONFIG_LINEAGE_CHANGED")
    if (
        lineage["permission_domain"] != "ENGINEERING_TEST_ONLY"
        or lineage["code_bundle"] != policy["bundle_sha256"]
        or config["protocol"] != PROTOCOL
    ):
        raise ContractError("EXACT_ENGINEERING_RESUME_PACKAGE_REQUIRED")
    if any(
        (root / n).exists()
        for n in ("result.json", "state.json", "trace.json", "transactions.json")
    ):
        raise ContractError("PARTIAL_PUBLICATION_REQUIRES_EVIDENCE_REVIEW")
    request = EngineeringBacktestRequest(bytes.fromhex(config["raw_request_hex"]))
    if (
        request.content_hash != config["request_sha256"]
        or request.content_hash != lineage["data_hash"]
    ):
        raise ContractError("RESUME_REQUEST_HASH_CHANGED")
    ledger.event(
        run_id,
        "ENGINEERING_RECOVERY_STARTED",
        {"original_config_hash": digest(config), "native_isolation": "DEFERRED / NOT VERIFIED"},
    )
    return _execute_engineering(request, ledger, run_id, lineage["code_commit"], policy)


def simulate_approved(request, ledger_root, code_commit):
    """Separate refusal path; never imports a provider or executes the simulator."""
    policy = reviewed_policy()
    ledger = ExperimentLedger(guard_path(ledger_root))
    raw = (
        request.raw
        if isinstance(request, EngineeringBacktestRequest)
        else canonical({"invalid_type": type(request).__name__})
    )
    lineage = {
        "code_commit": code_commit,
        "code_bundle": policy["bundle_sha256"],
        "data_hash": hashlib.sha256(raw).hexdigest(),
        "environment": runtime_manifest(),
        "protocol_hash": digest(PROTOCOL),
        "permission_domain": "FORMAL_APPROVAL_GATE",
        "seed": 0,
    }
    run = ledger.start({"request_hex": raw.hex(), "gate": "APPROVAL_REQUIRED"}, lineage)
    result = {
        "schema_version": "simulation-result/1.0.0",
        "run_id": run,
        "status": "REJECTED",
        "reasons": ["APPROVAL_REQUIRED"],
        "scope": "FORMAL_APPROVAL_GATE",
        "financial_approval": "NONE",
        "executable": False,
    }
    ledger.artifact(run, "result.json", result)
    result["manifest"] = ledger.finish(run, "FAILED")
    return BacktestResult(canonical(result))


def result_engineering(ledger_root, run_id):
    ledger = ExperimentLedger(guard_path(ledger_root))
    m = ledger.verify(run_id)
    if any(e["path"] == "publication-failure.json" for e in m["files"]):
        raise ContractError("PUBLICATION_FAILED_NOT_REPLAYABLE")
    return load(_bound_read(ledger, run_id, "result.json", m))


def replay_engineering(ledger_root, run_id, destination):
    ledger = ExperimentLedger(guard_path(ledger_root))
    manifest = ledger.verify(run_id)
    original = result_engineering(ledger_root, run_id)
    if original["status"] != "SUCCEEDED":
        raise ContractError("FAILED_SIMULATION_NOT_REPLAYABLE")
    lineage = load(_bound_read(ledger, run_id, "lineage.json", manifest))
    if lineage["code_bundle"] != reviewed_policy()["bundle_sha256"]:
        raise ContractError("EXACT_ORIGINAL_SIMULATION_PACKAGE_REQUIRED")
    config = load(_bound_read(ledger, run_id, "config.json", manifest))
    request = EngineeringBacktestRequest(bytes.fromhex(config["raw_request_hex"]))
    if request.content_hash != config["request_sha256"] or config["protocol"] != PROTOCOL:
        raise ContractError("REPLAY_CONFIG_PROTOCOL_MISMATCH")
    files = load(_bound_read(ledger, run_id, "transaction-files.json", manifest))
    for e in files:
        p = guard_path(ledger.path(run_id) / e["path"])
        if (
            not p.is_relative_to(ledger.path(run_id).absolute())
            or hashlib.sha256(p.read_bytes()).hexdigest() != e["sha256"]
        ):
            raise ContractError("REPLAY_TRANSACTION_FILE_CHANGED")
    state = thaw(load(_bound_read(ledger, run_id, "state.json", manifest)))
    if digest(freeze(state)) != original["state_sha256"]:
        raise ContractError("REPLAY_STATE_CHANGED")
    out = guard_path(Path(destination) / str(uuid.uuid4()))
    rerun = Simulator(validate(request), out, lineage["code_commit"])
    rerun.run()
    recomputed = projection(rerun.store.state)
    expected = {k: original[k] for k in recomputed}
    if recomputed != expected:
        raise ContractError("NUMERICAL_SIMULATION_REPLAY_MISMATCH")
    return {
        "status": "NUMERICAL_REPLAY_VERIFIED",
        "original_run_id": run_id,
        "state_sha256": recomputed["state_sha256"],
        "destination": str(out),
        "scope": "ENGINEERING_TEST_ONLY",
        "financial_approval": "NONE",
        "full_historical_host_reproduced": False,
    }
