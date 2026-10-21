from copy import deepcopy
from datetime import date
from decimal import Decimal

import pytest

from aqrp.core.contracts import QuerySpec
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, load_synthetic


@pytest.fixture
def tables():
    data = load_synthetic()
    for r in data["bars_daily"]:
        p = Decimal("100" if r["market_id"] == "SYN_A" else "200")
        for f in ("open", "high", "low", "close"):
            r[f] = p
        r["amount"] = p * 10
        r["source_amount"] = str(p * 10)
    return data


@pytest.fixture
def make_snapshot(tmp_path):
    def make(data, **kwargs):
        return publish_snapshot(deepcopy(data), dict(PROVENANCE), tmp_path / "snapshots", **kwargs)

    return make


@pytest.fixture
def spec():
    return QuerySpec(("SYN_A:001",), "SYN_A", "SYN_A_CAL", (date(2024, 1, 2), date(2024, 1, 3)))
