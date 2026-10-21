"""Exact original-wheel replay and declared numeric projections of immutable runs."""

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from packaging.requirements import Requirement

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.data.snapshot import safe_path
from aqrp.experiments.ledger import ExperimentLedger

ORIGINAL_WHEEL = "70b43271ee142b18d5d9d306d452936f8409322fda5e676431f24eb150871c9d"
ORIGINAL_LOCK = "86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb"
ORIGINAL_BUNDLE = "51933fe2508e61a25fef53ea73b4210a67cb19d6531e1bf614e206db32a1d62d"
ORIGINAL_PUBLICATION = "af7d3fd670135a44bbac077163a92b1fd92ecfeddb067656bd4fbb3cd5190c7f"


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _invoke(interpreter, wheel, payload):
    worker = Path(__file__).with_name("replay_worker.py")
    # No inherited Python configuration, tokens or real-account credentials.
    env = {
        k: v
        for k, v in os.environ.items()
        if k.upper() in ("SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "LANG", "LC_ALL")
    }
    with tempfile.TemporaryDirectory(prefix="aqrp-original-replay-") as cwd:
        result = subprocess.run(
            [str(interpreter), "-I", str(worker)],
            input=canonical(
                {"schema": "replay/1", "wheel": str(wheel), "wheel_hash": ORIGINAL_WHEEL, **payload}
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=cwd,
            timeout=120,
            check=False,
        )
    if result.returncode:
        raise ContractError("ORIGINAL_ENVIRONMENT_REPLAY_FAILED")
    return json.loads(result.stdout)


def archive_environment(interpreter, wheel, lock):
    """Trusted operator/developer registers an existing isolated managed old venv."""
    interpreter, wheel, lock = map(
        lambda p: Path(p).resolve(strict=True), (interpreter, wheel, lock)
    )
    if _sha(wheel) != ORIGINAL_WHEEL or _sha(lock) != ORIGINAL_LOCK:
        raise ContractError("UNAPPROVED_REPRODUCTION_ARCHIVE")
    inspection = _invoke(interpreter, wheel, {"mode": "inspect"})
    locked_lines = re.findall(r"^([A-Za-z0-9_-]+==[^\\\r\n]+)", lock.read_text(), re.M)
    requirements = [Requirement(line.strip()) for line in locked_lines]
    expected = {
        r.name: next(iter(r.specifier)).version
        for r in requirements
        if r.marker is None or r.marker.evaluate(inspection["markers"])
    }
    if (
        len(requirements) != 22
        or any(
            inspection["inventory"].get(k.lower().replace("_", "-")) != v
            for k, v in expected.items()
        )
        or inspection["bundle_hash"] != ORIGINAL_BUNDLE
    ):
        raise ContractError("ORIGINAL_ENVIRONMENT_LOCK_MISMATCH")
    return {
        "schema": "environment-archive/1",
        "interpreter": str(interpreter),
        "interpreter_hash": _sha(interpreter),
        "wheel": str(wheel),
        "wheel_hash": ORIGINAL_WHEEL,
        "lock": str(lock),
        "lock_hash": ORIGINAL_LOCK,
        "worker_hash": _sha(Path(__file__).with_name("replay_worker.py")),
        "inspection": inspection,
    }


def replay_original(archive, request):
    for name, key in (
        ("interpreter", "interpreter_hash"),
        ("wheel", "wheel_hash"),
        ("lock", "lock_hash"),
    ):
        if _sha(archive[name]) != archive[key]:
            raise ContractError("REPRODUCTION_ARCHIVE_CHANGED")
    if (
        archive["worker_hash"] != _sha(Path(__file__).with_name("replay_worker.py"))
        or archive["wheel_hash"] != ORIGINAL_WHEEL
        or archive["lock_hash"] != ORIGINAL_LOCK
    ):
        raise ContractError("UNAPPROVED_REPRODUCTION_ARCHIVE")
    allowed = {"snapshot", "query", "ref", "decision_time", "parameters", "seed"}
    if set(request) != allowed:
        raise ContractError("INVALID_REPLAY_REQUEST")
    current = _invoke(archive["interpreter"], archive["wheel"], {"mode": "compute", **request})
    if {
        k: v
        for k, v in current.items()
        if k not in ("rows", "config", "content_hash", "logical_hash")
    } != archive["inspection"]:
        raise ContractError("ORIGINAL_ENVIRONMENT_DRIFT")
    return {
        "status": "ORIGINAL_ARTIFACT_EXECUTED",
        "environment_hash": digest(archive),
        "raw_input_sha256": hashlib.sha256(canonical(request)).hexdigest(),
        "result": current,
    }


def replay_published_runs(archive, publication_root):
    """Verify every original byte, then replay all three actual P2 published runs."""
    root = Path(publication_root)
    manifest = root / "FILE_MANIFEST.json"
    if _sha(manifest) != ORIGINAL_PUBLICATION:
        raise ContractError("ORIGINAL_PUBLICATION_MANIFEST_CHANGED")
    entries = json.loads(manifest.read_bytes())["files"]
    for row in entries:
        path = safe_path(root, row["path"])
        if (
            (root / row["path"]).is_symlink()
            or _sha(path) != row["sha256"]
            or path.stat().st_size != row["bytes"]
        ):
            raise ContractError("ORIGINAL_PUBLICATION_ARTIFACT_CHANGED")
    results = []
    for path in sorted((root / "sdk/factor-runs").glob("*/manifest.json")):
        old_manifest = json.loads(path.read_bytes())
        for row in old_manifest["artifacts"]:
            if _sha(safe_path(path.parent, row["path"])) != row["sha256"]:
                raise ContractError("ORIGINAL_RUN_ARTIFACT_CHANGED")
        raw = (path.parent / "config.json").read_bytes()
        config = json.loads(raw)
        rows = json.loads((path.parent / "signals.json").read_bytes())
        if digest({"rows": rows, "config": raw.decode("utf-8")}) != old_manifest["content_hash"]:
            raise ContractError("ORIGINAL_CONTENT_HASH_CHANGED")
        spec = config["spec"]
        request = {
            "snapshot": {
                "root": str((root / "sdk/factor-dataset").resolve()),
                "snapshot_id": config["snapshot_id"],
                "manifest_hash": config["manifest_hash"],
            },
            "query": {
                "security_ids": config["security_ids"],
                "market_id": config["market_id"],
                "calendar_id": config["calendar_id"],
                "session_range": [config["sessions"][0][0], config["target_session"]],
                "fields": ["close", "volume"],
                "price_basis": spec["price_basis"],
            },
            "ref": {
                "factor_id": spec["factor_id"],
                "factor_version": spec["factor_version"],
                "implementation_hash": spec["implementation_version"],
            },
            "decision_time": config["decision_time"],
            "parameters": dict(config["params"]),
            "seed": config["seed"],
        }
        replay = replay_original(archive, request)
        result = replay["result"]

        def row_projection(values):
            return [
                {k: v for k, v in r.items() if k not in ("run_id", "computation_id")}
                for r in values
            ]

        def config_projection(value):
            return {
                k: v
                for k, v in value.items()
                if k not in ("run_id", "computation_id", "query_hash")
            }

        if (
            row_projection(rows) != row_projection(result["rows"])
            or config_projection(config) != config_projection(result["config"])
            or old_manifest["logical_hash"] != result["logical_hash"]
        ):
            raise ContractError("ORIGINAL_RUN_PROJECTION_MISMATCH")
        results.append(
            {
                "original_run": config["run_id"],
                "original_manifest_sha256": _sha(path),
                "input": request,
                "replay": replay,
                "allowed_changes": ["run_id", "computation_id", "path_bound_query_hash"],
                "status": "DECLARED_PROJECTION_MATCH",
            }
        )
    if len(results) != 3 or {r["input"]["ref"]["factor_id"] for r in results} != {
        "momentum",
        "reversal",
        "volume",
    }:
        raise ContractError("ORIGINAL_PUBLISHED_RUN_SET_INCOMPLETE")
    return {
        "publication_manifest_sha256": ORIGINAL_PUBLICATION,
        "verified_original_files": entries,
        "runs": results,
        "status": "ALL_ORIGINAL_BYTES_VERIFIED_AND_THREE_RUNS_REPLAYED",
    }


def reproduce_current(request, ledger_root, original_id):
    from aqrp.services.research import research

    ledger = ExperimentLedger(ledger_root)
    before = ledger.verify(original_id)
    root = ledger.path(original_id)
    if (root / "config.json").read_bytes() != request.config:
        raise ContractError("REPRODUCTION_CONFIG_CHANGED")
    original_lineage = json.loads((root / "lineage.json").read_bytes())
    if (
        original_lineage["code_commit"] != request.code_commit
        or original_lineage["data_hash"] != request.snapshot.manifest_hash
    ):
        raise ContractError("REPRODUCTION_CODE_OR_DATA_CHANGED")
    result = research(request, ledger_root)
    numerical = (
        "raw.json",
        "clean.json",
        "standardized.json",
        "neutralized.json",
        "final.json",
        "labels.json",
        "metrics.json",
        "oos.json",
        "inference.json",
    )
    differences = [
        name
        for name in numerical
        if (root / name).read_bytes() != (ledger.path(result["run_id"]) / name).read_bytes()
    ]
    if before != ledger.verify(original_id):
        raise ContractError("ORIGINAL_RUN_CHANGED_DURING_REPLAY")
    return {
        "original": original_id,
        "replay": result["run_id"],
        "status": "DECLARED_PROJECTION_MATCH" if not differences else "MISMATCH",
        "differences": differences,
        "original_manifest_hash": digest(before),
        "allowed_changed_fields": [
            "run_id",
            "request_uuid",
            "artifact_paths",
            "repeat_history",
            "family_contamination",
        ],
    }
