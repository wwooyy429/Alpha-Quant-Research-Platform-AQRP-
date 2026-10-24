"""Independent standard-library recomputation; prints no identifier values."""

import hashlib
import json
from pathlib import Path

p = Path(__file__).resolve().parent
proof = json.loads((p / "PROOF.json").read_bytes())
for r in proof["records"]:
    raw = (p / r["preimage"]["file"]).read_bytes()
    obj = json.loads(raw)
    canonical = json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf8")
    assert canonical == raw and len(raw) == r["preimage"]["bytes"]
    assert hashlib.sha256(raw).hexdigest() == r["public_config_sha256"] == r["preimage"]["sha256"]
    assert (
        hashlib.sha256(r["public_config_sha256"].encode()).hexdigest()
        == r["identifier_fingerprint_sha256"]
    )
print(
    "Two public synthetic configuration digests independently reproduced; no matched values printed."
)
