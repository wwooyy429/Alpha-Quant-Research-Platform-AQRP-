"""Check isolated Windows repair identity without rewriting frozen P3 release audits."""

import hashlib
import json
from pathlib import Path

from aqrp.factors.admission import bundle_manifest, reviewed_policy


def main():
    root = Path(__file__).resolve().parents[1]
    evidence = root / "docs/audits/windows-isolation-r3"
    identity = json.loads((evidence / "IDENTITY.json").read_bytes())
    assert bundle_manifest() == identity["bundle_manifest"]
    assert reviewed_policy()["bundle_sha256"] == identity["bundle_sha256"]
    for row in identity["preserved_files"]:
        assert hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"], row[
            "path"
        ]
    assert not any(
        (root / "src/aqrp" / n).exists()
        for n in ("portfolio", "risk", "backtest", "broker", "execution", "ui")
    )
    assert (
        json.loads((evidence / "STATUS.json").read_bytes())["overall_windows_isolation"]
        == "NOT_VERIFIED"
    )
    print(
        json.dumps(
            {
                "scope": "Developer repair identity, NOT independent OS validation",
                "preserved_files": len(identity["preserved_files"]),
                "modules": len(identity["bundle_manifest"]["files"]),
                "bundle_sha256": identity["bundle_sha256"],
                "result": "PASS",
            }
        )
    )


if __name__ == "__main__":
    main()
