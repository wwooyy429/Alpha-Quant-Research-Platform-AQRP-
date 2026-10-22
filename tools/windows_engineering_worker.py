"""R3 closed engineering worker candidate. NO deployment and NO FINAL_TEST execution.

Not executed by CI. Requires separately authorized real evaluator token, reviewed
read-only entry/config/runtime, new operator-prepared namespace and published
actual inputs. The old R2 entry and failed attempt are never edited or reused.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
import uuid
from datetime import UTC, date, datetime
from pathlib import Path

from aqrp.core.contracts import QuerySpec, SnapshotRef
from aqrp.core.environment import runtime_manifest, verify_runtime
from aqrp.core.errors import ContractError
from aqrp.factors import FactorEngine, FactorRegistry, builtin_spec, write_run
from aqrp.factors.admission import bundle_hash
from aqrp.validation.engineering_input import verify_engineering_input
from aqrp.validation.evaluator import OperatorPolicy, TestEvaluator
from aqrp.validation.windows_acl import WindowsTreePolicy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument(
        "--mode",
        choices=("before", "after", "race", "crash", "recover", "alias", "abort-before"),
        required=True,
    )
    args = parser.parse_args()
    raw = args.config.read_bytes()
    if os.name != "nt" or hashlib.sha256(raw).hexdigest() != args.sha256:
        raise SystemExit("FIXED_WINDOWS_ENGINEERING_CONFIG_REQUIRED")
    cfg = json.loads(raw)
    if cfg["scope"] != "ENGINEERING_DEMO_ONLY" or not cfg.get(
        "separate_user_execution_authorization"
    ):
        raise SystemExit("ENGINEERING_EXECUTION_NOT_AUTHORIZED")
    attempt = str(uuid.UUID(cfg["attempt_id"]))
    sealed = Path(cfg["sealed_root"]).absolute()
    if "verify-9ac5db0" in str(sealed) or sealed.name != "wi-r3-" + attempt:
        raise SystemExit("FRESH_R3_NAMESPACE_REQUIRED")
    probe_path = Path(__file__).with_name("windows_access_probe.py")
    if hashlib.sha256(probe_path.read_bytes()).hexdigest() != cfg["probe_sha256"]:
        raise SystemExit("REVIEWED_PROBE_MISMATCH")
    spec = importlib.util.spec_from_file_location("fixed_probe", probe_path)
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    actual = probe.token()
    principals = cfg["principals"]
    if actual["elevated"] or actual["sid"] != principals["evaluator"]:
        raise SystemExit("WRONG_REAL_EVALUATOR_TOKEN")
    if (
        Path(sys.executable).resolve() != Path(cfg["evaluator_python"]).resolve()
        or bundle_hash() != cfg["bundle_sha256"]
    ):
        raise SystemExit("FIXED_RUNTIME_MISMATCH")
    environment = runtime_manifest()
    verify_runtime(environment)
    tree = WindowsTreePolicy(
        sealed,
        owner=principals["trusted_owner"],
        evaluator=principals["evaluator"],
        research=principals["research"],
        auditor=principals["auditor"],
        inherited_roots=(sealed / "work", sealed / "control"),
        readonly_roots=(sealed / "inputs",),
        key_file=sealed / "operator-key",
    )
    policy = OperatorPolicy(
        sealed,
        sealed / "operator-key",
        evaluator=principals["evaluator"],
        research=principals["research"],
        auditor=principals["auditor"],
        trusted_owner=principals["trusted_owner"],
        windows_tree_policy=tree,
    )
    snapshot = SnapshotRef(sealed / "inputs", cfg["input_snapshot_id"], cfg["input_manifest_hash"])
    result = {
        "attempt_id": attempt,
        "scope": "ENGINEERING_DEMO_ONLY",
        "actual_token": actual,
        "mode": args.mode,
        "config_sha256": args.sha256,
        "bundle_sha256": bundle_hash(),
        "code_commit": cfg["reviewed_sha"],
        "environment": environment,
        "started_at_UTC": datetime.now(UTC).isoformat(),
        "formal_test": False,
        "financial_approval": "NONE",
    }
    if args.mode in ("before", "after"):
        policy.verify_host()
        receipt = verify_engineering_input(snapshot, tree_policy=tree)
        result["actual_input_inventory"] = receipt
        result["full_host_gate"] = "PASS"
        if args.mode == "before":
            query = QuerySpec(
                ("SYN_A:001",),
                "SYN_A",
                "SYN_A_CAL",
                (date(2024, 1, 2), date(2024, 1, 4)),
                ("close", "volume"),
                "split_adjusted",
            )
            registry = FactorRegistry()
            values = {}
            for name, expected in (
                ("momentum", 0.21),
                ("reversal", -0.21),
                ("volume", 0.6),
                ("price_volume", 0.06),
            ):
                factor = builtin_spec(name)
                registry.register(
                    factor.implementation_version,
                    factor,
                    actor="actual R3 evaluator engineering worker",
                    reason="fixed reviewed builtin, not financial approval",
                    evidence=factor.review_ref,
                )
                batch = FactorEngine(registry).run(
                    factor.ref, query, "2024-01-04T12:05:00Z", snapshot, parameters={"lookback": 2}
                )
                value = batch.rows[0].factor_value
                if abs(value - expected) > 1e-12:
                    raise ValueError("INDEPENDENT_FACTOR_ANSWER_MISMATCH")
                write_run(batch, sealed / "work/factor-runs", registry)
                values[name] = value
            result["engineering_factor_values"] = values
            policy.verify_host()
            result["post_factor_full_host_gate"] = "PASS"
    else:
        # Before/after whole-domain gates are separate quiescent phases. The
        # actual operator must not alter ACLs between them or during any mode.
        case = "demo-crash" if args.mode in ("crash", "recover") else "demo-race"
        control = sealed / "control" / case
        evaluator = TestEvaluator(control)
        bindings = {"holdout_lineage_id": case}
        if args.mode == "abort-before":
            if (sealed / "control/demo-abort/access.jsonl").exists():
                raise ValueError("PRE_RESERVATION_CHAIN_EXISTS")
            result["pre_reservation_no_chain"] = True
        elif args.mode == "recover":
            result["recovered"] = evaluator.recover()
            result["second_recover"] = evaluator.recover()
            if result["recovered"] != 1 or result["second_recover"] != 0:
                raise ValueError("RECOVERY_MISMATCH")
            try:
                evaluator.process(
                    bindings, lambda: {"public_constant": 18}, purpose="ENGINEERING_DEMO"
                )
            except ContractError as e:
                if e.code != "TEST_ALREADY_CONSUMED_OR_CONTAMINATED":
                    raise
                result["repeat_after_crash"] = e.code
            else:
                raise ValueError("CRASH_RETURNED_BUDGET")
        elif args.mode == "alias":
            for extra in (
                {"family": "renamed"},
                {"run_id": "renamed"},
                {"protocol_hash": "changed"},
                {"cache": "hit"},
            ):
                try:
                    evaluator.process(
                        {**bindings, **extra},
                        lambda: {"public_constant": 19},
                        purpose="ENGINEERING_DEMO",
                    )
                except ContractError as e:
                    if e.code != "TEST_ALREADY_CONSUMED_OR_CONTAMINATED":
                        raise
                else:
                    raise ValueError("ALIAS_RETURNED_BUDGET")
            result["four_repeat_controls"] = "PASS"
        else:
            if args.mode == "race":
                ready = sealed / "work" / ("ready-" + str(os.getpid()) + ".json")
                ready.write_bytes(b"engineering-only")
                deadline = time.monotonic() + 40
                while not (sealed / "work/race.go").exists():
                    if time.monotonic() > deadline:
                        raise TimeoutError("RACE_BARRIER_TIMEOUT")
                    time.sleep(0.02)

            def callback():
                if args.mode == "crash":
                    print(
                        json.dumps(
                            {
                                "event": "ENGINEERING_CRASH",
                                "actual_token": actual,
                                "attempt_id": attempt,
                            }
                        ),
                        file=sys.stderr,
                        flush=True,
                    )
                    os._exit(23)
                verify_engineering_input(snapshot, tree_policy=tree)
                return {"public_constant": 17}

            try:
                result["evaluation"] = evaluator.process(
                    bindings, callback, purpose="ENGINEERING_DEMO"
                )
            except ContractError as e:
                if e.code != "TEST_ALREADY_CONSUMED_OR_CONTAMINATED":
                    raise
                result["expected_rejection"] = e.code
                print(json.dumps(result))
                raise SystemExit(42)
    result["finished_at_UTC"] = datetime.now(UTC).isoformat()
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
