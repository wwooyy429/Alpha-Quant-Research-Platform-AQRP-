import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from aqrp.core.errors import ContractError
from aqrp.factors import FactorRef, SignalBatch, builtin_spec, write_run
from aqrp.factors.contracts import freeze_parameters
from aqrp.factors.engine import write_failure
from aqrp.factors.registry import FactorRegistry, PinnedFactor
from aqrp.factors.versions import compatible, version


@pytest.mark.parametrize(
    "bad", ["latest", "1", "1.0", "01.0.0", "1.0.0-alpha", "1.0.0+build", "-1.0.0", None]
)
def test_exact_versions_reject_floating_or_unsupported(bad):
    with pytest.raises(ContractError, match="VERSION"):
        version(bad)


@pytest.mark.parametrize(
    "bad", [None, "*", "^1.0.0", ">=2.0.0,<1.0.0", ">=1.0.0,<1.0.0", ">=bad,<2.0.0"]
)
def test_invalid_api_ranges(bad):
    with pytest.raises(ContractError):
        compatible(bad)


def test_api_range_boundaries():
    assert version("0.12.3") == (0, 12, 3)
    assert compatible(">=1.0.0,<2.0.0", "1.0.0")
    assert compatible(">=1.0.0,<2.0.0", "1.99.99")
    assert not compatible(">=1.0.0,<2.0.0", "2.0.0")
    assert not compatible(">=1.0.0,<2.0.0", "0.99.99")
    with pytest.raises(ContractError):
        version("1.1٠.0")


@pytest.mark.parametrize(
    "params",
    [
        {"extra": 1},
        [],
        {"lookback": True},
        {"lookback": 2.0},
        {"lookback": None},
        {"lookback": [2]},
        {"lookback": float("nan")},
        {"lookback": float("inf")},
        {"lookback": 0},
        {"lookback": 253},
    ],
)
def test_factor_001_invalid_parameters(params):
    with pytest.raises(ContractError):
        freeze_parameters(builtin_spec("momentum"), params)


def test_parameter_defaults_and_mutation():
    spec = builtin_spec("momentum")
    assert freeze_parameters(spec) == freeze_parameters(spec, {"lookback": 20})
    parameters = {"lookback": 2}
    frozen, checksum = freeze_parameters(spec, parameters)
    parameters["lookback"] = 5
    assert frozen == (("lookback", 2),) and checksum == freeze_parameters(spec, {"lookback": 2})[1]
    assert checksum != freeze_parameters(spec, parameters)[1]
    assert freeze_parameters(spec, {"lookback": 252})[0] == (("lookback", 252),)


@pytest.mark.parametrize(
    "changes",
    [
        {"factor_name": ""},
        {"review_ref": ""},
        {"implementation_version": "bad"},
        {"parameters": []},
        {"required_fields": ("volume",)},
        {"supported_frequency": "tick"},
        {"price_basis": "RAW"},
        {"factor_direction": -1},
        {"factor_direction": True},
        {"output_unit": "currency"},
        {"data_contract_version": "contracts/2.0.0"},
    ],
)
def test_factor_001_required_metadata(changes):
    with pytest.raises(ContractError):
        replace(builtin_spec("momentum"), **changes)


def test_ref_and_spec_immutability():
    spec = builtin_spec("momentum")
    assert spec.spec_hash == builtin_spec("momentum").spec_hash
    with pytest.raises(FrozenInstanceError):
        spec.factor_direction = -1
    for args in (("", "1.0.0", "0" * 64), ("momentum", "1.0.0", None)):
        with pytest.raises(ContractError):
            FactorRef(*args)


def test_factor_003_registry_idempotency_conflict_and_precise_ref(factor_registry):
    spec = builtin_spec("momentum")
    count = len(factor_registry.events)
    assert (
        factor_registry.register(
            spec.implementation_version,
            spec,
            actor="test",
            reason="retry",
            evidence=spec.review_ref,
        )
        == spec.ref
    )
    assert len(factor_registry.events) == count
    changed = replace(spec, factor_name="Different reviewed metadata")
    with pytest.raises(ContractError, match="CONFLICT"):
        factor_registry.register(
            changed.implementation_version,
            changed,
            actor="test",
            reason="conflict",
            evidence=spec.review_ref,
        )
    with pytest.raises(ContractError, match="UNKNOWN_FACTOR"):
        factor_registry.resolve(replace(spec.ref, implementation_hash="0" * 64))
    with pytest.raises(ContractError, match="EXACT"):
        factor_registry.resolve("momentum")
    assert factor_registry.events[0].action == "ENGINEERING_APPROVED"
    assert isinstance(factor_registry.events, tuple)


def test_new_version_compatibility_and_auditable_rollback(factor_registry):
    old = builtin_spec("momentum")
    new = builtin_spec("momentum", "1.0.1")
    factor_registry.register(
        new.implementation_version, new, actor="test", reason="new version", evidence=new.review_ref
    )
    assert factor_registry.resolve(new.ref).spec == new
    pin = factor_registry.resolve(old.ref)
    factor_registry.deactivate(
        old.ref, actor="test", reason="new runs disabled", evidence=old.review_ref
    )
    with pytest.raises(ContractError, match="DISABLED"):
        factor_registry.resolve(old.ref)
    assert factor_registry.check_pin(pin) == old
    assert (
        factor_registry.rollback(old.ref, actor="test", reason="rollback", evidence=old.review_ref)
        == pin
    )
    assert factor_registry.selection == old.ref and factor_registry.resolve(old.ref) == pin
    assert [x.seq for x in factor_registry.events] == list(
        range(1, len(factor_registry.events) + 1)
    )
    factor_registry.deactivate(
        old.ref,
        actor="test",
        reason="explicit termination",
        evidence=old.review_ref,
        emergency=True,
    )
    with pytest.raises(ContractError, match="EMERGENCY"):
        factor_registry.check_pin(pin)
    with pytest.raises(ContractError, match="EMERGENCY"):
        factor_registry.rollback(
            old.ref, actor="test", reason="not allowed", evidence=old.review_ref
        )


def test_registry_rejects_missing_review_incompatible_and_false_pins(factor_registry):
    registry = FactorRegistry()
    spec = builtin_spec("momentum")
    with pytest.raises(ContractError, match="UNAPPROVED"):
        registry.register("0" * 64, spec, actor="test", reason="bad", evidence="test")
    incompatible = builtin_spec("momentum", api_compatibility=">=2.0.0,<3.0.0")
    with pytest.raises(ContractError, match="INCOMPATIBLE"):
        registry.register(
            incompatible.implementation_version,
            incompatible,
            actor="test",
            reason="bad",
            evidence="test",
        )
    with pytest.raises(ContractError, match="MISSING"):
        registry.register(
            spec.implementation_version, spec, actor="", reason="bad", evidence="test"
        )
    with pytest.raises(ContractError, match="INVALID_FACTOR_PIN"):
        factor_registry.check_pin(None)
    with pytest.raises(ContractError, match="INVALID_FACTOR_PIN"):
        factor_registry.check_pin(PinnedFactor(replace(spec, factor_name="forged pin")))


@pytest.fixture
def batch(factor_tables, factor_query, factor_engine, make_snapshot):
    return factor_engine.run(
        builtin_spec("momentum").ref,
        factor_query,
        "2024-01-04T12:05:00Z",
        make_snapshot(factor_tables),
        parameters={"lookback": 2},
    )


def test_factor_002_signal_key_idempotency_and_conflict(batch):
    row = batch.rows[0]
    assert SignalBatch((row, row), batch.config_snapshot).rows == (row,)
    with pytest.raises(ContractError, match="CONFLICTING"):
        SignalBatch((row, replace(row, factor_value=0.3)), batch.config_snapshot)
    with pytest.raises(ContractError, match="MUTABLE"):
        SignalBatch(list(batch.rows), batch.config_snapshot)
    with pytest.raises(ContractError, match="MUTABLE"):
        SignalBatch(batch.rows, {})
    with pytest.raises(ContractError, match="SIGNAL_REQUIRED"):
        SignalBatch(({},), batch.config_snapshot)
    assert SignalBatch(tuple(reversed(batch.rows)), batch.config_snapshot).rows == batch.rows


@pytest.mark.parametrize(
    "changes",
    [
        {"factor_value": float("nan")},
        {"factor_value": float("inf")},
        {"factor_value": None},
        {"factor_value": 1},
        {"validity": "UNKNOWN"},
        {"processing_stage": "final"},
        {"reason": "MISSING"},
        {"validity": "INVALID", "factor_value": None},
        {"validity": "INVALID", "reason": "MISSING"},
        {"run_id": "../../unsafe"},
        {"computation_id": None},
        {"security_id": ""},
    ],
)
def test_signal_rejects_bad_output(batch, changes):
    with pytest.raises(ContractError):
        replace(batch.rows[0], **changes)


def test_signal_time_and_readonly(batch):
    with pytest.raises(ContractError, match="SIGNAL_TIME_ORDER"):
        replace(batch.rows[0], available_at=batch.rows[0].signal_time - timedelta(microseconds=1))
    with pytest.raises(FrozenInstanceError):
        batch.rows[0].factor_value = 0.0
    assert len(batch.content_hash) == len(batch.logical_hash) == 64


def test_factor_run_receipt_and_immutable_persistence(batch, factor_registry, tmp_path):
    root = write_run(batch, tmp_path, factor_registry)
    manifest = json.loads((root / "manifest.json").read_bytes())
    assert manifest["status"] == "SUCCEEDED" and manifest["financial_approval"] == "NONE"
    for entry in manifest["artifacts"]:
        assert hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
    with pytest.raises(FileExistsError):
        write_run(batch, tmp_path, factor_registry)
    malicious = json.loads(batch.config_snapshot)
    malicious["run_id"] = "../outside"
    with pytest.raises(ContractError, match="INVALID_RUN_ID"):
        write_run(
            replace(batch, config_snapshot=json.dumps(malicious).encode()),
            tmp_path,
            factor_registry,
        )
    malicious["run_id"] = "00000000-0000-0000-0000-000000000001"
    with pytest.raises(ContractError, match="LINEAGE"):
        write_run(
            replace(batch, config_snapshot=json.dumps(malicious).encode()),
            tmp_path,
            factor_registry,
        )
    failed = write_failure(tmp_path, malicious["run_id"], ContractError("UNAPPROVED_FACTOR"))
    assert json.loads((failed / "manifest.json").read_bytes())["status"] == "FAILED"
    second = write_failure(
        tmp_path, "00000000-0000-0000-0000-000000000002", ValueError("not leaked")
    )
    assert json.loads((second / "manifest.json").read_bytes())["code"] == "EXECUTION_ERROR"
    with pytest.raises(ContractError):
        write_failure(tmp_path, "../outside", ValueError())
