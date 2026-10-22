import importlib.metadata
from copy import deepcopy

import pytest

from aqrp.core.environment import runtime_manifest, verify_runtime
from aqrp.core.errors import ContractError


def test_actual_locked_environment_and_rejections(monkeypatch):
    manifest = runtime_manifest()
    verify_runtime(manifest)
    wrong = deepcopy(manifest)
    wrong["python"] = "3.12.0"
    with pytest.raises(ContractError, match="UNVERIFIED_RESEARCH_RUNTIME"):
        verify_runtime(wrong)
    wrong = deepcopy(manifest)
    wrong["packages"][0]["installed_record_sha256"] = None
    with pytest.raises(ContractError):
        verify_runtime(wrong)
    real = importlib.metadata.distribution

    def missing(name):
        if name == "numpy":
            raise importlib.metadata.PackageNotFoundError(name)
        return real(name)

    monkeypatch.setattr(importlib.metadata, "distribution", missing)
    invalid = runtime_manifest()
    assert next(r for r in invalid["packages"] if r["name"] == "numpy")["version"] is None
    with pytest.raises(ContractError):
        verify_runtime(invalid)
