"""Installed-wheel engineering portfolio/risk scenarios, verified immutable run artifacts."""

import hashlib
import json
import shutil
import sys
from pathlib import Path

from aqrp.core.canonical import canonical
from aqrp.portfolio.contracts import PortfolioRequest
from aqrp.portfolio.service import construct_approved, construct_engineering, replay_engineering


def main():
    output = Path(sys.argv[1]) / "portfolio"
    output.mkdir()
    source = Path(__file__).resolve().parents[1] / "tests/portfolio/fixtures"
    inputs = output / "inputs"
    shutil.copytree(source, inputs)
    expected = json.loads((inputs / "expected.json").read_bytes())["cases"]
    commit = json.loads((output.parent / "environment.json").read_bytes())["code_commit"]
    outcomes = []
    for name, known in expected.items():
        raw = (inputs / (name + ".json")).read_bytes()
        result = construct_engineering(PortfolioRequest(raw), output / "runs", commit).read()
        assert result["status"] == known["status"], name
        if "quantities" in known:
            assert result["target"]["quantities"] == known["quantities"], name
        if "reason" in known:
            assert known["reason"] in result["reasons"], name
        replay = replay_engineering(output / "runs", result["run_id"])
        assert replay["result"]["status"] == known["status"]
        outcomes.append(
            {
                "name": name,
                "status": result["status"],
                "run_id": result["run_id"],
                "input_sha256": hashlib.sha256(raw).hexdigest(),
                "manifest": result["manifest"],
                "replay": replay["status"],
            }
        )
    formal = construct_approved(
        PortfolioRequest((inputs / "base.json").read_bytes()), output / "formal-gate", commit
    ).read()
    assert formal["reasons"] == ["APPROVAL_REQUIRED"] and "target" not in formal
    (output / "summary.json").write_bytes(
        canonical(
            {
                "scope": "SYNTHETIC_ENGINEERING_ONLY",
                "financial_approval": "NONE",
                "outcomes": outcomes,
                "formal_gate": formal,
                "account_ledger_written": False,
                "orders_submitted": 0,
            }
        )
    )
    print(
        "P4 installed-wheel portfolio / full risk / refusal / immutable evidence smoke PASS; no financial approval"
    )


if __name__ == "__main__":
    main()
