"""The planned zero-research cancellation retains the real original financial proof."""

import hashlib
import json
from pathlib import Path

import pytest

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import (
    advance_actor,
    complete_actor,
    install_execution_plan,
    open_protocol_driver,
)
from aqrp.services.task_requests import catalogue, initialize
from aqrp.services.tasks import TaskService


def test_planned_queued_replay_cancel_rechecks_original_physical_source(tmp_path):
    initialize(tmp_path, "a" * 40)
    source_request = TaskService(tmp_path).freeze(
        {
            "kind": "engineering_pipeline",
            "start": "2024-01-06",
            "end": "2024-01-06",
            "horizons": [1],
        }
    )
    cat = catalogue(tmp_path)
    runner = Path(__file__).resolve()
    identity = {
        "runner_path": str(runner),
        "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }
    plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "PLANNED_CANCEL_SOURCE_PHYSICAL_PROOF_REGRESSION_NOT_MAIN_E2E",
        "data_hash": cat["snapshot"]["manifest_hash"],
        "catalogue_hash": digest(cat),
        **identity,
        "slots": [
            {
                "slot_id": "source",
                "service_kind": "TASK",
                "request_hash": source_request.config_hash,
                "output_root": str(tmp_path / "research-runs"),
                "requested_units": 1,
                "grant_capacity": 1,
                "max_admitted_owners": 1,
                "expected_status": "SUCCEEDED",
            },
            {
                "slot_id": "cancel",
                "service_kind": "TASK_REPLAY",
                "source_slot": "source",
                "originalsource_request_hash": source_request.config_hash,
                "request_hash": None,
                "profile": "P5_NUMERICAL",
                "request_template": {
                    "schema": "task-request/1",
                    "kind": "replay",
                    "defaults_revision": 0,
                    "payload": {"source_task": "$SOURCE_TASK", "profile": "P5_NUMERICAL"},
                },
                "output_root": str(tmp_path / "replay-runs"),
                "requested_units": 0,
                "grant_capacity": 0,
                "max_admitted_owners": 1,
                "expected_status": "CANCELLED",
            },
        ],
    }
    # Freeze the actual request envelope spelling, including its schema field.
    template = json.loads(
        TaskService(tmp_path)
        .freeze(
            {
                "kind": "replay",
                "source_task": "a" * 8
                + "-"
                + "a" * 4
                + "-"
                + "a" * 4
                + "-"
                + "a" * 4
                + "-"
                + "a" * 12,
            }
        )
        .raw
    )
    template["payload"]["source_task"] = "$SOURCE_TASK"
    plan["slots"][1]["request_template"] = template
    fixed = install_execution_plan(tmp_path, plan, identity)
    driver = open_protocol_driver(tmp_path, fixed, identity)
    advance_actor(driver, -1)
    first = TaskService(tmp_path)
    task = first.submit(source_request, "source")["task_id"]
    result = first.work(task)
    assert result["status"] == "SUCCEEDED", result
    path = tmp_path / "tasks" / task / "request.json"
    complete_actor(
        driver,
        {
            "owner_id": task,
            "status": "SUCCEEDED",
            "evidence": [
                {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            ],
        },
    )
    advance_actor(driver, 0)
    second = TaskService(tmp_path)
    replay = second.submit(second.freeze({"kind": "replay", "source_task": task}), "cancel")[
        "task_id"
    ]
    assert second.state.slots(replay) == {}
    binding = first.state.slots(task)["B"]["binding"]
    transaction_root = (
        Path(binding["physical_ledger_root"]) / binding["child_run_id"] / "transactions"
    )
    target = sorted(transaction_root.glob("commit-*.json"))[-1]
    original = target.read_bytes()
    target.write_bytes(original + b" ")
    with pytest.raises(ContractError, match="TASK_CANCEL_SOURCE_UNVERIFIED"):
        second.cancel(replay)
    assert second.state.get(replay)["status"] == "QUEUED"
    assert target.read_bytes() == original + b" "
    target.write_bytes(original)
    assert second.cancel(replay) == "CANCELLED"
    assert second.status(replay)["status"] == "CANCELLED"
    target.write_bytes(original + b" ")
    public = second.status(replay)
    assert public["status"] == "INTEGRITY_ERROR" and public["usable"] is False
    assert public["financial_verification_error"] == "TASK_CANCEL_SOURCE_UNVERIFIED"
    assert second.state.get(replay)["status"] == "CANCELLED"
    target.write_bytes(original)
    assert second.status(replay)["status"] == "CANCELLED"
    assert not (tmp_path / "replay-runs").exists()
