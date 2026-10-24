"""Real catalogue and shared request normalization/identity rejection."""

import json
from dataclasses import asdict

import pytest

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.factors.admission import builtin_spec
from aqrp.services.task_requests import EffectiveRequest, catalogue, freeze_request, initialize
from aqrp.services.tasks import TaskService


@pytest.fixture(scope="module")
def workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("request-workspace")
    initialize(root, "a" * 40)
    return root


def test_real_pinned_catalogue_and_default_request(workspace):
    c = catalogue(workspace)
    assert initialize(workspace, "a" * 40) == c
    assert len(c["factor_specs"]) == 4
    assert len(c["ui_environment"]["packages"]) == 29
    assert c["financial_approval"] == "NONE"
    req = freeze_request(
        workspace, {"factor_ids": ["momentum"], "weights_percent": {"momentum": "-12.50"}}
    )
    x = json.loads(req.raw)
    assert x["payload"]["execution"]["factor_weights"] == {"momentum": "-0.125"}
    assert x["payload"]["raw_draft"]["weights_percent"]["momentum"] == "-12.50"
    assert req.config_hash == digest(x)
    assert x["payload"]["research"]["candidates"][0]["ref"] == asdict(builtin_spec("momentum").ref)
    assert all(
        h in x["payload"]["research"]["family"]["definitions"]
        for h in x["payload"]["research"]["family"]["hypotheses"]
    )


@pytest.mark.parametrize(
    "draft",
    [
        {"root": "x"},
        {"authority": True},
        {"context": {}},
        {"trusted": True},
        {"code_commit": "f" * 40},
        {"api_key": "not-a-real-key"},
        {"kind": "formal"},
        {"kind": "FINAL_TEST"},
        {"kind": "arbitrary-DAG"},
        {"lookback": False},
        {"lookback": 0},
        {"lookback": 21},
        {"direction": True},
        {"direction": 0},
        {"neutralize": 1},
        {"factor_ids": []},
        {"factor_ids": ["unknown"]},
        {"factor_ids": ["momentum", "momentum"]},
        {"factor_refs": []},
        {"horizons": []},
        {"horizons": [0]},
        {"horizons": [True]},
        {"horizons": [11]},
        {"horizons": [1, 1]},
        {"start": "2030-01-01"},
        {"start": "2024-1-1"},
        {"start": "2024-02-30"},
        {"weights_percent": {"reversal": "100"}},
        {"weights_percent": {"momentum": "NaN"}},
        {"initial_cash": "-1"},
        {"fee_budget": "-1"},
        {"initial_cash": 1000},
        {"kind": "replay", "source_task": "not-a-uuid"},
        {"kind": "replay", "source_task": "a", "profile": "unknown"},
    ],
)
def test_untrusted_or_out_of_schema_input_refused(workspace, draft):
    with pytest.raises((ContractError, ValueError)):
        freeze_request(workspace, draft)


def test_same_request_through_shared_builder_and_frozen_tamper(workspace):
    service = TaskService(workspace)
    draft = {"kind": "research", "factor_ids": ["reversal"], "horizons": [1]}
    a = service.freeze(draft)
    b = service.freeze(json.loads(json.dumps(draft)))
    assert a.raw == b.raw
    r = service.submit(a, "request-identity")
    assert service.submit(b, "request-identity")["task_id"] == r["task_id"]
    with pytest.raises(ContractError, match="FROZEN_TASK_REQUEST_REQUIRED"):
        service.submit(a.raw, "other")
    corrupt = json.loads(a.raw)
    corrupt["code_commit"] = "b" * 40
    with pytest.raises(ContractError, match="EFFECTIVE_REQUEST_CHANGED"):
        service.submit(EffectiveRequest(canonical(corrupt)), "other")
    corrupt = json.loads(a.raw)
    corrupt["defaults_revision"] = 999
    with pytest.raises(ContractError, match="DEFAULTS_REVISION_IDENTITY_CHANGED"):
        service.submit(EffectiveRequest(canonical(corrupt)), "other")
    assert service.cancel(r["task_id"]) == "CANCELLED"
    assert service.work(r["task_id"])["status"] == "CANCELLED"


@pytest.mark.parametrize(
    "field,value,recompute",
    [
        ("schema", "changed", True),
        ("code_commit", "a" * 7, True),
        ("factor_specs", [], True),
        ("scope", "FORMAL", False),
        ("scope", "FORMAL", True),
        ("code_bundle", "0" * 64, True),
        ("financial_approval", "YES", True),
        ("ui_environment", {}, True),
    ],
)
def test_catalogue_identity_and_execution_environment_tamper(workspace, field, value, recompute):
    path = workspace / "catalog.json"
    original = path.read_bytes()
    x = json.loads(original)
    x[field] = value
    if recompute:
        x["revision"] = digest({k: v for k, v in x.items() if k != "revision"})
    try:
        path.write_bytes(canonical(x))
        with pytest.raises(ContractError):
            catalogue(workspace)
    finally:
        path.write_bytes(original)


def test_full_sha_required_and_outside_input_root_refused(workspace, tmp_path):
    with pytest.raises(ContractError, match="FULL_CODE_SHA_REQUIRED"):
        initialize(tmp_path, "a" * 7)
    path = workspace / "catalog.json"
    original = path.read_bytes()
    x = json.loads(original)
    x["snapshot"]["root"] = str(tmp_path)
    x["revision"] = digest({k: v for k, v in x.items() if k != "revision"})
    try:
        path.write_bytes(canonical(x))
        with pytest.raises(ContractError, match="CATALOG_INPUT_OUTSIDE_WORKSPACE"):
            catalogue(workspace)
    finally:
        path.write_bytes(original)


def test_default_revision_is_bound_and_existing_effective_request_immutable(workspace):
    service = TaskService(workspace)
    first = service.freeze({"kind": "research"})
    snapshot = first.raw
    d = service.state.defaults()
    revision = service.save_defaults(d["revision"], {"lookback": 3})
    service.register_campaign("defaults-revision3", [{"lookback": 3}])
    second = service.freeze({"kind": "research", "campaign_id": "defaults-revision3"})
    assert first.raw == snapshot and first.config_hash != second.config_hash
    assert json.loads(second.raw)["defaults_revision"] == revision
    assert json.loads(second.raw)["payload"]["research"]["candidates"][0]["parameters"] == {
        "lookback": 3
    }
    assert service.submit(first, "old-revision-still-valid")["status"] == "QUEUED"
    assert (
        service.cancel(service.submit(first, "old-revision-still-valid")["task_id"]) == "CANCELLED"
    )


@pytest.mark.parametrize(
    "draft",
    [
        None,
        [],
        {"source_task": "x"},
        {"factor_ids": "momentum"},
        {"factor_ids": [1]},
        {"horizons": "1"},
        {"weights_percent": []},
        {"policy": []},
        {"policy": {"execute": True}},
        {"policy": {"mode": "arbitrary"}},
        {"constraints": []},
        {"constraints": {"unknown": True}},
    ],
)
def test_additional_schema_type_refusals(workspace, draft):
    with pytest.raises(ContractError):
        freeze_request(workspace, draft)


def test_existing_catalogue_never_silently_uses_a_different_commit(workspace):
    with pytest.raises(ContractError, match="CATALOG_CODE_COMMIT_CHANGED"):
        initialize(workspace, "b" * 40)
