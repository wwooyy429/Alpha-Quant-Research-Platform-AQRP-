"""P6 admission with immutable prior answers/financial source and explicit adapters."""

import csv
import hashlib
import json
from pathlib import Path

from aqrp.factors.admission import LOCK_HASH, bundle_manifest, reviewed_policy

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / "docs/audits/phase-6"
    authorization = json.loads((folder / "IMPLEMENTATION_AUTHORIZATION.json").read_bytes())
    assert authorization["implementation_authorized"]
    assert authorization["G1_reviewed_sha"] == "e71f6f090b102e4abfd70a5999e495f49546a1b5"
    assert all(x == "EXPLICITLY_ACCEPTED" for x in authorization["conditions"].values())
    assert not authorization["deployment_live_formal_Test_financial_approval"]
    identity = json.loads((folder / "IMPLEMENTATION_IDENTITY.json").read_bytes())
    assert identity["bundle_manifest"] == bundle_manifest()
    assert identity["bundle_sha256"] == reviewed_policy()["bundle_sha256"]
    for item in identity["preserved_files"] + identity["current_files"]:
        p = ROOT / item["path"]
        assert (
            p.stat().st_size == item["bytes"]
            and hashlib.sha256(p.read_bytes()).hexdigest() == item["sha256"]
        ), item["path"]
    assert hashlib.sha256((ROOT / "requirements.lock").read_bytes()).hexdigest() == LOCK_HASH
    for name in ["windows", "linux"]:
        actual = (ROOT / f"requirements-ui-{name}.lock").read_bytes()
        assert actual == (folder / f"UI_EXTENSION_{name.upper()}.lock").read_bytes()
        assert actual == (ROOT / f"src/aqrp/ui/requirements-{name}.lock").read_bytes()
    rows = list(
        csv.DictReader((ROOT / "docs/requirements.csv").read_text(encoding="utf-8").splitlines())
    )
    selected = [r for r in rows if r["phase"] == "6"]
    assert len(rows) == 106 and len(selected) == 8
    assert sum(r["tier"] == "MVP" for r in selected) == 5
    assert (
        selected == json.loads((folder / "REQUIREMENTS_SNAPSHOT.json").read_bytes())["requirements"]
    )
    assert not any((ROOT / "src/aqrp" / name).exists() for name in ["competition", "broker"])
    for e in bundle_manifest()["files"]:
        if (
            e["path"].startswith(("backtest/", "execution/"))
            and e["path"] != "backtest/synthetic.py"
        ):
            text = (ROOT / "src/aqrp" / e["path"]).read_text(encoding="utf-8")
            assert not any(
                s in text for s in ["FactorRegistry", "import streamlit", "factors.builtins"]
            )
    print(
        json.dumps(
            {
                "scope": "P6 developer package/static gate, not independent G2",
                "requirements": 8,
                "MVP": 5,
                "Competition Ready": 3,
                "modules": len(bundle_manifest()["files"]),
                "preserved_files": len(identity["preserved_files"]),
                "result": "PASS",
            }
        )
    )


if __name__ == "__main__":
    main()
