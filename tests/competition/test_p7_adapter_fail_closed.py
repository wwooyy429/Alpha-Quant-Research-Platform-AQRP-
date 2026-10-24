"""Public adapter negative controls using real catalogues and original services."""

import pytest

from aqrp.competition import (
    AdapterReceipt,
    AdapterSpec,
    adapt_engineering,
    adapter_spec,
    capabilities,
    execute_engineering,
    input_reference,
    read_adapter_result,
)
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import load
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService

SINGLE = {
    "kind": "engineering_pipeline",
    "factor_ids": ["momentum"],
    "start": "2024-01-06",
    "end": "2024-01-06",
    "horizons": [1],
}


@pytest.fixture(scope="module")
def adapter_workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("p7-adapter-public-negative")
    initialize(root, "a" * 40)
    return root


def receipt_for(root, draft=None):
    spec = adapter_spec(root)
    return adapt_engineering(
        root,
        spec,
        input_reference(root),
        SINGLE if draft is None else draft,
        load(spec.raw)["rules"],
    )


@pytest.mark.parametrize("value", [object(), AdapterReceipt(b"{}"), AdapterSpec(bytearray(b"{}"))])
def test_spec_requires_exact_frozen_class_and_immutable_bytes(value):
    with pytest.raises(ContractError, match="FROZEN_ADAPTER_BYTES_REQUIRED"):
        capabilities(value, {})


@pytest.mark.parametrize("raw", [b"[]", b'{ "schema": "engineering-adapter/1" }'])
def test_spec_rejects_nonobject_or_noncanonical_frozen_json(raw):
    with pytest.raises(ContractError, match="NONCANONICAL_ADAPTER_BYTES"):
        capabilities(AdapterSpec(raw), {})


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", "engineering-adapter/2"),
        ("adapter_id", "unreviewed-provider"),
        ("version", "1.0.1"),
        ("kind", "REAL_MARKET"),
        ("scope", "FINANCIALLY_APPROVED"),
        ("approved_profile_id", "REAL_MARKET_V1"),
        ("source_id", "EXTERNAL"),
        ("source_authority", "unreviewed-authority"),
        ("license_statement", "unreviewed-license"),
        ("license_verification", "LEGAL_APPROVAL"),
        ("supported_request_kinds", ["research", "engineering_pipeline", "live"]),
        ("rules", {}),
        ("rule_profile_hash", "b" * 64),
    ],
)
def test_capability_entry_checks_complete_reviewed_spec(adapter_workspace, field, value):
    body = load(adapter_spec(adapter_workspace).raw)
    rules = body["rules"]
    body[field] = value
    with pytest.raises(ContractError, match="ADAPTER_SPEC_CHANGED"):
        capabilities(AdapterSpec(canonical(body)), rules)


@pytest.mark.parametrize("requirements", [None, [], {1: "not-a-rule-name"}])
def test_requirements_must_be_an_explicit_string_keyed_mapping(adapter_workspace, requirements):
    with pytest.raises(ContractError, match="ADAPTER_RULE_REQUIREMENTS_REQUIRED"):
        capabilities(adapter_spec(adapter_workspace), requirements)


def test_valid_catalogue_with_unreviewed_calendar_cannot_gain_adapter_profile(tmp_path):
    initialize(tmp_path, "a" * 40)
    path = tmp_path / "catalog.json"
    body = load(path.read_bytes())
    body["config"]["calendar_id"] = "UNREVIEWED_CALENDAR"
    body["revision"] = digest({k: v for k, v in body.items() if k != "revision"})
    path.write_bytes(canonical(body))
    # Rehashing a valid engineering catalogue does not approve a new market profile.
    with pytest.raises(ContractError, match="ADAPTER_SOURCE_PROFILE_NOT_REVIEWED"):
        adapter_spec(tmp_path)
    assert not (tmp_path / "tasks").exists()


@pytest.mark.parametrize(
    "change,expected",
    [
        ("draft-nonmapping", "ADAPTER_ENGINEERING_REQUEST_ONLY"),
        ("draft-live", "ADAPTER_ENGINEERING_REQUEST_ONLY"),
        ("input-reference", "ADAPTER_INPUT_OR_SPEC_CHANGED"),
        ("spec-identity", "ADAPTER_INPUT_OR_SPEC_CHANGED"),
        ("required-rule", "ADAPTER_REQUIRED_RULE_NOT_SUPPORTED"),
    ],
)
def test_frozen_receipt_revalidates_original_source_and_rules_before_submit(
    adapter_workspace, change, expected
):
    original = receipt_for(adapter_workspace)
    body = load(original.raw)
    if change == "draft-nonmapping":
        body["original_task_draft"] = []
    elif change == "draft-live":
        body["original_task_draft"]["kind"] = "live"
    elif change == "input-reference":
        body["input_reference"]["snapshot_manifest_hash"] = "b" * 64
    elif change == "spec-identity":
        spec = load(body["spec_utf8"].encode())
        spec["source_manifest_hash"] = "b" * 64
        body["spec_utf8"] = canonical(spec).decode()
    else:
        body["requirements"]["settlement"] = "T+0"
    service = TaskService(adapter_workspace)
    before = service.list()
    with pytest.raises(ContractError, match=expected):
        execute_engineering(adapter_workspace, AdapterReceipt(canonical(body)), "refuse-" + change)
    assert service.list() == before
    assert not (adapter_workspace / "research-runs/trials.jsonl").exists()


def test_existing_receipt_publication_must_match_exact_original_bytes(adapter_workspace):
    receipt = receipt_for(adapter_workspace)
    directory = adapter_workspace / "competition-adapters"
    directory.mkdir(exist_ok=True)
    path = directory / (receipt.checksum + ".json")
    damaged = receipt.raw + b" "
    path.write_bytes(damaged)
    before = TaskService(adapter_workspace).list()
    with pytest.raises(ContractError, match="ADAPTER_RECEIPT_CHANGED"):
        execute_engineering(adapter_workspace, receipt, "damaged-publication")
    assert path.read_bytes() == damaged
    assert TaskService(adapter_workspace).list() == before


def test_result_links_require_matching_request_and_verified_terminal(tmp_path):
    initialize(tmp_path, "a" * 40)
    receipt = receipt_for(tmp_path)
    service = TaskService(tmp_path)
    other = service.submit(service.freeze({**SINGLE, "factor_ids": ["reversal"]}), "other-factor")
    with pytest.raises(ContractError, match="ADAPTER_TASK_REQUEST_CHANGED"):
        read_adapter_result(tmp_path, receipt, other["task_id"])
    assert service.cancel(other["task_id"]) == "CANCELLED"
    queued = execute_engineering(tmp_path, receipt, "matching-queued", wait=False)
    assert queued["status"] == "QUEUED"
    with pytest.raises(ContractError, match="ADAPTER_VERIFIED_TERMINAL_REQUIRED"):
        read_adapter_result(tmp_path, receipt, queued["task_id"])
    assert service.cancel(queued["task_id"]) == "CANCELLED"
    links = read_adapter_result(tmp_path, receipt, queued["task_id"])
    assert links["status"] == "CANCELLED" and links["financial_approval"] == "NONE"


def test_waiting_adapter_preserves_original_risk_rejection_and_financial_result(tmp_path):
    initialize(tmp_path, "a" * 40)
    receipt = receipt_for(tmp_path, {**SINGLE, "constraints": {"gross_max": "0"}})
    row = execute_engineering(tmp_path, receipt, "adapter-risk-rejected", wait=True)
    assert row["status"] == "FAILED" and row["error"] == "REQUIRED_STAGE_REJECTED"
    service = TaskService(tmp_path)
    portfolio = load(service.artifact(row["task_id"], "P:0", "result.json"))
    backtest = load(service.artifact(row["task_id"], "B", "result.json"))
    assert portfolio["status"] == "REJECTED"
    assert backtest["status"] == "SUCCEEDED" and backtest["fills"] == []
    assert backtest["account"]["cash_total"] == "1000"
    links = read_adapter_result(tmp_path, receipt, row["task_id"])
    assert links["status"] == "FAILED" and links["error"] == "REQUIRED_STAGE_REJECTED"
    assert links["financial_approval"] == "NONE"
