"""Fixed isolated subprocess entry, also compatible with the archived 0.2 wheel."""

import hashlib
import importlib.metadata
import json
import platform
import sys
import zipfile
from pathlib import Path


def main():
    raw = sys.stdin.buffer.read(1_048_577)
    if len(raw) > 1_048_576:
        raise ValueError("replay input size")
    request = json.loads(raw)
    if request["schema"] != "replay/1" or request["mode"] not in ("inspect", "compute"):
        raise ValueError("replay schema")
    wheel = Path(request["wheel"])
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != request["wheel_hash"]:
        raise ValueError("archived wheel changed")
    dist = importlib.metadata.distribution("aqrp")
    if dist.version != "0.2.0" or platform.python_version() != "3.13.16":
        raise ValueError("original interpreter/wheel required")
    # Compare actual installed package bytes to the original wheel, not RECORD alone.
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith("aqrp/") and not name.endswith("/"):
                if Path(dist.locate_file(name)).read_bytes() != archive.read(name):
                    raise ValueError("installed archive byte mismatch")
    inventory = {
        d.metadata["Name"].lower().replace("_", "-"): d.version
        for d in importlib.metadata.distributions()
    }
    from aqrp.factors.admission import reviewed_policy

    policy = reviewed_policy()
    result = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "inventory": inventory,
        "bundle_hash": policy["bundle_sha256"],
        "receipt_sha256": hashlib.sha256(
            Path(dist.locate_file("aqrp/factors/reviewed_code.json")).read_bytes()
        ).hexdigest(),
    }
    from packaging.markers import default_environment

    result["markers"] = default_environment()
    if request["mode"] == "compute":
        from dataclasses import asdict
        from datetime import date

        from aqrp.core.contracts import QuerySpec, SnapshotRef
        from aqrp.factors import FactorEngine, FactorRegistry, builtin_spec

        s = request["snapshot"]
        snapshot = SnapshotRef(Path(s["root"]), s["snapshot_id"], s["manifest_hash"])
        query = request["query"]
        q = QuerySpec(
            tuple(query["security_ids"]),
            query["market_id"],
            query["calendar_id"],
            tuple(date.fromisoformat(d) for d in query["session_range"]),
            tuple(query["fields"]),
            query["price_basis"],
        )
        registry = FactorRegistry()
        spec = builtin_spec(request["ref"]["factor_id"], request["ref"]["factor_version"])
        if asdict(spec.ref) != request["ref"]:
            raise ValueError("exact original FactorRef required")
        registry.register(
            spec.implementation_version,
            spec,
            actor="archived-replay",
            reason="original-wheel",
            evidence=spec.review_ref,
        )
        batch = FactorEngine(registry).run(
            spec.ref,
            q,
            request["decision_time"],
            snapshot,
            parameters=request["parameters"],
            seed=request["seed"],
        )
        result["rows"] = [asdict(r) for r in batch.rows]
        result["config"] = json.loads(batch.config_snapshot)
        result["content_hash"] = batch.content_hash
        result["logical_hash"] = batch.logical_hash
    # datetime serialization is for transport; raw original artifacts are never rewritten.
    from aqrp.core.canonical import canonical

    sys.stdout.buffer.write(canonical(result) + b"\n")


if __name__ == "__main__":
    main()
