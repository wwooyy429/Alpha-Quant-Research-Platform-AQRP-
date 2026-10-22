"""New public engineering export, NOT old unreadable inputs or deployed publication.

P1 private mkdtemp/rename behavior is intentionally unchanged. An operator must
separately prebuild/review the NTFS input anchor and call publish_engineering_input
before evaluator launch; this tool never changes ACLs or enables accounts.
"""

import hashlib
import json
import sys
import uuid
import zipfile
from datetime import date
from decimal import Decimal
from pathlib import Path

from aqrp.core.canonical import canonical
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, load_synthetic
from aqrp.validation.engineering_input import input_inventory


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    data = load_synthetic(sessions=[(date(2024, 1, d), "12:00:00") for d in (2, 3, 4)])
    for r in data["bars_daily"]:
        i = r["session_date"].day - 2
        price, volume = Decimal((100, 110, 121)[i]), Decimal((100, 150, 200)[i])
        r.update({k: price for k in ("open", "high", "low", "close")})
        r.update(
            volume=volume,
            source_volume=str(volume),
            amount=price * volume,
            source_amount=str(price * volume),
        )
    (out / "SOURCE.json").write_bytes(canonical(data))
    ref = publish_snapshot(
        data, PROVENANCE, out / "private-source", snapshot_id="wi-r3-public-engineering-20261022"
    )
    inventory = input_inventory(ref)
    inventory.update(
        run_id=str(uuid.uuid4()),
        code_commit=sys.argv[2],
        source_fixture_sha256=hashlib.sha256((out / "SOURCE.json").read_bytes()).hexdigest(),
        deployment="NOT_DEPLOYED",
        actual_three_token_access="NOT_EXECUTED",
        old_unreadable_snapshot="cb10857f-e12b-4c82-8962-16a41fdf8377 remains NOT VERIFIED; not recovered or substituted",
        formal_test=False,
        financial_approval="NONE",
    )
    (out / "MANIFEST.json").write_bytes(canonical(inventory))
    archive = out / "nine-input-files-original.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for r in inventory["files"]:
            z.write(ref.root / ref.snapshot_id / r["path"], r["path"])
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist()) == 9
        for r in inventory["files"]:
            raw = z.read(r["path"])
            assert len(raw) == r["bytes"] and hashlib.sha256(raw).hexdigest() == r["sha256"]
    print(
        json.dumps(
            {
                "snapshot_manifest_hash": ref.manifest_hash,
                "export_zip_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                "files": 9,
                "scope": "NEW_ENGINEERING_EXPORT_ONLY_NOT_OS_PROOF",
            }
        )
    )


if __name__ == "__main__":
    main()
