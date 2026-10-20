"""Persist a small real SDK run and its immutable data/config/result evidence."""

import hashlib
import json
import sys
import uuid
from datetime import date
from pathlib import Path

from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import QuerySpec
from aqrp.data.query import query
from aqrp.data.snapshot import publish_snapshot, verify_snapshot
from aqrp.data.synthetic import PROVENANCE


def main():
    root = Path(__file__).resolve().parents[1]
    out = Path(sys.argv[1])
    source = root / "tests/golden/phase1_input.json"
    tables = json.loads(source.read_bytes())
    ref = publish_snapshot(tables, PROVENANCE, out / "dataset")
    manifest, _ = verify_snapshot(ref)
    spec = QuerySpec(("SYN_A:001",), "SYN_A", "SYN_A_CAL", (date(2024, 1, 2), date(2024, 1, 3)))
    view = query(spec, "2024-01-03T12:05:00Z", ref)
    rows = view.table.to_pylist()
    assert [str(r["close"]) for r in rows] == ["100.00000000", "100.00000000"]
    (out / "smoke-result.json").write_bytes(canonical(rows))
    (out / "smoke-snapshot.json").write_bytes(canonical(manifest))
    config = {
        "snapshot_id": ref.snapshot_id,
        "manifest_hash": ref.manifest_hash,
        "as_of": "2024-01-03T12:05:00Z",
        "profile_id": "SYNTHETIC_V1",
        "market_id": spec.market_id,
        "calendar_id": spec.calendar_id,
        "fields": list(spec.fields),
        "security_ids": list(spec.security_ids),
        "session_range": ["2024-01-02", "2024-01-03"],
        "price_basis": "RAW",
    }
    (out / "smoke-config.json").write_bytes(canonical(config))
    evidence = {
        "run_id": str(uuid.uuid4()),
        "config_hash": digest(config),
        "fixture_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "query_hash": view.query_hash,
        "result_hash": digest(rows),
        "snapshot_id": ref.snapshot_id,
        "manifest_hash": ref.manifest_hash,
        "dataset": str(ref.root),
        "rows": len(rows),
        "source": "SYNTHETIC ONLY",
    }
    (out / "smoke-run.json").write_bytes(canonical(evidence))
    print("Synthetic snapshot/query smoke PASS")


if __name__ == "__main__":
    main()
