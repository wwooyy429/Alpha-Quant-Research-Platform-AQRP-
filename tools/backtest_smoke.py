"""Installed-wheel P1/P3/P4/P5 replacement/replay and retained refusal/failure artifacts."""

import hashlib
import json
import sys
from pathlib import Path

from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.backtest.synthetic import research_backtests
from aqrp.core.canonical import canonical
from aqrp.factors.admission import bundle_manifest
from aqrp.services.backtest import replay_engineering, simulate_approved, simulate_engineering


def main():
    output = Path(sys.argv[1]) / "backtest"
    output.mkdir()
    commit = json.loads((output.parent / "environment.json").read_bytes())["code_commit"]
    requests = research_backtests(output / "input", commit)
    before = bundle_manifest()
    outcomes = {}
    for factor, request in requests.items():
        (output / (factor + "-request.json")).write_bytes(request.raw)
        root = output / (factor + "-runs")
        result = simulate_engineering(request, root, commit).read()
        assert result["status"] == "SUCCEEDED" and result["fills"], result
        replay = replay_engineering(root, result["run_id"], output / (factor + "-replay"))
        assert replay["status"] == "NUMERICAL_REPLAY_VERIFIED"
        outcomes[factor] = {
            "result": result,
            "replay": replay,
            "request_sha256": request.content_hash,
        }
        (output / (factor + "-result.json")).write_bytes(canonical(result))
    assert bundle_manifest() == before
    assert {f["security_id"] for f in outcomes["momentum"]["result"]["fills"]} != {
        f["security_id"] for f in outcomes["reversal"]["result"]["fills"]
    }
    formal = simulate_approved(
        next(iter(requests.values())), output / "formal-refusal-only", commit
    ).read()
    assert (
        formal["reasons"] == ["APPROVAL_REQUIRED"]
        and not (output / "formal-refusal-only" / formal["run_id"] / "transactions").exists()
    )
    bad = EngineeringBacktestRequest(b'{"schema_version":"future"}')
    failure = simulate_engineering(bad, output / "retained-failure", commit).read()
    assert failure["status"] == "FAILED" and "performance" not in failure
    (output / "summary.json").write_bytes(
        canonical(
            {
                "scope": "ENGINEERING_TEST_ONLY",
                "financial_approval": "NONE",
                "code_bundle": before,
                "code_bundle_sha256": hashlib.sha256(canonical(before)).hexdigest(),
                "outcomes": outcomes,
                "formal_refusal": formal,
                "retained_failure": failure,
                "Windows_R2": "DEFERRED / NOT VERIFIED",
                "formal_Test_executed": False,
            }
        )
    )
    print(
        "P5 installed-wheel real P1/P3/P4 simulations, factor replacement, exact numerical replay and fail-closed gates PASS"
    )


if __name__ == "__main__":
    main()
