"""Resealed-but-invalid terminal artifacts must still fail ownership/completion gates."""

import hashlib
import json
from contextlib import contextmanager
from pathlib import Path

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService, read_core


@pytest.fixture(scope="module")
def completed(tmp_path_factory):
    root = tmp_path_factory.mktemp("proof-controls")
    initialize(root, "a" * 40)
    s = TaskService(root)
    t = s.submit(
        s.freeze(
            {
                "kind": "engineering_pipeline",
                "start": "2024-01-06",
                "end": "2024-01-06",
                "horizons": [1],
            }
        ),
        "proof-controls",
    )["task_id"]
    r = s.work(t)
    assert r["status"] == "SUCCEEDED", r
    return s, t, r


@contextmanager
def reseal(binding, mutate_manifest=None, changes=None):
    root = Path(binding["physical_ledger_root"]) / binding["child_run_id"]
    originals = {
        p: p.read_bytes() for p in root.iterdir() if p.suffix in (".json", ".jsonl", ".html")
    }
    try:
        m = json.loads((root / "manifest.json").read_bytes())
        for name, change in (changes or {}).items():
            p = root / name
            x = json.loads(p.read_bytes())
            change(x)
            p.write_bytes(canonical(x))
        for entry in m["files"]:
            entry["sha256"] = hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest()
        if mutate_manifest:
            mutate_manifest(m)
        raw = canonical(m)
        (root / "manifest.json").write_bytes(raw)
        lines = (root / "events.jsonl").read_bytes().splitlines()
        end = json.loads(lines[-1])
        end["payload"]["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
        end["hash"] = digest({k: v for k, v in end.items() if k != "hash"})
        (root / "events.jsonl").write_bytes(b"\n".join([*lines[:-1], canonical(end)]) + b"\n")
        yield root
    finally:
        for p, raw in originals.items():
            p.write_bytes(raw)


@pytest.mark.parametrize("case", ["missing", "duplicate", "alias", "report", "lineage", "config"])
def test_resealed_research_artifacts_do_not_bypass_contract(completed, case):
    s, _, r = completed
    b = r["slots"]["R"]["binding"]
    mutations = {
        "missing": lambda m: m["files"].__setitem__(
            slice(None), [e for e in m["files"] if e["path"] != "metrics.json"]
        ),
        "duplicate": lambda m: m["files"].append(dict(m["files"][0])),
        "alias": lambda m: m["files"].append(
            {**next(e for e in m["files"] if e["path"] == "config.json"), "path": "./config.json"}
        ),
    }
    changes = {
        "report": {"report.json": lambda x: x.update(financial_approval="YES")},
        "lineage": {"lineage.json": lambda x: x.update(task_binding_hash="0" * 64)},
        "config": {"config.json": lambda x: x.update(seed=42)},
    }
    with reseal(b, mutations.get(case), changes.get(case)):
        with pytest.raises(ContractError):
            read_core(b)


@pytest.mark.parametrize("key", ["task_config_hash", "request_sha256", "slots", "decision_count"])
def test_frozen_execution_plan_cannot_be_changed(completed, key):
    s, t, _ = completed
    path = s.root / "tasks" / t / "resolved-plan.json"
    raw = path.read_bytes()
    x = json.loads(raw)
    x[key] = {} if key == "slots" else (0 if key == "decision_count" else "0" * 64)
    try:
        path.write_bytes(canonical(x))
        with pytest.raises((ContractError, KeyError, ValueError)):
            s._proofs(t)
    finally:
        path.write_bytes(raw)


@pytest.mark.parametrize(
    "target",
    [
        "adapted-missing",
        "adapted-raw",
        "transaction-files",
        "no-initial",
        "lineage-result",
        "lineage-missing",
        "financial",
        "financial-unknown",
    ],
)
def test_independent_completion_barrier_checks_actual_nested_inputs_and_finances(completed, target):
    s, t, r = completed
    b = r["slots"]["B"]["binding"]
    root = Path(b["physical_ledger_root"]) / b["child_run_id"]
    if target.startswith("adapted"):
        with s.state.transaction() as c:
            old = tuple(
                c.execute(
                    "SELECT task,slot,raw,hash FROM adapted_requests WHERE task=?", (t,)
                ).fetchone()
            )
            c.execute("DELETE FROM adapted_requests WHERE task=?", (t,))
            if target == "adapted-raw":
                c.execute(
                    "INSERT INTO adapted_requests VALUES (?,?,?,?)",
                    (old[0], old[1], old[2] + " ", old[3]),
                )
        try:
            with pytest.raises(ContractError, match="TASK_ADAPTED_REQUEST_CHANGED"):
                s._proofs(t)
        finally:
            with s.state.transaction() as c:
                c.execute("DELETE FROM adapted_requests WHERE task=?", (t,))
                c.execute("INSERT INTO adapted_requests VALUES (?,?,?,?)", old)
    elif target == "no-initial":
        p = root / "transactions/initial.json"
        raw = p.read_bytes()
        p.unlink()
        try:
            with pytest.raises(ContractError, match="TASK_TRANSACTION_FILES_MISSING"):
                s._proofs(t)
            with pytest.raises(ContractError, match="TASK_TRANSACTION_FILES_MISSING"):
                s.financial_result(t)
        finally:
            p.write_bytes(raw)
    else:
        changes = {
            "transaction-files": {"transaction-files.json": lambda x: x.clear()},
            "lineage-missing": {"portfolio-lineage.json": lambda x: x.clear()},
            "financial": {"result.json": lambda x: x["account"].update(cash_total="99.1")},
            "financial-unknown": {"result.json": lambda x: x.update(status="FAILED")},
            "lineage-result": {
                "portfolio-lineage.json": lambda x: x[0]["result"].update(
                    run_id="00000000-0000-0000-0000-000000000001"
                )
            },
        }
        with reseal(b, changes=changes[target]):
            with pytest.raises(ContractError):
                s._proofs(t)
            if target == "transaction-files":
                with pytest.raises(ContractError, match="TASK_FINANCIAL_RESULT_CHANGED"):
                    s.financial_result(t)


def test_service_metadata_and_unknown_task_refusals(completed):
    s, t, r = completed
    assert s.request(t)["kind"] == "engineering_pipeline"
    assert s.defaults()["revision"] == 0
    assert s.artifact_catalogue(t, "B")["status"] == "SUCCEEDED"
    with pytest.raises(ContractError, match="UNKNOWN_TASK_SLOT"):
        s.artifact_catalogue(t, "X")
    with pytest.raises(FileNotFoundError):
        s.worker_log(t)
    path = s.root / "tasks" / t / "worker.log"
    path.write_bytes(b"captured diagnostic prefix")
    assert s.worker_log(t) == b"captured diagnostic prefix"
    assert s.save_defaults(0, {"lookback": 3}) == 1
    assert s.rollback_defaults(1, 1) == 2
    pending = s.submit(s.freeze({"kind": "research"}), "no-b")
    with pytest.raises(ContractError, match="NO_BACKTEST_STAGE"):
        s.financial_result(pending["task_id"])
    with pytest.raises(ContractError, match="TASK_REQUIRED_SLOT_SET_MISMATCH"):
        s._proofs(pending["task_id"])
    s.cancel(pending["task_id"])


def test_original_bytes_changed_after_manifest_verification_are_not_accepted(
    completed, monkeypatch
):
    from aqrp.experiments.ledger import ExperimentLedger

    s, _, r = completed
    b = r["slots"]["R"]["binding"]
    path = Path(b["physical_ledger_root"]) / b["child_run_id"] / "metrics.json"
    original = path.read_bytes()
    verify = ExperimentLedger.verify

    def race(self, run):
        m = verify(self, run)
        if run == b["child_run_id"]:
            path.write_bytes(original + b" ")
        return m

    monkeypatch.setattr(ExperimentLedger, "verify", race)
    try:
        with pytest.raises(ContractError, match="TASK_CORE_ARTIFACT_CHANGED"):
            read_core(b)
    finally:
        path.write_bytes(original)


def test_invalid_completion_pointer_never_resolves_outside_task(completed):
    s, t, _ = completed
    old = s.state.get(t)["completion"]
    try:
        with s.state.transaction() as c:
            c.execute(
                "UPDATE tasks SET completion=? WHERE id=?",
                (json.dumps({"file": "../completion.json", "sha256": "0" * 64}), t),
            )
        assert s.status(t)["status"] == "INTEGRITY_ERROR"
    finally:
        with s.state.transaction() as c:
            c.execute("UPDATE tasks SET completion=? WHERE id=?", (old, t))


def test_explicit_unknown_flag_cannot_be_published_as_success(completed):
    s, t, r = completed
    with reseal(
        r["slots"]["B"]["binding"],
        changes={
            "result.json": lambda x: x.update(
                committed_state_verification={"financial_state_known": False}
            )
        },
    ):
        with pytest.raises(ContractError, match="TASK_FINANCIAL_RESULT_UNKNOWN"):
            s._proofs(t)
        with pytest.raises(ContractError, match="TASK_FINANCIAL_RESULT_UNKNOWN"):
            s.financial_result(t)
