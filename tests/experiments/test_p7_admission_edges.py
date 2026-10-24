"""Additional fail-closed controls on complete but inconsistent authority states."""

import json
import sqlite3
from pathlib import Path

import pytest
from test_p7_admission import _catalogue, _claim, reserve
from test_p7_admission import authority as authority

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments import admission


@pytest.mark.parametrize("same", [True, False])
def test_immutable_publisher_race_checks_the_winners_original_bytes(tmp_path, monkeypatch, same):
    target = tmp_path / "frozen.json"
    original_open = Path.open
    winner = b"{}" if same else b'{"different":1}'

    def race(path, mode="r", *args, **kwargs):
        if path == target and mode == "xb":
            with original_open(path, "wb") as stream:
                stream.write(winner)
            raise FileExistsError("literal competing publisher")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", race)
    if same:
        admission._immutable(target, b"{}")
    else:
        with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
            admission._immutable(target, b"{}")
    assert target.read_bytes() == winner


@pytest.mark.parametrize(
    "fault",
    [
        "meta",
        "anchor",
        "admission-column",
        "debit-definition",
        "unit-hash",
        "claim-hash",
        "domain-hash",
    ],
)
def test_valid_hashes_do_not_excuse_missing_or_inconsistent_authority_fields(authority, fault):
    owner = reserve(authority, "owner")
    _claim(authority, owner)
    c = sqlite3.connect(authority.db)
    if fault == "meta":
        c.execute("DELETE FROM admission_meta")
    elif fault == "anchor":
        authority.anchor.write_bytes(b"{}")
    elif fault == "admission-column":
        c.execute("UPDATE admissions SET owner_id='other-owner'")
    elif fault == "debit-definition":
        value = json.loads(c.execute("SELECT payload FROM admissions").fetchone()[0])
        value["debit"] = 2  # Independent literal: one reserved unit cannot debit two.
        c.execute(
            "UPDATE admissions SET debit=2,payload=?,hash=?",
            (canonical(value).decode(), digest(value)),
        )
    elif fault == "unit-hash":
        c.execute("UPDATE admission_units SET hash='different'")
    elif fault == "claim-hash":
        c.execute("UPDATE trial_claims SET hash='different'")
    else:
        c.execute("UPDATE budget_domains SET hash='different'")
    c.commit()
    c.close()
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        reserve(authority, "must-not-enter")


def test_authenticated_outbox_still_cannot_publish_outside_workspace(authority, tmp_path):
    owner = reserve(authority, "owner")
    path = authority.root / "frozen.json"
    with authority.transaction() as c:
        authority.queue_projection(c, path, b"{}", owner["admission_id"])
    c = sqlite3.connect(authority.db)
    outside = str(tmp_path / "outside.json")
    c.execute("UPDATE admission_outbox SET path=?", (outside,))
    seq, previous, kind, payload, _ = c.execute(
        "SELECT * FROM admission_events ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    payload = json.loads(payload)
    payload["path"] = outside
    body = {"seq": seq, "previous_hash": previous, "kind": kind, "payload": payload}
    c.execute(
        "UPDATE admission_events SET payload=?,hash=? WHERE seq=?",
        (canonical(payload).decode(), digest(body), seq),
    )
    c.commit()
    c.close()
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        authority.materialize()
    assert not Path(outside).exists()


def test_complete_hash_valid_trial_with_wrong_sequence_is_not_a_valid_projection(authority):
    owner = reserve(authority, "owner")
    with authority.transaction() as c:
        authority.claim(
            c,
            owner["admission_id"],
            0,
            authority.root / "research-runs",
            "owner",
            owner["request_hash"],
            "e" * 64,
        )
        record = {
            "seq": 9,
            "previous": "0" * 64,
            "recorded_at": "2026-10-25T00:00:00.000000+00:00",
            "kind": "TRIAL_ATTEMPT",
            "payload": {"run_id": "owner", "hypothesis": "h-0"},
        }
        record["hash"] = digest(record)
        authority.queue_projection(
            c,
            authority.root / "research-runs/trials.jsonl",
            canonical(record) + b"\n",
            owner["admission_id"],
            kind="TRIAL",
        )
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        authority.materialize()


@pytest.mark.parametrize(
    "fault",
    ["no-tables", "no-slot", "different-run", "different-config", "not-running", "no-owner"],
)
def test_task_claim_requires_the_actual_running_owner_and_original_r_binding(authority, fault):
    request = {"kind": "research", "literal": "frozen"}
    owner = reserve(authority, "task", owner_kind="TASK", request_hash=digest(request))
    with authority.transaction() as c:
        if fault != "no-tables":
            c.execute(
                "CREATE TABLE tasks(id TEXT,key TEXT,raw TEXT,hash TEXT,status TEXT,owner TEXT,epoch INTEGER)"
            )
            c.execute("CREATE TABLE slots(task TEXT,slot TEXT,binding TEXT)")
            c.execute(
                "INSERT INTO tasks VALUES ('task','key-task',?,?,'RUNNING','actual-owner',1)",
                (canonical(request).decode(), digest(request)),
            )
            if fault != "no-slot":
                binding = {
                    "child_run_id": "child",
                    "physical_ledger_root": str(authority.root / "research-runs"),
                    "core_config_hash": "c" * 64,
                }
                c.execute("INSERT INTO slots VALUES ('task','R',?)", (canonical(binding).decode(),))
            if fault == "not-running":
                c.execute("UPDATE tasks SET status='CANCELLED'")
            elif fault == "no-owner":
                c.execute("UPDATE tasks SET owner=NULL")
        with pytest.raises(ContractError, match="ADMISSION_OWNERSHIP_CONFLICT"):
            authority.claim(
                c,
                owner["admission_id"],
                0,
                authority.root / "research-runs",
                "wrong" if fault == "different-run" else "child",
                "wrong" if fault == "different-config" else "c" * 64,
                "e" * 64,
            )


def test_unowned_foreign_trial_file_cannot_be_adopted_as_empty_budget(authority):
    path = authority.root / "research-runs/trials.jsonl"
    path.parent.mkdir()
    path.write_bytes(b'{"unowned":"original"}\n')
    with pytest.raises(ContractError, match="ADMISSION_HISTORY_UNVERIFIED"):
        reserve(authority, "new")
    assert path.read_bytes() == b'{"unowned":"original"}\n'


def test_catalogue_hash_cannot_authorize_an_input_outside_its_physical_workspace(authority):
    cat = _catalogue(authority)
    cat["snapshot"]["root"] = str(authority.root.parent / "outside-input")
    cat["revision"] = digest({k: v for k, v in cat.items() if k != "revision"})
    (authority.root / "catalog.json").write_bytes(canonical(cat))
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        admission.resolve_admission_domain(authority.root / "research-runs")


@pytest.mark.parametrize(
    "fault",
    [
        "missing-source",
        "missing-binding",
        "changed-original",
        "nonterminal-source",
        "changed-template",
    ],
)
def test_replay_derivation_unit_refuses_incomplete_original_source_evidence(
    authority, monkeypatch, fault
):
    """Pure derivation guard tests; full public replay uses real source proofs elsewhere."""
    spec = {"slot_id": "source", "service_kind": "TASK", "request_hash": "a" * 64}
    slot = {
        "source_slot": "source",
        "originalsource_request_hash": "a" * 64,
        "profile": "P5_NUMERICAL",
        "request_template": {
            "kind": "replay",
            "payload": {"source_task": "$SOURCE_TASK", "profile": "P5_NUMERICAL"},
        },
    }
    if fault == "changed-original":
        spec["request_hash"] = "b" * 64
    if fault == "changed-template":
        slot["request_template"]["payload"]["source_task"] = "caller-chosen"
    monkeypatch.setattr(
        admission,
        "_task_terminal",
        lambda *args: {"status": "CANCELLED" if fault == "nonterminal-source" else "SUCCEEDED"},
    )
    with authority.transaction() as c:
        if fault != "missing-source":
            binding = (
                None
                if fault == "missing-binding"
                else canonical({"owner_id": "actual-bound-source"}).decode()
            )
            c.execute(
                "INSERT INTO execution_plan_slots(slot,ordinal,payload,hash,binding) VALUES ('source',0,?,?,?)",
                (canonical(spec).decode(), digest(spec), binding),
            )
        with pytest.raises(ContractError, match="EXECUTION_PLAN_SLOT_IDENTITY_CONFLICT"):
            admission._resolved_slot_request(c, authority, slot, None)


def test_input_and_output_from_two_distinct_managed_workspaces_cannot_mix(authority, tmp_path):
    from types import SimpleNamespace

    cat = _catalogue(authority)
    other = tmp_path / "other-managed-workspace"
    other.mkdir()
    independent = {
        **cat,
        "snapshot": {**cat["snapshot"], "root": str(other / "inputs/snapshot")},
        "exposures": {**cat["exposures"], "root": str(other / "inputs/exposures")},
    }
    independent["revision"] = digest({k: v for k, v in independent.items() if k != "revision"})
    (other / "catalog.json").write_bytes(canonical(independent))
    with pytest.raises(ContractError, match="ADMISSION_DOMAIN_CONFLICT"):
        admission.resolve_admission_domain(
            authority.root / "research-runs",
            snapshot_ref=SimpleNamespace(**independent["snapshot"]),
        )
