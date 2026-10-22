"""Enforce the independently reviewed module coverage gates without exclusions."""

import json
import sys


def main():
    report = json.load(open(sys.argv[1], encoding="utf-8"))
    critical = {
        "time.py",
        "units.py",
        "pit.py",
        "actions.py",
        "snapshot.py",
        "environment.py",
        "exposures.py",
        "numerics.py",
        "pipeline.py",
        "ledger.py",
        "reproduction.py",
    }
    failures = []
    for file, data in report["files"].items():
        s = data["summary"]
        line = 100 * s["covered_lines"] / max(1, s["num_statements"])
        branch = 100 * s["covered_branches"] / s["num_branches"] if s["num_branches"] else 100
        normalized = file.replace("\\", "/")
        factor_critical = "/factors/" in normalized and normalized.split("/")[-1] in {
            "contracts.py",
            "input.py",
            "admission.py",
            "builtins.py",
            "engine.py",
        }
        minimum = (
            (95, 90)
            if normalized.split("/")[-1] in critical
            or factor_critical
            or "/core/security/" in normalized
            or "/validation/" in normalized
            or "/portfolio/" in normalized
            or "/risk/" in normalized
            or normalized.endswith("/services/research.py")
            else (90, 85)
        )
        if s["num_statements"] and (line < minimum[0] or branch < minimum[1]):
            failures.append(f"{file}: line={line:.2f}, branch={branch:.2f}, required={minimum}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("Module line/branch coverage gates PASS")


if __name__ == "__main__":
    main()
