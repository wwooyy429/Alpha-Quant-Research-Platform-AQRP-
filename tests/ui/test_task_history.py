"""Actually execute the accepted old package/lock/Refs; host reproduction is not claimed."""

import json
import os
import shutil
import uuid
from pathlib import Path

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.services.task_context import authority
from aqrp.services.task_history import execute_history, history_catalogue, register_history
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService


@pytest.fixture(scope="module")
def history_workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("task-history")
    initialize(root, "a" * 40)
    archive_path = os.environ.get("AQRP_ORIGINAL_ENV_ARCHIVE")
    assert archive_path, (
        "Original environment archive is required, not a skipped history capability"
    )
    archive = json.loads(Path(archive_path).read_bytes())
    publication = Path(__file__).resolve().parents[2] / "docs/audits/phase-2/publication"
    register_history(root, archive, publication)
    return root, archive, publication


def test_real_old_ref_execution_and_completion_recovery(history_workspace):
    root, archive, publication = history_workspace
    history = history_catalogue(root)
    assert register_history(root, archive, publication) == history
    assert history["full_historical_host_verified"] is False
    s = TaskService(root)
    request = s.freeze(
        {
            "kind": "replay",
            "source_task": "published-original",
            "profile": "PUBLISHED_REF_PROJECTION",
        }
    )
    t = s.submit(request, "old-ref")["task_id"]
    actual = s.work(t)
    assert actual["status"] == "SUCCEEDED", actual
    out = json.loads(s.artifact(t, "E", "result.json"))
    assert out["status"] == "ALL_ORIGINAL_BYTES_VERIFIED_AND_THREE_RUNS_REPLAYED"
    assert len(out["runs"]) == 3
    assert all(x["status"] == "DECLARED_PROJECTION_MATCH" for x in out["runs"])
    assert len(actual["slots"]) == 1
    assert actual["result"]["full_historical_host_verified"] is False
    assert s.compare(t, t)["numeric_equal"]
    old = s.state.get(t)
    owner = str(uuid.uuid4())
    with s.state.transaction() as c:
        c.execute("UPDATE tasks SET owner=?,epoch=epoch+1,status='RUNNING' WHERE id=?", (owner, t))
    auth = authority(s.state, t, owner, old["epoch"] + 1)
    plan = root / "tasks" / t / "resolved-plan.json"
    original = plan.read_bytes()
    try:
        reused = execute_history(s, auth, json.loads(request.raw))
        assert (
            reused["historical_replay"]["manifest"]
            == actual["result"]["historical_replay"]["manifest"]
        )
        value = json.loads(original)
        value["decision_count"] = 1
        plan.write_bytes(canonical(value))
        with pytest.raises(ContractError, match="TASK_RESOLVED_PLAN_CHANGED"):
            execute_history(s, auth, json.loads(request.raw))
        wrong = json.loads(request.raw)
        wrong["payload"]["history_sha256"] = "0" * 64
        with pytest.raises(ContractError, match="HISTORICAL_CATALOG_CHANGED"):
            execute_history(s, auth, wrong)
    finally:
        plan.write_bytes(original)
        with s.state.transaction() as c:
            c.execute(
                "UPDATE tasks SET owner=?,epoch=?,status=? WHERE id=?",
                (old["owner"], old["epoch"], old["status"], t),
            )


@pytest.mark.parametrize("change", ["id", "profile", "hash", "archive", "manifest", "member"])
def test_history_current_bytes_are_reverified_without_mutating_original(
    history_workspace, tmp_path, change
):
    root, _, publication = history_workspace
    value = history_catalogue(root)
    own = tmp_path / "workspace"
    own.mkdir()
    if change in ("id", "profile", "hash"):
        key = {"id": "id", "profile": "profile", "hash": "publication_manifest_sha256"}[change]
        value[key] = "changed"
    elif change == "archive":
        copy = tmp_path / "old.whl"
        shutil.copy2(value["archive"]["wheel"], copy)
        value["archive"]["wheel"] = str(copy)
        copy.write_bytes(copy.read_bytes() + b" ")
    else:
        copy = tmp_path / "publication"
        shutil.copytree(publication, copy)
        value["publication_root"] = str(copy)
        target = copy / "FILE_MANIFEST.json"
        if change == "member":
            first = json.loads(target.read_bytes())["files"][0]["path"]
            target = copy / first
        target.write_bytes(target.read_bytes() + b" ")
    (own / "history.json").write_bytes(canonical(value))
    with pytest.raises(ContractError):
        history_catalogue(own)


def test_history_registration_rejects_changed_declaration(history_workspace, tmp_path):
    _, archive, publication = history_workspace
    with pytest.raises(ContractError, match="HISTORICAL_ENVIRONMENT_CHANGED"):
        register_history(tmp_path, {**archive, "wheel_hash": "0" * 64}, publication)
    copy = tmp_path / "publication"
    shutil.copytree(publication, copy)
    (copy / "FILE_MANIFEST.json").write_bytes(b"{}")
    with pytest.raises(ContractError, match="ORIGINAL_PUBLICATION_MANIFEST_CHANGED"):
        register_history(tmp_path, archive, copy)
    changed = tmp_path / "other"
    changed.mkdir()
    (changed / "history.json").write_text("{}")
    with pytest.raises(ContractError, match="HISTORICAL_CATALOG_IMMUTABLE"):
        register_history(changed, archive, publication)


def test_historical_replay_rejects_unknown_id(history_workspace):
    root, _, _ = history_workspace
    with pytest.raises(ContractError, match="HISTORICAL_CATALOG_CHANGED"):
        TaskService(root).freeze(
            {"kind": "replay", "source_task": "other", "profile": "PUBLISHED_REF_PROJECTION"}
        )
    assert digest(history_catalogue(root))


def test_history_core_start_hash_must_match_frozen_catalogue(history_workspace):
    root, _, _ = history_workspace
    s = TaskService(root)
    frozen = s.freeze(
        {
            "kind": "replay",
            "profile": "PUBLISHED_REF_PROJECTION",
            "source_task": "published-original",
        }
    )
    t = s.submit(frozen, "wrong-history-start")["task_id"]
    owner, epoch = s.state.claim(t)
    ctx = authority(s.state, t, owner, epoch).allocate(
        "E", "PUBLISHED_REF_PROJECTION", root / "replay-runs"
    )
    with pytest.raises(ContractError, match="TASK_PLANNED_REPLAY_CHANGED"):
        ctx.start(root / "replay-runs", {"registered_history_sha256": "0" * 64}, {})
