"""G1 finite design examples only: not a task runner, authority or UI implementation."""

import argparse
import importlib.util
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location("numeric_design_reference", ROOT / "reference_check.py")
numeric = importlib.util.module_from_spec(spec)
spec.loader.exec_module(numeric)


def completion_example(x):
    """Decide the declared model outcome; all flags are model premises, not real evidence."""
    def result(status, reason):
        return {"status": status, "reason": reason}

    if x.get("financial_unknown"):
        return result("FAILED", "COMMITTED_STATE_UNVERIFIED")
    if x.get("unknown_side_effects") or x.get("partial_publication"):
        return result("FAILED", "RECOVERY_REQUIRED")
    if x.get("binding_conflict") or x.get("artifact_corruption"):
        return result("FAILED", "RECOVERY_REQUIRED")
    if any(v == "FAILED" for v in x["slot_statuses"].values()):
        return result("FAILED", "REQUIRED_CHILD_FAILED")
    if any(v == "REJECTED" for v in x["slot_statuses"].values()):
        return result("FAILED", "REQUIRED_STAGE_REJECTED")
    if x.get("claimed_success") and not (
        x.get("completion_verified") and x.get("terminal_commit_verified")
    ):
        return result("FAILED", "INTEGRITY_ERROR")
    if x.get("cancel_intent") and not x.get("success_committed_first"):
        if x.get("quiescent") and x.get("safe_cancel_verified"):
            return result("CANCELLED", "SAFE_CANCELLATION_VERIFIED")
        return result("RUNNING", "CANCEL_REQUESTED")
    kind = x["kind"]
    if kind == "research":
        required = {"R", "RV"}
    elif kind == "engineering_pipeline":
        required = {"R", "PLAN", "B", "BV"}
        if not x.get("resolved_plan_frozen"):
            return result("FAILED", "INTEGRITY_ERROR") if x.get("claimed_success") else result("RUNNING", "PLAN_NOT_FROZEN")
        if x["decisions"] < 1:
            return result("FAILED", "NO_REQUIRED_DECISIONS")
        required |= {f"P:{i}" for i in range(x["decisions"])}
    elif kind == "replay":
        required = {"SV", "E", "CV"}
        if x["profile"] not in {"P5_NUMERICAL", "PUBLISHED_REF_PROJECTION"}:
            return result("FAILED", "REPLAY_PROFILE_NOT_APPROVED")
        if x["profile"] == "P5_NUMERICAL":
            required |= {f"P:{i}" for i in range(x["decisions"])}
    else:
        return result("FAILED", "TASK_KIND_NOT_APPROVED")
    registered = set(x["registry_slots"])
    if registered != required or len(x["registry_slots"]) != len(registered):
        return result("FAILED", "SLOT_SET_MISMATCH")
    statuses = x["slot_statuses"]
    if set(statuses) - required:
        return result("FAILED", "SLOT_SET_MISMATCH")
    if any(v == "FAILED" for v in statuses.values()):
        return result("FAILED", "REQUIRED_CHILD_FAILED")
    if any(v == "REJECTED" for v in statuses.values()):
        return result("FAILED", "REQUIRED_STAGE_REJECTED")
    complete = all(statuses.get(k) == "VERIFIED_SUCCESS" for k in required)
    if statuses.get("B") == "VERIFIED_SUCCESS" and any(
        statuses.get(k) != "VERIFIED_SUCCESS" for k in required if k.startswith("P:")
    ):
        return result("FAILED", "RECOVERY_REQUIRED")
    if x.get("claimed_success") and not (
        complete and x.get("completion_verified") and x.get("terminal_commit_verified")
    ):
        return result("FAILED", "INTEGRITY_ERROR")
    if x.get("cancel_intent") and not x.get("success_committed_first"):
        if x.get("quiescent") and x.get("safe_cancel_verified"):
            return result("CANCELLED", "SAFE_CANCELLATION_VERIFIED")
        return result("RUNNING", "CANCEL_REQUESTED")
    if not complete:
        return result("RUNNING", "REQUIRED_SLOTS_PENDING")
    if not x.get("required_artifacts_verified") or not x.get("all_bindings_verified"):
        return result("FAILED", "RECOVERY_REQUIRED")
    if kind == "replay" and not x.get("comparison_verified"):
        return result("FAILED", "REPLAY_COMPARISON_FAILED")
    if not x.get("dispatch_closed"):
        return result("RUNNING", "DISPATCH_NOT_CLOSED")
    if not x.get("completion_verified") or not x.get("terminal_commit_verified"):
        return result("RUNNING", "GLOBAL_COMPLETION_PENDING")
    return result("SUCCEEDED", "ALL_REQUIRED_EVIDENCE_COMMITTED")


def binding_example(x):
    """Compare literal premises only; this does not authenticate a live worker or filesystem."""
    if not x["has_context"]:
        return {"action": "LEGACY_UNCHANGED", "task_terminal": False}
    reject = {"action": "RECOVERY_REQUIRED", "task_terminal": False}
    if not x["record_preexists"] or not x["initial_binding_valid"]:
        return reject
    if not x["unique_active_claim"] or x["handle_epoch"] != x["active_epoch"]:
        return reject
    if x["actual"] != x["expected"]:
        return reject
    root = str(PurePosixPath(x["parent_root"]) / "portfolio-runs")
    if root != x["actual"]["physical_ledger_root"] or not x["root_enumeration_complete"]:
        return reject
    if not x["adapted_bytes_bound_before_call"]:
        return reject
    started, terminal = x["core_start_seq"], x["core_terminal_seq"]
    if started is not None and x["registration_seq"] >= started:
        return reject
    if terminal is not None:
        if started is None or terminal <= started or not x["terminal_verified"]:
            return reject
        return {"action": "REUSE_VERIFIED_SLOT", "task_terminal": False}
    if started is None and x["slot_state"] == "BOUND" and x["no_core_side_effects_proven"]:
        return {"action": "CALL_ONCE", "task_terminal": False}
    return reject


def evaluate(case):
    if case["kind"] == "task_completion":
        return completion_example(case["inputs"])
    if case["kind"] == "nested_binding":
        return binding_example(case["inputs"])
    if case["kind"] == "numeric_rejection":
        try:
            numeric.reference({"kind": case["inputs"]["numeric_kind"], "inputs": case["inputs"]["fields"]})
        except numeric.ReferenceNumberError as error:
            return {"error": error.code, "raw_retained": True}
        return {"error": None, "raw_retained": True}
    return numeric.reference(case)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads((ROOT / "SUPPLEMENTAL_CANDIDATES.json").read_bytes())
    records = []
    for case in data["cases"]:
        try:
            actual, error = evaluate(case), None
        except Exception as exc:
            actual, error = None, type(exc).__name__
        records.append({"id": case["id"], "expected": case["expected"], "actual": actual,
                        "error": error, "pass": error is None and type(actual) is type(case["expected"]) and actual == case["expected"]})
    result = {"executor": "Codex developer G1 reference, not independent GPT Work audit",
              "scope": "Finite design/numeric examples only; no actual TaskService/core/P6 UI/concurrency tests",
              "groups": len(records), "passed": sum(r["pass"] for r in records),
              "failed": sum(not r["pass"] for r in records), "records": records}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("scope", "groups", "passed", "failed")}))
    assert not result["failed"]


if __name__ == "__main__":
    main()
