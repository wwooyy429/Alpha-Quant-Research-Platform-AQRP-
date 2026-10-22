import pytest

from aqrp.core.errors import ContractError
from aqrp.validation.splits import overlaps, partition, purged_train, validate_splits, walk_forward


def rows():
    return [
        {
            "security_id": "A",
            "session": f"2024-01-0{i}",
            "horizon": 1,
            "label": 0.1,
            "available_at": f"2024-01-0{i + 1}T12:00:00Z",
            "information_interval": [f"2024-01-0{i}T12:00:00Z", f"2024-01-0{i + 1}T12:00:00Z"],
        }
        for i in range(1, 7)
    ]


def test_chronology_purge_closed_information_and_dedup():
    spec = {
        "train": ["2024-01-01", "2024-01-04"],
        "validation": ["2024-01-04", "2024-01-06"],
        "test": ["2024-01-06", "2024-01-08"],
        "embargo_sessions": 1,
    }
    validate_splits(spec)
    assert partition("2024-01-04", spec) == "validation"
    assert partition("2024-01-08", spec) == "outside"
    assert overlaps(
        ["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"],
        ["2024-01-02T00:00:00Z", "2024-01-03T00:00:00Z"],
    )
    calendar = [f"2024-01-0{i}" for i in range(1, 9)]
    r = purged_train(rows(), spec["train"], spec["validation"], "2024-01-08T00:00:00Z", calendar, 1)
    assert [x["session"] for x in r["train"]] == ["2024-01-01", "2024-01-02"]
    assert r["rejected"][0]["split_reason"] == "PURGED_INFORMATION_OVERLAP"
    fold = {
        "fit": spec["train"],
        "evaluate": spec["validation"],
        "fit_cutoff": "2024-01-04T00:00:00Z",
    }
    out = walk_forward(rows(), [fold, fold], calendar, 1)
    assert len(out[0]["eval"]) == 2 and out[1]["eval"] == []
    label = rows()
    label[0]["label"] = None
    r = purged_train(label, spec["train"], spec["validation"], "2024-01-02T00:00:00Z", calendar, 1)
    assert {x["split_reason"] for x in r["rejected"]} == {
        "INVALID_LABEL",
        "LABEL_NOT_AVAILABLE_AT_FIT",
    }


def test_invalid_split_and_walkforward():
    for spec in (
        {"train": ["2024-01-02", "2024-01-01"]},
        {"train": ["2024-01-01", "2024-01-04"], "validation": ["2024-01-03", "2024-01-05"]},
        {
            "train": ["2024-01-01", "2024-01-02"],
            "validation": ["2024-01-02", "2024-01-03"],
            "test": ["2024-01-03", "2024-01-04"],
            "embargo_sessions": True,
        },
    ):
        with pytest.raises(ContractError):
            validate_splits(spec)
    with pytest.raises(ContractError):
        walk_forward(
            [],
            [{"fit": ["2024-01-02", "2024-01-01"], "evaluate": ["2024-01-03", "2024-01-04"]}],
            [],
            1,
        )


def test_embargo_protects_prior_walk_forward_evaluations():
    labels = rows()
    labels[-1]["available_at"] = "2024-01-06T18:00:00Z"
    labels[-1]["information_interval"][1] = labels[-1]["available_at"]
    windows = [
        {
            "fit": ["2024-01-01", "2024-01-04"],
            "evaluate": ["2024-01-04", "2024-01-05"],
            "fit_cutoff": "2024-01-04T00:00:00Z",
        },
        {
            "fit": ["2024-01-01", "2024-01-08"],
            "evaluate": ["2024-01-08", "2024-01-09"],
            "fit_cutoff": "2024-01-08T00:00:00Z",
        },
    ]
    result = walk_forward(labels, windows, [f"2024-01-0{i}" for i in range(1, 10)], 1)
    assert any(
        r["session"] == "2024-01-06" and r["split_reason"] == "EMBARGO"
        for r in result[1]["rejected"]
    )
    windows[0]["fit_cutoff"] = "2024-01-04T00:00:00.000001Z"
    with pytest.raises(ContractError, match="FIT_CUTOFF_AFTER_EVALUATION_START"):
        walk_forward(labels, windows, [], 1)
