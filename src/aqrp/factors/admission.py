"""Pinned package-owned TEST_ONLY receipt, checked before builtin import."""

import hashlib
import json
import sys
from pathlib import Path

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.core.security import static_guard

from .contracts import FactorSpec

BUILTINS = ("momentum", "reversal", "volume", "price_volume")
PACKAGE = Path(__file__).resolve().parents[1]
LOCK_HASH = "86c7bf65c9a9690036006360062c8cd10a91279705b4070af7033d7699abffeb"


def bundle_manifest():
    files = [
        {
            "path": p.relative_to(PACKAGE).as_posix(),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in sorted(PACKAGE.rglob("*.py"))
    ]
    return {
        "factor_api": "1.0.0",
        "data_contract": "contracts/1.0.0",
        "dependency_lock_sha256": LOCK_HASH,
        "files": files,
    }


def bundle_hash():
    return digest(bundle_manifest())


def reviewed_policy():
    policy = json.loads((PACKAGE / "factors/reviewed_code.json").read_bytes())
    if (
        policy.get("state") != "ENGINEERING_APPROVED"
        or policy.get("environment") != "TEST_ONLY"
        or policy.get("financial_approval") != "NONE"
        or not policy.get("reviewer")
        or not policy.get("review_ref")
    ):
        raise ContractError("UNAPPROVED_CODE_RECEIPT", "reviewed_code.json")
    if policy.get("bundle_sha256") != bundle_hash():
        raise ContractError("IMPLEMENTATION_HASH_CHANGED", "bundle")
    if (
        policy.get("allowed_factor_ids") != list(BUILTINS)
        or sys.version_info[:3] != (3, 13, 16)
        or not sys._is_gil_enabled()
        or sys.maxsize <= 2**32
    ):
        raise ContractError("UNAPPROVED_EXECUTION_ENVIRONMENT", "receipt")
    static_guard((PACKAGE / "factors/builtins.py").read_text(encoding="utf-8"))
    return policy


def validate_admission(spec):
    if not isinstance(spec, FactorSpec) or spec.factor_id not in BUILTINS:
        raise ContractError("UNKNOWN_OR_EXTERNAL_FACTOR", "factor_id")
    policy = reviewed_policy()
    if (
        spec.implementation_version != policy["bundle_sha256"]
        or spec.review_ref != policy["review_ref"]
        or spec.bundle_manifest_ref != "reviewed_code.json"
    ):
        raise ContractError("UNAPPROVED_FACTOR_ARTIFACT", "FactorSpec")
    return policy


def builtin_spec(factor_id, factor_version="1.1.3", *, api_compatibility=">=1.0.0,<2.0.0"):
    if factor_id not in BUILTINS:
        raise ContractError("UNKNOWN_OR_EXTERNAL_FACTOR", "factor_id")
    policy = reviewed_policy()
    return FactorSpec(
        factor_id,
        factor_id.title(),
        factor_version,
        required_fields=("close", "volume")
        if factor_id == "price_volume"
        else (("volume",) if factor_id == "volume" else ("close",)),
        implementation_version=policy["bundle_sha256"],
        review_ref=policy["review_ref"],
        api_compatibility=api_compatibility,
    )
