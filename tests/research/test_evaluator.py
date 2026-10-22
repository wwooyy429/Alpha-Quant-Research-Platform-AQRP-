"""Control logic tests; mocks are never described as real deployed OS isolation."""

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger, append_chain, read_chain
from aqrp.validation.approvals import propose, record_decision
from aqrp.validation.evaluator import OperatorPolicy, TestEvaluator, identity, seal, verify_seal


def test_no_deployment_denies_before_callback(tmp_path):
    e = TestEvaluator(tmp_path / "control")
    with pytest.raises(ContractError, match="UNVERIFIED_ISOLATION"):
        e.process({}, lambda: pytest.fail("private data must not load"), purpose="FINAL_TEST")
    assert not e.root.exists()
    with pytest.raises(ContractError, match="INVALID_TEST_PURPOSE"):
        e.process({}, lambda: {}, purpose="development")
    root = tmp_path / "host"
    root.mkdir()
    key = root / "key"
    key.write_bytes(b"test-only-no-real-secret" * 2)
    policy = OperatorPolicy(
        root,
        key,
        evaluator="deliberately-not-current-identity",
        research="research",
        auditor="auditor",
        trusted_owner="owner",
    )
    with pytest.raises(ContractError, match="WRONG_EVALUATOR_PRINCIPAL"):
        policy.verify_host()
    assert identity()


def test_seal_and_single_consumption_across_renames(tmp_path):
    key = b"engineering-test-only-key-material-123456"
    envelope = seal({"a": 1}, key)
    assert verify_seal(envelope, key) == {"a": 1}
    envelope["payload"]["a"] = 2
    with pytest.raises(ContractError, match="OPERATOR_SEAL_MISMATCH"):
        verify_seal(envelope, key)
    with pytest.raises(ContractError, match="INVALID_OPERATOR_KEY"):
        seal({}, b"short")
    e = TestEvaluator(tmp_path)
    bindings = {"holdout_lineage_id": "public-synthetic-holdout"}
    r = e.process(bindings, lambda: {"secret_metric": 0.9}, purpose="ENGINEERING_DEMO")
    assert not r["independence_verified"] and "secret_metric" not in r and "path" not in r
    assert r["request_id"]
    with pytest.raises(ContractError, match="TEST_ALREADY_CONSUMED"):
        e.process({**bindings, "family": "renamed"}, lambda: {}, purpose="ENGINEERING_DEMO")
    assert e.recover() == 0
    assert read_chain(tmp_path / "access.jsonl")[-1]["kind"] == "REJECTED_REPEAT"


def test_failure_crash_and_concurrent_reservation(tmp_path):
    e = TestEvaluator(tmp_path)

    def fail():
        raise KeyboardInterrupt()

    with pytest.raises(KeyboardInterrupt):
        e.process({"holdout_lineage_id": "failed"}, fail, purpose="ENGINEERING_DEMO")
    with pytest.raises(ContractError):
        e.process({"holdout_lineage_id": "failed"}, lambda: {}, purpose="ENGINEERING_DEMO")
    append_chain(
        tmp_path / "access.jsonl", "RESERVED", {"test_id": "crash", "request_id": "orphan"}
    )
    assert e.recover() == 1
    assert e.recover() == 0

    def run(_):
        try:
            e.process(
                {"holdout_lineage_id": "racing"}, lambda: {"ok": 1}, purpose="ENGINEERING_DEMO"
            )
            return "COMPLETED"
        except ContractError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(run, range(2))) == [
            "COMPLETED",
            "TEST_ALREADY_CONSUMED_OR_CONTAMINATED",
        ]


def test_authorization_evidence_and_hashes(tmp_path, monkeypatch):
    key = b"test-only-generated-fixture-key-00000000"
    (tmp_path / "key").write_bytes(key)
    p = OperatorPolicy(
        tmp_path,
        tmp_path / "key",
        evaluator="eval",
        research="research",
        auditor="auditor",
        trusted_owner="owner",
    )
    monkeypatch.setattr(p, "verify_host", lambda: key)
    from aqrp.validation import evaluator as module

    monkeypatch.setattr(module, "readonly_runtime", lambda *a: None)
    bindings = {"fixed": "protocol"}
    claims = {
        "bindings": bindings,
        "principals": p.principals,
        "scope": "FINAL_TEST",
        "profile": "P3-ISO-OS-1",
        "human_approval_record": "test-simulation",
    }

    def write():
        (tmp_path / "authorization.json").write_bytes(canonical(seal(claims, key)))

    write()
    with pytest.raises(ContractError, match="DEPLOYMENT_EVIDENCE_INCOMPLETE"):
        p.authorize(bindings)
    artifact = {"path": "evidence", "sha256": hashlib.sha256(b"fixture").hexdigest()}
    (tmp_path / "evidence").write_bytes(b"fixture")
    claims.update(
        holdout_lineage_id="mock-only",
        deployment_evidence={
            k: artifact
            for k in (
                "dual_principal_negative_controls",
                "private_seed_and_backups",
                "runtime_readonly",
                "network_and_credentials",
                "auditor_access",
            )
        },
        runtime_artifacts=[artifact],
    )
    write()
    assert p.authorize(bindings)["holdout_lineage_id"] == "mock-only"
    claims["principals"] = {**p.principals, "research": "changed-subject"}
    write()
    with pytest.raises(ContractError, match="FINAL_TEST_NOT_AUTHORIZED"):
        p.authorize(bindings)
    claims["principals"] = p.principals
    write()
    e = TestEvaluator(tmp_path / "control", policy=p)
    assert e.process(bindings, lambda: {"mock_only": True}, purpose="FINAL_TEST")[
        "independence_verified"
    ]
    with pytest.raises(ContractError, match="CONTROL_OUTSIDE_SEALED_ROOT"):
        TestEvaluator(tmp_path.parent / "outside", policy=p).process(
            bindings, lambda: {}, purpose="FINAL_TEST"
        )
    with pytest.raises(ContractError, match="FINAL_TEST_NOT_AUTHORIZED"):
        p.authorize({"changed": "protocol"})
    (tmp_path / "evidence").write_bytes(b"changed")
    with pytest.raises(ContractError, match="DEPLOYMENT_ARTIFACT_MISMATCH"):
        p.authorize(bindings)


def proposal():
    return propose(
        "candidate",
        {
            "human_approval_record": "test-frozen-protocol",
            "frozen_at": "2024-01-01T00:00:00Z",
            "candidate_hash": digest("candidate"),
            "standards": {
                "min_mean_ic": 0.1,
                "min_days": 252,
                "max_adjusted_p": 0.05,
                "min_positive_fraction": 0.5,
            },
        },
        {"mean": 0.2, "n": 300, "positive_fraction": 0.6},
        {"complete": True, "adjusted": [0.01]},
        {"purpose": "FINAL_TEST", "independence_verified": True},
        {
            "all_candidates_recorded": True,
            "validation_first_access_at": "2024-01-02T00:00:00Z",
            "contaminated": False,
            **{
                k: "f" * 64
                for k in (
                    "independent_golden_ref",
                    "implementation_review_ref",
                    "code_hash",
                    "data_hash",
                    "environment_hash",
                    "frozen_protocol_hash",
                )
            },
        },
    )


def test_approval_domains_and_terminal_append(tmp_path):
    p = proposal()
    assert p["eligible"] and not p["strategy_approval"]
    rejected = propose(
        "candidate", {}, {"mean": None, "n": 0, "positive_fraction": None}, {}, {}, {}
    )
    assert set(rejected["failures"]) == {
        "UNAPPROVED_STANDARDS",
        "INDEPENDENT_TEST_NOT_VERIFIED",
        "FAMILY_INCOMPLETE_OR_CONTAMINATED",
        "INCOMPLETE_APPROVAL_EVIDENCE",
    }
    protocol = {
        "human_approval_record": "test",
        "standards": {
            "min_mean_ic": 0.1,
            "min_days": 252,
            "min_positive_fraction": 0.5,
            "max_adjusted_p": 0.05,
        },
    }
    r = propose(
        "x",
        protocol,
        {"mean": None, "n": 0, "positive_fraction": None},
        {"complete": True, "adjusted": [0.8]},
        p["evaluation"],
        p["evidence"],
    )
    assert (
        "IC_OR_SAMPLE_CRITERIA_FAILED" in r["failures"]
        and "STABILITY_CRITERIA_FAILED" in r["failures"]
        and "MULTIPLICITY_CRITERIA_FAILED" in r["failures"]
    )
    ledger = ExperimentLedger(tmp_path)
    run = ledger.start(
        {},
        {
            "code_commit": "a" * 40,
            "code_bundle": "b" * 64,
            "data_hash": "c" * 64,
            "environment": {},
            "protocol_hash": "d" * 64,
            "permission_domain": "TEST",
            "seed": 17,
        },
    )
    ledger.artifact(run, "approvals.json", {"candidate": p})
    m = ledger.finish(run, "SUCCEEDED")
    key = b"only-fixture-human-decision-key-000000000"
    envelope = seal(
        {"proposal_hash": digest(p), "human_actor": "fixture-user", "state": "ResearchValidated"},
        key,
    )
    assert record_decision(ledger, run, p, envelope, key)["state"] == "ResearchValidated"
    assert ledger.verify(run) == m
    envelope = seal(
        {"proposal_hash": "changed", "human_actor": "fixture-user", "state": "ResearchValidated"},
        key,
    )
    with pytest.raises(ContractError, match="INVALID_HUMAN_RESEARCH_DECISION"):
        record_decision(ledger, run, p, envelope, key)
    other = ledger.start({}, json.loads((ledger.path(run) / "lineage.json").read_bytes()))
    ledger.finish(other, "SUCCEEDED")
    valid_envelope = seal(
        {"proposal_hash": digest(p), "human_actor": "fixture-user", "state": "ResearchValidated"},
        key,
    )
    with pytest.raises(ContractError, match="PROPOSAL_NOT_IN_IMMUTABLE_RUN"):
        record_decision(ledger, other, p, valid_envelope, key)


def test_posthoc_nonfinite_threshold_and_hash_evidence_are_rejected():
    p = proposal()
    protocol = {
        "human_approval_record": "test-only",
        "frozen_at": "2024-01-03T00:00:00Z",
        "candidate_hash": digest("candidate"),
        "standards": {
            "min_mean_ic": 0.1,
            "min_days": 252,
            "max_adjusted_p": 0.05,
            "min_positive_fraction": 0.5,
        },
    }

    def call(metrics=None, multiplicity=None, evidence=None):
        return propose(
            "candidate",
            protocol,
            p["metrics"] if metrics is None else metrics,
            p["multiplicity"] if multiplicity is None else multiplicity,
            p["evaluation"],
            p["evidence"] if evidence is None else evidence,
        )

    assert "POSTHOC_APPROVAL_PROTOCOL" in call()["failures"]
    assert (
        "INVALID_APPROVAL_NUMBERS"
        in call(metrics={**p["metrics"], "mean": float("nan")})["failures"]
    )
    assert (
        "INVALID_APPROVAL_NUMBERS"
        in call(multiplicity={"complete": True, "adjusted": [None]})["failures"]
    )
    assert (
        "INCOMPLETE_APPROVAL_EVIDENCE"
        in call(evidence={**p["evidence"], "code_hash": "not-a-sha"})["failures"]
    )
    protocol["standards"]["max_adjusted_p"] = float("nan")
    # Nonfinite protocol cannot even have a canonical immutable hash.
    with pytest.raises(ValueError):
        call()


def test_formal_outcomes_are_opaque_and_control_root_cannot_reset_budget(tmp_path, monkeypatch):
    from types import SimpleNamespace

    policy = SimpleNamespace(
        root=tmp_path,
        authorize=lambda b: {"holdout_lineage_id": "true-id"},
        verify_host=lambda: None,
    )
    first = TestEvaluator(tmp_path / "results-one", policy)

    def failure():
        raise RuntimeError("test-private-diagnostics")

    response = first.process({}, failure, purpose="FINAL_TEST")
    assert response["status"] == "CONSUMED" and "error" not in str(response)
    with pytest.raises(ContractError, match="TEST_ALREADY_CONSUMED"):
        TestEvaluator(tmp_path / "renamed-results", policy).process(
            {}, lambda: {}, purpose="FINAL_TEST"
        )
    assert first.recover() == 0
    with pytest.raises(ContractError, match="ENGINEERING_DEMO_CANNOT_USE_SEALED_POLICY"):
        first.process({}, lambda: {}, purpose="ENGINEERING_DEMO")
