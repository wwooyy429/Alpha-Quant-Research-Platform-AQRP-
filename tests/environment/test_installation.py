import importlib.metadata
import sys

import duckdb
import numpy
import pandas
import pyarrow

import aqrp


def test_env_001_exact_runtime_and_imports():
    assert sys.version_info[:3] == (3, 13, 16)
    assert sys.maxsize > 2**32
    assert sys._is_gil_enabled()
    assert aqrp.__version__ == "0.3.1.dev1"
    for package, expected in {
        "numpy": "2.5.4",
        "pandas": "3.0.6",
        "pyarrow": "26.0.0",
        "duckdb": "1.5.6",
        "tzdata": "2026.5",
    }.items():
        assert importlib.metadata.version(package) == expected
    assert duckdb.sql("select 1").fetchone() == (1,)
    assert numpy.array([1, 2]).sum() == 3
    assert pandas.Series([1, 2]).sum() == 3
    assert pyarrow.array([1, None]).null_count == 1


def test_structured_error_contract():
    from aqrp.core.errors import ContractError, TimestampResolutionError

    error = TimestampResolutionError("NANOSECOND", "event_time", "request-1")
    assert isinstance(error, ContractError)
    assert (error.code, error.field, error.request_id, error.retryable) == (
        "NANOSECOND",
        "event_time",
        "request-1",
        False,
    )
