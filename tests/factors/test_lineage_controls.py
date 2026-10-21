import json
from dataclasses import replace

import pytest

from aqrp.core.errors import ContractError
from aqrp.factors import admission, builtin_spec
from aqrp.factors.contracts import SignalBatch


@pytest.mark.parametrize(
    "key,value",
    [
        ("snapshot_id", "wrong"),
        ("params_hash", "0" * 64),
        ("market_id", "wrong"),
        ("security_ids", []),
        ("decision_time", "2024-01-04T12:06:00Z"),
    ],
)
def test_batch_cannot_launder_lineage(
    key, value, factor_engine, factor_tables, factor_query, make_snapshot
):
    batch = factor_engine.run(
        builtin_spec("momentum").ref,
        factor_query,
        "2024-01-04T12:05:00Z",
        make_snapshot(factor_tables),
        parameters={"lookback": 2},
    )
    config = json.loads(batch.config_snapshot)
    config[key] = value
    with pytest.raises(ContractError, match="LINEAGE"):
        replace(batch, config_snapshot=json.dumps(config).encode())


@pytest.mark.parametrize("config", [b"{}", b"[]", b"invalid"])
def test_invalid_config_is_not_a_valid_batch(config):
    with pytest.raises(ContractError, match="CONFIG_SNAPSHOT"):
        SignalBatch((), config)


def test_standard_gil_and_64bit_are_required(monkeypatch):
    with monkeypatch.context() as patch:
        patch.setattr(admission.sys, "_is_gil_enabled", lambda: False)
        with pytest.raises(ContractError, match="ENVIRONMENT"):
            admission.reviewed_policy()
    with monkeypatch.context() as patch:
        patch.setattr(admission.sys, "maxsize", 2**31 - 1)
        with pytest.raises(ContractError, match="ENVIRONMENT"):
            admission.reviewed_policy()


def test_emergency_flag_type(factor_registry):
    with pytest.raises(ContractError, match="EMERGENCY_FLAG"):
        factor_registry.deactivate(
            builtin_spec("momentum").ref,
            actor="test",
            reason="bad",
            evidence="test",
            emergency="false",
        )
