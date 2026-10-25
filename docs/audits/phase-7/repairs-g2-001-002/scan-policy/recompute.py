"""Stdlib-only recomputation of public synthetic identifiers, never product execution."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PROOF = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf8")


def main():
    proof = json.loads((PROOF / "PROOF.json").read_bytes())
    assert proof["schema"] == "phase7-G2-public-digest-proof/1"
    records = {row["id"]: row for row in proof["records"]}
    assert len(records) == 7 and len(proof["locations"]) == 12
    for row in records.values():
        raw = (PROOF / row["preimage"]["file"]).read_bytes()
        assert canonical(json.loads(raw)) == raw and len(raw) == row["preimage"]["bytes"]
        assert hashlib.sha256(raw).hexdigest() == row["public_sha256"] == row["preimage"]["sha256"]
    for relative, expected in proof["projection_files"].items():
        raw = (ROOT / relative).read_bytes()
        assert (
            len(raw) == expected["bytes"] and hashlib.sha256(raw).hexdigest() == expected["sha256"]
        )
    for row in proof["locations"]:
        obj = json.loads((ROOT / row["repository_path"]).read_bytes())
        for token in row["json_pointer"].lstrip("/").split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            obj = obj[int(token)] if isinstance(obj, list) else obj[token]
        assert obj == records[row["public_digest_id"]]["public_sha256"]
    print(
        "Seven public identifiers and all twelve original locations recomputed; no credential or product calls"
    )


if __name__ == "__main__":
    main()
