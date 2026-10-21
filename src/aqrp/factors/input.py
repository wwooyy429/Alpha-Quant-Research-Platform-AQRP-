"""Validate restricted DataView and take per-security consecutive PIT sessions."""

from aqrp.core.contracts import DataView
from aqrp.core.errors import ContractError, DataQualityError, TimeLeakageError
from aqrp.core.time import utc


def windows(view, context):
    if not isinstance(view, DataView):
        raise ContractError("DATA_VIEW_REQUIRED", "view")
    if view.schema_version != context.spec.data_contract_version or not {
        "as_of",
        "calendar_id",
        "calendar_version",
        "price_basis",
    } <= set(view.metadata):
        raise ContractError("INVALID_FACTOR_VIEW_CONTRACT", "view")
    if (
        view.snapshot_ref.snapshot_id != context.snapshot_id
        or view.snapshot_ref.manifest_hash != context.manifest_hash
        or view.query_hash != context.query_hash
        or utc(view.metadata["as_of"]) != context.decision_time
        or view.metadata["calendar_id"] != context.calendar_id
        or view.metadata["calendar_version"] != context.calendar_version
        or view.metadata["price_basis"] != context.spec.price_basis
    ):
        raise ContractError("FACTOR_VIEW_CONTEXT_MISMATCH", "view")
    required = {
        "security_id",
        "market_id",
        "calendar_id",
        "session_date",
        "event_time",
        "available_at",
        "quality_status",
    } | set(context.spec.required_fields)
    if not required <= set(view.schema.names):
        raise ContractError("MISSING_FACTOR_INPUT_FIELD", "view")
    by_security = {sid: {} for sid in context.security_ids}
    for row in view.table.to_pylist():
        if row["event_time"] > context.decision_time or row["available_at"] > context.decision_time:
            raise TimeLeakageError("FUTURE_FACTOR_INPUT", "view")
        if (
            row["security_id"] not in by_security
            or row["market_id"] != context.market_id
            or row["calendar_id"] != context.calendar_id
        ):
            raise ContractError("FACTOR_INPUT_IDENTITY_MISMATCH", "view")
        records = by_security[row["security_id"]]
        if row["session_date"] in records:
            raise DataQualityError("DUPLICATE_FACTOR_SESSION", "view")
        records[row["session_date"]] = row
    schedule = dict(context.sessions)
    dates = sorted(schedule)
    length = dict(context.params)["lookback"] + 1
    signal_time = min(
        schedule.get(context.target_session, context.decision_time), context.decision_time
    )
    output = []
    for sid, records in by_security.items():
        reason, selected = "NONE", []
        if context.target_session not in schedule or context.target_session not in records:
            reason = "TARGET_NOT_VISIBLE"
        elif len(dates) < length:
            reason = "INSUFFICIENT_HISTORY"
        else:
            required_dates = dates[-length:]
            if any(day not in records for day in required_dates):
                reason = "MISSING_SESSION"
            else:
                selected = [records[day] for day in required_dates]
                if any(
                    r["quality_status"] != "VALID"
                    or any(r[f] is None for f in context.spec.required_fields)
                    for r in selected
                ):
                    reason = "MISSING_INPUT"
                elif any(
                    r[f] <= 0 if f == "close" else r[f] < 0
                    for r in selected
                    for f in context.spec.required_fields
                ):
                    raise DataQualityError("INVALID_PRICE_OR_VOLUME", sid)
        output.append((sid, signal_time, selected, reason))
    return tuple(output)
