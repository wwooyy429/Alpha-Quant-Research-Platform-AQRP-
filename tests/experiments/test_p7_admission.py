"""Literal authority answers; these are developer tests, not independent audit."""

import hashlib
import importlib.util
import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import (
    BudgetAuthority,
    PlanAuthority,
    advance_actor,
    bind_current_actor,
    capture_activation,
    complete_actor,
    install_execution_plan,
    resolve_admission_domain,
    verify_activation,
)

DATA = "d" * 64


@pytest.fixture
def authority(tmp_path):
    root = tmp_path / "workspace"
    (root / "task-control").mkdir(parents=True)
    db = sqlite3.connect(root / "task-control/tasks.sqlite", isolation_level=None)
    db.execute("CREATE TABLE workspace(id TEXT PRIMARY KEY)")
    db.execute("INSERT INTO workspace VALUES ('literal-workspace')")
    db.execute("BEGIN IMMEDIATE")
    budget = BudgetAuthority(root)
    budget.initialize(db, "literal-workspace")
    db.commit()
    db.close()
    return budget


def reserve(authority, index, n=1, **kwargs):
    with authority.transaction() as c:
        return authority.reserve(
            c,
            DATA,
            kwargs.pop("owner_kind", "LEGACY"),
            str(index),
            kwargs.pop("key", "key-" + str(index)),
            kwargs.pop("request_hash", digest(str(index))),
            [
                {"hypothesis_alias": f"h-{i}", "definition_hash": digest({"literal": i})}
                for i in range(n)
            ],
            **kwargs,
        )


def history(authority):
    with authority.transaction() as c:
        return authority.history(c, DATA)


def test_twelve_debits_no_refund_and_thirteenth_rejection(authority):
    for i in range(12):
        assert reserve(authority, i)["decision"] == "ADMITTED"
    rejected = reserve(authority, 12)
    assert (rejected["decision"], rejected["code"], rejected["debit"]) == (
        "REJECTED",
        "EXPERIMENT_BUDGET_EXCEEDED",
        0,
    )
    assert history(authority)["admitted_units"] == 12
    assert history(authority)["rejected_units"] == 1
    assert len(history(authority)["admissions"]) == 13


@pytest.mark.parametrize("owner_kind", ["TASK", "LEGACY"])
def test_all_n_atomic_at_remaining_one(authority, owner_kind):
    reserve(authority, "first", 11)
    attempt = reserve(authority, "two", 2, owner_kind=owner_kind)
    assert attempt["decision"] == "REJECTED"
    assert attempt["prior_debit"] == 11
    assert attempt["debit"] == 0
    assert history(authority)["admitted_units"] == 11
    assert history(authority)["registered_trials"] == 0


def test_mixed_entrances_concurrent_last_unit(authority):
    reserve(authority, "seed", 11)
    barrier = threading.Barrier(2)

    def attempt(kind):
        barrier.wait(timeout=10)
        return reserve(authority, kind, owner_kind=kind)["decision"]

    with ThreadPoolExecutor(2) as pool:
        futures = [pool.submit(attempt, kind) for kind in ("TASK", "LEGACY")]
        assert sorted(f.result() for f in futures) == ["ADMITTED", "REJECTED"]
    assert history(authority)["admitted_units"] == 12


def test_concurrent_same_key_one_admission(authority):
    with ThreadPoolExecutor(4) as pool:
        attempts = list(pool.map(lambda _: reserve(authority, "same"), range(4)))
    assert len({a["admission_id"] for a in attempts}) == 1
    assert history(authority)["admitted_units"] == 1


@pytest.mark.parametrize("change", ["request", "units", "owner", "family"])
def test_exact_identity_cannot_be_changed(authority, change):
    original = reserve(authority, "same")
    args = {"key": "key-same"}
    owner, n = "same", 1
    if change == "request":
        args["request_hash"] = "f" * 64
    elif change == "units":
        n = 2
    elif change == "owner":
        owner = "another"
    else:
        args["family_id"] = "new-family"
    with pytest.raises(ContractError, match="ADMISSION_IDEMPOTENCY_CONFLICT"):
        reserve(authority, owner, n, **args)
    assert reserve(authority, "same")["admission_id"] == original["admission_id"]
    assert history(authority)["admitted_units"] == 1


def test_family_sublimit_and_new_family_does_not_reset_domain(authority):
    reserve(authority, "first", 2, family_id="small", family_limit=2)
    assert (
        reserve(authority, "blocked", family_id="small", family_limit=2)["decision"] == "REJECTED"
    )
    reserve(authority, "second", 10, family_id="large", family_limit=12)
    assert (
        reserve(authority, "another-family", family_id="third", family_limit=12)["decision"]
        == "REJECTED"
    )
    assert history(authority)["admitted_units"] == 12


def test_family_limit_cannot_be_increased_after_original_admission(authority):
    reserve(authority, "original", 2, family_id="frozen-family", family_limit=2)
    with pytest.raises(ContractError, match="ADMISSION_FAMILY_CONFLICT"):
        reserve(authority, "caller-increased", family_id="frozen-family", family_limit=12)
    assert history(authority)["admitted_units"] == 2


def test_authority_rollback_has_no_debit(authority):
    with pytest.raises(RuntimeError):
        with authority.transaction() as c:
            authority.reserve(
                c,
                DATA,
                "LEGACY",
                "x",
                "x",
                "a" * 64,
                [{"hypothesis_alias": "h", "definition_hash": "b" * 64}],
            )
            raise RuntimeError("literal injected before commit")
    assert history(authority)["admitted_units"] == 0


def test_commit_before_sidecar_keeps_debit_and_recovers_exact_bytes(authority):
    admission = reserve(authority, "run")
    target = authority.root / "research-runs/run/admission.json"
    original = b'{"literal":"frozen"}'
    with authority.transaction() as c:
        authority.queue_projection(c, target, original, admission["admission_id"])
    assert not target.exists()
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
            authority.verify(c, require_projections=True)
    authority.materialize()
    authority.materialize()
    assert target.read_bytes() == original
    assert history(authority)["admitted_units"] == 1


def _claim(authority, admission, alias="h-0"):
    with authority.transaction() as c:
        claim = authority.claim(
            c,
            admission["admission_id"],
            0,
            authority.root / "research-runs",
            admission["owner_id"],
            admission["request_hash"],
            "e" * 64,
        )
        payload = {"run_id": admission["owner_id"], "hypothesis": alias, "literal": "answer"}
        record = authority.project_trial(c, admission["admission_id"], claim, payload)
    return claim, record


def test_inverse_projection_arrival_keeps_committed_order(authority):
    one, two = reserve(authority, "one"), reserve(authority, "two")
    claim_one, first = _claim(authority, one)
    claim_two, second = _claim(authority, two)
    # A publisher for the second transaction wins the file lock first. It must
    # drain both committed rows, rather than publishing its own record first.
    authority.materialize()
    authority.materialize()
    actual = (authority.root / "research-runs/trials.jsonl").read_bytes().splitlines()
    assert actual == [canonical(first), canonical(second)]
    assert first["seq"] == 0
    assert first["previous"] == "0" * 64
    assert second["seq"] == 1
    assert second["previous"] == first["hash"]
    assert history(authority)["registered_trials"] == 2
    assert claim_one != claim_two


def test_same_claim_and_completed_projection_recovery_never_duplicates(authority):
    admission = reserve(authority, "run")
    claim, record = _claim(authority, admission)
    target = authority.root / "research-runs/trials.jsonl"
    target.parent.mkdir()
    target.write_bytes(canonical(record) + b"\n")
    claim2, record2 = _claim(authority, admission)
    authority.materialize()
    assert claim == claim2
    assert record == record2
    assert len(target.read_bytes().splitlines()) == 1
    assert history(authority)["registered_trials"] == 1


@pytest.mark.parametrize("corruption", ["truncated", "changed", "foreign"])
def test_projection_corruption_is_preserved_and_blocks_new_admission(authority, corruption):
    admission = reserve(authority, "run")
    _, record = _claim(authority, admission)
    authority.materialize()
    target = authority.root / "research-runs/trials.jsonl"
    original = target.read_bytes()
    bad = (
        original[:-2]
        if corruption == "truncated"
        else original.replace(b"answer", b"edited")
        if corruption == "changed"
        else original + b"{}\n"
    )
    target.write_bytes(bad)
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        reserve(authority, "next")
    assert target.read_bytes() == bad


@pytest.mark.parametrize(
    "table", ["admissions", "admission_units", "trial_claims", "admission_outbox"]
)
def test_missing_authority_row_rejected(authority, table):
    admission = reserve(authority, "run")
    _claim(authority, admission)
    with sqlite3.connect(authority.db) as c:
        c.execute("DELETE FROM " + table)
    c.close()
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        reserve(authority, "next")


def test_deleted_database_never_resets_budget(authority):
    reserve(authority, "run")
    authority.db.unlink()
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        with authority.transaction():
            pass


def test_existing_history_needs_complete_verified_migration(tmp_path):
    root = tmp_path / "old"
    (root / "task-control").mkdir(parents=True)
    c = sqlite3.connect(root / "task-control/tasks.sqlite", isolation_level=None)
    c.execute("CREATE TABLE workspace(id TEXT)")
    c.execute("INSERT INTO workspace VALUES ('old')")
    c.execute("CREATE TABLE tasks(id TEXT)")
    c.execute("INSERT INTO tasks VALUES ('cancelled')")
    c.execute("BEGIN IMMEDIATE")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        BudgetAuthority(root).initialize(c, "old")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        BudgetAuthority(root).initialize(
            c,
            "old",
            history_verifier=lambda c: {"complete": False, "records": [], "evidence": "partial"},
        )
    c.rollback()
    c.close()


def test_live_legacy_execution_is_exclusive_and_crash_epoch_fences(authority):
    admission = reserve(authority, "owner")
    with authority.legacy_execution(admission["admission_id"]) as first:
        with pytest.raises(ContractError, match="ADMISSION_LEGACY_OWNER_ACTIVE"):
            with authority.legacy_execution(admission["admission_id"]):
                pytest.fail("same live owner executed twice")
    with authority.legacy_execution(admission["admission_id"]) as second:
        assert second["epoch"] == 1
        assert second["token"] != first["token"]
    assert history(authority)["admitted_units"] == 1


def _catalogue(authority):
    from aqrp.factors.admission import bundle_hash

    body = {
        "schema": "task-catalog/2",
        "scope": "ENGINEERING_TEST_ONLY",
        "financial_approval": "NONE",
        "snapshot": {"root": str(authority.root / "inputs/snapshot"), "manifest_hash": DATA},
        "exposures": {"root": str(authority.root / "inputs/exposures"), "manifest_hash": "e" * 64},
        "code_bundle": bundle_hash(),
        "code_commit": "c" * 40,
    }
    body["revision"] = digest(body)
    (authority.root / "catalog.json").write_bytes(canonical(body))
    return body


def test_true_standalone_and_managed_path_conflicts(authority, tmp_path):
    assert resolve_admission_domain(tmp_path / "standalone") is None
    cat = _catalogue(authority)
    assert resolve_admission_domain(authority.root / "research-runs").root == authority.root
    for destination in (authority.root / "other", tmp_path / "external"):
        with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
            resolve_admission_domain(
                destination,
                lineage={
                    "data_hash": DATA,
                    "code_bundle": cat["code_bundle"],
                    "admission_inputs": {"snapshot_root": cat["snapshot"]["root"]},
                },
            )


def test_managed_missing_anchor_fails_closed(authority):
    _catalogue(authority)
    authority.anchor.unlink()
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        resolve_admission_domain(authority.root / "research-runs")


def _driver(authority, tmp_path, slots):
    cat = _catalogue(authority)
    source = tmp_path / "driver.py"
    source.write_text(
        "from aqrp.experiments.admission import install_execution_plan, open_protocol_driver\n"
        "def install(w,p,i): return install_execution_plan(w,p,i)\n"
        "def open(w,h,i): return open_protocol_driver(w,h,i)\n",
        encoding="utf-8",
    )
    identity = {
        "runner_path": str(source),
        "runner_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }
    plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "FROZEN_TEST_FIXTURE",
        "data_hash": DATA,
        "catalogue_hash": digest(cat),
        **identity,
        "slots": slots,
    }
    module_spec = importlib.util.spec_from_file_location("literal_driver", source)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    fixed = module.install(authority.root, plan, identity)
    return module.open(authority.root, fixed, identity), plan, identity


def _slot(authority, name="first", service="LEGACY", request="request", capacity=1):
    return {
        "slot_id": name,
        "service_kind": service,
        "request_hash": digest(request),
        "output_root": str(authority.root / "research-runs"),
        "requested_units": 1,
        "grant_capacity": capacity,
        "max_admitted_owners": 1,
        "expected_status": "REJECTED",
        "expected_code": "EXPERIMENT_BUDGET_EXCEEDED",
    }


def test_plan_authority_requires_real_frozen_driver_file(authority, tmp_path):
    auth, plan, identity = _driver(authority, tmp_path, [_slot(authority)])
    assert auth.plan_hash == digest(plan)
    with pytest.raises(ContractError, match="TRUSTED_PROTOCOL_DRIVER_REQUIRED"):
        install_execution_plan(authority.root, plan, identity)
    with pytest.raises(ContractError, match="TRUSTED_PROTOCOL_DRIVER_REQUIRED"):
        PlanAuthority(authority, auth.plan_hash, identity, seal=object())


def test_activation_cas_no_automatic_next_slot_and_ui_first_key(authority, tmp_path):
    slots = [_slot(authority, "ui-one", "TASK"), _slot(authority, "ui-two", "TASK")]
    auth, _, _ = _driver(authority, tmp_path, slots)
    first = advance_actor(auth, -1)
    with pytest.raises(ContractError, match="EXECUTION_PLAN_ACTIVATION_STALE"):
        advance_actor(auth, -1)
    with authority.transaction() as c:
        binding = bind_current_actor(
            authority.root,
            "TASK",
            digest("request"),
            authority.root / "research-runs",
            "actual-ui-random-key",
            "literal-owner",
            1,
            first,
            c,
        )
        assert binding["owner_id"] == "literal-owner"
        assert binding["slot_id"] == "ui-one"
        with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_EXHAUSTED"):
            bind_current_actor(
                authority.root,
                "TASK",
                digest("request"),
                authority.root / "research-runs",
                "another-ui-key",
                "different-owner",
                1,
                first,
                c,
            )
    with pytest.raises(ContractError, match="EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED"):
        advance_actor(auth, 0)


def test_legacy_plan_lookup_happens_before_uuid_and_returns_original_owner(authority, tmp_path):
    auth, _, _ = _driver(authority, tmp_path, [_slot(authority)])
    first = advance_actor(auth, -1)
    with authority.transaction() as c:
        prospective = authority.lookup_legacy_actor(
            c, digest("request"), authority.root / "research-runs"
        )
        assert prospective["owner_id"] is None
        assert prospective["client_key"] == digest(
            {"plan_hash": auth.plan_hash, "slot_id": "first"}
        )
        admitted = authority.reserve(
            c,
            DATA,
            "LEGACY",
            "original-run",
            prospective["client_key"],
            digest("request"),
            [{"hypothesis_alias": "h", "definition_hash": "d" * 64}],
            service_kind="LEGACY",
            activation=first,
        )
    with authority.transaction() as c:
        repeated = authority.lookup_legacy_actor(
            c, digest("request"), authority.root / "research-runs"
        )
        assert repeated["owner_id"] == "original-run"
        assert repeated["client_key"] == prospective["client_key"]
    assert admitted["debit"] == 1
    assert history(authority)["admitted_units"] == 1


def test_probe_capacity_zero_cannot_be_relabelled_budget_rejection(authority, tmp_path):
    auth, _, _ = _driver(authority, tmp_path, [_slot(authority, capacity=0)])
    advance_actor(auth, -1)
    with authority.transaction() as c:
        binding = authority.lookup_legacy_actor(
            c, digest("request"), authority.root / "research-runs"
        )
        with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_EXHAUSTED"):
            authority.reserve(
                c,
                DATA,
                "LEGACY",
                "run",
                binding["client_key"],
                digest("request"),
                [{"hypothesis_alias": "h", "definition_hash": "d" * 64}],
                service_kind="LEGACY",
            )
    assert history(authority)["admitted_units"] == 0


def test_expired_browser_instance_cannot_claim_current_actor(authority, tmp_path):
    before = capture_activation(authority.root)
    assert before is None
    auth, _, _ = _driver(authority, tmp_path, [_slot(authority, service="TASK")])
    advance_actor(auth, -1)
    with pytest.raises(ContractError, match="EXECUTION_PLAN_ACTIVATION_STALE"):
        verify_activation(authority.root, before)


def test_zero_units_need_real_replay_request(authority):
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="ADMISSION_INTEGRITY_ERROR"):
            authority.reserve(c, DATA, "LEGACY", "free", "free", "a" * 64, [])
    assert history(authority)["admitted_units"] == 0


def test_whole_materialized_last_record_cannot_be_deleted_then_repaired(authority):
    one, two = reserve(authority, "one"), reserve(authority, "two")
    _, first = _claim(authority, one)
    _claim(authority, two)
    authority.materialize()
    target = authority.root / "research-runs/trials.jsonl"
    damaged = canonical(first) + b"\n"
    target.write_bytes(damaged)
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        authority.materialize()
    assert target.read_bytes() == damaged


def test_publisher_drains_a_later_committed_outbox_without_false_corruption(authority, monkeypatch):
    from contextlib import contextmanager

    from aqrp.experiments import ledger

    first, second = reserve(authority, "one"), reserve(authority, "two")
    with authority.transaction() as c:
        authority.queue_projection(
            c, authority.root / "one.json", b'{"literal":1}', first["admission_id"]
        )
    original_mutex = ledger.mutex
    entered = False

    @contextmanager
    def interleaved(path, timeout=5):
        import inspect

        nonlocal entered
        reading = any(frame.function == "_projection_bytes" for frame in inspect.stack())
        if not entered and not reading:
            entered = True
            # The second transaction commits after publisher A took its DB
            # snapshot, but before A acquires any file lock.
            with authority.transaction() as c:
                authority.queue_projection(
                    c, authority.root / "two.json", b'{"literal":2}', second["admission_id"]
                )
        with original_mutex(path, timeout=timeout):
            yield

    monkeypatch.setattr(ledger, "mutex", interleaved)
    authority.materialize()
    assert (authority.root / "one.json").read_bytes() == b'{"literal":1}'
    assert (authority.root / "two.json").read_bytes() == b'{"literal":2}'
    with authority.transaction() as c:
        authority.verify(c, require_projections=True)


@pytest.mark.parametrize("kind", ["event", "domain", "units", "outbox", "claim"])
def test_recomputed_partial_db_tampering_still_fails_original_history(authority, kind):
    admission = reserve(authority, "run")
    _claim(authority, admission)
    authority.materialize()
    c = sqlite3.connect(authority.db)
    if kind == "event":
        c.execute("UPDATE admission_events SET previous_hash=? WHERE seq=1", ("f" * 64,))
    elif kind == "domain":
        c.execute("DELETE FROM budget_domains")
    elif kind == "units":
        item = {"hypothesis_alias": "altered", "definition_hash": "d" * 64}
        c.execute(
            "UPDATE admission_units SET payload=?,hash=?", (canonical(item).decode(), digest(item))
        )
    elif kind == "outbox":
        c.execute(
            "UPDATE admission_outbox SET content=?,hash=?",
            (b"{}\n", hashlib.sha256(b"{}\n").hexdigest()),
        )
    else:
        item = json.loads(c.execute("SELECT payload FROM trial_claims").fetchone()[0])
        item["run_id"] = "forged"
        c.execute(
            "UPDATE trial_claims SET run_id=?,payload=?,hash=?",
            ("forged", canonical(item).decode(), digest(item)),
        )
    c.commit()
    c.close()
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        reserve(authority, "next")


@pytest.mark.parametrize("index", [-1, 1, "0"])
def test_claim_cannot_use_unknown_unit(authority, index):
    admission = reserve(authority, "run")
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
            authority.claim(
                c,
                admission["admission_id"],
                index,
                authority.root / "research-runs",
                "run",
                admission["request_hash"],
                "e" * 64,
            )


def test_legacy_claim_cannot_lend_another_run_or_config(authority):
    admission = reserve(authority, "run")
    for run, config in (("fake", admission["request_hash"]), ("run", "f" * 64)):
        with authority.transaction() as c:
            with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
                authority.claim(
                    c,
                    admission["admission_id"],
                    0,
                    authority.root / "research-runs",
                    run,
                    config,
                    "e" * 64,
                )


def test_rejected_reservation_has_no_claim(authority):
    reserve(authority, "full", 12)
    rejected = reserve(authority, "rejected")
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
            authority.claim(
                c,
                rejected["admission_id"],
                0,
                authority.root / "research-runs",
                "rejected",
                rejected["request_hash"],
                "e" * 64,
            )


def _old_authority(tmp_path):
    root = tmp_path / "old-workspace"
    (root / "task-control").mkdir(parents=True)
    c = sqlite3.connect(root / "task-control/tasks.sqlite", isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE workspace(id TEXT)")
    c.execute("INSERT INTO workspace VALUES ('old')")
    c.execute("CREATE TABLE old_marker(value TEXT)")
    raw = b'{"original":"preserved"}'
    original = root / "research-runs/old.json"
    original.parent.mkdir()
    original.write_bytes(raw)
    # A legacy chain exists, but its explicitly verified empty content is not
    # interpreted as proof that no historical admissions occurred.
    (root / "research-runs/trials.jsonl").write_bytes(b"")
    evidence = {
        "files": [
            {"path": str(original), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        ]
    }
    return BudgetAuthority(root), c, evidence, original, raw


def _migration_record(owner, units=1, decision="ADMITTED"):
    return {
        "data_hash": DATA,
        "owner_kind": "LEGACY",
        "owner_id": owner,
        "key": owner,
        "request_hash": digest(owner),
        "units": [
            {"hypothesis_alias": f"h-{i}", "definition_hash": digest(i)} for i in range(units)
        ],
        "family_id": "original",
        "family_limit": 12,
        "_migration_decision": decision,
    }


def test_complete_migration_retains_old_bytes_and_original_rejected_count(tmp_path):
    budget, c, evidence, original, raw = _old_authority(tmp_path)
    result = {
        "complete": True,
        "records": [
            _migration_record("eleven", 11),
            _migration_record("rejected-two", 2, "REJECTED"),
        ],
        "evidence": evidence,
        "projections": [
            {
                "owner_kind": "LEGACY",
                "owner_id": "eleven",
                "path": str(original),
                "kind": "SIDECAR",
                "content_hex": raw.hex(),
            }
        ],
    }
    c.execute("BEGIN IMMEDIATE")
    budget.initialize(c, "old", history_verifier=lambda c: result)
    c.commit()
    c.close()
    assert original.read_bytes() == raw
    stats = history(budget)
    assert (stats["admitted_units"], stats["requested_units"], stats["rejected_units"]) == (
        11,
        13,
        2,
    )
    assert all(a["migrated"] for a in stats["admissions"])
    assert reserve(budget, "no-refund")["decision"] == "REJECTED"
    assert history(budget)["admitted_units"] == 11


def test_migration_verifies_original_files_not_just_verifier_boolean(tmp_path):
    budget, c, evidence, original, raw = _old_authority(tmp_path)
    original.write_bytes(raw + b"changed")
    result = {"complete": True, "records": [], "evidence": evidence}
    c.execute("BEGIN IMMEDIATE")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        budget.initialize(c, "old", history_verifier=lambda c: result)
    c.rollback()
    c.close()
    assert original.read_bytes() == raw + b"changed"
    assert not budget.anchor.exists()


def test_migration_parent_trial_claim_is_charged_once(tmp_path):
    budget, c, evidence, original, raw = _old_authority(tmp_path)
    record = _migration_record("legacy-owner")
    payload = {"run_id": "legacy-owner", "hypothesis": "h-0"}
    trial = {
        "seq": 0,
        "previous": "0" * 64,
        "recorded_at": "2026-10-25T00:00:00.000000+00:00",
        "kind": "TRIAL_ATTEMPT",
        "payload": payload,
    }
    trial["hash"] = digest(trial)
    path = budget.root / "research-runs/trials.jsonl"
    trial_bytes = canonical(trial) + b"\n"
    path.write_bytes(trial_bytes)
    evidence["files"].append(
        {
            "path": str(path),
            "sha256": hashlib.sha256(trial_bytes).hexdigest(),
            "bytes": len(trial_bytes),
        }
    )
    result = {
        "complete": True,
        "records": [record],
        "evidence": evidence,
        "claims": [
            {
                "owner_kind": "LEGACY",
                "owner_id": "legacy-owner",
                "ordinal": 0,
                "ledger_root": str(path.parent),
                "run_id": "legacy-owner",
                "config_hash": digest("legacy-owner"),
                "lineage_hash": "e" * 64,
            }
        ],
        "projections": [
            {
                "owner_kind": "LEGACY",
                "owner_id": "legacy-owner",
                "path": str(path),
                "kind": "TRIAL",
                "content_hex": trial_bytes.hex(),
            }
        ],
    }
    c.execute("BEGIN IMMEDIATE")
    budget.initialize(c, "old", history_verifier=lambda c: result)
    c.commit()
    c.close()
    assert history(budget)["admitted_units"] == 1
    assert history(budget)["registered_trials"] == 1
    assert path.read_bytes() == trial_bytes


def _task_stub(authority, monkeypatch):
    """Only status/core-proof collaborators are stubbed for pure plan unit tests.

    Real P3/P4/P5 cancellation/finance coverage lives in integration tests and
    the fixed SDK. These literal unit answers test source/epoch/hash binding.
    """
    from aqrp.services import tasks

    with authority.transaction() as c:
        c.execute(
            "CREATE TABLE tasks(id TEXT PRIMARY KEY,key TEXT,raw TEXT,hash TEXT,status TEXT,owner TEXT,epoch INTEGER,cancel INTEGER,completion TEXT,error TEXT)"
        )
        c.execute(
            "CREATE TABLE slots(task TEXT,slot TEXT,binding TEXT,state TEXT,PRIMARY KEY(task,slot))"
        )

    class Status:
        def __init__(self, root):
            self.root = root

        def status(self, owner):
            with authority.transaction() as c:
                row = c.execute("SELECT status FROM tasks WHERE id=?", (owner,)).fetchone()
                return {"status": row[0]}

    manifest = {"run_id": "literal-child", "status": "SUCCEEDED", "files": []}
    monkeypatch.setattr(tasks, "TaskService", Status)
    monkeypatch.setattr(tasks, "read_core", lambda binding: (manifest, {}))

    def make(owner, request, status="SUCCEEDED"):
        raw = canonical(request)
        directory = authority.root / "tasks" / owner
        directory.mkdir(parents=True)
        (directory / "request.json").write_bytes(raw)
        binding = {
            "child_run_id": "literal-child",
            "physical_ledger_root": str(authority.root / "research-runs"),
        }
        proof = {
            "task_id": owner,
            "config_hash": digest(request),
            "claim_epoch": 0,
            "resolved_plan_sha256": None,
            "core_proofs": {
                "R": {
                    "binding_hash": digest(binding),
                    "manifest_hash": digest(manifest),
                    "status": "SUCCEEDED",
                }
            },
        }
        proof_raw = canonical(proof)
        (directory / "completion.json").write_bytes(proof_raw)
        pointer = canonical(
            {"file": "completion.json", "sha256": hashlib.sha256(proof_raw).hexdigest()}
        ).decode()
        with authority.transaction() as c:
            c.execute(
                "INSERT INTO tasks VALUES (?,?,?,?,?,NULL,0,0,?,NULL)",
                (owner, owner, raw.decode(), digest(request), "QUEUED", pointer),
            )
            if status == "SUCCEEDED":
                c.execute(
                    "INSERT INTO slots VALUES (?,'R',?,'VERIFIED_SUCCESS')",
                    (owner, canonical(binding).decode()),
                )
        return directory / "completion.json"

    return make


def test_derived_replay_uses_trusted_original_owner_not_caller_source(
    authority, tmp_path, monkeypatch
):
    make = _task_stub(authority, monkeypatch)
    source_request = {"kind": "research", "literal": "source-original"}
    source_slot = _slot(authority, "source", "TASK")
    source_slot.update(request_hash=digest(source_request), expected_status="SUCCEEDED")
    source_slot.pop("expected_code")
    template = {
        "kind": "replay",
        "payload": {"source_task": "$SOURCE_TASK", "profile": "P5_NUMERICAL"},
        "frozen_header": "original",
    }
    replay = {
        "slot_id": "cancel-replay",
        "service_kind": "TASK_REPLAY",
        "request_hash": None,
        "output_root": str(authority.root / "replay-runs"),
        "requested_units": 0,
        "grant_capacity": 0,
        "max_admitted_owners": 1,
        "expected_status": "CANCELLED",
        "source_slot": "source",
        "originalsource_request_hash": digest(source_request),
        "profile": "P5_NUMERICAL",
        "request_template": template,
    }
    auth, _, _ = _driver(authority, tmp_path, [source_slot, replay])
    first = advance_actor(auth, -1)
    proof = make("source-owner", source_request)
    with authority.transaction() as c:
        admitted = authority.reserve(
            c,
            DATA,
            "TASK",
            "source-owner",
            "source-owner",
            digest(source_request),
            [{"hypothesis_alias": "h", "definition_hash": "d" * 64}],
            service_kind="TASK",
            activation=first,
        )
        c.execute("UPDATE tasks SET status='SUCCEEDED' WHERE id='source-owner'")
    complete_actor(
        auth,
        {
            "owner_id": "source-owner",
            "status": "SUCCEEDED",
            "evidence": [
                {"path": str(proof), "sha256": hashlib.sha256(proof.read_bytes()).hexdigest()}
            ],
        },
    )
    second = advance_actor(auth, 0)
    actual = {**template, "payload": {"source_task": "source-owner", "profile": "P5_NUMERICAL"}}
    make("replay-owner", actual, "CANCELLED")
    with authority.transaction() as c:
        result = authority.reserve(
            c,
            DATA,
            "TASK",
            "replay-owner",
            "replay-owner",
            digest(actual),
            [],
            service_kind="TASK_REPLAY",
            output_root=authority.root / "replay-runs",
            activation=second,
        )
        c.execute("UPDATE tasks SET status='CANCELLED' WHERE id='replay-owner'")
        assert result["debit"] == 0
    assert history(authority)["admitted_units"] == 1
    # A late original key returns only its original owner; it never acquires the
    # current replay slot or creates a second research debit.
    with authority.transaction() as c:
        old = bind_current_actor(
            authority.root,
            "TASK",
            digest(source_request),
            authority.root / "research-runs",
            "source-owner",
            "source-owner",
            1,
            connection=c,
        )
        assert old["owner_id"] == "source-owner"
        assert old["activation"] == first
        with pytest.raises(ContractError, match="EXECUTION_PLAN_ACTIVATION_STALE"):
            authority.reserve(
                c,
                DATA,
                "TASK",
                "source-owner",
                "source-owner",
                digest(source_request),
                admitted["units"],
                service_kind="TASK",
                activation=first,
            )
    changed = {**actual, "payload": {"source_task": "other-valid-owner", "profile": "P5_NUMERICAL"}}
    make("forged-replay", changed, "CANCELLED")
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT"):
            authority.reserve(
                c,
                DATA,
                "TASK",
                "forged-replay",
                "forged-replay",
                digest(changed),
                [],
                service_kind="TASK_REPLAY",
                output_root=authority.root / "replay-runs",
                activation=second,
            )


@pytest.mark.parametrize(
    "target", ["request", "root", "units", "service", "missing-key", "missing-owner"]
)
def test_active_actor_binding_rejects_incomplete_or_changed_identity(authority, tmp_path, target):
    auth, _, _ = _driver(authority, tmp_path, [_slot(authority, service="TASK")])
    advance_actor(auth, -1)
    args = {
        "workspace_root": authority.root,
        "service_kind": "TASK",
        "canonical_request_hash": digest("request"),
        "physical_output_root": authority.root / "research-runs",
        "client_key": "literal-key",
        "owner_id": "owner",
        "units_count": 1,
    }
    if target == "request":
        args["canonical_request_hash"] = digest("altered")
    elif target == "root":
        args["physical_output_root"] = authority.root / "other"
    elif target == "units":
        args["units_count"] = 2
    elif target == "service":
        args["service_kind"] = "LEGACY"
    elif target == "missing-key":
        args["client_key"] = None
    else:
        args["owner_id"] = None
    with pytest.raises(ContractError):
        bind_current_actor(**args)
    assert history(authority)["admitted_units"] == 0


@pytest.mark.parametrize(
    "target", ["plan", "slot-set", "slot-payload", "binding", "activation", "completion"]
)
def test_plan_controls_cannot_be_silently_rewritten(authority, tmp_path, target):
    auth, _, _ = _driver(authority, tmp_path, [_slot(authority, service="TASK")])
    advance_actor(auth, -1)
    bind_current_actor(
        authority.root,
        "TASK",
        digest("request"),
        authority.root / "research-runs",
        "key",
        "owner",
        1,
    )
    c = sqlite3.connect(authority.db)
    if target == "plan":
        (authority.root / "task-control/execution-plan.json").write_bytes(b"{}")
    elif target == "slot-set":
        c.execute("DELETE FROM execution_plan_slots")
    elif target == "slot-payload":
        c.execute("UPDATE execution_plan_slots SET payload='{}'")
    elif target == "binding":
        c.execute("UPDATE execution_plan_slots SET owner_id='forged'")
    elif target == "activation":
        c.execute("UPDATE execution_plan_activations SET hash='forged'")
    else:
        c.execute("UPDATE execution_plan_activations SET completion='{}',completion_hash='forged'")
    c.commit()
    c.close()
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        capture_activation(authority.root)


def test_public_plan_objects_are_process_local_and_bad_seals_cannot_drive(authority, tmp_path):
    import pickle

    auth, plan, identity = _driver(authority, tmp_path, [_slot(authority)])
    with pytest.raises(TypeError, match="cannot be serialized"):
        pickle.dumps(auth)
    for function, args in ((advance_actor, ({}, -1)), (complete_actor, ({}, {}))):
        with pytest.raises(ContractError, match="TRUSTED_PROTOCOL_DRIVER_REQUIRED"):
            function(*args)
    # Original plan is immutable even when a trusted driver reopens it.
    spec = importlib.util.spec_from_file_location(
        "literal_reopened_driver", identity["runner_path"]
    )
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    assert driver.install(authority.root, plan, identity) == auth.plan_hash
    with pytest.raises(ContractError, match="TRUSTED_PROTOCOL_DRIVER_REQUIRED"):
        driver.open(authority.root, "f" * 64, identity)
    changed = {**plan, "purpose": "caller-relabeled"}
    with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT"):
        driver.install(authority.root, changed, identity)


def test_no_plan_binding_is_not_an_optional_token_bypass(authority):
    assert (
        bind_current_actor(authority.root, "LEGACY", digest("r"), authority.root / "research-runs")
        is None
    )
    assert verify_activation(authority.root, None) is None
    with authority.transaction() as c:
        assert authority.lookup_owner(c, "TASK", "unknown") is None
        assert authority.find_run(c, authority.root / "research-runs", "unknown") is None
        with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
            authority.get(c, "not-an-admission")


@pytest.mark.parametrize("kind", ["same-key-request", "same-key-owner"])
def test_bound_key_conflicts_cannot_claim_another_actor(authority, tmp_path, kind):
    auth, _, _ = _driver(authority, tmp_path, [_slot(authority, service="TASK")])
    advance_actor(auth, -1)
    bind_current_actor(
        authority.root,
        "TASK",
        digest("request"),
        authority.root / "research-runs",
        "key",
        "owner",
        1,
    )
    with pytest.raises(ContractError, match="ADMISSION_IDEMPOTENCY_CONFLICT"):
        bind_current_actor(
            authority.root,
            "TASK",
            digest("changed") if kind == "same-key-request" else digest("request"),
            authority.root / "research-runs",
            "key",
            "different" if kind == "same-key-owner" else "owner",
            1,
        )


def test_no_active_slot_refuses_new_entry_before_budget(authority, tmp_path):
    _driver(authority, tmp_path, [_slot(authority)])
    with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_UNAUTHORIZED"):
        bind_current_actor(
            authority.root, "LEGACY", digest("request"), authority.root / "research-runs"
        )


@pytest.mark.parametrize(
    "field,value",
    [("data_hash", "e" * 64), ("code_bundle", "e" * 64), ("admission_inputs", "caller-string")],
)
def test_managed_lineage_must_match_original_source_identity(authority, field, value):
    cat = _catalogue(authority)
    lineage = {"data_hash": DATA, "code_bundle": cat["code_bundle"]}
    lineage[field] = value
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        resolve_admission_domain(authority.root / "research-runs", lineage=lineage)


def test_snapshot_and_exposure_refs_cannot_be_swapped(authority):
    from types import SimpleNamespace

    cat = _catalogue(authority)
    snapshot = SimpleNamespace(**cat["snapshot"])
    exposure = SimpleNamespace(**cat["exposures"])
    assert (
        resolve_admission_domain(
            authority.root / "research-runs", snapshot_ref=snapshot, exposure_ref=exposure
        ).root
        == authority.root
    )
    exposure.manifest_hash = "f" * 64
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        resolve_admission_domain(
            authority.root / "research-runs", snapshot_ref=snapshot, exposure_ref=exposure
        )


def test_nested_workspace_anchor_and_foreign_input_rejected(authority):
    cat = _catalogue(authority)
    nested = authority.root / "inputs/nested"
    nested.mkdir(parents=True)
    (nested / "catalog.json").write_bytes(canonical(cat))
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        resolve_admission_domain(nested / "research-runs")


def test_bad_source_bundle_is_not_accepted_by_direct_ledger_resolver(authority):
    cat = _catalogue(authority)
    cat["code_bundle"] = "f" * 64
    cat["revision"] = digest({k: v for k, v in cat.items() if k != "revision"})
    (authority.root / "catalog.json").write_bytes(canonical(cat))
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        resolve_admission_domain(authority.root / "research-runs")


def test_queue_projection_is_immutable_and_reuses_exact_sidecar(authority):
    admitted = reserve(authority, "run")
    path = authority.root / "sidecar.json"
    with authority.transaction() as c:
        first = authority.queue_projection(c, path, b"{}", admitted["admission_id"])
        assert authority.queue_projection(c, path, b"{}", admitted["admission_id"]) == first
        with pytest.raises(ContractError, match="ADMISSION_INTEGRITY_ERROR"):
            authority.queue_projection(c, path, b'{"changed":1}', admitted["admission_id"])
        with pytest.raises(ContractError, match="ADMISSION_INTEGRITY_ERROR"):
            authority.queue_projection(
                c, path.parent.parent / "escape", b"{}", admitted["admission_id"]
            )
    authority.materialize()
    with authority.transaction() as c:
        authority.verify_admission_projections(c, admitted["admission_id"])


def test_owner_projection_verification_does_not_require_other_pending_owner(authority):
    one, two = reserve(authority, "one"), reserve(authority, "two")
    _claim(authority, one)
    authority.materialize()
    with authority.transaction() as c:
        authority.queue_projection(c, authority.root / "two.json", b"{}", two["admission_id"])
    with authority.transaction() as c:
        assert authority.verify_admission_projections(c, one["admission_id"])
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
            authority.verify_admission_projections(c, two["admission_id"])


def test_noncanonical_metadata_and_missing_original_fail_closed(tmp_path):
    from aqrp.experiments.admission import _immutable, _json, _read

    for raw in (b"not-json", b'{"a":1} ', b"{\xff}", b"[]", b"null"):
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
            _json(raw)
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        _read(tmp_path / "missing.json")
    target = tmp_path / "frozen.json"
    _immutable(target, b"{}")
    _immutable(target, b"{}")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        _immutable(target, b'{"changed":1}')
    assert target.read_bytes() == b"{}"


def test_hardlinked_path_cannot_supply_or_escape_an_admission_domain(tmp_path):
    import os

    from aqrp.experiments.admission import _guard

    source = tmp_path / "original.json"
    alias = tmp_path / "hardlink.json"
    source.write_bytes(b"{}")
    os.link(source, alias)
    with pytest.raises(ContractError, match="SIMULATION_LINK_PATH_FORBIDDEN"):
        _guard(alias)
    assert source.read_bytes() == b"{}"


def test_database_corruption_does_not_create_a_fresh_authority(authority):
    authority.db.write_bytes(b"not-a-sqlite-database")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        with authority.transaction():
            pass
    assert authority.db.read_bytes() == b"not-a-sqlite-database"


def test_authority_initialization_requires_existing_transaction_and_same_workspace(authority):
    c = sqlite3.connect(authority.db, isolation_level=None)
    with pytest.raises(ContractError, match="ADMISSION_TRANSACTION_REQUIRED"):
        authority.initialize(c, "literal-workspace")
    c.close()
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
            authority.initialize(c, "another-workspace")


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown-kind",
        "empty-owner",
        "empty-key",
        "malformed-unit",
        "duplicate-unit",
        "family-zero",
        "bad-migration-mode",
    ],
)
def test_invalid_reservation_schema_does_not_mutate_budget(authority, mutation):
    args = {
        "data_hash": DATA,
        "owner_kind": "LEGACY",
        "owner_id": "owner",
        "key": "key",
        "request_hash": "f" * 64,
        "units": [{"hypothesis_alias": "h", "definition_hash": "d" * 64}],
    }
    if mutation == "unknown-kind":
        args["owner_kind"] = "CALLER"
    elif mutation == "empty-owner":
        args["owner_id"] = ""
    elif mutation == "empty-key":
        args["key"] = ""
    elif mutation == "malformed-unit":
        args["units"] = [{"hypothesis_alias": "h"}]
    elif mutation == "duplicate-unit":
        args["units"] *= 2
    elif mutation == "family-zero":
        args["family_limit"] = 0
    else:
        args["_migration_decision"] = "ADMITTED"
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="ADMISSION_INTEGRITY_ERROR"):
            authority.reserve(c, **args)
    assert history(authority)["admitted_units"] == 0


def test_missing_anchor_table_cannot_be_recreated_as_zero(authority):
    c = sqlite3.connect(authority.db)
    c.execute("DROP TABLE admission_meta")
    c.commit()
    c.close()
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
            authority.initialize(c, "literal-workspace")


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate",
        "service",
        "negative-units",
        "two-owners",
        "outside-output",
        "unknown-terminal",
        "wrong-derived-source",
    ],
)
def test_frozen_plan_slot_schema_and_replay_source_must_be_exact(authority, tmp_path, mutation):
    slot = _slot(authority)
    slots = [slot]
    if mutation == "duplicate":
        slots.append(dict(slot))
    elif mutation == "service":
        slot["service_kind"] = "CALLER"
    elif mutation == "negative-units":
        slot["requested_units"] = -1
    elif mutation == "two-owners":
        slot["max_admitted_owners"] = 2
    elif mutation == "outside-output":
        slot["output_root"] = str(authority.root / "other")
    elif mutation == "unknown-terminal":
        slot["expected_status"] = "MAYBE"
    else:
        slot.update(source_slot="not-registered", originalsource_request_hash="a" * 64)
    with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT"):
        _driver(authority, tmp_path, slots)


def test_orphan_plan_file_blocks_unplanned_admission(authority):
    (authority.root / "task-control/execution-plan.json").write_bytes(b"{}")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        reserve(authority, "caller-omitted-plan")


def test_live_legacy_execution_cannot_claim_task_reservation(authority):
    admission = reserve(authority, "task", owner_kind="TASK")
    with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
        with authority.legacy_execution(admission["admission_id"]):
            pytest.fail("TASK reservation used as legacy")


def test_exact_claim_cannot_be_changed_after_commit(authority):
    admission = reserve(authority, "run")
    claim, record = _claim(authority, admission)
    with authority.transaction() as c:
        assert (
            authority.find_run(c, authority.root / "research-runs", "run")["admission_id"]
            == admission["admission_id"]
        )
        with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
            authority.claim(
                c,
                admission["admission_id"],
                0,
                authority.root / "research-runs",
                "run",
                admission["request_hash"],
                "different-lineage",
            )
        with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
            authority.project_trial(c, "wrong-admission", claim, record["payload"])
        with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
            authority.project_trial(
                c, admission["admission_id"], claim, {**record["payload"], "literal": "changed"}
            )


@pytest.mark.parametrize("remnant", ["database", "sidecars", "task-request", "corrupt-database"])
def test_deleting_catalog_and_anchor_cannot_downgrade_managed_history(authority, remnant):
    _catalogue(authority)
    (authority.root / "catalog.json").unlink()
    authority.anchor.unlink()
    if remnant == "sidecars":
        authority.db.unlink()
        (authority.root / "task-control/admissions").mkdir()
    elif remnant == "task-request":
        authority.db.unlink()
        path = authority.root / "tasks/original-owner/request.json"
        path.parent.mkdir(parents=True)
        path.write_bytes(canonical({"schema": "task-request/1", "kind": "research"}))
    elif remnant == "corrupt-database":
        authority.db.write_bytes(b"not-sqlite")
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        resolve_admission_domain(authority.root / "research-runs")


def test_generic_queue_without_managed_data_keeps_standalone_boundary(tmp_path):
    root = tmp_path / "generic-queue"
    control = root / "task-control"
    control.mkdir(parents=True)
    c = sqlite3.connect(control / "tasks.sqlite")
    c.execute("CREATE TABLE tasks(raw TEXT)")
    c.execute("INSERT INTO tasks VALUES (?)", (canonical({"kind": "research"}).decode(),))
    c.commit()
    c.close()
    assert resolve_admission_domain(root / "research-runs") is None


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "raw",
        "pointer",
        "completion",
        "core-status",
        "core-set",
        "plan-hash",
        "missing-required-slot",
        "pipeline-zero-decisions",
        "pipeline-plan-binding",
    ],
)
def test_original_terminal_proof_is_required_before_actor_completion(authority, monkeypatch, fault):
    from aqrp.experiments.admission import _task_terminal
    from aqrp.services import tasks

    make = _task_stub(authority, monkeypatch)
    request = {"kind": "research", "literal": "frozen"}
    proof = make("owner", request)
    with authority.transaction() as c:
        c.execute("UPDATE tasks SET status='SUCCEEDED' WHERE id='owner'")
    if fault == "raw":
        (proof.parent / "request.json").write_bytes(canonical({**request, "literal": "changed"}))
    elif fault == "pointer":
        with authority.transaction() as c:
            c.execute(
                "UPDATE tasks SET completion=?",
                (canonical({"file": "../completion.json", "sha256": "f" * 64}).decode(),),
            )
    elif fault == "completion":
        proof.write_bytes(b"{}")
    elif fault == "core-status":
        monkeypatch.setattr(tasks, "read_core", lambda binding: ({"status": "FAILED"}, {}))
    elif fault in (
        "core-set",
        "missing-required-slot",
        "pipeline-zero-decisions",
        "pipeline-plan-binding",
    ):
        value = json.loads(proof.read_bytes())
        if fault == "core-set":
            value["core_proofs"] = {}
        elif fault == "missing-required-slot":
            value["core_proofs"] = {}
            with authority.transaction() as c:
                c.execute("DELETE FROM slots")
        else:
            request = {**request, "kind": "engineering_pipeline"}
            request_raw = canonical(request)
            (proof.parent / "request.json").write_bytes(request_raw)
            with authority.transaction() as c:
                c.execute("UPDATE tasks SET raw=?,hash=?", (request_raw.decode(), digest(request)))
            value["config_hash"] = digest(request)
            resolved = {
                "task_config_hash": digest(request),
                "slots": {"R": "literal-child"},
                "decision_count": 0,
            }
            if fault == "pipeline-plan-binding":
                resolved["task_config_hash"] = "f" * 64
            plan_bytes = canonical(resolved)
            (proof.parent / "resolved-plan.json").write_bytes(plan_bytes)
            value["resolved_plan_sha256"] = hashlib.sha256(plan_bytes).hexdigest()
        proof_bytes = canonical(value)
        proof.write_bytes(proof_bytes)
        with authority.transaction() as c:
            c.execute(
                "UPDATE tasks SET completion=?",
                (
                    canonical(
                        {
                            "file": "completion.json",
                            "sha256": hashlib.sha256(proof_bytes).hexdigest(),
                        }
                    ).decode(),
                ),
            )
    elif fault == "plan-hash":
        (proof.parent / "resolved-plan.json").write_bytes(b"{}")
    with authority.transaction() as c:
        with pytest.raises(ContractError, match="EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED"):
            _task_terminal(
                c, authority, "unknown" if fault == "missing" else "owner", digest(request)
            )


@pytest.mark.parametrize("kind", ["engineering_pipeline", "replay"])
def test_terminal_plan_requires_the_complete_exact_slot_set(authority, monkeypatch, kind):
    from aqrp.experiments.admission import _task_terminal

    make = _task_stub(authority, monkeypatch)
    request = {"kind": kind, "literal": "frozen"}
    proof = make("owner", request)
    expected = ["R", "B", "P:0"] if kind == "engineering_pipeline" else ["E", "P:0"]
    binding = {
        "child_run_id": "literal-child",
        "physical_ledger_root": str(authority.root / "research-runs"),
    }
    manifest = {"run_id": "literal-child", "status": "SUCCEEDED", "files": []}
    resolved = {
        "task_config_hash": digest(request),
        "slots": {name: "literal-child" for name in expected},
        "decision_count": 1,
    }
    plan_bytes = canonical(resolved)
    (proof.parent / "resolved-plan.json").write_bytes(plan_bytes)
    value = json.loads(proof.read_bytes())
    value["core_proofs"] = {
        name: {
            "binding_hash": digest(binding),
            "manifest_hash": digest(manifest),
            "status": "SUCCEEDED",
        }
        for name in expected
    }
    value["resolved_plan_sha256"] = hashlib.sha256(plan_bytes).hexdigest()
    proof_bytes = canonical(value)
    proof.write_bytes(proof_bytes)
    with authority.transaction() as c:
        c.execute(
            "UPDATE tasks SET status='SUCCEEDED',completion=?",
            (
                canonical(
                    {"file": "completion.json", "sha256": hashlib.sha256(proof_bytes).hexdigest()}
                ).decode(),
            ),
        )
        c.execute("DELETE FROM slots")
        for name in expected:
            c.execute(
                "INSERT INTO slots VALUES (?,?,?,'VERIFIED_SUCCESS')",
                ("owner", name, canonical(binding).decode()),
            )
        assert _task_terminal(c, authority, "owner", digest(request))["status"] == "SUCCEEDED"


def _charged_legacy_plan(authority, tmp_path, monkeypatch):
    from aqrp.experiments.ledger import ExperimentLedger

    full = _slot(authority, "full", request="full")
    full.update(requested_units=12, grant_capacity=12, expected_status="SUCCEEDED")
    full.pop("expected_code")
    probe = _slot(authority, "expected-refusal", request="probe", capacity=0)
    auth, _, _ = _driver(authority, tmp_path, [full, probe])
    advance_actor(auth, -1)
    with authority.transaction() as c:
        binding = authority.lookup_legacy_actor(c, digest("full"), authority.root / "research-runs")
        authority.reserve(
            c,
            DATA,
            "LEGACY",
            "original-full-owner",
            binding["client_key"],
            digest("full"),
            [{"hypothesis_alias": f"h-{i}", "definition_hash": digest(i)} for i in range(12)],
            service_kind="LEGACY",
        )
    source = authority.root / "literal-terminal-evidence.json"
    source.write_bytes(b'{"original":"terminal"}')
    evidence = [{"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]
    # Pure authority tests provide an independently declared terminal collaborator.
    # The actual original CLI/P3/P5 chain is separately executed in integration.
    monkeypatch.setattr(
        ExperimentLedger, "verify", lambda self, owner: {"run_id": owner, "status": "SUCCEEDED"}
    )
    return auth, evidence


def test_expected_rejection_actor_uses_shared_cap_then_can_finish_exactly(
    authority, tmp_path, monkeypatch
):
    auth, evidence = _charged_legacy_plan(authority, tmp_path, monkeypatch)
    complete_actor(
        auth, {"owner_id": "original-full-owner", "status": "SUCCEEDED", "evidence": evidence}
    )
    advance_actor(auth, 0)
    with authority.transaction() as c:
        binding = authority.lookup_legacy_actor(
            c, digest("probe"), authority.root / "research-runs"
        )
        denied = authority.reserve(
            c,
            DATA,
            "LEGACY",
            "probe-owner",
            binding["client_key"],
            digest("probe"),
            [{"hypothesis_alias": "h", "definition_hash": digest("h")}],
            service_kind="LEGACY",
        )
    assert (denied["decision"], denied["code"], denied["debit"]) == (
        "REJECTED",
        "EXPERIMENT_BUDGET_EXCEEDED",
        0,
    )
    receipt = {"owner_id": "probe-owner", "status": "REJECTED", "evidence": evidence}
    assert complete_actor(auth, receipt) == receipt
    assert complete_actor(auth, receipt) == receipt
    with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_UNAUTHORIZED"):
        advance_actor(auth, 1)
    assert history(authority)["admitted_units"] == 12


@pytest.mark.parametrize(
    "fault", ["wrong-owner", "wrong-status", "empty-evidence", "changed-bytes", "outside-root"]
)
def test_actor_completion_cannot_accept_a_label_without_original_evidence(
    authority, tmp_path, monkeypatch, fault
):
    auth, evidence = _charged_legacy_plan(authority, tmp_path, monkeypatch)
    receipt = {"owner_id": "original-full-owner", "status": "SUCCEEDED", "evidence": evidence}
    if fault == "wrong-owner":
        receipt["owner_id"] = "not-the-bound-owner"
    elif fault == "wrong-status":
        receipt["status"] = "FAILED"
    elif fault == "empty-evidence":
        receipt["evidence"] = []
    elif fault == "changed-bytes":
        Path(evidence[0]["path"]).write_bytes(b'{"changed":"terminal"}')
    else:
        outside = tmp_path / "outside.json"
        outside.write_bytes(b"{}")
        receipt["evidence"] = [{"path": str(outside), "sha256": hashlib.sha256(b"{}").hexdigest()}]
    with pytest.raises(ContractError, match="EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED"):
        complete_actor(auth, receipt)
    with pytest.raises(ContractError, match="EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED"):
        advance_actor(auth, 0)


def test_actor_cannot_finish_before_current_slot_is_bound(authority, tmp_path):
    auth, _, _ = _driver(authority, tmp_path, [_slot(authority)])
    with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_UNAUTHORIZED"):
        complete_actor(auth, {})
    advance_actor(auth, -1)
    with pytest.raises(ContractError, match="EXECUTION_PLAN_PREVIOUS_ACTOR_UNVERIFIED"):
        complete_actor(auth, {})
