"""Thin simulation/status/result/replay CLI uses the same SDK application service."""

import argparse
import json
from pathlib import Path

from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.services.backtest import replay_engineering, result_engineering, simulate_engineering


def main(argv=None):
    parser = argparse.ArgumentParser(description="AQRP synthetic engineering simulation")
    parser.add_argument("operation", choices=("simulate", "status", "result", "replay"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--commit")
    parser.add_argument("--run-id")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args(argv)
    if args.operation == "simulate":
        if args.request is None or args.commit is None:
            parser.error("simulate requires --request and --commit")
        data = simulate_engineering(
            EngineeringBacktestRequest(args.request.read_bytes()), args.root, args.commit
        ).read()
    elif args.operation == "replay":
        if args.run_id is None or args.destination is None:
            parser.error("replay requires --run-id and --destination")
        data = replay_engineering(args.root, args.run_id, args.destination)
    else:
        if args.run_id is None:
            parser.error("status/result requires --run-id")
        data = result_engineering(args.root, args.run_id)
        if args.operation == "status":
            data = {k: data[k] for k in ("run_id", "status", "scope", "financial_approval")}
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))
    return 0
