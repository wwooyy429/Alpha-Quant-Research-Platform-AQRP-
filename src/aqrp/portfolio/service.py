"""One immutable engineering service: source/PIT gates, risk, targets and run evidence."""

import hashlib
import json
import platform
import sys

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.factors.admission import reviewed_policy
from aqrp.risk.checks import check_target

from .construct import build_candidate
from .contracts import PortfolioRequest, PortfolioResult, load


def construct_engineering(request, ledger_root, code_commit):
    policy = reviewed_policy()
    if not isinstance(request, PortfolioRequest):
        raise ContractError("FROZEN_REQUEST_REQUIRED")
    ledger = ExperimentLedger(ledger_root)
    config = {
        "schema_version": "portfolio-run/1.0.0",
        "raw_request_hex": request.raw.hex(),
        "request_sha256": request.content_hash,
    }
    lineage = {
        "code_commit": code_commit,
        "code_bundle": policy["bundle_sha256"],
        "data_hash": request.content_hash,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "lock_sha256": "86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb",
        },
        "protocol_hash": digest(
            {"profile": "SYNTHETIC_PORTFOLIO_1", "G1": "265af16353d85ce8c2d229a7517809d707498da8"}
        ),
        "permission_domain": "ENGINEERING_TEST_ONLY",
        "seed": 0,
    }
    run_id = ledger.start(config, lineage)
    result = {
        "schema_version": "portfolio-result/1.0.0",
        "run_id": run_id,
        "scope": "ENGINEERING_TEST_ONLY",
        "financial_approval": "NONE",
        "executable": False,
        "request_hash": request.content_hash,
        "code_bundle": policy["bundle_sha256"],
        "input_lineage": lineage,
        "status": "REJECTED",
    }
    try:
        candidate = build_candidate(request)
        decision = check_target(candidate, request)
        ledger.artifact(run_id, "candidate.json", load(candidate.raw))
        ledger.artifact(run_id, "risk.json", decision)
        result["risk"] = decision
        if decision["passed"]:
            target = {
                **decision["post"]["metrics"],
                "scope": "ENGINEERING_TEST_ONLY",
                "executable": False,
                "request_hash": request.content_hash,
                "risk_hash": decision["content_sha256"],
            }
            target["content_sha256"] = digest(target)
            result["target"] = target
            result["rebalance_proposals"] = [
                {
                    "security_id": sid,
                    "delta_qty": qty,
                    "executable": False,
                    "scope": "ENGINEERING_TEST_ONLY",
                    "source_price_ref": load(request.raw)["inputs"]["prices"]["ref"],
                    "decision_time": load(request.raw)["context"]["decision_time"],
                    "request_hash": request.content_hash,
                }
                for sid, qty in target["deltas"].items()
                if qty != "0"
            ]
            result["status"] = "SUCCEEDED"
        else:
            result["reasons"] = sorted(
                {
                    c["code"]
                    for phase in ("pre", "post")
                    for c in decision[phase]["checks"]
                    if not c["passed"]
                }
            )
        ledger.artifact(run_id, "result.json", result)
        ledger.finish(run_id, "SUCCEEDED" if result["status"] == "SUCCEEDED" else "FAILED")
    except ContractError as exc:
        result["status"] = "INFEASIBLE" if exc.code.startswith("INFEASIBLE") else "REJECTED"
        result["reasons"] = [exc.code]
        result["error"] = {
            "code": exc.code,
            "field": exc.field,
            "request_id": run_id,
            "risk": "NOT_EVALUATED_INVALID_INPUT",
        }
        ledger.artifact(run_id, "result.json", result)
        ledger.finish(run_id, "FAILED")
    except Exception as exc:
        ledger.artifact(run_id, "failure.json", {"type": type(exc).__name__, "message": str(exc)})
        ledger.finish(run_id, "FAILED")
        raise
    result["manifest"] = ledger.verify(run_id)
    return PortfolioResult(canonical(result))


def construct_approved(request, ledger_root, code_commit):
    """Real financial approval is deferred; package policy cannot grant it from caller flags."""
    policy = reviewed_policy()
    if policy["financial_approval"] == "NONE":
        # Do not run any ranking/target arithmetic or fall back to the engineering path.
        ledger = ExperimentLedger(ledger_root)
        raw = (
            request.raw
            if isinstance(request, PortfolioRequest)
            else canonical({"invalid_input_type": type(request).__name__})
        )
        lineage = {
            "code_commit": code_commit,
            "code_bundle": policy["bundle_sha256"],
            "data_hash": hashlib.sha256(raw).hexdigest(),
            "environment": {"python": sys.version},
            "protocol_hash": digest({"formal": "NOT_APPROVED"}),
            "permission_domain": "FORMAL_APPROVAL_GATE",
            "seed": 0,
        }
        run_id = ledger.start({"raw_request_hex": raw.hex()}, lineage)
        result = {
            "schema_version": "portfolio-result/1.0.0",
            "run_id": run_id,
            "status": "REJECTED",
            "reasons": ["APPROVAL_REQUIRED"],
            "scope": "FORMAL_APPROVAL_GATE",
            "financial_approval": "NONE",
            "executable": False,
        }
        ledger.artifact(run_id, "result.json", result)
        result["manifest"] = ledger.finish(run_id, "FAILED")
        return PortfolioResult(canonical(result))
    raise ContractError("UNAPPROVED_EXECUTION_ENVIRONMENT")


def replay_engineering(ledger_root, run_id):
    """Verify immutable original result and hashes; no financial reapproval or new order."""
    ledger = ExperimentLedger(ledger_root)
    manifest = ledger.verify(run_id)
    rows = [e for e in manifest["files"] if e["path"] == "result.json"]
    if len(rows) != 1:
        raise ContractError("RESULT_NOT_IN_TERMINAL_MANIFEST")
    path = ledger.path(run_id) / "result.json"
    raw = path.read_bytes()
    if path.is_symlink() or hashlib.sha256(raw).hexdigest() != rows[0]["sha256"]:
        raise ContractError("RESULT_BYTES_CHANGED")
    result = json.loads(raw)
    return {
        "status": "IMMUTABLE_ORIGINAL_RESULT_VERIFIED",
        "result": result,
        "manifest": manifest,
        "financial_approval": "NONE",
    }
