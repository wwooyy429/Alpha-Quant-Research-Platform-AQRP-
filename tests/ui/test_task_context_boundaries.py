"""Negative pre-call guards use actual frozen plans and completed core artifacts."""

import json
import uuid
from contextlib import contextmanager
from pathlib import Path

import pytest
from test_task_proofs import completed as completed
from test_task_proofs import reseal

from aqrp.backtest.contracts import EngineeringBacktestRequest
from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import PortfolioRequest
from aqrp.services.task_context import authority


@contextmanager
def active(service, task):
    old = service.state.get(task)
    owner = str(uuid.uuid4())
    with service.state.transaction() as c:
        c.execute(
            "UPDATE tasks SET status='RUNNING',owner=?,epoch=epoch+1 WHERE id=?", (owner, task)
        )
    try:
        yield authority(service.state, task, owner, old["epoch"] + 1)
    finally:
        with service.state.transaction() as c:
            c.execute(
                "UPDATE tasks SET status=?,owner=?,epoch=? WHERE id=?",
                (old["status"], old["owner"], old["epoch"], task),
            )


def test_p4_wrong_parent_and_incompatible_existing_context(completed):
    s, t, _ = completed
    with active(s, t) as auth:
        r = auth.context("R")
        with pytest.raises(ContractError, match="TASK_SLOT_SCHEMA_MISMATCH"):
            auth.allocate("P:0", "P4", s.root, parent=r, index=0)
        auth.context("B").checkpoint()


@pytest.mark.parametrize("target", ["P3", "P5", "P4"])
def test_changed_planned_core_request_is_rejected_before_start(completed, target):
    s, t, r = completed
    slot = {"P3": "R", "P5": "B", "P4": "P:0"}[target]
    binding = r["slots"][slot]["binding"]
    root = Path(binding["physical_ledger_root"]) / binding["child_run_id"]
    config = json.loads((root / "config.json").read_bytes())
    if target == "P3":
        config["seed"] = 99
    elif target == "P5":
        config["raw_request_hex"] = "00"
    else:
        config["request_sha256"] = "0" * 64
    line = {"code_commit": "a" * 40, "code_bundle": binding["code_bundle"]}
    with active(s, t) as auth:
        with pytest.raises(ContractError, match="TASK_PLANNED"):
            auth.context(slot).start(root.parent, config, line)


@pytest.mark.parametrize("change", ["time", "request", "raw-record"])
def test_actual_nested_adapted_request_time_and_raw_bytes_are_bound(completed, change):
    s, t, r = completed
    with s.state.transaction() as c:
        old = tuple(
            c.execute(
                "SELECT task,slot,raw,hash FROM adapted_requests WHERE task=?", (t,)
            ).fetchone()
        )
    raw = json.loads(old[2])
    if change == "time":
        raw["context"]["decision_time"] = "2024-01-07T16:00:00+00:00"
    if change == "request":
        raw["policy"]["top_k"] = 2
    if change == "raw-record":
        with s.state.transaction() as c:
            c.execute("UPDATE adapted_requests SET raw=raw||' ' WHERE task=?", (t,))
    try:
        with active(s, t) as auth:
            parent = auth.context("B")
            with pytest.raises(ContractError):
                parent.child(
                    0,
                    PortfolioRequest(canonical(raw)),
                    r["slots"]["P:0"]["binding"]["physical_ledger_root"],
                )
    finally:
        with s.state.transaction() as c:
            c.execute(
                "UPDATE adapted_requests SET raw=?,hash=? WHERE task=? AND slot=?",
                (old[2], old[3], t, "P:0"),
            )


@pytest.mark.parametrize("change", ["duplicate", "alias", "initial-record", "result-membership"])
def test_context_verification_checks_terminal_membership_and_initial_record(completed, change):
    s, t, r = completed
    b = r["slots"]["R"]["binding"]
    mutation = {
        "duplicate": lambda m: m["files"].append(dict(m["files"][0])),
        "alias": lambda m: m["files"].append(
            {**m["files"][0], "path": "./" + m["files"][0]["path"]}
        ),
        "result-membership": lambda m: m["files"].__setitem__(
            slice(None), [e for e in m["files"] if e["path"] != "report.json"]
        ),
    }.get(change)
    changes = (
        {"lineage.json": lambda x: x.update(extra_unbound_value="changed")}
        if change == "initial-record"
        else None
    )
    with active(s, t) as auth, reseal(b, mutation, changes):
        with pytest.raises(ContractError):
            auth.context("R").existing()


def test_replay_start_must_match_original_frozen_execution_request(completed):
    s, t, r = completed
    replay = s.submit(s.freeze({"kind": "replay", "source_task": t}), "replay-plan-control")[
        "task_id"
    ]
    owner, epoch = s.state.claim(replay)
    auth = authority(s.state, replay, owner, epoch)
    e = auth.allocate("E", "P5_REPLAY", s.root / "replay-runs")
    b = r["slots"]["B"]["binding"]
    config = json.loads(
        (Path(b["physical_ledger_root"]) / b["child_run_id"] / "config.json").read_bytes()
    )
    s._plan(auth, e, EngineeringBacktestRequest(bytes.fromhex(config["raw_request_hex"])))
    with pytest.raises(ContractError, match="TASK_PLANNED_REPLAY_CHANGED"):
        e.start(
            s.root / "replay-runs",
            {"request_sha256": "0" * 64},
            {"code_commit": "a" * 40, "code_bundle": b["code_bundle"]},
        )
