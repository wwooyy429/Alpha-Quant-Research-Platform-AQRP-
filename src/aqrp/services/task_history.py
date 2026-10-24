"""Trusted registration of the already approved original package/Ref replay scope."""

import hashlib
from pathlib import Path

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.environment import runtime_manifest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger, immutable_write
from aqrp.experiments.reproduction import (
    ORIGINAL_PUBLICATION,
    archive_environment,
    replay_published_runs,
)
from aqrp.factors.admission import bundle_hash
from aqrp.portfolio.contracts import load


def register_history(root, archive, publication):
    """Local trusted launcher only; no history paths or interpreters from browser drafts."""
    verified = archive_environment(archive["interpreter"], archive["wheel"], archive["lock"])
    if any(archive.get(k) != v for k, v in verified.items()) or set(archive) - set(verified) - {
        "dependency_wheels"
    }:
        raise ContractError("HISTORICAL_ENVIRONMENT_CHANGED")
    publication = guard_path(publication)
    if (
        hashlib.sha256((publication / "FILE_MANIFEST.json").read_bytes()).hexdigest()
        != ORIGINAL_PUBLICATION
    ):
        raise ContractError("ORIGINAL_PUBLICATION_MANIFEST_CHANGED")
    history = {
        "id": "published-original",
        "profile": "PUBLISHED_REF_PROJECTION",
        "archive": archive,
        "publication_root": str(publication),
        "publication_manifest_sha256": ORIGINAL_PUBLICATION,
        "scope": "REGISTERED_OLD_PACKAGE_LOCK_REFS_AND_RESULT_PROJECTION",
        "full_historical_host_verified": False,
    }
    path = guard_path(Path(root) / "history.json")
    if path.exists():
        if path.read_bytes() != canonical(history):
            raise ContractError("HISTORICAL_CATALOG_IMMUTABLE")
    else:
        immutable_write(path, canonical(history))
    return history


def history_catalogue(root):
    value = load(guard_path(Path(root) / "history.json").read_bytes())
    if (
        value["id"] != "published-original"
        or value["profile"] != "PUBLISHED_REF_PROJECTION"
        or value["publication_manifest_sha256"] != ORIGINAL_PUBLICATION
    ):
        raise ContractError("HISTORICAL_CATALOG_CHANGED")
    for name, key in [
        ("interpreter", "interpreter_hash"),
        ("wheel", "wheel_hash"),
        ("lock", "lock_hash"),
    ]:
        if (
            hashlib.sha256(guard_path(value["archive"][name]).read_bytes()).hexdigest()
            != value["archive"][key]
        ):
            raise ContractError("HISTORICAL_ARCHIVE_CHANGED")
    publication = guard_path(value["publication_root"])
    manifest_raw = (publication / "FILE_MANIFEST.json").read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != ORIGINAL_PUBLICATION:
        raise ContractError("ORIGINAL_PUBLICATION_MANIFEST_CHANGED")
    for entry in load(manifest_raw)["files"]:
        path = guard_path(publication / entry["path"])
        if (
            not path.is_relative_to(publication)
            or path.stat().st_size != entry["bytes"]
            or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]
        ):
            raise ContractError("ORIGINAL_PUBLICATION_ARTIFACT_CHANGED")
    return value


def execute_history(service, auth, request):
    history = history_catalogue(service.root)
    if digest(history) != request["payload"]["history_sha256"]:
        raise ContractError("HISTORICAL_CATALOG_CHANGED")
    context = auth.allocate("E", "PUBLISHED_REF_PROJECTION", service.root / "replay-runs")
    plan = {
        "task_config_hash": auth.check()["hash"],
        "request_sha256": digest(history),
        "request_utf8": canonical(history).decode(),
        "decision_count": 0,
        "slots": {"E": context.binding()["child_run_id"]},
    }
    path = guard_path(service.root / "tasks" / auth.task / "resolved-plan.json")
    if path.exists():
        if path.read_bytes() != canonical(plan):
            raise ContractError("TASK_RESOLVED_PLAN_CHANGED")
    else:
        immutable_write(path, canonical(plan))
    prior = context.existing()
    if prior is None:
        ledger = ExperimentLedger(service.root / "replay-runs")
        run = ledger.start(
            {"registered_history_sha256": digest(history)},
            {
                "code_commit": request["code_commit"],
                "code_bundle": bundle_hash(),
                "data_hash": history["publication_manifest_sha256"],
                "environment": runtime_manifest(),
                "protocol_hash": digest(history),
                "permission_domain": "ENGINEERING_TEST_ONLY",
                "seed": 0,
            },
            task_context=context,
        )
        result = replay_published_runs(history["archive"], history["publication_root"])
        context.checkpoint()
        ledger.artifact(run, "result.json", result)
        ledger.artifact(run, "source-registration.json", history)
        manifest = ledger.finish(run, "SUCCEEDED")
        context.mark_verified(manifest)
        prior = {**result, "manifest": manifest}
    return {
        "profile": "PUBLISHED_REF_PROJECTION",
        "historical_replay": prior,
        "full_historical_host_verified": False,
    }
