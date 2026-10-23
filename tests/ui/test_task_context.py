"""Trust, pre-call ownership and stale-claim negative controls on real SQLite."""

import json
import uuid

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.factors.admission import bundle_hash
from aqrp.services.task_context import TaskAuthority, TaskRunContext, authority, require_context
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService


@pytest.fixture(scope="module")
def root(tmp_path_factory):
    p = tmp_path_factory.mktemp("context-controls")
    initialize(p, "a" * 40)
    return p


@pytest.fixture
def claimed(root):
    s = TaskService(root)
    t = s.submit(s.freeze({"kind": "research"}), str(uuid.uuid4()))["task_id"]
    owner, epoch = s.state.claim(t)
    return s, t, authority(s.state, t, owner, epoch)


def test_non_launcher_objects_and_constructor_seals_refused(claimed):
    s, t, auth = claimed
    with pytest.raises(ContractError, match="TRUSTED_TASK_LAUNCHER_REQUIRED"):
        TaskAuthority(s.state, t, auth.owner, auth.epoch, seal=object())
    with pytest.raises(ContractError, match="TRUSTED_TASK_CONTEXT_REQUIRED"):
        TaskRunContext(auth, "R", seal=object())
    for obj in (None, {}, object(), auth):
        with pytest.raises(ContractError, match="TRUSTED_TASK_CONTEXT_REQUIRED"):
            require_context(obj)
    with pytest.raises(ContractError, match="UNREGISTERED_TASK_SLOT"):
        auth.context("R")
    c = auth.allocate("R", "P3", root=s.root / "research-runs")
    assert require_context(c) is c and c.existing() is None


@pytest.mark.parametrize(
    "slot,service", [("R", "P5"), ("B", "P3"), ("Z", "P3"), ("E", "P5_REPLAY"), ("B", "P5")]
)
def test_schema_and_task_kind_mismatch(claimed, slot, service):
    s, _, auth = claimed
    with pytest.raises(ContractError):
        auth.allocate(slot, service, s.root / "research-runs")


def test_wrong_physical_root_and_request_bytes_fail_closed(claimed, tmp_path):
    s, t, auth = claimed
    with pytest.raises(ContractError, match="TASK_SLOT_ROOT_OR_KIND_MISMATCH"):
        auth.allocate("R", "P3", tmp_path)
    p = s.root / "tasks" / t / "request.json"
    original = p.read_bytes()
    try:
        p.write_bytes(original + b" ")
        with pytest.raises(ContractError, match="TASK_REQUEST_IDENTITY_CHANGED"):
            auth.check()
        with pytest.raises(ContractError, match="TASK_REQUEST_IDENTITY_CHANGED"):
            s.status(t)
        assert any(x["task_id"] == t and x["status"] == "INTEGRITY_ERROR" for x in s.list())
    finally:
        p.write_bytes(original)


def test_recovery_epoch_invalidates_old_context_and_cancel_is_intent(claimed):
    s, t, old = claimed
    old.allocate("R", "P3", s.root / "research-runs")
    s.state.abandon(t, old.owner, old.epoch)
    owner, epoch = s.state.claim(t, recover=True)
    assert epoch == old.epoch + 1
    with pytest.raises(ContractError, match="STALE_TASK_CLAIM"):
        old.check()
    new = authority(s.state, t, owner, epoch)
    c = new.allocate("R", "P3", s.root / "research-runs")
    assert s.cancel(t) == "CANCEL_REQUESTED"
    assert s.state.get(t)["status"] == "RUNNING"
    with pytest.raises(KeyboardInterrupt, match="TASK_SAFE_CANCEL_CHECKPOINT"):
        c.checkpoint()


def test_initial_binding_and_single_start_intent(claimed):
    s, t, auth = claimed
    ctx = auth.allocate("R", "P3", s.root / "research-runs")
    assert auth.allocate("R", "P3", s.root / "research-runs").binding() == ctx.binding()
    cfg = json.loads(s.state.get(t)["raw"])["payload"]["research"]
    line = {"code_commit": "a" * 40, "code_bundle": bundle_hash()}
    with pytest.raises(ContractError, match="TASK_PLANNED_RESEARCH_CHANGED"):
        ctx.start(s.root / "research-runs", {**cfg, "seed": 999}, line)
    with pytest.raises(ContractError, match="TASK_CORE_IDENTITY_MISMATCH"):
        ctx.start(s.root / "research-runs", cfg, {**line, "code_commit": "b" * 40})
    run, bound = ctx.start(s.root / "research-runs", cfg, line)
    assert bound["task_binding_hash"] == digest(bound["task_binding"])
    assert run == ctx.binding()["child_run_id"]
    with pytest.raises(ContractError, match="TASK_SLOT_ALREADY_STARTED"):
        ctx.start(s.root / "research-runs", cfg, line)
    with pytest.raises(ContractError, match="RECOVERY_REQUIRED"):
        ctx.existing()
    with pytest.raises(ContractError, match="TASK_CORE_OWNERSHIP_MISMATCH"):
        ctx.verify(s.root, run)
    with pytest.raises(ContractError, match="TASK_CORE_OWNERSHIP_MISMATCH"):
        ctx.verify(s.root / "research-runs", str(uuid.uuid4()))


def test_unregistered_directory_is_not_a_prior_run(claimed):
    s, _, auth = claimed
    ctx = auth.allocate("R", "P3", s.root / "research-runs")
    directory = s.root / "research-runs" / ctx.binding()["child_run_id"]
    directory.mkdir(parents=True)
    with pytest.raises(ContractError, match="TASK_UNREGISTERED_CORE_DIRECTORY"):
        ctx.existing()


@pytest.mark.parametrize("index", [None, True, -1, "0"])
def test_p4_child_requires_own_exact_execution_parent(claimed, index):
    s, _, auth = claimed
    r = auth.allocate("R", "P3", s.root / "research-runs")
    with pytest.raises(ContractError, match="TASK_SLOT_SCHEMA_MISMATCH"):
        auth.allocate(f"P:{index}", "P4", s.root, parent=r, index=index)


def test_existing_binding_cannot_change_non_config_identity(claimed):
    s, t, auth = claimed
    ctx = auth.allocate("R", "P3", s.root / "research-runs")
    b = ctx.binding()
    b["code_sha"] = "f" * 40
    with s.state.transaction() as c:
        c.execute(
            "UPDATE slots SET binding=? WHERE task=? AND slot='R'", (canonical(b).decode(), t)
        )
    with pytest.raises(ContractError, match="TASK_SLOT_BINDING_CONFLICT"):
        auth.allocate("R", "P3", s.root / "research-runs")
