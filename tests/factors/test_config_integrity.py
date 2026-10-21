"""WORK-P2-002/003: exact artifact bytes and independently derived parameter lineage."""

import hashlib
import json
from dataclasses import replace

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.factors import SignalBatch, builtin_spec, write_run


@pytest.fixture
def batch(factor_engine, factor_query, factor_tables, make_snapshot):
    return factor_engine.run(
        builtin_spec("momentum").ref,
        factor_query,
        "2024-01-04T12:05:00Z",
        make_snapshot(factor_tables),
        parameters={"lookback": 2},
    )


@pytest.mark.parametrize("encoding", ["indented", "reverse_keys", "trailing_whitespace"])
def test_work_p2_002_json_roundtrip_preserves_batch_and_file_hashes(
    batch, factor_registry, tmp_path, encoding
):
    config = json.loads(batch.config_snapshot)
    raw = (
        json.dumps(config, indent=2).encode()
        if encoding == "indented"
        else json.dumps(dict(reversed(list(config.items())))).encode()
        if encoding == "reverse_keys"
        else batch.config_snapshot + b"\n \t"
    )
    assert raw != batch.config_snapshot and json.loads(raw) == config
    roundtrip = SignalBatch(batch.rows, raw)
    assert roundtrip == batch
    assert roundtrip.content_hash == batch.content_hash
    root = write_run(roundtrip, tmp_path, factor_registry)
    assert (root / "config.json").read_bytes() == batch.config_snapshot
    manifest = json.loads((root / "manifest.json").read_bytes())
    assert manifest["content_hash"] == roundtrip.content_hash
    for item in manifest["artifacts"]:
        assert hashlib.sha256((root / item["path"]).read_bytes()).hexdigest() == item["sha256"]


def test_work_p2_003_real_parameter_change_is_distinct(
    batch, factor_engine, factor_query, factor_tables, make_snapshot
):
    one = factor_engine.run(
        builtin_spec("momentum").ref,
        factor_query,
        "2024-01-04T12:05:00Z",
        make_snapshot(factor_tables),
        parameters={"lookback": 1},
    )
    # Independent manual ratios: 121/100-1 and 121/110-1.
    assert batch.rows[0].factor_value == 0.21
    assert one.rows[0].factor_value == 0.1
    assert one.rows[0].params_hash != batch.rows[0].params_hash
    config = json.loads(batch.config_snapshot)
    config["params"] = [["lookback", 1]]
    with pytest.raises(ContractError, match="PARAMETER_LINEAGE_MISMATCH"):
        replace(batch, config_snapshot=canonical(config))


@pytest.mark.parametrize(
    "params",
    [
        [["lookback", 2], ["lookback", 2]],
        [["lookback", 1], ["lookback", 2]],
        [],
        {"lookback": 2},
        [["lookback", True]],
        [["lookback", 2.0]],
        [["lookback", "2"]],
        [["lookback", 0]],
        [["lookback", 253]],
        [["window", 2]],
        [["lookback", 2, 3]],
        [[1, 2]],
        [None],
        None,
    ],
)
def test_work_p2_003_invalid_or_ambiguous_config_params_rejected(batch, params):
    config = json.loads(batch.config_snapshot)
    config["params"] = params
    with pytest.raises(ContractError):
        replace(batch, config_snapshot=canonical(config))


def test_work_p2_003_signal_hash_cannot_disagree_with_recomputed_config(batch):
    config = json.loads(batch.config_snapshot)
    config["params"] = [["lookback", 1]]
    # A correct hash for the new parameter still cannot relabel the old Signal.
    config["params_hash"] = hashlib.sha256(canonical({"lookback": 1})).hexdigest()
    with pytest.raises(ContractError, match="SIGNAL_RUN_LINEAGE_MISMATCH"):
        replace(batch, config_snapshot=canonical(config))


@pytest.mark.parametrize("field", ["params_hash", "spec"])
def test_work_p2_002_duplicate_json_object_keys_are_ambiguous(batch, field):
    config = json.loads(batch.config_snapshot)
    raw = batch.config_snapshot[:-1] + b"," + canonical({field: config[field]})[1:]
    with pytest.raises(ContractError, match="DUPLICATE_FACTOR_CONFIG_KEY"):
        replace(batch, config_snapshot=raw)


@pytest.mark.parametrize("raw", [b"\xff", b'{"ignored":NaN}'])
def test_work_p2_002_invalid_json_encoding_is_structured(raw):
    with pytest.raises(ContractError, match="INVALID_FACTOR_CONFIG_SNAPSHOT"):
        SignalBatch((), raw)


def test_work_p2_002_nonfinite_unknown_json_value_is_not_canonical(batch):
    config = json.loads(batch.config_snapshot)
    config["note"] = float("nan")
    with pytest.raises(ContractError, match="INVALID_FACTOR_CONFIG_SNAPSHOT"):
        replace(batch, config_snapshot=json.dumps(config).encode())


def test_work_p2_003_config_schema_is_validated(batch):
    config = json.loads(batch.config_snapshot)
    config["spec"]["parameters"][0][1] = "float"
    with pytest.raises(ContractError, match="UNSUPPORTED_PARAMETER_SCHEMA"):
        replace(batch, config_snapshot=canonical(config))
