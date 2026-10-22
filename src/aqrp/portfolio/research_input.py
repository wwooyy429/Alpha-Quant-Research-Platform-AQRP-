"""Read-only terminal-manifest-bound projection of synthetic P3 stage scores."""

import hashlib
from copy import deepcopy
from pathlib import Path

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.experiments.ledger import ExperimentLedger

from .contracts import PortfolioRequest, fields, load

STAGES = ("raw", "clean", "standardized", "neutralized", "final")


def _ledger(root):
    if not isinstance(root, (str, Path)) or not Path(root).is_dir():
        raise ContractError("RESEARCH_ROOT_NOT_FOUND")
    return ExperimentLedger(root)


def _read(ledger, run_id, name, manifest):
    entries = [e for e in manifest["files"] if e["path"] == name]
    if len(entries) != 1:
        raise ContractError("RESEARCH_ARTIFACT_NOT_MANIFESTED", name)
    path = ledger.path(run_id) / name
    raw = path.read_bytes()
    if path.is_symlink() or hashlib.sha256(raw).hexdigest() != entries[0]["sha256"]:
        raise ContractError("RESEARCH_ARTIFACT_BYTES_CHANGED", name)
    return load(raw), hashlib.sha256(raw).hexdigest()


def _projection(binding, context, assets):
    fields(
        binding,
        {
            "ledger_root",
            "run_id",
            "factor_key",
            "stage",
            "manifest_sha256",
            "artifact_sha256",
            "source_calendar_id",
        },
        "research_binding",
    )
    if binding["stage"] not in STAGES:
        raise ContractError("INVALID_RESEARCH_STAGE")
    ledger = _ledger(binding["ledger_root"])
    manifest = ledger.verify(binding["run_id"])
    manifest_bytes = (ledger.path(binding["run_id"]) / "manifest.json").read_bytes()
    if (
        manifest["status"] != "SUCCEEDED"
        or hashlib.sha256(manifest_bytes).hexdigest() != binding["manifest_sha256"]
    ):
        raise ContractError("RESEARCH_MANIFEST_BINDING_MISMATCH")
    stage, hash_value = _read(ledger, binding["run_id"], binding["stage"] + ".json", manifest)
    config, _ = _read(ledger, binding["run_id"], "config.json", manifest)
    lineage, _ = _read(ledger, binding["run_id"], "lineage.json", manifest)
    report, _ = _read(ledger, binding["run_id"], "report.json", manifest)
    if hash_value != binding["artifact_sha256"] or (
        config["market_id"],
        config["currency"],
        config["calendar_id"],
        lineage["data_hash"],
    ) != (
        context["market_id"],
        context["currency"],
        binding["source_calendar_id"],
        context["snapshot_sha256"],
    ):
        raise ContractError("RESEARCH_SOURCE_BINDING_MISMATCH")
    if report["financial_approval"] != "NONE" or report["independence_verified"]:
        raise ContractError("ENGINEERING_RESEARCH_SCOPE_REQUIRED")
    selected = [
        r
        for r in stage["rows"]
        if r["factor_key"] == binding["factor_key"]
        and utc(r["decision_time"]) == utc(context["decision_time"])
        and r["security_id"] in assets
    ]
    if not selected:
        raise ContractError("RESEARCH_SCORE_PROJECTION_EMPTY")
    first = selected[0]
    if any(
        (r["factor_ref"], r["params_hash"], r["stage"])
        != (first["factor_ref"], first["params_hash"], binding["stage"])
        for r in selected
    ):
        raise ContractError("MIXED_RESEARCH_SCORE_IDENTITIES")
    return {
        "factor_key": binding["factor_key"],
        "factor_ref": first["factor_ref"],
        "params_hash": first["params_hash"],
        "stage": binding["stage"],
        "rows": [
            {
                "security_id": r["security_id"],
                "score": r["score"],
                "valid": r["validity"] == "VALID",
                "signal_time": r["signal_time"],
                "session_index": context["session_index"],
                "event_time": r["signal_time"],
                "available_at": r["available_at"],
                "as_of": context["decision_time"],
            }
            for r in selected
        ],
    }


def verify_bindings(x):
    bindings = x["source"]["research_bindings"]
    if not isinstance(bindings, list) or len(bindings) != len(x["inputs"]["scores"]):
        raise ContractError("RESEARCH_BINDINGS_REQUIRED")
    for b, e in zip(bindings, x["inputs"]["scores"]):
        expected = _projection(
            b, x["context"], {r["security_id"] for r in x["inputs"]["securities"]["data"]}
        )
        if digest(expected) != digest(e["data"]):
            raise ContractError("RESEARCH_SCORE_PROJECTION_CHANGED")


def bind_research(value, ledger_root, run_id, *, stage="final"):
    """Explicit new engineering input; never changes a running request or account."""
    x = deepcopy(value)
    if stage not in STAGES:
        raise ContractError("INVALID_RESEARCH_STAGE")
    ledger = _ledger(ledger_root)
    m = ledger.verify(run_id)
    _, ah = _read(ledger, run_id, stage + ".json", m)
    config, _ = _read(ledger, run_id, "config.json", m)
    bindings = []
    envelopes = []
    for key in sorted(x["policy"]["factor_weights"]):
        b = {
            "ledger_root": str(Path(ledger_root).resolve()),
            "run_id": run_id,
            "factor_key": key,
            "stage": stage,
            "manifest_sha256": hashlib.sha256(
                (ledger.path(run_id) / "manifest.json").read_bytes()
            ).hexdigest(),
            "artifact_sha256": ah,
            "source_calendar_id": config["calendar_id"],
        }
        data = _projection(
            b, x["context"], {r["security_id"] for r in x["inputs"]["securities"]["data"]}
        )
        e = {
            "schema_version": "portfolio-input/1.0.0",
            "kind": "scores",
            "ref": f"p3-{run_id}-{stage}-{key}",
            "context": x["context"],
            "event_time": max((r["event_time"] for r in data["rows"]), key=utc),
            "available_at": max((r["available_at"] for r in data["rows"]), key=utc),
            "as_of": x["context"]["decision_time"],
            "data": data,
        }
        e["content_sha256"] = digest(e)
        envelopes.append(e)
        bindings.append(b)
    x["inputs"]["scores"] = envelopes
    all_inputs = [e for k, e in x["inputs"].items() if k != "scores"] + envelopes
    x["source"] = {
        "kind": "RESEARCH_ARTIFACT",
        "scope": "ENGINEERING_TEST_ONLY",
        "dataset_kind": "SYNTHETIC",
        "financial_approval": "NONE",
        "fixture_manifest": {e["ref"]: e["content_sha256"] for e in all_inputs},
        "research_bindings": bindings,
    }
    return PortfolioRequest.create(x)
