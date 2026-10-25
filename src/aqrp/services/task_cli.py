"""Fixed-command task CLI, delegates all work to the same TaskService."""

import argparse
import json
from pathlib import Path

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import load
from aqrp.services.task_requests import EffectiveRequest, initialize
from aqrp.services.tasks import TaskService


def main(argv=None):
    parser = argparse.ArgumentParser(description="AQRP engineering tasks")
    parser.add_argument(
        "operation",
        choices=[
            "init",
            "catalogue",
            "campaigns",
            "campaign-register",
            "freeze",
            "submit",
            "work",
            "status",
            "list",
            "cancel",
            "logs",
            "artifact",
            "replay",
            "compare",
            "defaults",
            "rollback",
            "adapter-spec",
            "adapter-capabilities",
            "adapter-freeze",
            "adapter-submit",
        ],
    )
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--commit")
    parser.add_argument("--task")
    parser.add_argument("--right")
    parser.add_argument("--slot", default="R")
    parser.add_argument("--name", default="report.json")
    parser.add_argument("--key")
    parser.add_argument("--campaign")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--revision", type=int)
    parser.add_argument("--target", type=int)
    parser.add_argument("--execution-sessions", nargs="+")
    parser.add_argument("--rules", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.execution_sessions is not None and args.operation not in {
            "freeze",
            "submit",
            "adapter-freeze",
            "adapter-submit",
        }:
            raise ContractError("EXECUTION_SELECTION_PIPELINE_ONLY")
        service = None if args.operation == "init" else TaskService(args.workspace)
        if args.operation == "init":
            result = initialize(args.workspace, args.commit)
        elif args.operation == "catalogue":
            from aqrp.services.task_requests import catalogue

            result = catalogue(args.workspace)
        elif args.operation == "campaigns":
            result = service.campaigns()
        elif args.operation == "campaign-register":
            result = service.register_campaign(args.campaign, load(args.request.read_bytes()))
        elif args.operation.startswith("adapter-"):
            from aqrp.competition import (
                AdapterReceipt,
                adapt_engineering,
                adapter_spec,
                capabilities,
                execute_engineering,
                input_reference,
            )

            spec = adapter_spec(args.workspace)
            if args.operation == "adapter-spec":
                result = load(spec.raw)
            else:
                if args.rules is None:
                    raise ContractError("ADAPTER_RULE_REQUIREMENTS_REQUIRED")
                rules = load(args.rules.read_bytes())
                if args.operation == "adapter-capabilities":
                    result = load(capabilities(spec, rules).raw)
                else:
                    request_raw = args.request.read_bytes()
                    draft = load(request_raw)
                    if draft.get("schema") == "engineering-adapter-receipt/1":
                        if args.operation != "adapter-submit":
                            raise ContractError("FROZEN_ADAPTER_RECEIPT_SUBMIT_ONLY")
                        if args.execution_sessions is not None:
                            raise ContractError("FROZEN_ADAPTER_SELECTION_OVERRIDE")
                        if canonical(draft.get("requirements")) != canonical(rules):
                            raise ContractError("ADAPTER_RECEIPT_RULES_CHANGED")
                        receipt = AdapterReceipt(request_raw)
                    else:
                        if args.execution_sessions is not None:
                            if "execution_sessions" in draft:
                                raise ContractError("DUPLICATE_EXECUTION_SELECTION_SOURCE")
                            draft["execution_sessions"] = args.execution_sessions
                        receipt = adapt_engineering(
                            args.workspace, spec, input_reference(args.workspace), draft, rules
                        )
                    result = (
                        load(receipt.raw)
                        if args.operation == "adapter-freeze"
                        else execute_engineering(args.workspace, receipt, args.key, wait=args.wait)
                    )
        elif args.operation in ("freeze", "submit"):
            raw = args.request.read_bytes()
            value = load(raw)
            if args.execution_sessions is not None:
                if value.get("schema") == "task-request/1" or "execution_sessions" in value:
                    raise ContractError("FROZEN_OR_DUPLICATE_EXECUTION_SELECTION")
                value["execution_sessions"] = args.execution_sessions
            frozen = (
                EffectiveRequest(canonical(value))
                if value.get("schema") == "task-request/1"
                else service.freeze(value)
            )
            if args.operation == "freeze":
                result = load(frozen.raw)
            else:
                result = service.submit(frozen, args.key)
                if args.wait:
                    result = service.work(result["task_id"])
        elif args.operation == "work":
            result = service.work(args.task, recover=args.recover)
        elif args.operation == "status":
            result = service.status(args.task)
        elif args.operation == "list":
            result = service.list()
        elif args.operation == "cancel":
            result = {"status": service.cancel(args.task)}
        elif args.operation == "logs":
            result = service.logs(args.task)
        elif args.operation == "compare":
            result = service.compare(args.task, args.right)
        elif args.operation == "replay":
            result = service.submit(
                service.freeze({"kind": "replay", "source_task": args.task}), args.key
            )
            if args.wait:
                result = service.work(result["task_id"])
        elif args.operation == "artifact":
            raw = service.artifact(args.task, args.slot, args.name)
            if args.output is None:
                raise ContractError("ARTIFACT_OUTPUT_REQUIRED")
            with args.output.open("xb") as f:
                f.write(raw)
            result = {"status": "VERIFIED_ARTIFACT_SAVED"}
        elif args.operation == "defaults":
            result = (
                service.state.defaults()
                if args.request is None
                else {
                    "revision": service.save_defaults(
                        args.revision, load(args.request.read_bytes())
                    )
                }
            )
        else:
            result = {"revision": service.state.rollback_defaults(args.revision, args.target)}
        content = json.dumps(result, ensure_ascii=False, sort_keys=True)
        if args.output and args.operation != "artifact":
            with args.output.open("xb") as f:
                f.write(
                    frozen.raw
                    if args.operation == "freeze"
                    else canonical(result)
                    if args.operation.startswith("adapter-")
                    else (content + "\n").encode("utf-8")
                )
        print(content)
        return 0
    except (ContractError, ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "REJECTED", "code": getattr(exc, "code", type(exc).__name__)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
