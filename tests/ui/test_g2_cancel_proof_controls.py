"""Resealed reports cannot replace the current physical financial authority."""

import json
from pathlib import Path

import pytest
from test_task_proofs import completed as completed
from test_task_proofs import reseal

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import append_chain
from aqrp.services.task_context import authority


@pytest.mark.parametrize("damage", ["cash", "unknown", "files", "status"])
def test_resealed_financial_report_cannot_certify_cancellation(completed, damage):
    s, t, r = completed
    binding = r["slots"]["B"]["binding"]

    def mutate(x):
        if damage == "cash":
            x["account"]["cash_total"] = "1000"
        elif damage == "unknown":
            x["committed_state_verification"] = {"financial_state_known": False}
        else:
            x["status"] = "CANCELLED"

    changes = (
        {"transaction-files.json": lambda x: x.clear()}
        if damage == "files"
        else {"result.json": mutate}
    )
    with reseal(binding, changes=changes):
        with pytest.raises(ContractError):
            s._verify_cancelled_finances(t)


def test_only_unstarted_and_absent_p5_slot_is_safe_to_skip(completed):
    s, _, _ = completed
    frozen = s.freeze(
        {
            "kind": "engineering_pipeline",
            "start": "2024-01-06",
            "end": "2024-01-06",
            "horizons": [1],
        }
    )
    task = s.submit(frozen, "absent-p5")["task_id"]
    owner, epoch = s.state.claim(task)
    ctx = authority(s.state, task, owner, epoch).allocate("B", "P5", s.root / "backtest-runs")
    s._verify_cancelled_finances(task)
    b = ctx.binding()
    directory = Path(b["physical_ledger_root"]) / b["child_run_id"]
    directory.mkdir()
    with pytest.raises((ContractError, FileNotFoundError)):
        s._verify_cancelled_finances(task)


def test_legacy_data_attempts_consume_shared_quota_without_automatic_registration(tmp_path):
    from aqrp.core.canonical import digest
    from aqrp.experiments.ledger import ExperimentLedger
    from aqrp.services.research import hypotheses, hypothesis_definition
    from aqrp.services.task_requests import build_research_config, catalogue, initialize
    from aqrp.services.tasks import TaskService

    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    draft = {"start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}
    cat = catalogue(tmp_path)
    data_hash = cat["snapshot"]["manifest_hash"]
    config = build_research_config(cat, draft)
    config["family"] = {"id": "legacy-family", "budget": 12}
    units = hypotheses(config)
    config["family"]["hypotheses"] = [u["hypothesis"] for u in units]
    config["family"].update(
        definitions={
            u["hypothesis"]: hypothesis_definition(
                u, config, data_hash, cat["exposures"]["manifest_hash"], cat["coverage"]["checksum"]
            )
            for u in units
        },
    )
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(
        config,
        {
            "code_commit": cat["code_commit"],
            "code_bundle": cat["code_bundle"],
            "data_hash": data_hash,
            "exposure_hash": cat["exposures"]["manifest_hash"],
            "coverage_hash": cat["coverage"]["checksum"],
            "environment": {},
            "protocol_hash": digest(config),
            "permission_domain": "ENGINEERING_DEMO",
            "seed": 17,
        },
    )
    ledger.register_trial(run, "legacy-family", units[0]["hypothesis"], budget=12)
    ledger.finish(run, "CANCELLED")
    with pytest.raises(ContractError, match="EXPLICIT_CAMPAIGN_REQUIRED_AFTER_DATA_ACCESS"):
        s.freeze(draft)
    p = s.register_campaign("after-legacy", [draft])
    assert p["registration_history"]["contaminated_before_registration"]
    assert p["registration_history"]["prior_research_trials"] == 1
    task = s.submit(s.freeze({**draft, "campaign_id": p["id"]}), "new")
    assert task["research_control"]["prior_legacy_trials"] == 1
    assert task["research_control"]["prior_reserved_units"] == 1
    assert task["research_control"]["prior_other_family_legacy_trials"] == 1
    with s.state.transaction() as c:
        old = c.execute(
            "SELECT payload FROM campaign_attempts WHERE task=?", (task["task_id"],)
        ).fetchone()[0]
        record = json.loads(old)
        record["units"] = 0
        c.execute(
            "UPDATE campaign_attempts SET payload=? WHERE task=?",
            (canonical(record).decode(), task["task_id"]),
        )
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        s.status(task["task_id"])


def test_unowned_legacy_append_cannot_become_verified_campaign_history(tmp_path):
    """BUD-024 rejects foreign writes without adopting them as authentic trials."""
    from aqrp.experiments.admission import BudgetAuthority
    from aqrp.services.task_requests import catalogue, initialize
    from aqrp.services.tasks import TaskService

    initialize(tmp_path, "a" * 40)
    s = TaskService(tmp_path)
    root = tmp_path / "research-runs"
    root.mkdir()
    append_chain(
        root / "trials.jsonl",
        "TRIAL_ATTEMPT",
        {
            "run_id": "historical-retained-attempt",
            "data_hash": catalogue(tmp_path)["snapshot"]["manifest_hash"],
            "family": "legacy-family",
        },
    )
    original = (root / "trials.jsonl").read_bytes()
    draft = {"start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        s.freeze(draft)
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        s.register_campaign("after-foreign", [draft])
    assert (root / "trials.jsonl").read_bytes() == original
    with BudgetAuthority(tmp_path).transaction() as c:
        assert c.execute("SELECT count(*) FROM admissions").fetchone()[0] == 0
        assert c.execute("SELECT count(*) FROM tasks").fetchone()[0] == 0
