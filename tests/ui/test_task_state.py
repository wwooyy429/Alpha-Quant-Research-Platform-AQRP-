"""Real SQLite transactions/process concurrency and immutable request/default revisions."""

import json
import subprocess
import sys

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.services.task_state import TaskState


def test_allocate_same_key_and_conflicting_config(tmp_path):
    s = TaskState(tmp_path)
    raw = canonical({"kind": "research"})
    a = s.submit(raw, "key")
    assert s.submit(raw, "key") == a
    with pytest.raises(ContractError, match="IDEMPOTENCY_CONFIG_CONFLICT"):
        s.submit(canonical({"kind": "replay"}), "key")
    assert (tmp_path / "tasks" / a / "request.json").read_bytes() == raw
    assert s.get(a)["status"] == "QUEUED"
    with pytest.raises(ContractError, match="UNKNOWN_TASK"):
        s.get("unknown")
    for key in [None, "", False, "x" * 129]:
        with pytest.raises(ContractError, match="INVALID_IDEMPOTENCY_KEY"):
            s.submit(raw, key)


def test_claim_release_epoch_cancel_and_no_pid_takeover(tmp_path):
    s = TaskState(tmp_path)
    t = s.submit(canonical({"kind": "research"}), "k")
    owner, epoch = s.claim(t)
    with pytest.raises(ContractError, match="TASK_ALREADY_CLAIMED"):
        s.claim(t, recover=True)
    with pytest.raises(ContractError, match="STALE_TASK_CLAIM"):
        s.abandon(t, "wrong", epoch)
    s.abandon(t, owner, epoch)
    with pytest.raises(ContractError, match="TASK_RECOVERY_REQUIRED"):
        s.claim(t)
    next_owner, next_epoch = s.claim(t, recover=True)
    assert next_epoch == epoch + 1 and next_owner != owner
    assert s.cancel(t) == "CANCEL_REQUESTED"
    s.abandon(t, next_owner, next_epoch)
    other = s.submit(canonical({"kind": "research"}), "other")
    assert s.cancel(other) == "CANCELLED"
    assert s.cancel(other) == "TOO_LATE"
    with pytest.raises(ContractError, match="TASK_NOT_CLAIMABLE"):
        s.claim(other)
    with pytest.raises(ContractError, match="UNKNOWN_TASK"):
        s.cancel("missing")
    with pytest.raises(ContractError, match="TASK_NOT_CLAIMABLE"):
        s.claim("missing")
    with pytest.raises(ContractError, match="STALE_TASK_CLAIM"):
        s.abandon("missing", "wrong", 1)


def test_cas_defaults_history_and_rollback_add_revision(tmp_path):
    s = TaskState(tmp_path)
    assert s.defaults()["revision"] == 0
    assert s.save_defaults(0, {"fee_budget": "10"}) == 1
    with pytest.raises(ContractError, match="DEFAULTS_REVISION_CONFLICT"):
        s.save_defaults(0, {})
    assert s.save_defaults(1, {"fee_budget": "20"}) == 2
    assert s.rollback_defaults(2, 1) == 3
    assert json.loads(s.defaults()["payload"]) == {"fee_budget": "10"}
    with s.transaction() as c:
        assert [r[0] for r in c.execute("SELECT payload FROM defaults ORDER BY revision")] == [
            '{"fee_budget":"10"}',
            '{"fee_budget":"20"}',
            '{"fee_budget":"10"}',
        ]
    with pytest.raises(ContractError, match="UNKNOWN_DEFAULTS_REVISION"):
        s.rollback_defaults(3, 99)


def test_ten_real_processes_allocate_one_task_and_one_workspace(tmp_path):
    source = "from aqrp.services.task_state import TaskState; from aqrp.core.canonical import canonical; import sys,json; s=TaskState(sys.argv[1]); print(json.dumps([s.workspace_id,s.submit(canonical({'kind':'research'}),'same-key')]))"
    processes = [
        subprocess.Popen(
            [sys.executable, "-I", "-c", source, str(tmp_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(10)
    ]
    outputs = []
    for index, p in enumerate(processes):
        out, err = p.communicate(timeout=90)
        (tmp_path / f"process-{index}.stdout.log").write_bytes(out)
        (tmp_path / f"process-{index}.stderr.log").write_bytes(err)
        assert p.returncode == 0, err.decode()
        outputs.append(tuple(json.loads(out)))
    assert len(set(outputs)) == 1
    with TaskState(tmp_path).transaction() as c:
        assert c.execute("SELECT count(*) FROM tasks").fetchone()[0] == 1
        assert c.execute("SELECT count(*) FROM workspace").fetchone()[0] == 1
