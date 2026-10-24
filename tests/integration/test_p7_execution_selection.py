"""Actual P3 remains complete; fixed P5/P4 subset and replay retain its identity."""

import json
from copy import deepcopy

from aqrp.core.canonical import canonical
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService

DRAFT = {
    "kind": "engineering_pipeline",
    "factor_ids": ["momentum"],
    "lookback": 2,
    "horizons": [1],
    "start": "2024-01-04",
    "end": "2024-01-08",
    "execution_sessions": ["2024-01-04", "2024-01-06", "2024-01-08"],
    "initial_cash": "1000",
    "fee_budget": "50",
    "policy": {"mode": "LONG_SHORT", "gross": "0.5", "net": "0.5"},
}


def test_real_research_complete_selected_p4_set_and_replay_binding(tmp_path):
    initialize(tmp_path, "a" * 40)
    service = TaskService(tmp_path)
    frozen = service.freeze(DRAFT)
    request = json.loads(frozen.raw)
    assert len(request["payload"]["research"]["decisions"]) == 5
    submitted = service.submit(frozen, "selected-pipeline")
    done = service.work(submitted["task_id"])
    assert done["status"] == "SUCCEEDED", done
    task = done["task_id"]
    plan_path = tmp_path / "tasks" / task / "resolved-plan.json"
    original = plan_path.read_bytes()
    plan = json.loads(original)
    assert plan["decision_count"] == 3
    assert [r["research_ordinal"] for r in plan["execution_selection"]["resolved"]] == [0, 2, 4]
    assert set(done["slots"]) == {"R", "B", "P:0", "P:1", "P:2"}
    full_research = json.loads(service.artifact(task, "R", "config.json"))
    assert full_research == request["payload"]["research"]
    assert len(full_research["decisions"]) == 5
    assert {
        r["session"] for r in json.loads(service.artifact(task, "R", "final.json"))["rows"]
    } == {"2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07", "2024-01-08"}
    tampered = deepcopy(plan)
    tampered["execution_selection"]["resolved"][1]["research_ordinal"] = 1
    plan_path.write_bytes(canonical(tampered))
    assert service.status(task)["status"] == "INTEGRITY_ERROR"
    plan_path.write_bytes(original)
    assert service.status(task)["status"] == "SUCCEEDED"
    replay = service.submit(
        service.freeze({"kind": "replay", "source_task": task}), "selected-replay"
    )
    replayed = service.work(replay["task_id"])
    assert replayed["status"] == "SUCCEEDED", replayed
    replay_plan = json.loads(
        (tmp_path / "tasks" / replay["task_id"] / "resolved-plan.json").read_bytes()
    )
    assert replay_plan["execution_selection"] == plan["execution_selection"]
    assert replay_plan["request_sha256"] == plan["request_sha256"]
    assert set(replayed["slots"]) == {"E", "P:0", "P:1", "P:2"}
    assert service.compare(task, replay["task_id"])["numeric_equal"] is True


def test_all_research_decisions_default_keeps_original_request_without_selection_field(tmp_path):
    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    draft = {k: v for k, v in DRAFT.items() if k != "execution_sessions"}
    first = s.freeze(draft)
    assert "selection" not in json.loads(first.raw)["payload"]["execution"]
    assert first.raw == s.freeze(draft).raw
    explicit_all = s.freeze(
        {**draft, "execution_sessions": [f"2024-01-{i:02d}" for i in range(4, 9)]}
    )
    assert explicit_all.config_hash != first.config_hash
    assert (
        json.loads(explicit_all.raw)["payload"]["research"]
        == json.loads(first.raw)["payload"]["research"]
    )
