"""Offline engineering adapter; specific providers and live execution are refused."""

from .adapter import (
    AdapterReceipt,
    AdapterSpec,
    CapabilityReport,
    adapt_engineering,
    adapter_spec,
    capabilities,
    execute_engineering,
    input_reference,
    read_adapter_result,
)

__all__ = [
    "AdapterReceipt",
    "AdapterSpec",
    "CapabilityReport",
    "adapt_engineering",
    "adapter_spec",
    "capabilities",
    "execute_engineering",
    "input_reference",
    "read_adapter_result",
]
