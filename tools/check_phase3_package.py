"""Read-only Phase3 package checks; never rewrites historical audit files."""

import csv
import hashlib
import json
from pathlib import Path

from aqrp.factors.admission import bundle_manifest, reviewed_policy

ROOT = Path(__file__).resolve().parents[1]


def main():
    identity = json.loads((ROOT / "docs/audits/phase-3/IMPLEMENTATION_IDENTITY.json").read_bytes())
    rows = list(
        csv.DictReader((ROOT / "docs/requirements.csv").read_text(encoding="utf-8").splitlines())
    )
    selected = [r for r in rows if r["phase"] == "3"]
    assert len(rows) == 106 and len({r["id"] for r in rows}) == 106
    assert len(selected) == 26 and sum(r["tier"] == "MVP" for r in selected) == 23
    assert sum(r["tier"] == "Competition Ready" for r in selected) == 3
    assert (
        hashlib.sha256((ROOT / "docs/requirements.csv").read_bytes()).hexdigest()
        == identity["requirements_sha256"]
    )
    assert reviewed_policy()["bundle_sha256"] == identity["code_bundle_sha256"]
    assert bundle_manifest() == identity["code_bundle_manifest"]
    for r in identity["frozen_files"]:
        path = ROOT / r["path"]
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == r["sha256"], r[
            "path"
        ]
    for name in (
        "IMPLEMENTATION_AUTHORIZATION.json",
        "IMPLEMENTATION_NOTES.md",
        "IMPLEMENTATION_TRACEABILITY.md",
        "CODE_REVIEW.md",
    ):
        assert (ROOT / "docs/audits/phase-3" / name).is_file()
    assert not any(
        (ROOT / "src/aqrp" / n).exists()
        for n in ("portfolio", "backtest", "ui", "broker", "execution")
    )
    print(
        json.dumps(
            {
                "scope": "Phase3 read-only checks, not independent acceptance",
                "requirements": len(selected),
                "frozen_files_verified": len(identity["frozen_files"]),
                "bundle": identity["code_bundle_sha256"],
                "result": "PASS",
            }
        )
    )


if __name__ == "__main__":
    main()
