"""Immutable engineering contracts; no research or strategy approval domain."""

import json
import math
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol

from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc

from .versions import compatible, version


def identifier(value, field):
    if not isinstance(value, str) or not value:
        raise ContractError("MISSING_FACTOR_FIELD", field)


def content_hash(value):
    if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{64}", value):
        raise ContractError("INVALID_CONTENT_HASH", "implementation_hash")


def uuid_value(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ContractError("INVALID_RUN_ID", "run_id") from exc


@dataclass(frozen=True)
class FactorRef:
    factor_id: str
    factor_version: str
    implementation_hash: str

    def __post_init__(self):
        identifier(self.factor_id, "factor_id")
        version(self.factor_version)
        content_hash(self.implementation_hash)


@dataclass(frozen=True)
class FactorSpec:
    factor_id: str
    factor_name: str
    factor_version: str
    parameters: tuple = (("lookback", "int", 20, 1, 252),)
    required_fields: tuple = ("close",)
    lookback_window: str = "L+1 consecutive visible sessions ending at target"
    supported_frequency: str = "daily"
    signal_available_time: str = "decision_time; simulated compute delay=0"
    output_unit: str = "dimensionless_ratio"
    factor_direction: int = 1
    implementation_version: str = ""
    api_compatibility: str = ">=1.0.0,<2.0.0"
    data_contract_version: str = "contracts/1.0.0"
    review_ref: str = ""
    price_basis: str = "split_adjusted"
    bundle_manifest_ref: str = "reviewed_code.json"

    def __post_init__(self):
        self.ref
        for field in ("factor_name", "lookback_window", "signal_available_time", "review_ref"):
            identifier(getattr(self, field), field)
        if self.parameters != (("lookback", "int", 20, 1, 252),):
            raise ContractError("UNSUPPORTED_PARAMETER_SCHEMA", "parameters")
        if self.required_fields != (("volume",) if self.factor_id == "volume" else ("close",)):
            raise ContractError("INVALID_REQUIRED_FIELDS", "required_fields")
        if self.supported_frequency != "daily" or self.price_basis != "split_adjusted":
            raise ContractError("UNSUPPORTED_FACTOR_PROFILE", "FactorSpec")
        if type(self.factor_direction) is not int or self.factor_direction != 1:
            raise ContractError("INVALID_FACTOR_DIRECTION", "factor_direction")
        if (
            self.output_unit != "dimensionless_ratio"
            or self.data_contract_version != "contracts/1.0.0"
        ):
            raise ContractError("INCOMPATIBLE_DATA_CONTRACT", "FactorSpec")
        compatible(self.api_compatibility)

    @property
    def ref(self):
        return FactorRef(self.factor_id, self.factor_version, self.implementation_version)

    @property
    def spec_hash(self):
        return digest(asdict(self))


def freeze_parameters(spec, values=None):
    values = {} if values is None else values
    if not isinstance(values, dict) or set(values) - {"lookback"}:
        raise ContractError("UNKNOWN_FACTOR_PARAMETER", "parameters")
    lookback = values.get("lookback", spec.parameters[0][2])
    if type(lookback) is not int:
        raise ContractError("INVALID_PARAMETER_TYPE", "lookback")
    if not 1 <= lookback <= 252:
        raise ContractError("PARAMETER_OUT_OF_RANGE", "lookback")
    frozen = (("lookback", lookback),)
    return frozen, digest(dict(frozen))


@dataclass(frozen=True)
class FactorContext:
    spec: FactorSpec
    run_id: str
    computation_id: str
    decision_time: datetime
    target_session: date
    snapshot_id: str
    manifest_hash: str
    query_hash: str
    calendar_id: str
    calendar_version: str
    sessions: tuple
    symbols: tuple
    market_id: str
    security_ids: tuple
    params: tuple
    params_hash: str
    seed: int = 0
    requested_weight: Decimal | None = None

    def __post_init__(self):
        object.__setattr__(self, "run_id", uuid_value(self.run_id))
        object.__setattr__(self, "computation_id", uuid_value(self.computation_id))
        object.__setattr__(self, "decision_time", utc(self.decision_time))
        if type(self.target_session) is not date or type(self.seed) is not int:
            raise ContractError("INVALID_FACTOR_CONTEXT", "FactorContext")
        if self.requested_weight is not None and (
            not isinstance(self.requested_weight, Decimal) or not self.requested_weight.is_finite()
        ):
            raise ContractError("INVALID_WEIGHT_METADATA", "requested_weight")
        if (
            type(self.security_ids) is not tuple
            or not self.security_ids
            or len(set(self.security_ids)) != len(self.security_ids)
        ):
            raise ContractError("INVALID_SECURITY_IDS", "security_ids")
        for sid in self.security_ids:
            identifier(sid, "security_id")
        if any(not isinstance(x, tuple) for x in (self.sessions, self.symbols, self.params)):
            raise ContractError("MUTABLE_CONTEXT", "FactorContext")
        if any(
            type(pair) is not tuple or len(pair) != 2
            for group in (self.sessions, self.symbols, self.params)
            for pair in group
        ):
            raise ContractError("MUTABLE_CONTEXT", "FactorContext")
        if any(type(day) is not date for day, _ in self.sessions):
            raise ContractError("INVALID_FACTOR_SESSION", "sessions")
        if len({d for d, _ in self.sessions}) != len(self.sessions):
            raise ContractError("DUPLICATE_FACTOR_SESSION", "sessions")
        object.__setattr__(
            self, "sessions", tuple((day, utc(close)) for day, close in self.sessions)
        )
        if any(
            not isinstance(sid, str) or (symbol is not None and not isinstance(symbol, str))
            for sid, symbol in self.symbols
        ):
            raise ContractError("INVALID_FACTOR_SYMBOL", "symbols")
        params, checksum = freeze_parameters(self.spec, dict(self.params))
        if self.params != params or self.params_hash != checksum:
            raise ContractError("PARAMETER_HASH_MISMATCH", "params")
        content_hash(self.manifest_hash)
        content_hash(self.query_hash)


@dataclass(frozen=True)
class Signal:
    signal_time: datetime
    security_id: str
    symbol: str | None
    market_id: str
    factor_id: str
    factor_version: str
    factor_value: float | None
    available_at: datetime
    validity: str
    reason: str
    snapshot_id: str
    params_hash: str
    run_id: str
    computation_id: str
    implementation_hash: str
    processing_stage: str = "raw"

    def __post_init__(self):
        object.__setattr__(self, "signal_time", utc(self.signal_time))
        object.__setattr__(self, "available_at", utc(self.available_at))
        FactorRef(self.factor_id, self.factor_version, self.implementation_hash)
        object.__setattr__(self, "run_id", uuid_value(self.run_id))
        object.__setattr__(self, "computation_id", uuid_value(self.computation_id))
        content_hash(self.params_hash)
        for key in ("security_id", "market_id", "snapshot_id", "reason"):
            identifier(getattr(self, key), key)
        valid = self.validity == "VALID"
        if self.validity not in ("VALID", "INVALID") or self.processing_stage != "raw":
            raise ContractError("INVALID_SIGNAL_STATUS", "Signal")
        if (
            valid
            and (
                type(self.factor_value) is not float
                or not math.isfinite(self.factor_value)
                or self.reason != "NONE"
            )
        ) or (not valid and (self.factor_value is not None or self.reason == "NONE")):
            raise ContractError("INVALID_SIGNAL_VALUE", "factor_value")
        if self.available_at < self.signal_time:
            raise ContractError("SIGNAL_TIME_ORDER", "available_at")

    @property
    def key(self):
        return (
            self.run_id,
            self.factor_id,
            self.factor_version,
            self.params_hash,
            self.security_id,
            self.signal_time,
            self.processing_stage,
        )


@dataclass(frozen=True)
class SignalBatch:
    rows: tuple[Signal, ...]
    config_snapshot: bytes

    def __post_init__(self):
        if type(self.rows) is not tuple or type(self.config_snapshot) is not bytes:
            raise ContractError("MUTABLE_SIGNAL_BATCH", "SignalBatch")
        unique = {}
        for row in self.rows:
            if not isinstance(row, Signal):
                raise ContractError("SIGNAL_REQUIRED", "rows")
            if row.key in unique and unique[row.key] != row:
                raise ContractError("CONFLICTING_SIGNAL_KEY", "SignalBatch")
            unique[row.key] = row
        object.__setattr__(
            self,
            "rows",
            tuple(sorted(unique.values(), key=lambda r: (r.signal_time, r.security_id))),
        )
        try:
            config = json.loads(self.config_snapshot, object_pairs_hook=_unique_config_object)
            run_id = uuid_value(config["run_id"])
            computation_id = uuid_value(config["computation_id"])
            spec_config = config["spec"]
            spec = FactorSpec(
                **(
                    spec_config
                    | {
                        "parameters": tuple(tuple(p) for p in spec_config["parameters"]),
                        "required_fields": tuple(spec_config["required_fields"]),
                    }
                )
            )
            params = config["params"]
            if not isinstance(params, list) or any(
                not isinstance(pair, list) or len(pair) != 2 or not isinstance(pair[0], str)
                for pair in params
            ):
                raise ContractError("INVALID_FACTOR_PARAMETERS", "params")
            frozen, checksum = freeze_parameters(spec, dict(params))
            if params != [list(pair) for pair in frozen] or config["params_hash"] != checksum:
                raise ContractError("PARAMETER_LINEAGE_MISMATCH", "params")
            expected = {
                "run_id": run_id,
                "computation_id": computation_id,
                "params_hash": checksum,
                "snapshot_id": config["snapshot_id"],
                "factor_id": config["spec"]["factor_id"],
                "factor_version": config["spec"]["factor_version"],
                "implementation_hash": config["spec"]["implementation_version"],
                "market_id": config["market_id"],
                "available_at": utc(config["decision_time"]),
            }
            if any(
                any(getattr(row, key) != value for key, value in expected.items())
                or row.security_id not in config["security_ids"]
                for row in self.rows
            ):
                raise ContractError("SIGNAL_RUN_LINEAGE_MISMATCH", "SignalBatch")
            object.__setattr__(self, "config_snapshot", canonical(config))
        except ContractError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise ContractError("INVALID_FACTOR_CONFIG_SNAPSHOT", "SignalBatch") from exc

    @property
    def logical_hash(self):
        excluded = {"snapshot_id", "run_id", "computation_id"}
        return digest(
            [{k: v for k, v in asdict(row).items() if k not in excluded} for row in self.rows]
        )

    @property
    def content_hash(self):
        return digest(
            {"rows": [asdict(r) for r in self.rows], "config": self.config_snapshot.decode("utf-8")}
        )


class Factor(Protocol):
    def compute(self, view, context: FactorContext) -> SignalBatch: ...


def config_bytes(context):
    return canonical(asdict(context))


def _unique_config_object(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ContractError("DUPLICATE_FACTOR_CONFIG_KEY", "config_snapshot")
    return result
