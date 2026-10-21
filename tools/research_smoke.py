"""Installed-wheel full research and replacement; explicitly public engineering."""

import json
import sys
from dataclasses import asdict
from pathlib import Path

from aqrp.core.canonical import canonical
from aqrp.experiments.reproduction import reproduce_current
from aqrp.research.synthetic import synthetic_research
from aqrp.services.research import ResearchRequest, research


def main():
    output = Path(sys.argv[1]) / "research"
    commit = json.loads((output.parent / "environment.json").read_bytes())["code_commit"]
    c, s, e, v = synthetic_research(
        output / "inputs", sessions=24, assets=6, factor_ids=("momentum", "price_volume")
    )
    c["composite"] = {
        "hypothesis": "fixed-research-composite",
        "factor_keys": ["momentum", "price_volume"],
        "weights": [1, 2],
        "directions": [1, 1],
        "direction_applied": False,
        "normalization": "cross_sectional_sample_z",
        "input_stage": "final",
        "min_n": 3,
        "redundancy": {"tau": 0.8, "min_pair_n": 3, "min_days": 3, "min_fraction": 0.5},
    }
    from aqrp.services.research import hypotheses, hypothesis_definition

    c["family"]["hypotheses"] = [r["hypothesis"] for r in hypotheses(c)]
    c["family"]["definitions"] = {
        r["hypothesis"]: hypothesis_definition(r, c, s.manifest_hash, e.manifest_hash, v.checksum)
        for r in hypotheses(c)
    }
    request = ResearchRequest.create(c, s, e, v, commit)
    result = research(request, output / "runs")
    assert result["manifest"]["status"] == "SUCCEEDED"
    assert not result["report"]["independence_verified"]
    replay = reproduce_current(request, output / "runs", result["run_id"])
    assert replay["status"] == "DECLARED_PROJECTION_MATCH"
    c2, s2, e2, v2 = synthetic_research(
        output / "replacement-inputs", sessions=24, assets=6, factor_ids=("reversal",)
    )
    replacement = research(
        ResearchRequest.create(c2, s2, e2, v2, commit), output / "replacement-runs"
    )
    assert replacement["manifest"]["status"] == "SUCCEEDED"
    (output / "request.json").write_bytes(
        canonical(
            {
                "config": c,
                "snapshot": {**asdict(s), "root": str(s.root)},
                "exposures": {**asdict(e), "root": str(e.root)},
                "coverage": v.read(s.manifest_hash),
                "code_commit": commit,
            }
        )
    )
    (output / "result.json").write_bytes(
        canonical(
            {
                "run_id": result["run_id"],
                "reproduction": replay,
                "replacement_run": replacement["run_id"],
                "formal_test": "NOT_DEPLOYED_NOT_EXECUTED",
            }
        )
    )
    print(
        "P3 full research / synthesis / exact-run projection / replacement PASS (developer engineering only)"
    )


if __name__ == "__main__":
    main()
