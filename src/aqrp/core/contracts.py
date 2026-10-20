"""Frozen request/view types; no storage connection escapes the SDK."""

import uuid
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from types import MappingProxyType

import pyarrow as pa

from .errors import ContractError


@dataclass(frozen=True)
class SnapshotRef:
    root: Path
    snapshot_id: str
    manifest_hash: str


@dataclass(frozen=True)
class QuerySpec:
    security_ids: tuple[str, ...]
    market_id: str
    calendar_id: str
    session_range: tuple[date, date]
    fields: tuple[str, ...] = ("close", "volume")
    price_basis: str = "RAW"
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "contracts/1.0.0"

    def __post_init__(self):
        if (
            not isinstance(self.security_ids, tuple)
            or not self.security_ids
            or any(not isinstance(s, str) or not s for s in self.security_ids)
            or len(set(self.security_ids)) != len(self.security_ids)
            or not isinstance(self.fields, tuple)
            or not self.fields
            or len(set(self.fields)) != len(self.fields)
        ):
            raise ContractError("INVALID_QUERY_KEYS", "QuerySpec", self.request_id)
        if (
            not isinstance(self.session_range, tuple)
            or len(self.session_range) != 2
            or any(type(d) is not date for d in self.session_range)
            or self.session_range[0] > self.session_range[1]
        ):
            raise ContractError("INVALID_SESSION_RANGE", "session_range", self.request_id)
        if self.schema_version != "contracts/1.0.0" or self.price_basis not in (
            "RAW",
            "split_adjusted",
            "total_return",
        ):
            raise ContractError("UNSUPPORTED_QUERY_CONTRACT", "QuerySpec", self.request_id)


@dataclass(frozen=True)
class DataView:
    _ipc: bytes
    query_hash: str
    snapshot_ref: SnapshotRef
    lineage: tuple
    quality_counts: tuple
    request_id: str
    schema_version: str = "contracts/1.0.0"

    @classmethod
    def from_table(cls, table, **metadata):
        sink = pa.BufferOutputStream()
        with pa.ipc.new_stream(sink, table.schema) as writer:
            writer.write_table(table)
        return cls(_ipc=sink.getvalue().to_pybytes(), **metadata)

    @property
    def table(self):
        # Fresh buffers prevent even a caller mutating a memoryview from altering this view.
        return pa.ipc.open_stream(pa.py_buffer(bytearray(self._ipc))).read_all()

    @property
    def schema(self):
        return self.table.schema

    @property
    def metadata(self):
        return MappingProxyType(dict(self.lineage))

    def to_pandas(self):
        return self.table.to_pandas().copy(deep=True)
