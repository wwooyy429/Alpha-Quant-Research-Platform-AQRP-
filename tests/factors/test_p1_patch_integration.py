"""Phase 1 repair boundaries must hold through the Phase 2 host and code gate."""

from copy import deepcopy

import pytest

from aqrp.core.errors import ContractError, TimeLeakageError, TimestampResolutionError
from aqrp.factors import admission, builtin_spec
from aqrp.factors.builtins import BuiltinFactor


def forbid_compute(*args, **kwargs):
    pytest.fail("Rejected host input or changed code must not reach factor computation")


@pytest.mark.parametrize(
    "decision_time",
    ["2024-01-04T12:05:00.0000001Z", "2024-01-04T12:05:00+00:00:00.0000001"],
)
def test_data_002_factor_012_host_rejects_submicrosecond_decisions(
    decision_time, factor_tables, factor_query, factor_engine, make_snapshot, monkeypatch
):
    spec = builtin_spec("momentum")
    snapshot = make_snapshot(factor_tables)
    monkeypatch.setattr(BuiltinFactor, "compute", forbid_compute)
    with pytest.raises(TimestampResolutionError, match="SUB_MICROSECOND"):
        factor_engine.run(spec.ref, factor_query, decision_time, snapshot)


@pytest.mark.parametrize("table", ["calendar", "universe_membership"])
def test_data_002_factor_012_unknown_auxiliary_data_cannot_feed_factor(
    table, factor_tables, factor_query, factor_engine, make_snapshot, monkeypatch
):
    factor_tables[table][0].update(
        quality_status="UNKNOWN_AVAILABILITY", reason_code="SOURCE_HISTORY_UNVERIFIED"
    )
    snapshot = make_snapshot(factor_tables, exploratory=True)
    spec = builtin_spec("momentum")
    monkeypatch.setattr(BuiltinFactor, "compute", forbid_compute)
    with pytest.raises(TimeLeakageError, match="EXPLORATORY_SNAPSHOT"):
        factor_engine.run(spec.ref, factor_query, "2024-01-04T12:05:00Z", snapshot)


@pytest.mark.parametrize("changed_path", ["core/time.py", "data/pit.py"])
def test_sec_001_shared_code_drift_invalidates_existing_factor_pin(
    changed_path, factor_tables, factor_query, factor_engine, make_snapshot, monkeypatch
):
    spec = builtin_spec("momentum")
    snapshot = make_snapshot(factor_tables)
    manifest = deepcopy(admission.bundle_manifest())
    next(item for item in manifest["files"] if item["path"] == changed_path)["sha256"] = "0" * 64
    monkeypatch.setattr(admission, "bundle_manifest", lambda: manifest)
    monkeypatch.setattr(BuiltinFactor, "compute", forbid_compute)
    with pytest.raises(ContractError, match="IMPLEMENTATION_HASH_CHANGED"):
        factor_engine.run(spec.ref, factor_query, "2024-01-04T12:05:00Z", snapshot)
