"""Original service execution plus strict source/rules/receipt boundaries."""

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
from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import load
from aqrp.services.task_cli import main
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
def workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("p7-adapter")
    initialize(root, "a" * 40)
    return root


def test_actual_source_eight_tables_sidecars_rules_and_original_request(workspace):
    spec = adapter_spec(workspace)
    body = load(spec.raw)
    source = input_reference(workspace)
    assert len(source["tables"]) == 8
    assert set(source["tables"]) == {
        "security_master",
        "symbol_alias",
        "security_status",
        "universe_membership",
        "bars_daily",
        "corporate_actions",
        "calendar",
        "adjustment_factors",
    }
    assert source["snapshot_manifest_hash"] == body["source_manifest_hash"]
    assert source["coverage_checksum"] == body["coverage_checksum"]
    assert source["exposure_manifest_hash"] == body["exposure_manifest_hash"]
    report = load(capabilities(spec, body["rules"]).raw)
    assert report["runnable"]
    assert set(r["status"] for r in report["rows"]) == {"EXACT", "DECLARED_SYNTHETIC"}
    receipt = adapt_engineering(workspace, spec, source, SINGLE, body["rules"])
    assert (
        load(receipt.raw)["task_request_utf8"].encode() == TaskService(workspace).freeze(SINGLE).raw
    )
    assert body["license_verification"] == "DECLARATION_ONLY_NOT_LEGAL_APPROVAL"


@pytest.mark.parametrize(
    "rule,value,status",
    [
        ("provider", "vendor", "UNKNOWN_EXTERNAL"),
        ("real_market", "XNYS", "UNKNOWN_EXTERNAL"),
        ("live_orders", True, "UNSUPPORTED"),
        ("new_tax", "0", "UNSUPPORTED"),
        ("settlement", "T+0", "UNSUPPORTED"),
        ("market_id", "REAL_A", "UNSUPPORTED"),
        ("network", 0, "UNSUPPORTED"),
        ("unit_mapping", "MULTIPLY_100", "UNSUPPORTED"),
    ],
)
def test_unknown_or_conflicting_rule_refused_before_task_or_trial(workspace, rule, value, status):
    spec = adapter_spec(workspace)
    rules = {**load(spec.raw)["rules"], rule: value}
    before = TaskService(workspace).list()
    report = load(capabilities(spec, rules).raw)
    assert not report["runnable"]
    assert next(r for r in report["rows"] if r["rule"] == rule)["status"] == status
    with pytest.raises(ContractError, match="ADAPTER_REQUIRED_RULE_NOT_SUPPORTED"):
        adapt_engineering(workspace, spec, input_reference(workspace), SINGLE, rules)
    assert TaskService(workspace).list() == before


@pytest.mark.parametrize(
    "missing",
    ["settlement", "calendar_version", "commission", "slippage", "liquidity", "short_restriction"],
)
def test_missing_required_rule_cannot_fall_back_to_default(workspace, missing):
    spec = adapter_spec(workspace)
    rules = load(spec.raw)["rules"]
    del rules[missing]
    assert not capabilities(spec, rules).runnable
    with pytest.raises(ContractError, match="ADAPTER_REQUIRED_RULE_NOT_SUPPORTED"):
        adapt_engineering(workspace, spec, input_reference(workspace), SINGLE, rules)


@pytest.mark.parametrize(
    "kind", ["formal", "formal_test", "live", "replay", ["engineering_pipeline"]]
)
def test_adapter_never_opens_other_execution_kinds(workspace, kind):
    spec = adapter_spec(workspace)
    with pytest.raises(ContractError, match="ADAPTER_ENGINEERING_REQUEST_ONLY"):
        adapt_engineering(
            workspace,
            spec,
            input_reference(workspace),
            {**SINGLE, "kind": kind},
            load(spec.raw)["rules"],
        )


@pytest.mark.parametrize(
    "field",
    [
        "source_manifest_hash",
        "code_bundle",
        "source_authority",
        "license_statement",
        "catalogue_revision",
        "core_lock_hash",
        "ui_lock_hash",
    ],
)
def test_rehashed_legal_spec_identities_do_not_override_trusted_catalogue(workspace, field):
    body = load(adapter_spec(workspace).raw)
    body[field] = "b" * 64
    with pytest.raises(ContractError, match="ADAPTER_INPUT_OR_SPEC_CHANGED"):
        adapt_engineering(
            workspace,
            AdapterSpec(canonical(body)),
            input_reference(workspace),
            SINGLE,
            body["rules"],
        )


@pytest.mark.parametrize(
    "field",
    [
        "workspace",
        "snapshot_id",
        "original_manifest_sha256",
        "exposure_manifest_hash",
        "coverage_checksum",
    ],
)
def test_rehashed_input_reference_mismatch_rejected(workspace, field):
    spec = adapter_spec(workspace)
    source = input_reference(workspace)
    source[field] = "b" * 64
    with pytest.raises(ContractError, match="ADAPTER_INPUT_OR_SPEC_CHANGED"):
        adapt_engineering(workspace, spec, source, SINGLE, load(spec.raw)["rules"])


def test_original_core_executes_known_answer_not_adapter_math(workspace):
    spec = adapter_spec(workspace)
    receipt = adapt_engineering(
        workspace, spec, input_reference(workspace), SINGLE, load(spec.raw)["rules"]
    )
    row = execute_engineering(workspace, receipt, "p7-adapter-known")
    assert row["status"] == "SUCCEEDED", row
    assert set(row["slots"]) == {"R", "B", "P:0"}
    service = TaskService(workspace)
    result = load(service.artifact(row["task_id"], "B", "result.json"))
    # 1000 - 9*100.10 - 1 commission; mark nine shares at100.
    assert result["account"]["cash_total"] == "98.1"
    assert result["account"]["equity"] == "998.1"
    links = read_adapter_result(workspace, receipt, row["task_id"])
    assert links["status"] == "SUCCEEDED" and links["financial_approval"] == "NONE"
    assert execute_engineering(workspace, receipt, "p7-adapter-known")["task_id"] == row["task_id"]
    mutated = load(receipt.raw)
    mutated["field_mapping"] = "UNREVIEWED_CONVERSION"
    with pytest.raises(ContractError, match="ADAPTER_RECEIPT_CHANGED"):
        execute_engineering(workspace, AdapterReceipt(canonical(mutated)), "tampered")


def test_cli_adapter_preserves_canonical_receipt_and_requires_rules(workspace, tmp_path):
    source, rules_path, output = (
        tmp_path / "draft.json",
        tmp_path / "rules.json",
        tmp_path / "receipt.json",
    )
    source.write_bytes(canonical(SINGLE))
    rules_path.write_bytes(canonical(load(adapter_spec(workspace).raw)["rules"]))
    assert main(["adapter-freeze", "--workspace", str(workspace), "--request", str(source)]) == 2
    assert (
        main(
            [
                "adapter-freeze",
                "--workspace",
                str(workspace),
                "--request",
                str(source),
                "--rules",
                str(rules_path),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert canonical(load(output.read_bytes())) == output.read_bytes()
    assert (
        load(output.read_bytes())["task_request_utf8"].encode()
        == TaskService(workspace).freeze(SINGLE).raw
    )


def test_receipt_freezes_defaults_revision_without_later_drift(workspace):
    service = TaskService(workspace)
    spec = adapter_spec(workspace)
    receipt = adapt_engineering(
        workspace, spec, input_reference(workspace), SINGLE, load(spec.raw)["rules"]
    )
    defaults = service.defaults()
    service.save_defaults(defaults["revision"], {"initial_cash": "2000"})
    row = execute_engineering(workspace, receipt, "p7-adapter-defaults-pinned", wait=False)
    assert service.request(row["task_id"])["payload"]["execution"]["initial_cash"] == "1000"
    assert service.cancel(row["task_id"]) == "CANCELLED"


def test_cli_submits_original_frozen_receipt_after_defaults_change(tmp_path):
    root = tmp_path / "frozen-receipt-cli"
    initialize(root, "a" * 40)
    spec = adapter_spec(root)
    rules = tmp_path / "rules.json"
    draft = tmp_path / "draft.json"
    receipt = tmp_path / "receipt.json"
    result = tmp_path / "submitted.json"
    rules.write_bytes(canonical(load(spec.raw)["rules"]))
    draft.write_bytes(canonical(SINGLE))
    assert (
        main(
            [
                "adapter-freeze",
                "--workspace",
                str(root),
                "--request",
                str(draft),
                "--rules",
                str(rules),
                "--output",
                str(receipt),
            ]
        )
        == 0
    )
    original = receipt.read_bytes()
    service = TaskService(root)
    service.save_defaults(0, {"initial_cash": "2000"})
    assert (
        main(
            [
                "adapter-submit",
                "--workspace",
                str(root),
                "--request",
                str(receipt),
                "--rules",
                str(rules),
                "--key",
                "frozen-original",
                "--output",
                str(result),
            ]
        )
        == 0
    )
    task = load(result.read_bytes())["task_id"]
    assert service.state.get(task)["raw"].encode() == load(original)["task_request_utf8"].encode()
    assert service.request(task)["payload"]["execution"]["initial_cash"] == "1000"
    assert receipt.read_bytes() == original
    assert service.cancel(task) == "CANCELLED"


@pytest.mark.parametrize("change", ["receipt", "rules", "execution-selection"])
def test_cli_frozen_receipt_rejects_tampering_and_overrides(workspace, tmp_path, change):
    spec = adapter_spec(workspace)
    source = input_reference(workspace)
    rules_value = load(spec.raw)["rules"]
    receipt = adapt_engineering(workspace, spec, source, SINGLE, rules_value)
    path, rules = tmp_path / "receipt.json", tmp_path / "rules.json"
    path.write_bytes(receipt.raw)
    arguments = [
        "adapter-submit",
        "--workspace",
        str(workspace),
        "--request",
        str(path),
        "--rules",
        str(rules),
        "--key",
        "refuse-" + change,
    ]
    if change == "receipt":
        body = load(receipt.raw)
        body["field_mapping"] = "MODIFIED_AFTER_FREEZE"
        path.write_bytes(canonical(body))
    elif change == "rules":
        rules_value["settlement"] = "T+0"
    else:
        arguments.extend(["--execution-sessions", "2024-01-06"])
    rules.write_bytes(canonical(rules_value))
    service = TaskService(workspace)
    before = service.list()
    assert main(arguments) == 2
    assert service.list() == before
