"""Immutable PIT exposure sidecar; never extends or rewrites the P1 eight tables."""

import hashlib
import json
import math
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError, SnapshotMismatch
from aqrp.core.time import utc
from aqrp.data.store import read_snapshot


@dataclass(frozen=True)
class ExposureRef:
    root: Path
    manifest_hash: str
    parent_hash: str


def publish_exposures(rows, parent, destination):
    _, tables = read_snapshot(parent)
    identities = {
        (r["security_id"], r["market_id"], r["currency"])
        for r in tables["security_master"].to_pylist()
    }
    normalized = []
    keys = set()
    for item in rows:
        row = dict(item)
        for name in ("security_id", "market_id", "currency", "industry_version"):
            if not isinstance(row[name], str) or not row[name]:
                raise ContractError("INVALID_EXPOSURE_ID", name)
        if (row["security_id"], row["market_id"], row["currency"]) not in identities:
            raise ContractError("EXPOSURE_PARENT_IDENTITY_MISMATCH")
        if row["industry"] is not None and (
            not isinstance(row["industry"], str) or not row["industry"]
        ):
            raise ContractError("INVALID_INDUSTRY")
        risk = row.pop("risk_exposures", {})
        if not isinstance(risk, dict) or any(
            not isinstance(k, str)
            or not k
            or (v is not None and (type(v) not in (int, float) or not math.isfinite(v)))
            for k, v in risk.items()
        ):
            raise ContractError("INVALID_RISK_EXPOSURE")
        row["risk_exposures_json"] = canonical(risk).decode("utf-8")
        for name in ("event_time", "available_at", "effective_from"):
            row[name] = utc(row[name])
        row["effective_to"] = utc(row["effective_to"]) if row["effective_to"] is not None else None
        if row["available_at"] < row["event_time"] or (
            row["effective_to"] is not None and row["effective_to"] <= row["effective_from"]
        ):
            raise ContractError("INVALID_EXPOSURE_TIME")
        if type(row["revision_id"]) is not int or row["revision_id"] < 1:
            raise ContractError("INVALID_EXPOSURE_REVISION")
        if row["market_cap"] is not None:
            cap = Decimal(str(row["market_cap"]))
            if not cap.is_finite() or cap <= 0:
                raise ContractError("INVALID_MARKET_CAP")
            row["market_cap"] = str(cap)
        key = (row["security_id"], row["market_id"], row["effective_from"], row["revision_id"])
        if key in keys:
            raise ContractError("DUPLICATE_EXPOSURE")
        keys.add(key)
        normalized.append(row)
    if not normalized:
        raise ContractError("EMPTY_EXPOSURES")
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(dir=root, prefix=".exposure-"))
    try:
        pq.write_table(pa.Table.from_pylist(normalized), temp / "exposures.parquet")
        m = {
            "schema": "exposures/1.0.0",
            "parent_snapshot_hash": parent.manifest_hash,
            "data_sha256": hashlib.sha256((temp / "exposures.parquet").read_bytes()).hexdigest(),
            "n": len(normalized),
            "unit": "currency",
            "profile": "SYNTHETIC_V1",
        }
        (temp / "manifest.json").write_bytes(canonical(m))
        target = root / str(uuid.uuid4())
        temp.rename(target)
        return ExposureRef(target, digest(m), parent.manifest_hash)
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def exposures_as_of(ref, cutoff, market, currency, security_ids):
    cutoff = utc(cutoff)
    root = Path(ref.root)
    m = json.loads((root / "manifest.json").read_bytes())
    data = root / "exposures.parquet"
    if (
        root.is_symlink()
        or data.is_symlink()
        or digest(m) != ref.manifest_hash
        or m["parent_snapshot_hash"] != ref.parent_hash
        or hashlib.sha256(data.read_bytes()).hexdigest() != m["data_sha256"]
    ):
        raise SnapshotMismatch("EXPOSURE_HASH_MISMATCH")
    groups = {}
    for row in pq.read_table(data).to_pylist():
        if row["event_time"] > cutoff or row["available_at"] > cutoff:
            continue
        key = (row["security_id"], row["market_id"], row["effective_from"])
        groups.setdefault(key, []).append(row)
    latest = {}
    for key, versions in groups.items():
        available = max(r["available_at"] for r in versions)
        selected = [r for r in versions if r["available_at"] == available]
        if len(selected) != 1:
            raise ContractError("CONFLICTING_VISIBLE_EXPOSURE")
        latest[key] = selected[0]
    result = {}
    for row in latest.values():
        if (
            row["security_id"] not in security_ids
            or not row["effective_from"] <= cutoff
            or (row["effective_to"] is not None and cutoff >= row["effective_to"])
        ):
            continue
        if row["market_id"] != market or row["currency"] != currency:
            raise ContractError("EXPOSURE_MARKET_OR_CURRENCY_MISMATCH")
        if row["security_id"] in result:
            raise ContractError("OVERLAPPING_EXPOSURE_INTERVAL")
        result[row["security_id"]] = {
            **row,
            "risk_exposures": json.loads(row["risk_exposures_json"]),
        }
    return result
