"""Read-only P4 authorization, source admission, frozen inputs and prior audit checks."""

import csv
import hashlib
import json
from pathlib import Path

from aqrp.factors.admission import bundle_manifest, reviewed_policy

ROOT = Path(__file__).resolve().parents[1]


def main():
    d = ROOT / "docs/audits/phase-4"
    auth = json.loads((d / "IMPLEMENTATION_AUTHORIZATION.json").read_bytes())
    assert auth["G1_sha"] == "265af16353d85ce8c2d229a7517809d707498da8"
    assert not auth["merge_tag_deployment_live_P5_authorized"]
    rows = list(
        csv.DictReader((ROOT / "docs/requirements.csv").read_text(encoding="utf-8").splitlines())
    )
    selected = [r for r in rows if r["phase"] == "4"]
    assert (
        len(rows) == 106 and len(selected) == 7 and sum(r["tier"] == "MVP" for r in selected) == 4
    )
    identity = json.loads((d / "IMPLEMENTATION_IDENTITY.json").read_bytes())
    assert identity["bundle_manifest"] == bundle_manifest()
    assert identity["bundle_sha256"] == reviewed_policy()["bundle_sha256"]
    for entry in (
        identity["preserved_files"] + json.loads((d / "FROZEN_INPUTS.json").read_bytes())["files"]
    ):
        p = ROOT / entry["path"]
        assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == entry["sha256"], entry[
            "path"
        ]
    assert all((ROOT / "src/aqrp" / n).exists() for n in ("portfolio", "risk"))
    assert not any(
        (ROOT / "src/aqrp" / n).exists() for n in ("backtest", "execution", "broker", "ui")
    )
    print(
        json.dumps(
            {
                "scope": "Developer P4 package checks; not independent G2",
                "requirements": 7,
                "preserved_files": len(identity["preserved_files"]),
                "bundle": identity["bundle_sha256"],
                "result": "PASS",
            }
        )
    )


if __name__ == "__main__":
    main()
