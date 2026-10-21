"""Actual locked runtime identity; a lock hash is never an installed-version claim."""

import hashlib
import importlib.metadata
import platform
import sys
from pathlib import Path

from aqrp.core.errors import ContractError

LOCKED = {
    "coverage": "7.16.2",
    "duckdb": "1.5.6",
    "hypothesis": "6.170.5",
    "iniconfig": "2.3.1",
    "numpy": "2.5.4",
    "packaging": "26.3",
    "pandas": "3.0.6",
    "pip": "26.2.1",
    "pluggy": "1.7.0",
    "pyarrow": "26.0.0",
    "pygments": "2.21.0",
    "pytest": "9.1.1",
    "pytest-cov": "7.1.0",
    "python-dateutil": "2.9.0.post0",
    "ruff": "0.17.1",
    "setuptools": "84.2.0",
    "six": "1.17.0",
    "sortedcontainers": "2.4.0",
    "tzdata": "2026.5",
    "uv": "0.13.4",
    "wheel": "0.48.0",
}


def runtime_manifest():
    names = sorted(set(LOCKED) | ({"colorama"} if sys.platform == "win32" else set()))
    records = []
    for name in names:
        try:
            dist = importlib.metadata.distribution(name)
            record = dist.read_text("RECORD")
            records.append(
                {
                    "name": name,
                    "version": dist.version,
                    "installed_record_sha256": hashlib.sha256(record.encode()).hexdigest()
                    if record is not None
                    else None,
                }
            )
        except importlib.metadata.PackageNotFoundError:
            records.append({"name": name, "version": None, "installed_record_sha256": None})
    return {
        "python": platform.python_version(),
        "standard_gil": sys._is_gil_enabled(),
        "x64": sys.maxsize > 2**32,
        "platform": platform.platform(),
        "interpreter_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
        "packages": records,
        "record_scope": "Actual distribution RECORD metadata; clean SDK additionally verifies original dependency wheel hashes",
    }


def verify_runtime(manifest):
    expected = {**LOCKED, **({"colorama": "0.4.6"} if sys.platform == "win32" else {})}
    if (
        manifest["python"] != "3.13.16"
        or not manifest["standard_gil"]
        or not manifest["x64"]
        or {r["name"]: r["version"] for r in manifest["packages"]} != expected
        or any(r["installed_record_sha256"] is None for r in manifest["packages"])
    ):
        raise ContractError("UNVERIFIED_RESEARCH_RUNTIME")
