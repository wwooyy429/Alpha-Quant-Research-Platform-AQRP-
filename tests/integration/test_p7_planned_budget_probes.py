"""Actual cross-entry probes after a frozen twelve-owner fixture; never main E2E."""

import hashlib
import json
import subprocess
import sys
import uuid
from dataclasses import asdict
from pathlib import Path

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import (
    advance_actor,
    complete_actor,
    install_execution_plan,
    open_protocol_driver,
)
from aqrp.experiments.ledger import ExperimentLedger, append_chain, immutable_write
from aqrp.factors.admission import bundle_hash
from aqrp.services.research import hypotheses
from aqrp.services.task_requests import catalogue, initialize, research_request
from aqrp.services.tasks import TaskService


def evidence(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def legacy_lineage(req):
    return {
        "code_commit": req.code_commit,
        "code_bundle": bundle_hash(),
        "data_hash": req.snapshot.manifest_hash,
        "exposure_hash": req.exposures.manifest_hash,
        "coverage_hash": req.coverage.checksum,
        "environment": {},
        "protocol_hash": digest(json.loads(req.config)),
        "permission_domain": "ENGINEERING_DEMO",
        "seed": 17,
        "admission_inputs": {
            "snapshot_root": str(req.snapshot.root),
            "exposure_root": str(req.exposures.root),
        },
    }


@pytest.mark.parametrize("probe", ["legacy-cli", "direct-ledger", "task"])
def test_frozen_thirteenth_probe_hits_shared_cap_before_zero_grant_capacity(tmp_path, probe):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    frozen = s.freeze(
        {"factor_ids": ["momentum"], "horizons": [1], "start": "2024-01-06", "end": "2024-01-06"}
    )
    req = research_request(tmp_path, json.loads(frozen.raw))
    cfg = json.loads(req.config)
    cat = catalogue(tmp_path)
    source = Path(__file__).resolve()
    identity = {
        "runner_path": str(source),
        "runner_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }
    initial_kind = "LEGACY" if probe == "task" else "TASK"
    initial_hash = digest(cfg) if probe == "task" else frozen.config_hash
    final_kind = "TASK" if probe == "task" else "LEGACY"
    slots = [
        {
            "slot_id": "reserved-" + str(i),
            "service_kind": initial_kind,
            "request_hash": initial_hash,
            "output_root": str(tmp_path / "research-runs"),
            "requested_units": 1,
            "grant_capacity": 1,
            "max_admitted_owners": 1,
            "expected_status": "CANCELLED",
        }
        for i in range(12)
    ]
    slots.append(
        {
            "slot_id": "expected-budget-refusal",
            "service_kind": final_kind,
            "request_hash": frozen.config_hash if probe == "task" else digest(cfg),
            "output_root": str(tmp_path / "research-runs"),
            "requested_units": 1,
            "grant_capacity": 0,
            "max_admitted_owners": 1,
            "expected_status": "FAILED" if probe == "task" else "REJECTED",
            "expected_code": "EXPERIMENT_BUDGET_EXCEEDED",
        }
    )
    plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "PREREGISTERED_CROSS_ENTRY_BUDGET_REGRESSION_NOT_MAIN_E2E",
        "data_hash": req.snapshot.manifest_hash,
        "catalogue_hash": digest(cat),
        **identity,
        "slots": slots,
    }
    fixed = install_execution_plan(tmp_path, plan, identity)
    driver = open_protocol_driver(tmp_path, fixed, identity)
    for index in range(12):
        advance_actor(driver, index - 1)
        if initial_kind == "TASK":
            actor = TaskService(tmp_path)
            row = actor.submit(frozen, "fixed-owner-" + str(index))
            assert actor.cancel(row["task_id"]) == "CANCELLED"
            owner = row["task_id"]
            path = tmp_path / "tasks" / owner / "request.json"
        else:
            ledger = ExperimentLedger(tmp_path / "research-runs")
            owner = ledger.start(cfg, legacy_lineage(req))
            ledger.finish(owner, "CANCELLED")
            path = ledger.path(owner) / "manifest.json"
        complete_actor(
            driver, {"owner_id": owner, "status": "CANCELLED", "evidence": [evidence(path)]}
        )
    advance_actor(driver, 11)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    if probe == "legacy-cli":
        request = {
            "config": cfg,
            "code_commit": req.code_commit,
            "snapshot": {**asdict(req.snapshot), "root": str(req.snapshot.root)},
            "exposures": {**asdict(req.exposures), "root": str(req.exposures.root)},
            "coverage": req.coverage.read(req.snapshot.manifest_hash),
        }
        path = tmp_path / "legacy-probe-request.json"
        immutable_write(path, canonical(request))
        command = [
            sys.executable,
            "-m",
            "aqrp.services.cli",
            str(path),
            "--output",
            str(tmp_path / "research-runs"),
        ]
        completed = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90
        )
        immutable_write(tmp_path / "legacy-probe.stdout.log", completed.stdout)
        immutable_write(tmp_path / "legacy-probe.stderr.log", completed.stderr)
        immutable_write(
            tmp_path / "legacy-probe-command.json",
            canonical({"argv": command, "returncode": completed.returncode}),
        )
        assert completed.returncode != 0 and b"EXPERIMENT_BUDGET_EXCEEDED" in completed.stderr
    elif probe == "direct-ledger":
        run = str(uuid.uuid4())
        root = ledger.path(run)
        root.mkdir()
        lineage = legacy_lineage(req)
        immutable_write(root / "config.json", canonical(cfg))
        immutable_write(root / "lineage.json", canonical(lineage))
        append_chain(
            root / "events.jsonl",
            "RUNNING",
            {"config_hash": digest(cfg), "lineage_hash": digest(lineage)},
        )
        with pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
            ledger.register_trial(
                run, cfg["family"]["id"], hypotheses(cfg)[0]["hypothesis"], budget=12
            )
    else:
        row = TaskService(tmp_path).submit(frozen, "expected-task-refusal")
        assert row["status"] == "FAILED" and row["error"] == "EXPERIMENT_BUDGET_EXCEEDED"
        assert row["slots"] == {}
    with driver.budget.transaction() as c:
        stats = driver.budget.history(c)
        last = stats["admissions"][-1]
    assert (stats["admitted_units"], stats["requested_units"], stats["rejected_units"]) == (
        12,
        13,
        1,
    )
    assert stats["registered_trials"] == 0 and last["decision"] == "REJECTED"
    assert not (tmp_path / "research-runs/trials.jsonl").exists()
    path = tmp_path / (
        "tasks/" + last["owner_id"] + "/request.json"
        if probe == "task"
        else "task-control/admissions/" + last["admission_id"] + ".json"
    )
    complete_actor(
        driver,
        {
            "owner_id": last["owner_id"],
            "status": "FAILED" if probe == "task" else "REJECTED",
            "evidence": [evidence(path)],
        },
    )
