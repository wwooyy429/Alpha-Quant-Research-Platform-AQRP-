"""Strict, identity-only offline mapping into the original application service.

There is no price, risk, fee, account or order calculation in this module. Rules
describe the original engineering kernel; callers cannot fill missing rules with
market defaults or use an adapter receipt as execution/financial approval.
"""

import hashlib
from dataclasses import dataclass

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.data.snapshot import verify_snapshot
from aqrp.data.synthetic import PROVENANCE
from aqrp.experiments.ledger import immutable_write, mutex
from aqrp.factors.admission import LOCK_HASH
from aqrp.portfolio.contracts import load
from aqrp.services.task_requests import catalogue, references

RULES = {
    "market_id": "SYN_A",
    "currency": "SYNCCY",
    "calendar_id": "SYN_A_CAL",
    "calendar_version": "synthetic-calendar/1",
    "unit_version": "synthetic-units/1",
    "temporal_mapping": "IDENTITY_P1_EVENT_AVAILABLE_DECISION_HISTORY",
    "execution_profile": "SYNTHETIC_V1",
    "portfolio_profile": "SYNTHETIC_PORTFOLIO_1",
    "price_domain": "INCLUSIVE_CENT_CEIL_0.95_FLOOR_1.05",
    "order_types": ["MARKET", "LIMIT"],
    "time_in_force": ["DAY"],
    "slippage": "BUY_CEIL_CENT_1.001_SELL_FLOOR_CENT_0.999",
    "commission": "ROUND_CENT_MAX_1_QTY_PRICE_DIV_1000",
    "partial_fill_fee_bound": "ORIGINAL_CUMULATIVE_PER_SHARE_UPPER",
    "liquidity": "VISIBLE_COMPLETED_ADV_LOOKBACK_1_MIN_10_CAP_MIN_10_ADV",
    "lot": "1_WITH_ORIGINAL_TARGET_DELTA_AND_FULL_CLOSE_RULES",
    "settlement": "SYNTHETIC_SESSION_PLUS_1",
    "short_restriction": "ORIGINAL_NO_DOUBLE_FREEZE",
    "actions_and_statistics": "ORIGINAL_P3_LABEL_P5_ENTITLEMENT_BORROW_FIFO",
    "unit_mapping": "IDENTITY_ONLY",
    "network": False,
    "financial_approval": "NONE",
}
EXTERNAL_RULES = {"provider", "competition_id", "source_license_approval", "real_market"}
FORBIDDEN_RULES = {
    "live_account",
    "live_orders",
    "deployment",
    "formal_test",
    "financial_approval_granted",
}
_RULE_BYTES = canonical(RULES)


def _rules():
    return load(_RULE_BYTES)


@dataclass(frozen=True)
class AdapterSpec:
    raw: bytes


@dataclass(frozen=True)
class CapabilityReport:
    raw: bytes

    @property
    def runnable(self):
        return load(self.raw)["runnable"]


@dataclass(frozen=True)
class AdapterReceipt:
    raw: bytes

    @property
    def checksum(self):
        return hashlib.sha256(self.raw).hexdigest()


def _body(value, cls):
    if type(value) is not cls or type(value.raw) is not bytes:
        raise ContractError("FROZEN_ADAPTER_BYTES_REQUIRED")
    body = load(value.raw)
    if type(body) is not dict or canonical(body) != value.raw:
        raise ContractError("NONCANONICAL_ADAPTER_BYTES")
    return body


def _trusted(root):
    cat = catalogue(root)
    snapshot, _, _ = references(root, cat)
    manifest, _ = verify_snapshot(snapshot)
    if (
        manifest["provenance"] != PROVENANCE
        or manifest["pit_status"] != "PIT_VERIFIED"
        or [cat["config"][k] for k in ("market_id", "currency", "calendar_id")]
        != ["SYN_A", "SYNCCY", "SYN_A_CAL"]
    ):
        raise ContractError("ADAPTER_SOURCE_PROFILE_NOT_REVIEWED")
    return cat, manifest


def input_reference(root):
    """Read actual verified catalogue inputs; never accept browser file paths."""
    cat, manifest = _trusted(root)
    return {
        "schema": "engineering-adapter-input/1",
        "workspace": str(guard_path(root)),
        "catalogue_revision": cat["revision"],
        "snapshot_id": cat["snapshot"]["snapshot_id"],
        "snapshot_manifest_hash": cat["snapshot"]["manifest_hash"],
        "original_manifest_sha256": hashlib.sha256(
            (
                guard_path(cat["snapshot"]["root"])
                / cat["snapshot"]["snapshot_id"]
                / "manifest.json"
            ).read_bytes()
        ).hexdigest(),
        "tables": {
            name: {k: item[k] for k in ("path", "sha256", "rows")}
            for name, item in sorted(manifest["tables"].items())
        },
        "exposure_manifest_hash": cat["exposures"]["manifest_hash"],
        "coverage_checksum": cat["coverage"]["checksum"],
    }


def adapter_spec(root):
    cat, manifest = _trusted(root)
    rules = _rules()
    body = {
        "schema": "engineering-adapter/1",
        "adapter_id": "aqrp-offline-synthetic",
        "version": "1.0.0",
        "scope": "ENGINEERING_TEST_ONLY",
        "kind": "OFFLINE_SYNTHETIC",
        "approved_profile_id": "SYNTHETIC_V1",
        "source_id": "SYNTHETIC",
        "source_manifest_hash": cat["snapshot"]["manifest_hash"],
        "source_authority": "project-public-synthetic-generator",
        "license_statement": manifest["provenance"]["source_license"],
        "license_verification": "DECLARATION_ONLY_NOT_LEGAL_APPROVAL",
        "catalogue_revision": cat["revision"],
        "snapshot_id": cat["snapshot"]["snapshot_id"],
        "exposure_manifest_hash": cat["exposures"]["manifest_hash"],
        "coverage_checksum": cat["coverage"]["checksum"],
        "rules": rules,
        "rule_profile_hash": digest(rules),
        "supported_request_kinds": ["research", "engineering_pipeline"],
        "code_commit": cat["code_commit"],
        "code_bundle": cat["code_bundle"],
        "core_lock_hash": LOCK_HASH,
        "ui_lock_hash": cat["ui_environment"]["lock_sha256"],
    }
    body["capability_matrix_hash"] = digest(
        {"rules": rules, "external": sorted(EXTERNAL_RULES), "forbidden": sorted(FORBIDDEN_RULES)}
    )
    return AdapterSpec(canonical(body))


def capabilities(spec, requested_requirements):
    body = _body(spec, AdapterSpec)
    rules = _rules()
    if (
        body.get("schema") != "engineering-adapter/1"
        or body.get("adapter_id") != "aqrp-offline-synthetic"
        or body.get("version") != "1.0.0"
        or body.get("kind") != "OFFLINE_SYNTHETIC"
        or body.get("scope") != "ENGINEERING_TEST_ONLY"
        or body.get("approved_profile_id") != "SYNTHETIC_V1"
        or body.get("source_id") != "SYNTHETIC"
        or body.get("source_authority") != "project-public-synthetic-generator"
        or body.get("license_statement") != "project-generated-test-data"
        or body.get("license_verification") != "DECLARATION_ONLY_NOT_LEGAL_APPROVAL"
        or body.get("supported_request_kinds") != ["research", "engineering_pipeline"]
        or body.get("rules") != rules
        or body.get("rule_profile_hash") != digest(rules)
    ):
        raise ContractError("ADAPTER_SPEC_CHANGED")
    if type(requested_requirements) is not dict:
        raise ContractError("ADAPTER_RULE_REQUIREMENTS_REQUIRED")
    rows = []
    if any(type(name) is not str for name in requested_requirements):
        raise ContractError("ADAPTER_RULE_REQUIREMENTS_REQUIRED")
    for name in sorted(set(rules) | set(requested_requirements)):
        present = name in requested_requirements
        actual = rules.get(name)
        requested = requested_requirements.get(name)
        if name in EXTERNAL_RULES:
            status = "UNKNOWN_EXTERNAL"
        elif (
            name in FORBIDDEN_RULES
            or name not in rules
            or not present
            or requested != actual
            or type(requested) is not type(actual)
        ):
            status = "UNSUPPORTED"
        else:
            status = (
                "DECLARED_SYNTHETIC"
                if name
                in {"market_id", "currency", "calendar_id", "calendar_version", "unit_version"}
                else "EXACT"
            )
        rows.append(
            {
                "rule": name,
                "required": True,
                "provided": present,
                "requested": requested,
                "actual": actual,
                "status": status,
                "source": "ORIGINAL_REVIEWED_ENGINEERING_KERNEL",
                "rule_profile_hash": digest(rules),
            }
        )
    result = {
        "schema": "engineering-capabilities/1",
        "spec_sha256": hashlib.sha256(spec.raw).hexdigest(),
        "requirements_sha256": digest(requested_requirements),
        "rows": rows,
        "runnable": all(r["status"] in {"EXACT", "DECLARED_SYNTHETIC"} for r in rows),
        "financial_approval": "NONE",
    }
    return CapabilityReport(canonical(result))


def adapt_engineering(root, spec, trusted_input_ref, task_draft, requested_requirements):
    """Verify all identities before freezing through the original service."""
    _body(spec, AdapterSpec)
    if spec.raw != adapter_spec(root).raw or trusted_input_ref != input_reference(root):
        raise ContractError("ADAPTER_INPUT_OR_SPEC_CHANGED")
    report = capabilities(spec, requested_requirements)
    if not report.runnable:
        raise ContractError("ADAPTER_REQUIRED_RULE_NOT_SUPPORTED")
    if type(task_draft) is not dict or task_draft.get("kind", "research") not in (
        "research",
        "engineering_pipeline",
    ):
        raise ContractError("ADAPTER_ENGINEERING_REQUEST_ONLY")
    from aqrp.services.tasks import TaskService

    frozen = TaskService(root).freeze(task_draft)
    return _receipt(spec, trusted_input_ref, task_draft, requested_requirements, report, frozen)


def _receipt(spec, trusted_input_ref, task_draft, requested_requirements, report, frozen):
    body = {
        "schema": "engineering-adapter-receipt/1",
        "spec_utf8": spec.raw.decode(),
        "input_reference": trusted_input_ref,
        "requirements": requested_requirements,
        "capabilities_utf8": report.raw.decode(),
        "original_task_draft": task_draft,
        "task_request_utf8": frozen.raw.decode(),
        "task_request_sha256": frozen.config_hash,
        "field_mapping": "IDENTITY_NO_DATE_UNIT_PRICE_OR_RULE_CONVERSION",
        "scope": "ENGINEERING_TEST_ONLY",
        "financial_approval": "NONE",
    }
    return AdapterReceipt(canonical(body))


def _verify_receipt(root, receipt):
    body = _body(receipt, AdapterReceipt)
    if type(body["original_task_draft"]) is not dict or body["original_task_draft"].get(
        "kind", "research"
    ) not in ("research", "engineering_pipeline"):
        raise ContractError("ADAPTER_ENGINEERING_REQUEST_ONLY")
    spec = AdapterSpec(body["spec_utf8"].encode())
    if spec.raw != adapter_spec(root).raw or body["input_reference"] != input_reference(root):
        raise ContractError("ADAPTER_INPUT_OR_SPEC_CHANGED")
    report = capabilities(spec, body["requirements"])
    if not report.runnable:
        raise ContractError("ADAPTER_REQUIRED_RULE_NOT_SUPPORTED")
    from aqrp.services.task_requests import freeze_request
    from aqrp.services.tasks import TaskService

    original = load(body["task_request_utf8"].encode())
    service = TaskService(root)
    defaults = service.defaults(original["defaults_revision"])
    frozen = freeze_request(
        root, body["original_task_draft"], defaults["revision"], load(defaults["payload"].encode())
    )
    service.validate_effective(frozen.raw)
    expected = _receipt(
        spec,
        body["input_reference"],
        body["original_task_draft"],
        body["requirements"],
        report,
        frozen,
    )
    if expected.raw != receipt.raw:
        raise ContractError("ADAPTER_RECEIPT_CHANGED")
    return body


def execute_engineering(root, receipt, idempotency_key, *, wait=True):
    body = _verify_receipt(root, receipt)
    from aqrp.services.task_requests import EffectiveRequest
    from aqrp.services.tasks import TaskService

    directory = guard_path(guard_path(root) / "competition-adapters")
    directory.mkdir(parents=True, exist_ok=True)
    path = guard_path(directory / (receipt.checksum + ".json"))
    with mutex(directory / ".publication-lock"):
        if path.exists():
            if path.read_bytes() != receipt.raw:
                raise ContractError("ADAPTER_RECEIPT_CHANGED")
        else:
            immutable_write(path, receipt.raw)
    service = TaskService(root)
    result = service.submit(EffectiveRequest(body["task_request_utf8"].encode()), idempotency_key)
    return service.work(result["task_id"]) if wait else result


def read_adapter_result(root, receipt, task_id):
    body = _verify_receipt(root, receipt)
    from aqrp.services.tasks import TaskService

    service = TaskService(root)
    if canonical(service.request(task_id)) != body["task_request_utf8"].encode():
        raise ContractError("ADAPTER_TASK_REQUEST_CHANGED")
    row = service.status(task_id)  # Original completion/slot/lineage/finance verification.
    if row["status"] not in {"SUCCEEDED", "FAILED", "CANCELLED"}:
        raise ContractError("ADAPTER_VERIFIED_TERMINAL_REQUIRED")
    return {
        "schema": "engineering-adapter-result-links/1",
        "receipt_sha256": receipt.checksum,
        "task_id": task_id,
        "status": row["status"],
        "error": row.get("error"),
        "result": row.get("result"),
        "slots": row.get("slots", {}),
        "scope": "ENGINEERING_TEST_ONLY",
        "financial_approval": "NONE",
    }
