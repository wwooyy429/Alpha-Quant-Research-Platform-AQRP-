"""Actual optional UI distribution/RECORD identity, separate from the core lock."""

import hashlib
import importlib.metadata
import re
import sys
from pathlib import Path

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError


def ui_environment():
    lock = Path(__file__).with_name(
        "requirements-windows.lock" if sys.platform == "win32" else "requirements-linux.lock"
    )
    rows = []
    for name, version in re.findall(r"^([a-z0-9-]+)==([^\s\\]+)", lock.read_text(), re.M):
        try:
            dist = importlib.metadata.distribution(name)
            record = dist.read_text("RECORD")
        except importlib.metadata.PackageNotFoundError as exc:
            raise ContractError("UI_DEPENDENCY_MISSING", name) from exc
        if dist.version != version or record is None:
            raise ContractError("UI_DEPENDENCY_IDENTITY_MISMATCH", name)
        rows.append(
            {
                "name": name,
                "version": version,
                "RECORD_sha256": hashlib.sha256(record.encode()).hexdigest(),
            }
        )
    if len(rows) != 29:
        raise ContractError("UI_EXTENSION_LOCK_CHANGED")
    return {
        "lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "packages": rows,
        "packages_hash": digest(rows),
    }
