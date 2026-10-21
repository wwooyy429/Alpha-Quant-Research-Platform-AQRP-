import json
from copy import deepcopy
from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.synthetic import record
from aqrp.factors import builtin_spec, write_run


@pytest.mark.parametrize("weight", [Decimal("0.25"), Decimal("-1"), Decimal("0")])
def test_factor_010_weight_is_only_metadata(
    weight, factor_tables, factor_query, factor_engine, make_snapshot
):
    result = factor_engine.run(
        builtin_spec("momentum").ref,
        factor_query,
        "2024-01-04T12:05:00Z",
        make_snapshot(factor_tables),
        parameters={"lookback": 2},
        requested_weight=weight,
    )
    assert result.rows[0].factor_value == 0.21
    assert json.loads(result.config_snapshot)["requested_weight"] == str(weight)


@pytest.mark.parametrize("weight", [0.5, True, "0.5", Decimal("NaN"), Decimal("Infinity")])
def test_invalid_weight_metadata(input_case, weight):
    with pytest.raises(ContractError, match="WEIGHT_METADATA"):
        replace(input_case[1], requested_weight=weight)


def test_factor_010_old_pin_runs_after_disable(
    factor_tables, factor_query, factor_engine, factor_registry, make_snapshot
):
    spec = builtin_spec("momentum")
    snapshot = make_snapshot(factor_tables)
    pin = factor_registry.resolve(spec.ref)
    before = factor_engine.run_pinned(
        pin, factor_query, "2024-01-04T12:05:00Z", snapshot, parameters={"lookback": 2}
    )
    factor_registry.deactivate(
        spec.ref, actor="test", reason="new runs only", evidence=spec.review_ref
    )
    after = factor_engine.run_pinned(
        pin, factor_query, "2024-01-04T12:05:00Z", snapshot, parameters={"lookback": 2}
    )
    assert before.logical_hash == after.logical_hash
    with pytest.raises(ContractError, match="DISABLED"):
        factor_engine.run(spec.ref, factor_query, "2024-01-04T12:05:00Z", snapshot)


def test_future_action_and_calendar_do_not_change_past(
    factor_tables, factor_query, factor_engine, make_snapshot
):
    query = replace(factor_query, session_range=(date(2024, 1, 2), date(2024, 1, 3)))
    spec = builtin_spec("momentum")
    cutoff = "2024-01-03T12:05:00Z"
    before = factor_engine.run(
        spec.ref, query, cutoff, make_snapshot(factor_tables), parameters={"lookback": 1}
    )
    future = deepcopy(factor_tables)
    future["corporate_actions"].append(
        record(
            "corporate_actions",
            action_id="future-split",
            security_id="SYN_A:001",
            revision_id=1,
            type="SPLIT",
            announcement_at=utc("2024-01-04T08:00:00Z"),
            effective_at=utc("2024-01-04T09:00:00Z"),
            event_time=utc("2024-01-04T08:00:00Z"),
            available_at=utc("2024-01-04T08:00:00Z"),
            split_ratio=Decimal(2),
            ex_date=date(2024, 1, 4),
            currency="SYNCCY",
        )
    )
    calendar = deepcopy(future["calendar"][0])
    calendar.update(
        session_date=date(2024, 1, 5),
        open_at=utc("2024-01-05T09:00:00Z"),
        close_at=utc("2024-01-05T12:00:00Z"),
        event_time=utc("2024-01-05T09:00:00Z"),
    )
    future["calendar"].append(calendar)
    after = factor_engine.run(
        spec.ref, query, cutoff, make_snapshot(future), parameters={"lookback": 1}
    )
    assert before.logical_hash == after.logical_hash


def test_persistence_requires_validated_batch(tmp_path, factor_registry):
    with pytest.raises(ContractError, match="SIGNAL_BATCH_REQUIRED"):
        write_run(object(), tmp_path, factor_registry)
