"""Real managed entry points, one authority, no financial model substitutions."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from threading import Barrier

import pytest

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import BudgetAuthority
from aqrp.experiments.ledger import ExperimentLedger, read_chain
from aqrp.factors.admission import bundle_hash
from aqrp.services.research import hypotheses, research
from aqrp.services.task_requests import initialize, research_request
from aqrp.services.task_state import TaskState
from aqrp.services.tasks import TaskService

SINGLE = {"factor_ids": ["momentum"], "horizons": [1], "start": "2024-01-06", "end": "2024-01-06"}


def service(root):
    initialize(root, "a" * 40)
    s = TaskService(root)
    frozen = s.freeze(SINGLE)
    request = research_request(root, json.loads(frozen.raw))
    return s, frozen, request


def lineage(req):
    return {
        "code_commit": req.code_commit,
        "code_bundle": bundle_hash(),
        "data_hash": req.snapshot.manifest_hash,
        "exposure_hash": req.exposures.manifest_hash,
        "coverage_hash": req.coverage.checksum,
        "environment": {},
        "protocol_hash": digest(json.loads(req.config)),
        "permission_domain": "ENGINEERING_DEMO",
        "seed": 7,
        "admission_inputs": {
            "snapshot_root": str(req.snapshot.root),
            "exposure_root": str(req.exposures.root),
        },
    }


def history(root):
    b = BudgetAuthority(root)
    b.materialize()
    with b.transaction() as c:
        return b.history(c)


def cancel_tasks(s, frozen, n):
    for i in range(n):
        row = s.submit(frozen, "cancel-" + str(i))
        assert row["status"] == "QUEUED"
        assert s.cancel(row["task_id"]) == "CANCELLED"


def legacy_reserve(root, req):
    ledger = ExperimentLedger(root / "research-runs")
    run = ledger.start(json.loads(req.config), lineage(req))
    ledger.finish(run, "CANCELLED")
    return run


def test_twelve_cancelled_tasks_block_actual_public_legacy_before_factor_access(
    tmp_path, monkeypatch
):
    s, frozen, req = service(tmp_path)
    cancel_tasks(s, frozen, 12)
    from aqrp.factors.engine import FactorEngine

    monkeypatch.setattr(
        FactorEngine, "run", lambda *a, **k: pytest.fail("no factor access after refusal")
    )
    with pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
        research(req, tmp_path / "research-runs")
    from aqrp.services.cli import main

    old_cli_request = {
        "config": json.loads(req.config),
        "code_commit": req.code_commit,
        "snapshot": {**asdict(req.snapshot), "root": str(req.snapshot.root)},
        "exposures": {**asdict(req.exposures), "root": str(req.exposures.root)},
        "coverage": req.coverage.read(req.snapshot.manifest_hash),
    }
    old_cli_path = tmp_path / "frozen-legacy-probe.json"
    old_cli_path.write_text(json.dumps(old_cli_request), encoding="utf-8")
    with pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
        main([str(old_cli_path), "--output", str(tmp_path / "research-runs")])
    stats = history(tmp_path)
    assert (stats["admitted_units"], stats["requested_units"], stats["rejected_units"]) == (
        12,
        14,
        2,
    )
    assert stats["registered_trials"] == 0
    assert all(r["status"] == "CANCELLED" for r in s.list())


def test_legacy_first_reservations_include_pre_trial_cancellations_and_refuse_task(tmp_path):
    s, frozen, req = service(tmp_path)
    for _ in range(12):
        legacy_reserve(tmp_path, req)
    row = s.submit(frozen, "after-legacy")
    assert row["status"] == "FAILED" and row["error"] == "EXPERIMENT_BUDGET_EXCEEDED"
    assert row["research_control"]["prior_legacy_admission_units"] == 12
    assert row["research_control"]["prior_reserved_units"] == 12
    assert row["slots"] == {}
    assert history(tmp_path)["admitted_units"] == 12


@pytest.mark.parametrize("entry", ["public", "direct"])
def test_remaining_one_refuses_complete_two_hypothesis_set_atomically(tmp_path, entry):
    s, frozen, _ = service(tmp_path)
    s.register_campaign("two", [{**SINGLE, "horizons": [1, 2]}])
    double = s.freeze({**SINGLE, "horizons": [1, 2], "campaign_id": "two"})
    cancel_tasks(s, frozen, 11)
    req = research_request(tmp_path, json.loads(double.raw))
    with pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
        if entry == "public":
            research(req, tmp_path / "research-runs")
        else:
            legacy_reserve(tmp_path, req)
    stats = history(tmp_path)
    assert stats["admitted_units"] == 11 and stats["rejected_units"] == 2
    assert stats["registered_trials"] == 0


def test_real_task_child_claims_two_units_without_parent_double_debit(tmp_path):
    s, _, _ = service(tmp_path)
    frozen = s.freeze({**SINGLE, "horizons": [1, 2]})
    row = s.submit(frozen, "two-units")
    done = s.work(row["task_id"])
    assert done["status"] == "SUCCEEDED", done
    stats = history(tmp_path)
    assert stats["admitted_units"] == 2 and stats["registered_trials"] == 2
    trials = read_chain(tmp_path / "research-runs/trials.jsonl")
    assert len(trials) == 2 and all(
        t["payload"]["run_id"] == done["result"]["research_run_id"] for t in trials
    )


@pytest.mark.parametrize("relative", ["other", "other/research-runs", "outside"])
def test_managed_input_cannot_escape_to_another_output(tmp_path, relative):
    _, _, req = service(tmp_path / "W")
    target = tmp_path / relative if relative == "outside" else tmp_path / "W" / relative
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        research(req, target)
    assert history(tmp_path / "W")["admitted_units"] == 0


def test_task_and_legacy_mixed_concurrency_share_one_remaining_unit(tmp_path):
    s, frozen, req = service(tmp_path)
    cancel_tasks(s, frozen, 11)
    barrier = Barrier(2)

    def task():
        barrier.wait()
        return s.submit(frozen, "concurrent")["status"]

    def legacy():
        barrier.wait()
        try:
            legacy_reserve(tmp_path, req)
            return "QUEUED"
        except ContractError as exc:
            assert exc.code == "EXPERIMENT_BUDGET_EXCEEDED"
            return "FAILED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        left, right = pool.submit(task), pool.submit(legacy)
        states = [left.result(), right.result()]
    assert sorted(states) == ["FAILED", "QUEUED"]
    stats = history(tmp_path)
    assert stats["admitted_units"] == 12 and stats["rejected_units"] == 1


def test_concurrent_exact_task_retry_has_one_owner_and_one_debit(tmp_path):
    s, frozen, _ = service(tmp_path)
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(lambda _: s.submit(frozen, "same-owner"), range(12)))
    assert len({r["task_id"] for r in rows}) == 1
    stats = history(tmp_path)
    assert len(stats["admissions"]) == 1 and stats["admitted_units"] == 1


def test_concurrent_direct_registration_claims_once_and_keeps_exact_chain(tmp_path):
    _, _, req = service(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    cfg = json.loads(req.config)
    run = ledger.start(cfg, lineage(req))
    hypothesis = hypotheses(cfg)[0]["hypothesis"]
    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(
            pool.map(
                lambda _: ledger.register_trial(run, cfg["family"]["id"], hypothesis, budget=12),
                range(10),
            )
        )
    assert all(r == rows[0] for r in rows)
    assert len(read_chain(tmp_path / "research-runs/trials.jsonl")) == 1
    assert (
        len(
            [
                e
                for e in read_chain(ledger.path(run) / "events.jsonl")
                if e["kind"] == "TRIAL_REGISTERED"
            ]
        )
        == 1
    )
    stats = history(tmp_path)
    assert stats["admitted_units"] == 1 and stats["registered_trials"] == 1


def test_committed_outbox_failure_is_recovered_by_exact_retry_without_refund(tmp_path, monkeypatch):
    s, frozen, _ = service(tmp_path)
    original = s.state.budget.materialize
    calls = 0

    def fail_after_commit():
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated publication interruption")
        original()

    monkeypatch.setattr(s.state.budget, "materialize", fail_after_commit)
    with pytest.raises(OSError, match="publication interruption"):
        s.submit(frozen, "recover-original")
    with s.state.transaction() as c:
        assert c.execute("SELECT sum(debit) FROM admissions").fetchone()[0] == 1
        task = c.execute("SELECT id FROM tasks").fetchone()[0]
    assert not (tmp_path / "tasks" / task / "request.json").exists()
    monkeypatch.setattr(s.state.budget, "materialize", original)
    row = s.submit(frozen, "recover-original")
    assert row["task_id"] == task and row["status"] == "QUEUED"
    assert history(tmp_path)["admitted_units"] == 1


@pytest.mark.parametrize("damage", ["truncated", "foreign"])
def test_trial_corruption_fails_closed_and_original_bytes_are_preserved(tmp_path, damage):
    s, frozen, req = service(tmp_path)
    result = research(req, tmp_path / "research-runs")
    path = tmp_path / "research-runs/trials.jsonl"
    original = path.read_bytes()
    corrupted = original[:-1] if damage == "truncated" else original + original
    path.write_bytes(corrupted)
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        s.submit(frozen, "after-corruption")
    assert path.read_bytes() == corrupted
    assert result["manifest"]["status"] == "SUCCEEDED"


def test_forged_task_binding_without_context_cannot_borrow_reserved_unit(tmp_path):
    s, frozen, req = service(tmp_path)
    row = s.submit(frozen, "reserved-owner")
    ledger = ExperimentLedger(tmp_path / "research-runs")
    cfg, line = json.loads(req.config), lineage(req)
    line["task_binding"] = {"task_id": row["task_id"]}
    line["task_binding_hash"] = digest(line["task_binding"])
    run = ledger.start(cfg, line)
    with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
        ledger.register_trial(run, cfg["family"]["id"], hypotheses(cfg)[0]["hypothesis"], budget=12)
    stats = history(tmp_path)
    assert stats["admitted_units"] == 2 and stats["registered_trials"] == 0


def test_standalone_legacy_retains_original_non_twelve_family_budget(tmp_path):
    from aqrp.research.synthetic import synthetic_research
    from aqrp.services.research import ResearchRequest

    cfg, snapshot, exposure, coverage = synthetic_research(
        tmp_path / "unmanaged", sessions=24, assets=6
    )
    req = ResearchRequest.create(cfg, snapshot, exposure, coverage, "a" * 40)
    ledger = ExperimentLedger(tmp_path / "standalone")
    run = ledger.start({"x": 1}, {**lineage(req), "admission_inputs": {}})
    assert ledger.register_trial(run, "standalone-family", "one", budget=1)["over_budget"] is False
    with pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
        ledger.register_trial(run, "standalone-family", "two", budget=1)
    assert not (tmp_path / "task-control").exists()


def remove_authority_schema_for_frozen_legacy_fixture(s):
    """Explicit same-bundle pre-control-schema fixture; original run bytes stay fixed."""
    with s.state.transaction() as c:
        names = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for name in names:
            if name.startswith(("admission_", "execution_plan")) or name in {
                "budget_domains",
                "admissions",
                "trial_claims",
                "legacy_execution_owners",
            }:
                c.execute('DROP TABLE "' + name + '"')
    (s.root / "task-control/admission-anchor.json").unlink()


@pytest.mark.parametrize("kind", ["research", "engineering_pipeline"])
def test_complete_same_bundle_history_import_deduplicates_parent_and_real_child(tmp_path, kind):
    s, frozen, _ = service(tmp_path)
    if kind != "research":
        frozen = s.freeze({**SINGLE, "kind": kind})
    row = s.submit(frozen, "old-schema-source")
    done = s.work(row["task_id"])
    assert done["status"] == "SUCCEEDED"
    original = {
        p.relative_to(tmp_path).as_posix(): p.read_bytes()
        for directory in ("tasks", "research-runs", "research-campaigns")
        for p in (tmp_path / directory).rglob("*")
        if p.is_file()
    }
    remove_authority_schema_for_frozen_legacy_fixture(s)
    migrated = TaskState(tmp_path)
    assert migrated.workspace_id == s.state.workspace_id
    stats = history(tmp_path)
    assert stats["admitted_units"] == 1 and stats["registered_trials"] == 1
    assert stats["admissions"][0]["migrated"] is True
    assert all((tmp_path / name).read_bytes() == raw for name, raw in original.items())
    assert TaskService(tmp_path).status(row["task_id"])["status"] == "SUCCEEDED"


def test_complete_legacy_only_history_import_preserves_all_claims_without_refund(tmp_path):
    s, _, _ = service(tmp_path)
    frozen = s.freeze({**SINGLE, "horizons": [1, 2]})
    req = research_request(tmp_path, json.loads(frozen.raw))
    config = json.loads(req.config)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage(req))
    for unit in hypotheses(config):
        ledger.register_trial(run, config["family"]["id"], unit["hypothesis"], budget=12)
    ledger.finish(run, "CANCELLED")
    original = {p: p.read_bytes() for p in ledger.path(run).iterdir() if p.is_file()}
    original_trials = (ledger.root / "trials.jsonl").read_bytes()
    remove_authority_schema_for_frozen_legacy_fixture(s)
    TaskState(tmp_path)
    stats = history(tmp_path)
    assert (stats["admitted_units"], stats["registered_trials"]) == (2, 2)
    assert stats["admissions"][0]["migrated"] is True
    assert stats["admissions"][0]["owner_kind"] == "LEGACY"
    assert all(p.read_bytes() == raw for p, raw in original.items())
    assert (ledger.root / "trials.jsonl").read_bytes() == original_trials


def test_original_rejected_attempt_stays_rejected_after_versioned_history_import(tmp_path):
    s, frozen, _ = service(tmp_path)
    cancel_tasks(s, frozen, 12)
    refused = s.submit(frozen, "original-rejected")
    assert refused["status"] == "FAILED"
    original = (tmp_path / "tasks" / refused["task_id"] / "campaign-attempt.json").read_bytes()
    remove_authority_schema_for_frozen_legacy_fixture(s)
    TaskState(tmp_path)
    stats = history(tmp_path)
    assert (stats["admitted_units"], stats["requested_units"], stats["rejected_units"]) == (
        12,
        13,
        1,
    )
    with s.state.budget.transaction() as c:
        retained = s.state.budget.lookup_owner(c, "TASK", refused["task_id"])
    assert retained["decision"] == "REJECTED" and retained["migrated"] is True
    assert (
        tmp_path / "tasks" / refused["task_id"] / "campaign-attempt.json"
    ).read_bytes() == original
    row = TaskService(tmp_path).submit(frozen, "after-original-rejection")
    assert row["status"] == "FAILED" and row["error"] == "EXPERIMENT_BUDGET_EXCEEDED"


@pytest.mark.parametrize("missing", ["task", "campaign", "request", "trial"])
def test_missing_legacy_history_is_not_imported_as_an_empty_budget(tmp_path, missing):
    s, frozen, _ = service(tmp_path)
    row = s.submit(frozen, "legacy-with-damage")
    done = s.work(row["task_id"])
    assert done["status"] == "SUCCEEDED"
    remove_authority_schema_for_frozen_legacy_fixture(s)
    if missing in {"task", "campaign"}:
        with s.state.transaction() as c:
            c.execute("DELETE FROM " + ("tasks" if missing == "task" else "campaign_attempts"))
    elif missing == "request":
        (tmp_path / "tasks" / row["task_id"] / "request.json").unlink()
    else:
        (tmp_path / "research-runs/trials.jsonl").unlink()
    with pytest.raises(
        (ContractError, OSError),
        match="ADMISSION_HISTORY_UNVERIFIED|CAMPAIGN_ATTEMPT_HISTORY_INCOMPLETE|No such file",
    ):
        TaskState(tmp_path)


def test_removed_or_corrupt_database_with_anchor_is_never_recreated(tmp_path):
    s, frozen, _ = service(tmp_path)
    row = s.submit(frozen, "keep-proof")
    original_anchor = (tmp_path / "task-control/admission-anchor.json").read_bytes()
    db = tmp_path / "task-control/tasks.sqlite"
    (tmp_path / "original-database.bin").write_bytes(db.read_bytes())
    db.write_bytes(b"not a SQLite database")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        TaskService(tmp_path)
    assert db.read_bytes() == b"not a SQLite database"
    assert (tmp_path / "task-control/admission-anchor.json").read_bytes() == original_anchor
    assert (tmp_path / "tasks" / row["task_id"] / "request.json").exists()


def test_direct_ledger_managed_origin_remains_bound_after_copy(tmp_path):
    import shutil

    _, _, req = service(tmp_path / "W")
    ledger = ExperimentLedger(tmp_path / "W/research-runs")
    cfg, line = json.loads(req.config), lineage(req)
    del line["admission_inputs"]
    run = ledger.start(cfg, line)
    original_lineage = json.loads((ledger.path(run) / "lineage.json").read_bytes())
    assert original_lineage["admission_inputs"]["snapshot_root"] == str(req.snapshot.root)
    destination = ExperimentLedger(tmp_path / "copied-unmanaged")
    shutil.copytree(ledger.path(run), destination.path(run))
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        destination.register_trial(
            run, cfg["family"]["id"], hypotheses(cfg)[0]["hypothesis"], budget=12
        )


def test_terminal_managed_run_cannot_create_new_claim_or_trial(tmp_path):
    _, _, req = service(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    cfg = json.loads(req.config)
    run = ledger.start(cfg, lineage(req))
    ledger.finish(run, "CANCELLED")
    with pytest.raises(ContractError, match="IMMUTABLE_TERMINAL_RUN"):
        ledger.register_trial(run, cfg["family"]["id"], hypotheses(cfg)[0]["hypothesis"], budget=12)
    assert history(tmp_path)["registered_trials"] == 0


def test_versioned_import_keeps_cancelled_unstarted_r_reservation(tmp_path):
    from aqrp.services.task_context import authority

    s, frozen, _ = service(tmp_path)
    row = s.submit(frozen, "allocated-before-cancel")
    owner, epoch = s.state.claim(row["task_id"])
    auth = authority(s.state, row["task_id"], owner, epoch)
    auth.allocate("R", "P3", tmp_path / "research-runs")
    assert s.cancel(row["task_id"]) == "CANCEL_REQUESTED"
    s.state.abandon(row["task_id"], owner, epoch)
    assert s.work(row["task_id"], recover=True)["status"] == "CANCELLED"
    assert not any(p.is_dir() for p in (tmp_path / "research-runs").iterdir())
    remove_authority_schema_for_frozen_legacy_fixture(s)
    TaskState(tmp_path)
    stats = history(tmp_path)
    assert stats["admitted_units"] == 1 and stats["registered_trials"] == 0


def test_managed_same_key_changed_registered_request_is_admission_conflict(tmp_path):
    s, frozen, _ = service(tmp_path)
    s.register_campaign("second", [{**SINGLE, "lookback": 3}])
    second = s.freeze({**SINGLE, "lookback": 3, "campaign_id": "second"})
    original = s.submit(frozen, "frozen-owner")
    with pytest.raises(ContractError, match="ADMISSION_IDEMPOTENCY_CONFLICT"):
        s.submit(second, "frozen-owner")
    assert s.status(original["task_id"])["status"] == "QUEUED"
    assert history(tmp_path)["admitted_units"] == 1


def test_crash_between_frozen_trial_projection_and_run_event_reuses_exact_wrapper(
    tmp_path, monkeypatch
):
    _, _, req = service(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    cfg = json.loads(req.config)
    run = ledger.start(cfg, lineage(req))
    alias = hypotheses(cfg)[0]["hypothesis"]
    original = ledger._publish_trial_events
    monkeypatch.setattr(
        ledger,
        "_publish_trial_events",
        lambda *a: (_ for _ in ()).throw(OSError("after frozen projection")),
    )
    with pytest.raises(OSError, match="after frozen projection"):
        ledger.register_trial(run, cfg["family"]["id"], alias, budget=12)
    sidecar = ledger.path(run) / "admission-trial-event-0.json"
    frozen = sidecar.read_bytes()
    assert len(read_chain(ledger.path(run) / "events.jsonl")) == 1
    monkeypatch.setattr(ledger, "_publish_trial_events", original)
    ledger.register_trial(run, cfg["family"]["id"], alias, budget=12)
    assert sidecar.read_bytes() == frozen
    assert read_chain(ledger.path(run) / "events.jsonl")[1] == json.loads(frozen)
    assert len(read_chain(tmp_path / "research-runs/trials.jsonl")) == 1
    assert history(tmp_path)["admitted_units"] == 1


def test_concurrent_distinct_units_reserve_unique_frozen_event_sequence(tmp_path):
    s, _, _ = service(tmp_path)
    frozen = s.freeze({**SINGLE, "horizons": [1, 2]})
    req = research_request(tmp_path, json.loads(frozen.raw))
    cfg = json.loads(req.config)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(cfg, lineage(req))
    aliases = [h["hypothesis"] for h in hypotheses(cfg)]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda alias: ledger.register_trial(run, cfg["family"]["id"], alias, budget=12),
                aliases,
            )
        )
    assert {r["hypothesis"] for r in results} == set(aliases)
    events = read_chain(ledger.path(run) / "events.jsonl")
    assert [e["seq"] for e in events] == [0, 1, 2]
    assert {e["payload"]["hypothesis"] for e in events[1:]} == set(aliases)
    stats = history(tmp_path)
    assert stats["admitted_units"] == 2 and stats["registered_trials"] == 2


@pytest.mark.parametrize("damage", ["different-committed-event", "missing-newline"])
def test_frozen_run_event_recovery_rejects_changed_prefix_without_rewriting_it(
    tmp_path, monkeypatch, damage
):
    _, _, req = service(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    cfg = json.loads(req.config)
    run = ledger.start(cfg, lineage(req))
    alias = hypotheses(cfg)[0]["hypothesis"]
    original = ledger._publish_trial_events
    monkeypatch.setattr(
        ledger, "_publish_trial_events", lambda *a: (_ for _ in ()).throw(OSError("frozen-first"))
    )
    with pytest.raises(OSError, match="frozen-first"):
        ledger.register_trial(run, cfg["family"]["id"], alias, budget=12)
    path = ledger.path(run) / "events.jsonl"
    if damage == "different-committed-event":
        ledger.event(run, "CONTROLLED_DIFFERENT_PREFIX", {})
    else:
        path.write_bytes(path.read_bytes()[:-1])
    changed = path.read_bytes()
    monkeypatch.setattr(ledger, "_publish_trial_events", original)
    with pytest.raises(
        ContractError, match="ADMISSION_INTEGRITY_ERROR|ADMISSION_HISTORY_UNVERIFIED"
    ):
        ledger.register_trial(run, cfg["family"]["id"], alias, budget=12)
    assert path.read_bytes() == changed
    assert history(tmp_path)["admitted_units"] == 1


def test_initial_running_wrapper_is_frozen_before_managed_run_creation(tmp_path):
    _, _, req = service(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(json.loads(req.config), lineage(req))
    path = tmp_path / "task-control/start-events" / (run + ".json")
    frozen = path.read_bytes()
    assert json.loads(frozen) == read_chain(ledger.path(run) / "events.jsonl")[0]
    budget = BudgetAuthority(tmp_path)
    with budget.transaction() as c:
        row = c.execute(
            "SELECT content,materialized FROM admission_outbox WHERE path=?", (str(path),)
        ).fetchone()
        assert bytes(row[0]) == frozen and row[1] == 1
