"""Public cross-entry contamination controls, with separate engineering roots."""

import json
import subprocess
import sys
from dataclasses import asdict

import pytest

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import BudgetAuthority
from aqrp.experiments.ledger import ExperimentLedger, read_chain
from aqrp.factors.admission import bundle_hash
from aqrp.services.research import hypotheses, research
from aqrp.services.task_requests import initialize, research_request
from aqrp.services.tasks import TaskService

SINGLE = {"factor_ids": ["momentum"], "horizons": [1], "start": "2024-01-06", "end": "2024-01-06"}


def campaigns(root, names=("campaign-a", "campaign-b")):
    cat = initialize(root, "a" * 40)
    service = TaskService(root)
    plans = [service.register_campaign(name, [SINGLE]) for name in names]
    assert all(not p["registration_history"]["contaminated_before_registration"] for p in plans)
    # The supported preregistrar binds every campaign to a distinct immutable family.
    assert len({p["family_id"] for p in plans}) == len(names)
    for plan in plans:
        for config in plan["variants"].values():
            assert (
                config["family"]["id"] == "ui-campaign-" + config["family"]["campaign"]["identity"]
            )
    frozen = [service.freeze({**SINGLE, "campaign_id": name}) for name in names]
    return cat, service, frozen


def stats(root):
    authority = BudgetAuthority(root)
    authority.materialize()
    with authority.transaction() as c:
        return authority.history(c)


def request(root, frozen):
    return research_request(root, json.loads(frozen.raw))


def run_entry(root, cat, service, frozen, entry):
    req = request(root, frozen)
    if entry == "api":
        run = research(req, root / "research-runs")["run_id"]
    elif entry == "cli":
        payload = {
            "config": json.loads(req.config),
            "code_commit": req.code_commit,
            "snapshot": {**asdict(req.snapshot), "root": str(req.snapshot.root)},
            "exposures": {**asdict(req.exposures), "root": str(req.exposures.root)},
            "coverage": req.coverage.read(req.snapshot.manifest_hash),
        }
        path = root / "actual-legacy-request.json"
        path.write_text(json.dumps(payload), encoding="utf8")
        argv = [
            sys.executable,
            "-B",
            "-m",
            "aqrp.services.cli",
            str(path),
            "--output",
            str(root / "research-runs"),
        ]
        result = subprocess.run(argv, cwd=root, capture_output=True)
        (root / "actual-legacy-cli.stdout.log").write_bytes(result.stdout)
        (root / "actual-legacy-cli.stderr.log").write_bytes(result.stderr)
        (root / "actual-legacy-cli.command.json").write_text(
            json.dumps({"argv": argv, "exit": result.returncode}), encoding="utf8"
        )
        assert result.returncode == 0, result.stderr.decode(errors="replace")
        run = json.loads(result.stdout)["run_id"]
    else:
        row = service.submit(frozen, "actual-task-b")
        row = service.work(row["task_id"])
        assert row["status"] == "SUCCEEDED"
        run = row["result"]["research_run_id"]
    trial = next(
        r["payload"]
        for r in read_chain(root / "research-runs/trials.jsonl")
        if r["payload"]["run_id"] == run
    )
    report = json.loads((root / "research-runs" / run / "report.json").read_bytes())
    return run, trial, report


@pytest.mark.parametrize("entry", ["api", "cli", "task"])
def test_cancelled_before_R_contaminates_first_B_in_three_independent_roots(tmp_path, entry):
    cat, service, (a, b) = campaigns(tmp_path)
    first = service.submit(a, "cancel-before-R")
    assert service.cancel(first["task_id"]) == "CANCELLED"
    assert service.status(first["task_id"])["slots"] == {}
    assert not (tmp_path / "research-runs/trials.jsonl").exists()
    _, trial, report = run_entry(tmp_path, cat, service, b, entry)
    assert trial["repeat_of"] == []
    assert stats(tmp_path)["admitted_units"] == 2
    assert stats(tmp_path)["registered_trials"] == 1
    assert trial["cross_campaign_data_access"] is True
    assert report["multiplicity"]["contaminated"] is True


def start_legacy(root, frozen):
    req = request(root, frozen)
    config = json.loads(req.config)
    lineage = {
        "code_commit": req.code_commit,
        "code_bundle": bundle_hash(),
        "data_hash": req.snapshot.manifest_hash,
        "exposure_hash": req.exposures.manifest_hash,
        "coverage_hash": req.coverage.checksum,
        "environment": {},
        "protocol_hash": digest(config),
        "permission_domain": "ENGINEERING_DEMO",
        "seed": 7,
    }
    ledger = ExperimentLedger(root / "research-runs")
    run = ledger.start(config, lineage)
    return ledger, run, config


def register(ledger, run, config):
    return ledger.register_trial(
        run,
        config["family"]["id"],
        hypotheses(config)[0]["hypothesis"],
        budget=config["family"]["budget"],
    )


def admission_for(root, owner_kind, owner):
    authority = BudgetAuthority(root)
    with authority.transaction() as c:
        authority.verify(c)
        return authority.lookup_owner(c, owner_kind, owner)


def test_failed_Task_before_TRIAL_is_not_a_clean_history(tmp_path, monkeypatch):
    cat, service, (a, b) = campaigns(tmp_path)
    import aqrp.services.tasks as tasks

    def fail_before_read(*args, **kwargs):
        raise ContractError("INJECTED_PRE_TRIAL_FAILURE")

    first = service.submit(a, "fail-before-trial")
    with monkeypatch.context() as patch:
        patch.setattr(tasks, "research", fail_before_read)
        failed = service.work(first["task_id"])
    assert failed["status"] == "FAILED" and failed["error"] == "INJECTED_PRE_TRIAL_FAILURE"
    assert not (tmp_path / "research-runs/trials.jsonl").exists()
    _, trial, report = run_entry(tmp_path, cat, service, b, "api")
    assert trial["repeat_of"] == [] and trial["cross_campaign_data_access"] is True
    assert report["multiplicity"]["contaminated"] is True
    assert stats(tmp_path)["admitted_units"] == 2


@pytest.mark.parametrize("terminal", ["CANCELLED", "FAILED"])
def test_legacy_before_TRIAL_cancel_or_failure_contaminates_reverse_Task_entry(tmp_path, terminal):
    cat, service, (a, b) = campaigns(tmp_path)
    ledger, first, _ = start_legacy(tmp_path, a)
    ledger.finish(first, terminal)
    assert not (tmp_path / "research-runs/trials.jsonl").exists()
    _, trial, report = run_entry(tmp_path, cat, service, b, "task")
    prior = admission_for(tmp_path, "LEGACY", first)
    assert trial["admission_history"]["prior_admission_ids"] == [prior["admission_id"]]
    assert trial["admission_history"]["prior_other_family_admitted_units"] == 1
    assert trial["repeat_of"] == [] and trial["cross_campaign_data_access"] is True
    assert report["multiplicity"]["contaminated"] is True
    assert stats(tmp_path)["admitted_units"] == 2


def test_direct_ledger_without_context_observes_cancelled_reservation_and_retries_once(tmp_path):
    _, service, (a, b) = campaigns(tmp_path)
    first = service.submit(a, "cancel-first")
    assert service.cancel(first["task_id"]) == "CANCELLED"
    ledger, run, config = start_legacy(tmp_path, b)
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda _: register(ledger, run, config), range(6)))
    assert all(row == rows[0] for row in rows)
    assert rows[0]["cross_campaign_data_access"] is True and rows[0]["repeat_of"] == []
    prior = admission_for(tmp_path, "TASK", first["task_id"])
    assert rows[0]["admission_history"]["prior_other_family_admission_ids"] == [
        prior["admission_id"]
    ]
    assert len(read_chain(tmp_path / "research-runs/trials.jsonl")) == 1
    assert (
        sum(e["kind"] == "TRIAL_REGISTERED" for e in read_chain(ledger.path(run) / "events.jsonl"))
        == 1
    )
    assert stats(tmp_path)["admitted_units"] == 2


def test_current_unclaimed_and_later_cancelled_owners_are_not_earlier_access(tmp_path):
    _, service, (a, b) = campaigns(tmp_path)
    ledger, run, config = start_legacy(tmp_path, b)
    later = service.submit(a, "later-other-campaign")
    assert service.cancel(later["task_id"]) == "CANCELLED"
    trial = register(ledger, run, config)
    assert trial["cross_campaign_data_access"] is False and trial["repeat_of"] == []
    assert trial["admission_history"]["prior_admission_ids"] == []
    assert trial["admission_history"]["prior_admitted_units"] == 0
    assert stats(tmp_path)["admitted_units"] == 2


def test_same_campaign_preTRIAL_debit_does_not_become_other_campaign_access(tmp_path):
    cat, service, (_, b) = campaigns(tmp_path)
    ledger, first, _ = start_legacy(tmp_path, b)
    ledger.finish(first, "CANCELLED")
    _, trial, report = run_entry(tmp_path, cat, service, b, "api")
    assert trial["cross_campaign_data_access"] is False and trial["repeat_of"] == []
    assert trial["admission_history"]["prior_admitted_units"] == 1
    assert trial["admission_history"]["prior_other_family_admitted_units"] == 0
    assert report["multiplicity"]["contaminated"] is False
    assert stats(tmp_path)["admitted_units"] == 2


def test_concurrent_reservations_use_committed_authority_order_not_file_publication(tmp_path):
    _, _, frozen = campaigns(tmp_path)
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    barrier = Barrier(2)

    def start(value):
        barrier.wait()
        return start_legacy(tmp_path, value)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(start, frozen))
    authority = BudgetAuthority(tmp_path)
    with authority.transaction() as c:
        authority.verify(c)
        ordered = [
            json.loads(row[0])
            for row in c.execute(
                "SELECT payload FROM admission_events WHERE kind='ADMISSION' ORDER BY seq"
            )
        ]
    by_run = {run: (ledger, config) for ledger, run, config in results}
    first, second = ordered
    ledger, config = by_run[first["owner_id"]]
    first_trial = register(ledger, first["owner_id"], config)
    ledger, config = by_run[second["owner_id"]]
    second_trial = register(ledger, second["owner_id"], config)
    assert first_trial["admission_history"]["prior_admission_ids"] == []
    assert first_trial["cross_campaign_data_access"] is False
    assert second_trial["admission_history"]["prior_admission_ids"] == [first["admission_id"]]
    assert second_trial["cross_campaign_data_access"] is True
    assert stats(tmp_path)["admitted_units"] == 2


def test_committed_trial_recovery_freezes_original_prefix_despite_later_admission(
    tmp_path, monkeypatch
):
    _, service, (a, b, c) = campaigns(tmp_path, ("campaign-a", "campaign-b", "campaign-c"))
    first = service.submit(a, "first-cancel")
    service.cancel(first["task_id"])
    ledger, run, config = start_legacy(tmp_path, b)
    original = BudgetAuthority.materialize
    calls = 0

    def fail_after_trial_commit(self):
        nonlocal calls
        calls += 1
        if calls == 3:
            raise OSError("INJECTED_AFTER_TRIAL_OUTBOX_COMMIT")
        return original(self)

    with monkeypatch.context() as patch:
        patch.setattr(BudgetAuthority, "materialize", fail_after_trial_commit)
        with pytest.raises(OSError, match="AFTER_TRIAL_OUTBOX_COMMIT"):
            register(ledger, run, config)
    authority = BudgetAuthority(tmp_path)
    with authority.transaction() as connection:
        frozen = [
            bytes(row[0])
            for row in connection.execute("SELECT content FROM admission_outbox WHERE kind='TRIAL'")
        ]
        assert len(frozen) == 1
        saved = json.loads(frozen[0])["payload"]
    assert saved["cross_campaign_data_access"] is True
    later = service.submit(c, "after-committed-trial")
    service.cancel(later["task_id"])
    recovered = register(ledger, run, config)
    assert recovered == saved
    assert recovered["admission_history"]["prior_admitted_units"] == 1
    assert stats(tmp_path)["admitted_units"] == 3 and stats(tmp_path)["registered_trials"] == 1
    assert len(read_chain(tmp_path / "research-runs/trials.jsonl")) == 1


def test_corrupt_authority_cannot_downgrade_contamination_to_false(tmp_path):
    _, service, (a, b) = campaigns(tmp_path)
    row = service.submit(a, "first-cancel")
    service.cancel(row["task_id"])
    ledger, run, config = start_legacy(tmp_path, b)
    authority = BudgetAuthority(tmp_path)
    with authority.transaction() as c:
        event = c.execute(
            "SELECT seq,payload FROM admission_events WHERE kind='ADMISSION' ORDER BY seq LIMIT 1"
        ).fetchone()
        original = event[1]
        c.execute("UPDATE admission_events SET payload=? WHERE seq=?", (original + " ", event[0]))
        before_counts = (
            c.execute("SELECT count(*) FROM admissions").fetchone()[0],
            c.execute("SELECT count(*) FROM trial_claims").fetchone()[0],
        )
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        register(ledger, run, config)
    assert not (tmp_path / "research-runs/trials.jsonl").exists()
    with authority.transaction() as c:
        assert (
            c.execute("SELECT payload FROM admission_events WHERE seq=?", (event[0],)).fetchone()[0]
            == original + " "
        )
        assert (
            c.execute("SELECT count(*) FROM admissions").fetchone()[0],
            c.execute("SELECT count(*) FROM trial_claims").fetchone()[0],
        ) == before_counts
