from copy import deepcopy
from decimal import Decimal

import pytest

from aqrp.core.errors import ContractError, DataQualityError
from aqrp.core.time import utc
from aqrp.data.quality import validate_dataset
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, record


def test_revision_ids_are_monotonic(tables):
    old = deepcopy(tables["bars_daily"][0])
    old.update(revision_id=0, available_at=utc("2024-01-04T00:00:00Z"))
    tables["bars_daily"].append(old)
    with pytest.raises(DataQualityError, match="NONMONOTONIC"):
        validate_dataset(tables)


def test_calendar_provenance_version(tables, tmp_path):
    p = dict(PROVENANCE)
    p["calendar_version"] = "wrong"
    with pytest.raises(ContractError, match="CALENDAR_VERSION"):
        publish_snapshot(tables, p, tmp_path)


def test_adjustment_lineage(tables):
    effective = utc("2024-01-03T00:00:00Z")
    factor = record(
        "adjustment_factors",
        security_id="SYN_A:001",
        effective_at=effective,
        revision_id=1,
        ratio=Decimal(2),
        action_id="s1",
        method="SPLIT",
        view_cutoff=effective,
    )
    tables["adjustment_factors"] = [factor]
    with pytest.raises(DataQualityError, match="ADJUSTMENT_FACTOR"):
        validate_dataset(tables)
    tables["corporate_actions"] = [
        record(
            "corporate_actions",
            action_id="s1",
            revision_id=1,
            security_id="SYN_A:001",
            type="SPLIT",
            announcement_at=utc("2024-01-01T00:00:00Z"),
            effective_at=effective,
            split_ratio=Decimal(2),
            currency="SYNCCY",
            ex_date=effective.date(),
        )
    ]
    assert validate_dataset(tables)["adjustment_factors"].report.valid == 1
