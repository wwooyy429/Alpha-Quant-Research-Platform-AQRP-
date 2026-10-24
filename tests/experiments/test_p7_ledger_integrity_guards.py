"""Frozen admission, caller identity and committed run-publication boundaries.

Faults below are explicit engineering negatives, never admitted research results.
Every rejected mutation retains the original SQL rows and JSON/hash-chain bytes.
"""

import hashlib
import json
import sqlite3
import uuid
from contextlib import closing, contextmanager
from copy import deepcopy
from pathlib import Path

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import (
    BudgetAuthority,
    advance_actor,
    install_execution_plan,
    open_protocol_driver,
)
from aqrp.experiments.ledger import ExperimentLedger, append_chain, immutable_write, read_chain
from aqrp.factors.admission import bundle_hash
from aqrp.services.research import hypotheses, hypothesis_definition
from aqrp.services.task_context import authority
from aqrp.services.task_requests import catalogue, initialize, research_request
from aqrp.services.task_state import TaskState
from aqrp.services.tasks import TaskService

SINGLE = {"factor_ids": ["momentum"], "horizons": [1], "start": "2024-01-06", "end": "2024-01-06"}


def managed(root, **patch):
    initialize(root, "a" * 40)  # Declared synthetic identity, not a source-version assertion.
    service = TaskService(root)
    frozen = service.freeze({**SINGLE, **patch})
    request = research_request(root, json.loads(frozen.raw))
    config = json.loads(request.config)
    lineage = {
        "code_commit": request.code_commit,
        "code_bundle": bundle_hash(),
        "data_hash": request.snapshot.manifest_hash,
        "exposure_hash": request.exposures.manifest_hash,
        "coverage_hash": request.coverage.checksum,
        "environment": {},
        "protocol_hash": digest(config),
        "permission_domain": "ENGINEERING_DEMO",
        "seed": 17,
        "admission_inputs": {
            "snapshot_root": str(request.snapshot.root),
            "exposure_root": str(request.exposures.root),
        },
    }
    return service, frozen, config, lineage


def sql_rows(root):
    with closing(sqlite3.connect(root / "task-control/tasks.sqlite")) as connection:
        names = [
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        ]
        return {
            name: list(connection.execute('SELECT * FROM "' + name + '" ORDER BY rowid'))
            for name in names
        }


def json_bytes(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and path.suffix in (".json", ".jsonl", ".html")
    }


@contextmanager
def unchanged(root):
    rows, files = sql_rows(root), json_bytes(root)
    yield
    assert sql_rows(root) == rows
    assert json_bytes(root) == files


def history(root):
    budget = BudgetAuthority(root)
    budget.materialize()
    with budget.transaction() as connection:
        return budget.history(connection)


def valid_definitions(config, lineage):
    """Construct valid input declarations; no test expectation is derived here."""
    config["family"]["definitions"].update(
        {
            candidate["hypothesis"]: hypothesis_definition(
                candidate,
                config,
                lineage["data_hash"],
                lineage["exposure_hash"],
                lineage["coverage_hash"],
            )
            for candidate in hypotheses(config)
        }
    )


def replace_initial_binding(ledger, run, config, lineage):
    """Explicit caller file fault: internally hash-consistent, not trusted by SQL."""
    path = ledger.path(run)
    (path / "config.json").write_bytes(canonical(config))
    (path / "lineage.json").write_bytes(canonical(lineage))
    event = read_chain(path / "events.jsonl")[0]
    event["payload"] = {"config_hash": digest(config), "lineage_hash": digest(lineage)}
    event["hash"] = digest({key: value for key, value in event.items() if key != "hash"})
    (path / "events.jsonl").write_bytes(canonical(event) + b"\n")


def legacy_plan(root, config):
    cat = catalogue(root)
    source = Path(__file__).resolve()
    identity = {
        "runner_path": str(source),
        "runner_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }
    plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "FINITE_LEDGER_OWNER_RETRY_REGRESSION_NOT_MAIN_E2E",
        "data_hash": cat["snapshot"]["manifest_hash"],
        "catalogue_hash": digest(cat),
        **identity,
        "slots": [
            {
                "slot_id": "only-original-owner",
                "service_kind": "LEGACY",
                "request_hash": digest(config),
                "output_root": str(root / "research-runs"),
                "requested_units": 1,
                "grant_capacity": 1,
                "max_admitted_owners": 1,
                "expected_status": "CANCELLED",
            }
        ],
    }
    fixed = install_execution_plan(root, plan, identity)
    driver = open_protocol_driver(root, fixed, identity)
    advance_actor(driver, -1)
    return driver


def test_changed_definition_is_rejected_before_any_reservation(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    config["family"]["definitions"][hypotheses(config)[0]["hypothesis"]] = "f" * 64
    ledger = ExperimentLedger(tmp_path / "research-runs")
    with (
        unchanged(tmp_path),
        pytest.raises(ContractError, match="HYPOTHESIS_CHANGED_AFTER_PREREGISTRATION"),
    ):
        ledger.prepare_research(config, lineage)
    assert history(tmp_path)["admitted_units"] == 0


def test_extra_source_claim_cannot_be_added_to_a_real_managed_input(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    lineage["admission_inputs"]["unrecognized_source_claim"] = "caller-supplied"
    ledger = ExperimentLedger(tmp_path / "research-runs")
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        ledger.prepare_research(config, lineage)
    assert history(tmp_path)["admitted_units"] == 0


def test_prepared_config_cannot_change_before_start_and_does_not_refund(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    admission = ledger.prepare_research(config, lineage)
    changed = {**config, "seed": config["seed"] + 1}
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_IDEMPOTENCY_CONFLICT"):
        ledger.start(changed, lineage)
    assert not ledger.path(admission["owner_id"]).exists()
    assert (history(tmp_path)["admitted_units"], history(tmp_path)["registered_trials"]) == (1, 0)


def test_planned_legacy_exact_start_retry_cannot_allocate_a_replacement_run(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    legacy_plan(tmp_path, config)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    ledger.finish(run, "CANCELLED")
    with (
        unchanged(tmp_path),
        pytest.raises(ContractError, match="ADMISSION_LEGACY_ALREADY_STARTED"),
    ):
        ExperimentLedger(ledger.root).start(config, lineage)
    assert {path.name for path in ledger.root.iterdir() if path.is_dir()} == {run}
    assert history(tmp_path)["admitted_units"] == 1


@pytest.mark.parametrize("field", ["config.json", "lineage.json"])
def test_trial_registration_rejects_noncanonical_original_input_bytes(tmp_path, field):
    _, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    path = ledger.path(run) / field
    path.write_bytes(path.read_bytes() + b" ")
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        ledger.register_trial(
            run, config["family"]["id"], hypotheses(config)[0]["hypothesis"], budget=12
        )
    assert history(tmp_path)["registered_trials"] == 0


@pytest.mark.parametrize("fault", ["family", "hypothesis", "budget"])
def test_managed_trial_rejects_wrong_owner_profile_without_new_claim(tmp_path, fault):
    _, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    family, alias, budget = config["family"]["id"], hypotheses(config)[0]["hypothesis"], 12
    if fault == "family":
        family = "different-family"
    elif fault == "hypothesis":
        alias = "not-preregistered"
    else:
        budget = 11
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
        ledger.register_trial(run, family, alias, budget=budget)
    assert (history(tmp_path)["admitted_units"], history(tmp_path)["registered_trials"]) == (1, 0)


def test_running_wrapper_is_idempotent_but_rejects_changed_payload_and_unadmitted_run(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    frozen = read_chain(ledger.path(run) / "events.jsonl")[0]
    with unchanged(tmp_path):
        assert ledger._freeze_running_event(run, config, lineage, None) == frozen
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_INTEGRITY_ERROR"):
        ledger._freeze_running_event(run, {**config, "seed": config["seed"] + 1}, lineage, None)
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
        ledger._freeze_running_event(str(uuid.uuid4()), config, lineage, None)
    assert history(tmp_path)["admitted_units"] == 1


def task_run(root):
    service, frozen, config, lineage = managed(root, kind="engineering_pipeline")
    task = service.submit(frozen, "original-task")["task_id"]
    owner, epoch = service.state.claim(task)
    auth = authority(service.state, task, owner, epoch)
    context = auth.allocate("R", "P3", root / "research-runs")
    ledger = ExperimentLedger(root / "research-runs")
    run = ledger.start(config, lineage, task_context=context)
    return service, auth, context, ledger, run, config


def test_execution_context_cannot_be_used_to_claim_research_unit(tmp_path):
    _, auth, _, ledger, run, config = task_run(tmp_path)
    execution = auth.allocate("B", "P5", tmp_path / "backtest-runs")
    with (
        unchanged(tmp_path),
        pytest.raises(ContractError, match="RESEARCH_CAMPAIGN_CONTEXT_REQUIRED"),
    ):
        ledger.register_trial(
            run,
            config["family"]["id"],
            hypotheses(config)[0]["hypothesis"],
            budget=12,
            task_context=execution,
        )
    assert history(tmp_path)["registered_trials"] == 0


def test_self_consistent_file_rehash_cannot_change_trusted_task_binding(tmp_path):
    _, _, context, ledger, run, config = task_run(tmp_path)
    lineage = json.loads((ledger.path(run) / "lineage.json").read_bytes())
    lineage["task_binding_hash"] = "f" * 64
    replace_initial_binding(ledger, run, config, lineage)
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
        ledger.register_trial(
            run,
            config["family"]["id"],
            hypotheses(config)[0]["hypothesis"],
            budget=12,
            task_context=context,
        )
    assert history(tmp_path)["registered_trials"] == 0


def test_correlated_config_and_initial_rehash_cannot_borrow_an_old_unit(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    changed = deepcopy(config)
    changed["seed"] += 1
    valid_definitions(changed, lineage)
    replace_initial_binding(ledger, run, changed, lineage)
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
        ledger.register_trial(
            run, changed["family"]["id"], hypotheses(changed)[0]["hypothesis"], budget=12
        )
    assert (history(tmp_path)["admitted_units"], history(tmp_path)["registered_trials"]) == (1, 0)


def test_existing_claim_rejects_a_different_fingerprint_without_second_trial(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    alias = hypotheses(config)[0]["hypothesis"]
    ledger.register_trial(run, config["family"]["id"], alias, budget=12)
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
        ledger.register_trial(
            run,
            config["family"]["id"],
            alias,
            budget=12,
            hypothesis_spec={"caller_option": "different"},
        )
    assert (history(tmp_path)["admitted_units"], history(tmp_path)["registered_trials"]) == (1, 1)


def test_rejected_direct_registration_retry_retains_one_refusal_and_no_claim(tmp_path):
    _, _, config, lineage = managed(tmp_path)
    config["family"]["budget"] = 1
    valid_definitions(config, lineage)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    first = ledger.start(config, lineage)
    ledger.finish(first, "CANCELLED")
    second = str(uuid.uuid4())
    path = ledger.path(second)
    path.mkdir()
    immutable_write(path / "config.json", canonical(config))
    immutable_write(path / "lineage.json", canonical(lineage))
    append_chain(
        path / "events.jsonl",
        "RUNNING",
        {"config_hash": digest(config), "lineage_hash": digest(lineage)},
    )
    alias = hypotheses(config)[0]["hypothesis"]
    with pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
        ledger.register_trial(second, config["family"]["id"], alias, budget=1)
    with unchanged(tmp_path), pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
        ledger.register_trial(second, config["family"]["id"], alias, budget=1)
    stats = history(tmp_path)
    assert (
        stats["admitted_units"],
        stats["requested_units"],
        stats["rejected_units"],
        stats["registered_trials"],
    ) == (1, 2, 1, 0)


@pytest.mark.parametrize("damage", ["missing-newline", "different-valid-tip"])
def test_committed_trial_publisher_rejects_changed_run_prefix_without_repair(
    tmp_path, monkeypatch, damage
):
    _, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    alias = hypotheses(config)[0]["hypothesis"]
    publisher = ledger._publish_trial_events
    monkeypatch.setattr(
        ledger,
        "_publish_trial_events",
        lambda *args: (_ for _ in ()).throw(OSError("committed before append")),
    )
    with pytest.raises(OSError, match="committed before append"):
        ledger.register_trial(run, config["family"]["id"], alias, budget=12)
    monkeypatch.setattr(ledger, "_publish_trial_events", publisher)
    path = ledger.path(run) / "events.jsonl"
    if damage == "missing-newline":
        path.write_bytes(path.read_bytes()[:-1])
    else:
        event = read_chain(path)[0]
        event["recorded_at"] = "2020-01-01T00:00:00.000000+00:00"
        event["hash"] = digest({key: value for key, value in event.items() if key != "hash"})
        path.write_bytes(canonical(event) + b"\n")
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_INTEGRITY_ERROR"):
        if damage == "missing-newline":
            # Recovery boundary itself must reject, even without the public precheck.
            publisher(BudgetAuthority(tmp_path), run)
        else:
            ledger.register_trial(run, config["family"]["id"], alias, budget=12)
    assert (history(tmp_path)["admitted_units"], history(tmp_path)["registered_trials"]) == (1, 1)


def test_migrated_original_trial_retry_never_adds_or_replaces_terminal_bytes(tmp_path):
    service, _, config, lineage = managed(tmp_path)
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    alias = hypotheses(config)[0]["hypothesis"]
    item = ledger.register_trial(run, config["family"]["id"], alias, budget=12)
    ledger.finish(run, "CANCELLED")
    original = json_bytes(tmp_path)
    # Explicit same-bundle pre-control-schema fixture; no synthetic quota rows.
    with service.state.transaction() as connection:
        names = [
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        ]
        for name in names:
            if name.startswith(("admission_", "execution_plan")) or name in {
                "budget_domains",
                "admissions",
                "trial_claims",
                "legacy_execution_owners",
            }:
                connection.execute('DROP TABLE "' + name + '"')
    (tmp_path / "task-control/admission-anchor.json").unlink()
    TaskState(tmp_path)
    assert all(
        (tmp_path / name).read_bytes() == raw
        for name, raw in original.items()
        if not name.endswith("admission-anchor.json")
    )
    with unchanged(tmp_path):
        assert ledger.register_trial(run, config["family"]["id"], alias, budget=12) == item
    budget = BudgetAuthority(tmp_path)
    with unchanged(tmp_path), pytest.raises(ContractError, match="ADMISSION_INTEGRITY_ERROR"):
        with budget.transaction() as connection:
            budget.verify(connection)
            admitted = budget.lookup_owner(connection, "LEGACY", run)
            assert admitted["migrated"] is True
            ledger._freeze_trial_event(
                connection, budget, admitted, 0, run, {**item, "over_budget": True}
            )
    assert (history(tmp_path)["admitted_units"], history(tmp_path)["registered_trials"]) == (1, 1)


def test_terminal_publication_boundary_cannot_append_an_unclaimed_second_trial(tmp_path):
    _, _, config, lineage = managed(tmp_path, horizons=[1, 2])
    ledger = ExperimentLedger(tmp_path / "research-runs")
    run = ledger.start(config, lineage)
    aliases = [candidate["hypothesis"] for candidate in hypotheses(config)]
    first = ledger.register_trial(run, config["family"]["id"], aliases[0], budget=12)
    ledger.finish(run, "CANCELLED")
    budget = BudgetAuthority(tmp_path)
    with unchanged(tmp_path), pytest.raises(ContractError, match="IMMUTABLE_TERMINAL_RUN"):
        with budget.transaction() as connection:
            budget.verify(connection)
            admission = budget.lookup_owner(connection, "LEGACY", run)
            ledger._freeze_trial_event(
                connection, budget, admission, 1, run, {**first, "hypothesis": aliases[1]}
            )
    assert (history(tmp_path)["admitted_units"], history(tmp_path)["registered_trials"]) == (2, 1)
