"""Phase-specific admission: old financial source/answers plus explicit packaging changes."""

import csv
import hashlib
import json
from pathlib import Path

from aqrp.factors.admission import bundle_manifest, reviewed_policy

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZED_PACKAGING = {
    ".github/workflows/ci.yml",
    "pyproject.toml",
    "src/aqrp/__init__.py",
    "src/aqrp/factors/reviewed_code.json",
    "tests/environment/test_installation.py",
    "tools/check_coverage.py",
    "tools/ci.py",
}


def main():
    d = ROOT / "docs/audits/phase-5"
    auth = json.loads((d / "IMPLEMENTATION_AUTHORIZATION.json").read_bytes())
    assert auth["G1_sha"] == "5262032bee4f631f68763e57510e1878945f6b8c"
    assert auth["implementation_authorized"] and auth["C-P5-001"] == "EXPLICITLY_ACCEPTED"
    assert not auth["main_merge_tag_deployment_live_formal_Test_financial_approval_P6_authorized"]
    identity = json.loads((d / "IMPLEMENTATION_IDENTITY.json").read_bytes())
    assert set(identity["explicit_packaging_changes"]) == AUTHORIZED_PACKAGING
    assert identity["bundle_manifest"] == bundle_manifest()
    assert identity["bundle_sha256"] == reviewed_policy()["bundle_sha256"]
    for e in identity["preserved_files"] + identity["current_implementation_files"]:
        path = ROOT / e["path"]
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == e["sha256"], e[
            "path"
        ]
    original = json.loads((d / "DESIGN_REVISION_IDENTITY.json").read_bytes())
    for e in original["files"]:
        assert hashlib.sha256((d / e["path"]).read_bytes()).hexdigest() == e["sha256"]
    rows = list(
        csv.DictReader((ROOT / "docs/requirements.csv").read_text(encoding="utf-8").splitlines())
    )
    selected = [r for r in rows if r["phase"] == "5"]
    assert len(rows) == 106 and len(selected) == 12
    assert selected == json.loads((d / "REQUIREMENTS_SNAPSHOT.json").read_bytes())["requirements"]
    assert sum(r["tier"] == "MVP" for r in selected) == 10
    assert not any((ROOT / "src/aqrp" / n).exists() for n in ("broker", "ui"))
    for e in bundle_manifest()["files"]:
        if (
            e["path"].startswith(("backtest/", "execution/"))
            and e["path"] != "backtest/synthetic.py"
        ):
            text = (ROOT / "src/aqrp" / e["path"]).read_text(encoding="utf-8")
            assert not any(
                s in text for s in ("FactorRegistry", "import streamlit", "factors.builtins")
            ), e["path"]
    print(
        json.dumps(
            {
                "scope": "Developer P5 package/static checks, not independent G2",
                "requirements": 12,
                "preserved_files": len(identity["preserved_files"]),
                "modules": len(identity["bundle_manifest"]["files"]),
                "result": "PASS",
            }
        )
    )


if __name__ == "__main__":
    main()
