"""Thin JSON CLI delegates numerical work to the same SDK service."""

import argparse
import json
from pathlib import Path

from aqrp.core.contracts import SnapshotRef
from aqrp.data.exposures import ExposureRef
from aqrp.services.research import ResearchRequest, research
from aqrp.validation.labels import CoverageRef


def main(argv=None):
    parser = argparse.ArgumentParser(description="AQRP preregistered PIT research")
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    raw = json.loads(args.request.read_bytes())
    s = raw["snapshot"]
    e = raw.get("exposures")
    snapshot = SnapshotRef(Path(s["root"]), s["snapshot_id"], s["manifest_hash"])
    exposures = ExposureRef(Path(e["root"]), e["manifest_hash"], e["parent_hash"]) if e else None
    c = raw["coverage"]
    coverage = CoverageRef.create(
        c["parent_hash"], c["versions"], authority=c["authority"], scope=c["scope"]
    )
    result = research(
        ResearchRequest.create(raw["config"], snapshot, exposures, coverage, raw["code_commit"]),
        args.output,
    )
    print(
        json.dumps(
            {
                "run_id": result["run_id"],
                "status": result["manifest"]["status"],
                "financial_approval": "NONE",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
