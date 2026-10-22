from copy import deepcopy
from dataclasses import replace
from datetime import date

import numpy as np
import pandas as pd
import pytest

from aqrp.core.errors import ContractError, SnapshotMismatch
from aqrp.core.time import utc
from aqrp.data.exposures import exposures_as_of, publish_exposures
from aqrp.data.synthetic import load_synthetic
from aqrp.research.pipeline import compose, operators, pipeline


def frame():
    return pd.DataFrame(
        [
            {
                "factor_key": k,
                "session": "2024-01-04",
                "security_id": f"SYN_A:{i + 1:03d}",
                "score": v,
                "decision_time": utc("2024-01-04T12:05:00Z"),
                "available_at": utc("2024-01-04T12:00:00Z"),
                "stage": "final",
            }
            for k, values in (("a", [1, 2, 3, 4, 6, 8]), ("b", [8, 6, 4, 3, 2, 1]))
            for i, v in enumerate(values)
        ]
    )


def composition():
    return {
        "factor_keys": ["a", "b"],
        "weights": [1, 1],
        "directions": [1, -1],
        "direction_applied": False,
        "normalization": "cross_sectional_sample_z",
        "input_stage": "final",
        "min_n": 3,
        "redundancy": {"tau": 0.9, "min_pair_n": 3, "min_days": 1, "min_fraction": 0.5},
    }


def exposures():
    return [
        {
            "security_id": f"SYN_A:{i + 1:03d}",
            "market_id": "SYN_A",
            "currency": "SYNCCY",
            "industry_version": "v1",
            "industry": "A" if i % 2 else "B",
            "market_cap": str(100 * (i + 1) ** 2),
            "event_time": "2024-01-01T00:00:00Z",
            "available_at": "2024-01-01T00:00:00Z",
            "effective_from": "2024-01-01T00:00:00Z",
            "effective_to": None,
            "revision_id": 1,
        }
        for i in range(6)
    ]


def parent_tables():
    tables = load_synthetic(sessions=[(date(2024, 1, 4), "12:00:00")])
    for i in range(2, 7):
        row = deepcopy(tables["security_master"][0])
        row["security_id"] = f"SYN_A:{i:03d}"
        tables["security_master"].append(row)
    return tables


def test_five_stages_and_ols_pit_reference(make_snapshot, tmp_path):
    s = make_snapshot(parent_tables())
    ref = publish_exposures(exposures(), s, tmp_path / "exposures")
    stages = pipeline(
        frame(),
        {
            "clean": {"method": "mad", "k": 3},
            "standardized": {"method": "zscore"},
            "neutralize": True,
        },
        ref,
        market="SYN_A",
        currency="SYNCCY",
    )
    assert list(stages) == ["raw", "clean", "standardized", "neutralized", "final"]
    for key, section in stages["final"]["rows"].groupby("factor_key"):
        residual = section["score"].to_numpy()
        assert sum(residual) == pytest.approx(0, abs=1e-12)
        assert sum(residual[[0, 2, 4]]) == pytest.approx(0, abs=1e-12)
        assert residual @ np.log([100 * (i + 1) ** 2 for i in range(6)]) == pytest.approx(
            0, abs=1e-11
        )
    skipped = pipeline(
        frame(),
        {"clean": {"method": "none"}, "standardized": {"method": "none"}, "neutralize": False},
    )
    assert (
        skipped["clean"]["status"]
        == skipped["standardized"]["status"]
        == skipped["neutralized"]["status"]
        == "SKIPPED"
    )
    with pytest.raises(ContractError, match="EXPOSURES_REQUIRED"):
        pipeline(
            frame(),
            {"clean": {"method": "none"}, "standardized": {"method": "none"}, "neutralize": True},
        )


def test_composite_common_mask_direction_once_and_redundancy():
    f = frame()
    spec = composition()
    result = compose(f, spec)
    # Independent analytic sample-z of the common six-asset intersection.
    a = np.array([1, 2, 3, 4, 6, 8])
    b = np.array([8, 6, 4, 3, 2, 1])
    expected = ((a - 4) / np.sqrt(6.8) - (b - 4) / np.sqrt(6.8)) / 2
    assert [r["score"] for r in result["scores"]] == pytest.approx(expected)
    assert result["pairs"][0]["spearman"]["value"] == pytest.approx(-1)
    assert result["redundancy"][0]["flag"] and not result["redundancy"][0]["auto_weight_change"]
    f.loc[0, "score"] = None
    assert len(compose(f, spec)["scores"]) == 5
    spec["redundancy"] = None
    assert compose(f, spec)["redundancy"][0]["flag"] is None
    spec["min_n"] = 20
    assert compose(f, spec)["pairs"][0]["reason"] == "INSUFFICIENT_INTERSECTION"
    spec["min_n"] = 3
    f["score"] = 1
    assert compose(f, spec)["pairs"][0]["reason"] == "ZERO_VARIANCE"


@pytest.mark.parametrize(
    "change",
    [
        {"weights": [-1, 1]},
        {"weights": [0, 0]},
        {"weights": [True, 1]},
        {"directions": [1, True]},
        {"direction_applied": True},
        {"factor_keys": ["a", "a"]},
        {"weights": [1]},
        {"weights": [1, 0]},
        {"normalization": "raw"},
    ],
)
def test_composite_rejections(change):
    with pytest.raises(ContractError):
        compose(frame(), {**composition(), **change})


def test_stage_pit_missing_exposures_and_grid_gaps(monkeypatch):
    import aqrp.research.pipeline as module

    spec = {"clean": {"method": "none"}, "standardized": {"method": "none"}, "neutralize": False}
    with pytest.raises(ContractError, match="DUPLICATE_STAGE_SCORE"):
        pipeline(pd.concat([frame(), frame()], ignore_index=True), spec)
    f = frame()
    f.loc[0, "decision_time"] = utc("2024-01-04T12:04:59Z")
    with pytest.raises(ContractError, match="MIXED_DECISION_TIMES"):
        pipeline(f, spec)
    f = frame().assign(available_at=utc("2024-01-04T12:06:00Z"))
    with pytest.raises(ContractError, match="STAGE_INPUT_NOT_AVAILABLE_AT_DECISION"):
        pipeline(f, spec)
    f = frame().astype({"score": float})
    f.loc[0, "score"] = float("inf")
    raw = pipeline(f, spec)["raw"]["rows"]
    assert raw.iloc[0]["reason"] == "RAW_NONFINITE_INPUT"
    monkeypatch.setattr(module, "exposures_as_of", lambda *a: {})
    result = pipeline(frame(), {**spec, "neutralize": True}, exposure_ref=object())
    assert result["neutralized"]["rows"]["score"].isna().all()
    assert result["neutralized"]["diagnostics"][0]["reason"] == "NO_VALID_EXPOSURES"
    f = pd.concat([frame().assign(session="2024-01-02"), frame()], ignore_index=True)
    result = operators(
        f, [{"op": "mean", "length": 2}], calendar_grid=["2024-01-02", "2024-01-03", "2024-01-04"]
    )
    assert result["score"].isna().all()
    for change in (
        {"min_n": 1},
        {"redundancy": {"min_pair_n": 1, "min_days": 1, "tau": 0.9, "min_fraction": 1}},
    ):
        with pytest.raises(ContractError):
            compose(frame(), {**composition(), **change})


def test_operator_grid_and_composite_stage():
    f = frame()
    f.loc[0, "stage"] = "raw"
    with pytest.raises(ContractError, match="COMPOSITE_STAGE_MISMATCH"):
        compose(f, composition())
    f = pd.concat([frame().assign(session="2024-01-03"), frame()], ignore_index=True)
    out = operators(
        f,
        [
            {"op": "delta", "length": 1},
            {"op": "rank"},
            {"op": "conditional", "comparison": "gt", "threshold": 0.5, "otherwise": 0},
        ],
    )
    assert out[out["session"] == "2024-01-03"]["score"].isna().all()
    correlated = operators(f, [{"op": "correlation", "length": 2, "other_factor": "b"}])
    assert correlated["score"].isna().all()  # every two-point time series is constant


def test_exposure_revision_visibility_units_missing_and_integrity(make_snapshot, tmp_path):
    s = make_snapshot(parent_tables())
    rows = exposures()
    revision = deepcopy(rows[0])
    revision.update(revision_id=2, industry="future", available_at="2024-02-01T00:00:00Z")
    ref = publish_exposures(rows + [revision], s, tmp_path)
    actual = exposures_as_of(
        ref, "2024-01-04T00:00:00Z", "SYN_A", "SYNCCY", {r["security_id"] for r in rows}
    )
    assert actual["SYN_A:001"]["industry"] == "B"
    assert (
        exposures_as_of(ref, "2024-02-02T00:00:00Z", "SYN_A", "SYNCCY", {"SYN_A:001"})["SYN_A:001"][
            "industry"
        ]
        == "future"
    )
    assert exposures_as_of(ref, "2023-12-31T00:00:00Z", "SYN_A", "SYNCCY", {"SYN_A:001"}) == {}
    with pytest.raises(ContractError, match="EXPOSURE_MARKET_OR_CURRENCY_MISMATCH"):
        exposures_as_of(ref, "2024-01-04T00:00:00Z", "SYN_A", "USD", {"SYN_A:001"})
    with pytest.raises(SnapshotMismatch):
        exposures_as_of(
            replace(ref, manifest_hash="0" * 64), "2024-01-04T00:00:00Z", "SYN_A", "SYNCCY", set()
        )


@pytest.mark.parametrize(
    "change",
    [
        {"market_cap": 0},
        {"market_cap": "NaN"},
        {"revision_id": True},
        {"security_id": ""},
        {"available_at": "2023-01-01T00:00:00Z"},
        {"effective_to": "2023-01-01T00:00:00Z"},
    ],
)
def test_exposure_contract_rejections(make_snapshot, tmp_path, change):
    row = {**exposures()[0], **change}
    with pytest.raises(ContractError):
        publish_exposures([row], make_snapshot(load_synthetic()), tmp_path)
