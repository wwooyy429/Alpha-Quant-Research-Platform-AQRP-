"""Research contract failures and sealed-entry wiring, distinct from deployment tests."""

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.research.synthetic import synthetic_research
from aqrp.services import research as module
from aqrp.services.research import ResearchRequest, hypotheses, hypothesis_definition, research
from aqrp.validation.labels import CoverageRef
from aqrp.validation.splits import partition

SHA = "3861ef1637bc2b4c28725d7afc5f2e1f02242e80"


@pytest.fixture(scope="module")
def inputs(tmp_path_factory):
    return synthetic_research(tmp_path_factory.mktemp("guard-inputs"), sessions=24, assets=6)


def request(inputs, config, coverage=None):
    _, s, e, v = inputs
    v = v if coverage is None else coverage
    config["family"]["hypotheses"] = [r["hypothesis"] for r in hypotheses(config)]
    config["family"]["definitions"] = {
        c["hypothesis"]: hypothesis_definition(
            c, config, s.manifest_hash, e.manifest_hash, v.checksum
        )
        for c in hypotheses(config)
    }
    return ResearchRequest.create(config, s, e, v, SHA)


@pytest.mark.parametrize(
    "change,code",
    [
        (lambda c: c.update(seed=True), "INVALID_RESEARCH_NUMERIC_PROFILE"),
        (lambda c: c.update(min_ic_n=0), "INVALID_RESEARCH_NUMERIC_PROFILE"),
        (lambda c: c["candidates"][0].update(direction=True), "INVALID_FACTOR_DIRECTION"),
        (lambda c: c["decisions"].reverse(), "INVALID_DECISION_GRID"),
        (
            lambda c: c["decisions"][0].update(session="2023-01-01"),
            "DECISION_OUTSIDE_REGISTERED_SPLITS",
        ),
    ],
)
def test_invalid_profiles_are_failed_runs(inputs, tmp_path, change, code):
    c = deepcopy(inputs[0])
    change(c)
    with pytest.raises(ContractError, match=code):
        research(request(inputs, c), tmp_path)
    assert ExperimentLedger(tmp_path).catalogue()[0]["status"] == "FAILED"


def test_preregistration_is_not_redefined_after_observation(inputs, tmp_path):
    c, s, e, v = inputs
    changed = deepcopy(c)
    changed["candidates"][0]["parameters"]["lookback"] = 3
    with pytest.raises(ContractError, match="HYPOTHESIS_CHANGED_AFTER_PREREGISTRATION"):
        research(ResearchRequest.create(changed, s, e, v, SHA), tmp_path / "changed")
    changed = deepcopy(c)
    changed["family"]["definitions"] = {}
    with pytest.raises(ContractError, match="INCOMPLETE_PREREGISTERED_HYPOTHESES"):
        research(ResearchRequest.create(changed, s, e, v, SHA), tmp_path / "missing")
    changed = deepcopy(c)
    changed["candidates"][0]["hypothesis"] = "unregistered"
    with pytest.raises(ContractError, match="UNREGISTERED_HYPOTHESIS"):
        research(ResearchRequest.create(changed, s, e, v, SHA), tmp_path / "unregistered")
    changed = deepcopy(c)
    changed["candidates"][0]["ref"]["implementation_hash"] = "0" * 64
    with pytest.raises(ContractError, match="EXACT_RESEARCH_REF_MISMATCH"):
        research(ResearchRequest.create(changed, s, e, v, SHA), tmp_path / "ref")
    with pytest.raises(ContractError, match="EXPOSURE_RESEARCH_PARENT_MISMATCH"):
        research(
            ResearchRequest.create(c, s, replace(e, parent_hash="0" * 64), v, SHA),
            tmp_path / "parent",
        )


def test_calendar_and_universe_guards(inputs, tmp_path, monkeypatch):
    req = request(inputs, deepcopy(inputs[0]))
    real_reader = module.read_snapshot

    def ambiguous(ref):
        m, tables = real_reader(ref)
        calendar = tables["calendar"].to_pylist()
        tables["calendar"] = SimpleNamespace(to_pylist=lambda: calendar + [calendar[0]])
        return m, tables

    monkeypatch.setattr(module, "read_snapshot", ambiguous)
    with pytest.raises(ContractError, match="RESEARCH_CALENDAR_REVISION_MUST_BE_FROZEN"):
        research(req, tmp_path / "calendar")
    monkeypatch.setattr(module, "read_snapshot", real_reader)
    monkeypatch.setattr(module, "universe_at", lambda *a: ())
    with pytest.raises(ContractError, match="EMPTY_HISTORICAL_UNIVERSE"):
        research(req, tmp_path / "universe")
    monkeypatch.setattr(
        module, "verify_snapshot", lambda *a: (_ for _ in ()).throw(KeyboardInterrupt())
    )
    with pytest.raises(KeyboardInterrupt):
        research(req, tmp_path / "cancelled")
    assert ExperimentLedger(tmp_path / "cancelled").catalogue()[0]["status"] == "CANCELLED"


def test_development_cutoff_and_no_test_selection(inputs, tmp_path):
    c = deepcopy(inputs[0])
    c["purpose"] = "DEVELOPMENT"
    with pytest.raises(ContractError, match="DEVELOPMENT_CUTOFF_ENTERS_TEST"):
        research(request(inputs, c), tmp_path / "cutoff")
    c["development_cutoff"] = c["evaluation_cutoff"] = c["splits"]["test"][0] + "T00:00:00Z"
    # Exact Test boundary is forbidden, not a one-day timestamp approximation.
    with pytest.raises(ContractError, match="DEVELOPMENT_CUTOFF_ENTERS_TEST"):
        research(request(inputs, c), tmp_path / "equal")
    from datetime import timedelta

    from aqrp.core.time import utc

    c["evaluation_cutoff"] = c["development_cutoff"] = (
        utc(c["splits"]["test"][0] + "T00:00:00Z") - timedelta(microseconds=1)
    ).isoformat()
    with pytest.raises(ContractError, match="TEST_ACCESS_FORBIDDEN_IN_DEVELOPMENT"):
        research(request(inputs, c), tmp_path / "selection")
    c["decisions"] = [r for r in c["decisions"] if partition(r["session"], c["splits"]) != "test"]
    result = research(request(inputs, c), tmp_path / "allowed")
    assert result["manifest"]["status"] == "SUCCEEDED"
    assert all(r["split"] in ("train", "validation") for r in result["report"]["metrics"]["daily"])


def test_sealed_coverage_and_formal_math_wiring_only(inputs, tmp_path):
    c = deepcopy(inputs[0])
    _, s, e, v = inputs
    sealed = CoverageRef.create(
        s.manifest_hash,
        v.read(s.manifest_hash)["versions"],
        authority="unit-test-not-deployed",
        scope="OPERATOR_SEALED",
    )
    with pytest.raises(ContractError, match="ENGINEERING_INPUT_MUST_BE_PUBLIC"):
        research(request(inputs, c, sealed), tmp_path / "public-denied")
    c["purpose"] = "FINAL_TEST"
    c["horizons"] = [1]
    with pytest.raises(ContractError, match="FORMAL_COVERAGE_MUST_BE_SEALED"):
        module._research(
            request(inputs, c), tmp_path / "formal-public", operator_claims={"unit_mock": True}
        )
    grid = [r["session"] for r in c["decisions"] if partition(r["session"], c["splits"]) == "test"]
    q = {
        "planned_n": len(grid),
        "planned_session_grid": grid,
        "actual_session_grid": grid,
        "complete_session_grid": True,
        "horizon": 1,
        "m0": 0,
    }
    c["inference"]["qualification"] = q
    req = request(inputs, c, sealed)
    r = module._research(
        req, tmp_path / "mock-private", operator_claims={"qualification_hash": digest(q)}
    )
    assert (
        json.loads((tmp_path / "mock-private" / r["run_id"] / "inference.json").read_bytes())[
            "momentum::h=1"
        ]["reason"]
        == "INSUFFICIENT_HAC_SAMPLE"
    )
    with pytest.raises(ContractError, match="FORMAL_QUALIFICATION_NOT_AUTHORIZED"):
        module._research(
            req, tmp_path / "mock-private", operator_claims={"qualification_hash": "wrong"}
        )


def test_sealed_entry_binds_hashes_and_paths_without_deploying(inputs, tmp_path, monkeypatch):
    c = deepcopy(inputs[0])
    c["purpose"] = "FINAL_TEST"
    req = request(inputs, c)
    root = req.snapshot.root.parents[1]
    policy = SimpleNamespace(root=root, authorize=lambda b: {"unit_mock": True})
    evaluator = SimpleNamespace(
        root=root / "unit-control",
        policy=policy,
        process=lambda bindings, evaluate, purpose: evaluate(),
    )
    monkeypatch.setattr(
        module, "_research", lambda request, output, operator_claims: {"unit_wiring": True}
    )
    assert module.evaluate_sealed(req, evaluator) == {"unit_wiring": True}
    policy.root = tmp_path
    with pytest.raises(ContractError, match="FINAL_INPUT_OUTSIDE_SEALED_ROOT"):
        module.evaluate_sealed(req, evaluator)
    with pytest.raises(ContractError, match="SEALED_FINAL_TEST_REQUIRED"):
        module.evaluate_sealed(request(inputs, deepcopy(inputs[0])), evaluator)
    assert module.serial({"a": [float("inf"), float("nan")]}) == {"a": [None, None]}
    with pytest.raises(ValueError):
        synthetic_research(Path(tmp_path / "too-small"), sessions=2)
