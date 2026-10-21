import json
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pytest

from aqrp.core.contracts import DataView
from aqrp.core.errors import ContractError
from aqrp.core.security import static_guard
from aqrp.factors import admission, builtin_spec
from aqrp.factors.input import windows


def view_with(view, table):
    return DataView.from_table(
        table,
        query_hash=view.query_hash,
        snapshot_ref=view.snapshot_ref,
        lineage=view.lineage,
        quality_counts=view.quality_counts,
        request_id=view.request_id,
    )


def test_factor_012_view_copies_and_reproducibility(input_case):
    view, context = input_case
    first = windows(view, context)
    changed = view.to_pandas()
    changed.loc[:, "close"] = 999
    assert windows(view, context) == first
    assert context.params == (("lookback", 2),)
    assert not hasattr(context, "account") and not hasattr(context, "network")


@pytest.mark.parametrize(
    "changes",
    [
        {"snapshot_id": "other"},
        {"manifest_hash": "0" * 64},
        {"query_hash": "0" * 64},
        {"calendar_id": "other"},
        {"calendar_version": "other"},
        {"decision_time": "2024-01-04T13:00:00Z"},
    ],
)
def test_view_context_mismatch(input_case, changes):
    view, context = input_case
    with pytest.raises(ContractError, match="CONTEXT_MISMATCH"):
        windows(view, replace(context, **changes))


def test_missing_schema_metadata_and_type(input_case):
    view, context = input_case
    with pytest.raises(ContractError, match="DATA_VIEW_REQUIRED"):
        windows(None, context)
    with pytest.raises(ContractError, match="VIEW_CONTRACT"):
        windows(replace(view, lineage=()), context)
    with pytest.raises(ContractError, match="VIEW_CONTRACT"):
        windows(replace(view, schema_version="contracts/2.0.0"), context)
    with pytest.raises(ContractError, match="MISSING_FACTOR_INPUT_FIELD"):
        windows(view_with(view, view.table.drop(["close"])), context)
    with pytest.raises(ContractError, match="CONTEXT_MISMATCH"):
        windows(
            replace(
                view,
                lineage=tuple((k, "RAW" if k == "price_basis" else v) for k, v in view.lineage),
            ),
            context,
        )


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("security_id", "SYN_B:001", "IDENTITY"),
        ("market_id", "SYN_B", "IDENTITY"),
        ("calendar_id", "SYN_B_CAL", "IDENTITY"),
        ("close", Decimal(0), "INVALID_PRICE"),
    ],
)
def test_reject_forged_view_inputs(input_case, field, value, code):
    view, context = input_case
    rows = view.table.to_pylist()
    rows[0][field] = value
    with pytest.raises(ContractError, match=code):
        windows(view_with(view, pa.Table.from_pylist(rows, schema=view.schema)), context)


@pytest.mark.parametrize("field", ["event_time", "available_at"])
def test_forged_future_row_rejected(input_case, field):
    view, context = input_case
    rows = view.table.to_pylist()
    rows[0][field] = context.decision_time + timedelta(microseconds=1)
    with pytest.raises(ContractError, match="FUTURE_FACTOR_INPUT"):
        windows(view_with(view, pa.Table.from_pylist(rows, schema=view.schema)), context)


def test_duplicates_and_negative_volume(input_case):
    view, context = input_case
    rows = view.table.to_pylist()
    with pytest.raises(ContractError, match="DUPLICATE_FACTOR_SESSION"):
        windows(
            view_with(view, pa.Table.from_pylist(rows + [rows[0]], schema=view.schema)), context
        )
    volume_context = replace(context, spec=builtin_spec("volume"))
    rows[0]["volume"] = Decimal(-1)
    with pytest.raises(ContractError, match="INVALID_PRICE_OR_VOLUME"):
        windows(view_with(view, pa.Table.from_pylist(rows, schema=view.schema)), volume_context)


@pytest.mark.parametrize(
    "changes",
    [
        {"target_session": "2024-01-04"},
        {"seed": True},
        {"security_ids": []},
        {"security_ids": ("A", "A")},
        {"security_ids": ("",)},
        {"sessions": []},
        {"sessions": ([date(2024, 1, 2), None],)},
        {"sessions": (("2024-01-02", None),)},
        {"symbols": (("A", []),)},
        {"params_hash": "0" * 64},
        {"params": (("lookback", 1),)},
    ],
)
def test_deep_context_contract(input_case, changes):
    _, context = input_case
    with pytest.raises(ContractError):
        replace(context, **changes)


def test_duplicate_context_calendar(input_case):
    _, context = input_case
    with pytest.raises(ContractError, match="DUPLICATE_FACTOR_SESSION"):
        replace(context, sessions=(context.sessions[0], context.sessions[0]))


@pytest.mark.parametrize(
    "source",
    [
        "import os",
        "from os import system",
        "from . import other",
        "eval('1')",
        "exec('x=1')",
        "compile('1','','eval')",
        "__import__('os')",
        "open('x')",
        "obj.open('x')",
        "obj.__class__",
        "global x",
        "def f():\n nonlocal x",
    ],
)
def test_sec_001_static_rules_are_supplemental(source):
    with pytest.raises(ContractError, match="UNSAFE_PLUGIN"):
        static_guard(source)


def test_static_guard_valid_and_syntax_failure():
    assert (
        static_guard("from fractions import Fraction\nx = Fraction(1,2)")
        == "STATIC_GUARD_PASS_NOT_OS_SANDBOX"
    )
    with pytest.raises(ContractError, match="INVALID_PLUGIN_SYNTAX"):
        static_guard("def invalid(")


@pytest.mark.parametrize(
    "factor_id", ["volatility", "os.system", "C:/factor.py", "https://factor", lambda: 1]
)
def test_unknown_code_rejected_before_loading(factor_id, monkeypatch):
    def forbidden():
        raise AssertionError("Unknown candidate must not reach trusted policy or builtin loader")

    monkeypatch.setattr(admission, "reviewed_policy", forbidden)
    with pytest.raises(ContractError, match="UNKNOWN_OR_EXTERNAL"):
        builtin_spec(factor_id)


@pytest.mark.parametrize(
    "change",
    [
        {"state": "CANDIDATE"},
        {"environment": "PRODUCTION"},
        {"financial_approval": "STRATEGY_APPROVED"},
        {"reviewer": ""},
        {"review_ref": ""},
        {"bundle_sha256": "0" * 64},
        {"allowed_factor_ids": ["momentum"]},
    ],
)
def test_code_receipt_denial(change, monkeypatch):
    path = admission.PACKAGE / "factors/reviewed_code.json"
    policy = json.loads(path.read_bytes()) | change
    read_bytes = Path.read_bytes
    monkeypatch.setattr(
        Path,
        "read_bytes",
        lambda self: json.dumps(policy).encode() if self == path else read_bytes(self),
    )
    with pytest.raises(ContractError):
        admission.reviewed_policy()


def test_factor_hash_mismatch_wrong_metadata_and_runtime(monkeypatch):
    spec = builtin_spec("momentum")
    for changed in (
        None,
        replace(spec, factor_id="unknown"),
        replace(spec, implementation_version="0" * 64),
        replace(spec, review_ref="forged"),
        replace(spec, bundle_manifest_ref="other.json"),
    ):
        with pytest.raises(ContractError):
            admission.validate_admission(changed)
    monkeypatch.setattr(admission.sys, "version_info", (3, 11, 2))
    with pytest.raises(ContractError, match="ENVIRONMENT"):
        admission.reviewed_policy()


@pytest.mark.parametrize("mode", ["strategy", "research", "live"])
def test_no_unapproved_execution_modes(
    mode, factor_tables, factor_query, factor_engine, make_snapshot
):
    with pytest.raises(ContractError, match="UNSUPPORTED"):
        factor_engine.run(
            builtin_spec("momentum").ref,
            factor_query,
            "2024-01-04T12:05:00Z",
            make_snapshot(factor_tables),
            mode=mode,
        )


@pytest.mark.parametrize("change", [{"price_basis": "RAW"}, {"fields": ("open",)}])
def test_query_contract_mismatch(change, factor_tables, factor_query, factor_engine, make_snapshot):
    with pytest.raises(ContractError, match="FACTOR_QUERY"):
        factor_engine.run(
            builtin_spec("momentum").ref,
            replace(factor_query, **change),
            "2024-01-04T12:05:00Z",
            make_snapshot(factor_tables),
        )


def test_query_type_mismatch(factor_engine):
    with pytest.raises(ContractError, match="FACTOR_QUERY"):
        factor_engine.run(builtin_spec("momentum").ref, None, None, None)
