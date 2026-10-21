"""Atomic immutable Parquet snapshots, trusted reference hashes and safe paths."""

import hashlib
import json
import shutil
import tempfile
import uuid
from pathlib import Path, PureWindowsPath

import pyarrow as pa
import pyarrow.parquet as pq

from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import SnapshotRef
from aqrp.core.errors import ContractError, SnapshotMismatch

from .quality import validate_dataset
from .schemas import SCHEMAS

PROVENANCE_KEYS = {
    "source_version",
    "source_license",
    "unit_version",
    "calendar_version",
    "universe_version",
    "actions_version",
    "profile_id",
    "parent_snapshot",
}


def safe_path(root, relative):
    root = Path(root).resolve(strict=True)
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise SnapshotMismatch("UNSAFE_PATH", "path")
    path = Path(relative)
    if (
        path.is_absolute()
        or PureWindowsPath(relative).drive
        or any(p in ("..", ".", "") for p in relative.split("/"))
    ):
        raise SnapshotMismatch("UNSAFE_PATH", "path")
    target = root.joinpath(path).resolve()
    if not target.is_relative_to(root) or target == root:
        raise SnapshotMismatch("PATH_ESCAPE", "path")
    return target


def manifest_digest(manifest):
    return digest({k: v for k, v in manifest.items() if k not in ("snapshot_id", "manifest_hash")})


def publish_snapshot(tables, provenance, destination, *, snapshot_id=None, exploratory=False):
    if set(provenance) != PROVENANCE_KEYS or provenance["profile_id"] != "SYNTHETIC_V1":
        raise ContractError("PROVENANCE_MISMATCH", "provenance")
    if any(
        not isinstance(v, str) or not v for k, v in provenance.items() if k != "parent_snapshot"
    ):
        raise ContractError("MISSING_PROVENANCE", "provenance")
    validated = validate_dataset(tables, exploratory=exploratory)
    if any(
        r["calendar_version"] != provenance["calendar_version"]
        for r in validated["calendar"].table.to_pylist()
    ):
        raise ContractError("CALENDAR_VERSION_MISMATCH", "calendar_version")
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    sid = str(uuid.uuid4()) if snapshot_id is None else snapshot_id
    if (
        not isinstance(sid, str)
        or not sid
        or any(
            c not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_" for c in sid
        )
    ):
        raise SnapshotMismatch("INVALID_SNAPSHOT_ID", "snapshot_id")
    target = safe_path(root, sid)
    if target.exists():
        raise SnapshotMismatch("IMMUTABLE_SNAPSHOT", "snapshot_id")
    temp = Path(tempfile.mkdtemp(prefix=".publish-", dir=root))
    try:
        manifest = {
            "schema_version": "snapshot/1.0.0",
            "data_schema_version": "data/1.0.0",
            "snapshot_id": sid,
            "provenance": dict(provenance),
            "pit_status": "EXPLORATORY_ONLY" if exploratory else "PIT_VERIFIED",
            "tables": {},
        }
        for name, result in sorted(validated.items()):
            table = result.table.set_column(
                result.table.schema.get_field_index("snapshot_id"),
                "snapshot_id",
                pa.array([sid] * result.table.num_rows, type=pa.string()),
            )
            path = temp / f"{name}.parquet"
            pq.write_table(
                table,
                path,
                compression="zstd",
                version="2.6",
                coerce_timestamps="us",
                allow_truncated_timestamps=False,
            )
            records = table.to_pylist()
            times = [r["event_time"] for r in records]
            manifest["tables"][name] = {
                "path": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "rows": table.num_rows,
                "security_ids": sorted({r["security_id"] for r in records if "security_id" in r}),
                "event_min": min(times) if times else None,
                "event_max": max(times) if times else None,
                "quality": {
                    "input": result.report.input,
                    "valid": result.report.valid,
                    "duplicate": result.report.duplicate,
                    "missing": result.report.missing,
                    "rejected": result.report.rejected,
                },
            }
        manifest["manifest_hash"] = manifest_digest(manifest)
        (temp / "manifest.json").write_bytes(canonical(manifest))
        ref = SnapshotRef(root, sid, manifest["manifest_hash"])
        # Validate sealed bytes before publishing. No destination replacement.
        _verify(temp, sid, ref.manifest_hash)
        temp.rename(target)
        return ref
    finally:
        if temp.exists():
            # Only the freshly created, verified child of this snapshot root is removable.
            if temp.resolve().parent != root or not temp.name.startswith(".publish-"):
                raise SnapshotMismatch("TEMP_PATH_ESCAPE", "path")
            shutil.rmtree(temp)


def _verify(directory, sid, expected_hash):
    try:
        raw = safe_path(directory, "manifest.json").read_bytes()
        manifest = json.loads(raw)
        if (
            canonical(manifest) != raw
            or manifest["schema_version"] != "snapshot/1.0.0"
            or manifest["data_schema_version"] != "data/1.0.0"
            or manifest["snapshot_id"] != sid
            or manifest_digest(manifest) != expected_hash
            or manifest["manifest_hash"] != expected_hash
            or set(manifest["tables"]) != set(SCHEMAS)
            or set(manifest["provenance"]) != PROVENANCE_KEYS
            or manifest["pit_status"] not in ("PIT_VERIFIED", "EXPLORATORY_ONLY")
        ):
            raise SnapshotMismatch("MANIFEST_MISMATCH", "manifest")
        tables = {}
        for name, item in manifest["tables"].items():
            path = safe_path(directory, item["path"])
            binary = path.read_bytes()
            if hashlib.sha256(binary).hexdigest() != item["sha256"]:
                raise SnapshotMismatch("FILE_HASH_MISMATCH", name)
            table = pq.read_table(pa.BufferReader(binary))
            if table.schema != SCHEMAS[name] or table.num_rows != item["rows"]:
                raise SnapshotMismatch("SCHEMA_OR_ROW_COUNT", name)
            if any(r["snapshot_id"] != sid for r in table.to_pylist()):
                raise SnapshotMismatch("MIXED_SNAPSHOT", name)
            records = table.to_pylist()
            times = [r["event_time"] for r in records]
            summary = {
                "security_ids": sorted({r["security_id"] for r in records if "security_id" in r}),
                "event_min": min(times) if times else None,
                "event_max": max(times) if times else None,
            }
            if canonical(summary) != canonical({k: item[k] for k in summary}):
                raise SnapshotMismatch("RANGE_SUMMARY_MISMATCH", name)
            q = item["quality"]
            if (
                any(
                    type(q[k]) is not int or q[k] < 0
                    for k in ("input", "valid", "duplicate", "missing", "rejected")
                )
                or q["input"] != q["valid"] + q["duplicate"] + q["missing"] + q["rejected"]
                or q["valid"] + q["missing"] != table.num_rows
                or q["rejected"] != 0
            ):
                raise SnapshotMismatch("QUALITY_COUNT_MISMATCH", name)
            tables[name] = table
        validate_dataset(tables, exploratory=manifest["pit_status"] == "EXPLORATORY_ONLY")
        if any(
            r["calendar_version"] != manifest["provenance"]["calendar_version"]
            for r in tables["calendar"].to_pylist()
        ):
            raise SnapshotMismatch("CALENDAR_VERSION_MISMATCH", "calendar")
        return manifest, tables
    except (OSError, ValueError, KeyError, TypeError, ContractError) as e:
        if isinstance(e, SnapshotMismatch):
            raise
        raise SnapshotMismatch("SNAPSHOT_INVALID", "manifest") from e


def verify_snapshot(ref):
    if not isinstance(ref, SnapshotRef):
        raise SnapshotMismatch("SNAPSHOT_REF_REQUIRED", "ref")
    directory = safe_path(ref.root, ref.snapshot_id)
    return _verify(directory, ref.snapshot_id, ref.manifest_hash)
