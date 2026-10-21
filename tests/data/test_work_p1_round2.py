"""Semantic boundaries for WORK-P1-006 through WORK-P1-009."""

from copy import deepcopy
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from importlib.resources import files

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import (
    ContractError,
    DataQualityError,
    SnapshotMismatch,
    TimeLeakageError,
    TimestampResolutionError,
)
from aqrp.core.time import iana, utc
from aqrp.data.pit import visible_rows
from aqrp.data.quality import normalize, validate_table
from aqrp.data.query import (
    actions_as_of,
    aliases_at,
    announcements_as_of,
    query,
    status_at,
    universe_at,
)
from aqrp.data.schemas import SCHEMAS
from aqrp.data.snapshot import manifest_digest, verify_snapshot
from aqrp.data.synthetic import record

CUTOFF = "2024-01-03T12:05:00Z"


@pytest.fixture
def populated(tables):
    tables["corporate_actions"] = [
        record(
            "corporate_actions",
            action_id="split",
            revision_id=1,
            security_id="SYN_A:001",
            type="SPLIT",
            announcement_at=utc("2024-01-01T00:00:00Z"),
            effective_at=utc("2024-01-03T00:00:00Z"),
            ex_date=date(2024, 1, 3),
            split_ratio=Decimal(2),
            currency="SYNCCY",
        )
    ]
    tables["adjustment_factors"] = [
        record(
            "adjustment_factors",
            action_id="split",
            revision_id=1,
            security_id="SYN_A:001",
            effective_at=utc("2024-01-03T00:00:00Z"),
            ratio=Decimal(2),
            method="SPLIT",
            view_cutoff=utc(CUTOFF),
        )
    ]
    return tables


@pytest.mark.parametrize("table", sorted(SCHEMAS))
@pytest.mark.parametrize("missing_time", [False, True])
def test_work_p1_006_unknown_formal_rejected(populated, make_snapshot, table, missing_time):
    row = populated[table][0]
    row.update(quality_status="UNKNOWN_AVAILABILITY", reason_code="SOURCE_HISTORY_UNVERIFIED")
    if missing_time:
        row["available_at"] = None
    with pytest.raises(DataQualityError, match="UNKNOWN_AVAILABILITY"):
        make_snapshot(populated)


@pytest.mark.parametrize("table", sorted(SCHEMAS))
def test_work_p1_006_exploratory_preserves_unknown(populated, make_snapshot, table):
    populated[table][0].update(
        quality_status="UNKNOWN_AVAILABILITY", reason_code="SOURCE_HISTORY_UNVERIFIED"
    )
    ref = make_snapshot(populated, exploratory=True)
    manifest, loaded = verify_snapshot(ref)
    assert manifest["pit_status"] == "EXPLORATORY_ONLY"
    assert any(
        r["quality_status"] == "UNKNOWN_AVAILABILITY"
        and r["reason_code"] == "SOURCE_HISTORY_UNVERIFIED"
        for r in loaded[table].to_pylist()
    )
    assert manifest["tables"][table]["quality"]["missing"] == 1


@pytest.mark.parametrize(
    "entry", ["query", "universe", "status", "aliases", "actions", "announcements"]
)
def test_work_p1_006_all_formal_entries_reject_exploratory(tables, make_snapshot, spec, entry):
    tables["bars_daily"][0].update(
        quality_status="UNKNOWN_AVAILABILITY", reason_code="SOURCE_HISTORY_UNVERIFIED"
    )
    ref = make_snapshot(tables, exploratory=True)
    calls = {
        "query": lambda: query(spec, CUTOFF, ref),
        "universe": lambda: universe_at("SYN_U", CUTOFF, ref),
        "status": lambda: status_at("SYN_A:001", CUTOFF, ref),
        "aliases": lambda: aliases_at("SYN_A", "DUP", CUTOFF, ref),
        "actions": lambda: actions_as_of(CUTOFF, ref),
        "announcements": lambda: announcements_as_of(CUTOFF, ref),
    }
    with pytest.raises(TimeLeakageError, match="EXPLORATORY"):
        calls[entry]()


def test_work_p1_006_missing_price_must_not_erase_unknown(tables, make_snapshot):
    row = tables["bars_daily"][0]
    row.update(
        close=None, quality_status="UNKNOWN_AVAILABILITY", reason_code="SOURCE_HISTORY_UNVERIFIED"
    )
    result = validate_table("bars_daily", [row])
    assert result.table.to_pylist()[0]["quality_status"] == "UNKNOWN_AVAILABILITY"
    assert result.table.to_pylist()[0]["reason_code"] == "SOURCE_HISTORY_UNVERIFIED"
    with pytest.raises(DataQualityError, match="UNKNOWN_AVAILABILITY"):
        make_snapshot(tables)


@pytest.mark.parametrize("table", sorted(SCHEMAS))
def test_work_p1_006_visible_boundary_checks_flag_even_future(populated, table):
    row = populated[table][0]
    row.update(quality_status="UNKNOWN_AVAILABILITY", reason_code="SOURCE_HISTORY_UNVERIFIED")
    with pytest.raises(TimeLeakageError, match="UNKNOWN_AVAILABILITY"):
        visible_rows(table, [row], "2023-01-01T00:00:00Z")


@pytest.mark.parametrize(
    "table", ["bars_daily", "security_master", "calendar", "universe_membership"]
)
def test_work_p1_006_resealed_formal_claim_is_revalidated(tables, make_snapshot, table):
    tables[table][0].update(
        quality_status="UNKNOWN_AVAILABILITY", reason_code="SOURCE_HISTORY_UNVERIFIED"
    )
    ref = make_snapshot(tables, exploratory=True)
    path = ref.root / ref.snapshot_id / "manifest.json"
    manifest, _ = verify_snapshot(ref)
    manifest["pit_status"] = "PIT_VERIFIED"
    # Adversarial input construction, not an expected-value oracle.
    manifest["manifest_hash"] = manifest_digest(manifest)
    path.write_bytes(canonical(manifest))
    with pytest.raises(SnapshotMismatch, match="SNAPSHOT_INVALID"):
        verify_snapshot(replace(ref, manifest_hash=manifest["manifest_hash"]))


@pytest.mark.parametrize(
    "bad",
    [
        "C:\\outside.tzif",
        "C:/outside.tzif",
        "C:outside.tzif",
        "\\\\server\\clock",
        "\\UTC",
        "/UTC",
        "Etc\\UTC",
        "../UTC",
        "Etc/../UTC",
        "Etc/./UTC",
        "Etc//UTC",
        "UTC/",
        " UTC",
        "UTC\x00",
    ],
)
def test_work_p1_007_timezone_key_namespace(bad):
    with pytest.raises(ContractError, match="INVALID_TIMEZONE"):
        iana(bad)


@pytest.mark.parametrize("name", ["UTC", "Etc/GMT+12", "America/New_York", "Asia/Shanghai"])
def test_work_p1_007_real_iana_keys(name):
    assert iana(name).key == name


def test_work_p1_007_external_bytes_cannot_affect_fixed_snapshot(
    tmp_path, tables, make_snapshot, spec
):
    outside = tmp_path / "external.tzif"
    outside.write_bytes(files("tzdata.zoneinfo").joinpath("UTC").read_bytes())
    with pytest.raises(ContractError):
        iana(str(outside))
    ref = make_snapshot(tables)
    before = query(spec, CUTOFF, ref).table.to_pylist()
    manifest_bytes = (ref.root / ref.snapshot_id / "manifest.json").read_bytes()
    outside.write_bytes(files("tzdata.zoneinfo").joinpath("Etc", "GMT+12").read_bytes())
    assert query(spec, CUTOFF, ref).table.to_pylist() == before
    assert verify_snapshot(ref)[0]["manifest_hash"] == ref.manifest_hash
    assert (ref.root / ref.snapshot_id / "manifest.json").read_bytes() == manifest_bytes


@pytest.mark.parametrize("bad", [2**63, 2**100, -(2**63) - 1, -1, True, "1", 1.0])
def test_work_p1_008_int64_bad_row_counted(tables, make_snapshot, bad):
    row = tables["bars_daily"][0]
    row["revision_id"] = bad
    result = validate_table("bars_daily", [row])
    assert (result.report.input, result.report.valid, result.report.rejected) == (1, 0, 1)
    assert result.report.reasons
    assert result.table.num_rows == 0
    with pytest.raises(DataQualityError, match="QUARANTINED_ROWS"):
        make_snapshot(tables)


def test_work_p1_008_mixed_rows_conserve_counts_and_locate_field(tables):
    good = tables["bars_daily"][0]
    maximum = deepcopy(good)
    maximum["revision_id"] = 2**63 - 1
    overflow = deepcopy(good)
    overflow["revision_id"] = 2**63
    with pytest.raises(ContractError) as exc:
        normalize("bars_daily", overflow)
    assert (exc.value.code, exc.value.field) == ("INTEGER_OUT_OF_RANGE", "revision_id")
    result = validate_table("bars_daily", [good, maximum, overflow])
    q = result.report
    assert (q.input, q.valid, q.duplicate, q.missing, q.rejected) == (3, 2, 0, 0, 1)
    assert q.input == q.valid + q.duplicate + q.missing + q.rejected
    assert result.report.reasons == ((2, "INTEGER_OUT_OF_RANGE"),)


@pytest.mark.parametrize(
    "value",
    [
        "2024-01-02T16:00:00.000000+00:00:00.000000001",
        "2024-01-02T16:00:00+00:00:00.000000001",
        "2024-01-02T16:00:00.000000-01:00:00.000000001",
        "2024-01-02T16:00:00,000000+01:00:00,000000001",
        "2024-01-02T16:00:00.123456001+00:00:00.000000000",
    ],
)
def test_work_p1_009_all_fractional_parts_lossless(value):
    with pytest.raises(TimestampResolutionError, match="SUB_MICROSECOND"):
        utc(value)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("2024-01-02T16:00:00.123456000Z", datetime(2024, 1, 2, 16, 0, 0, 123456, tzinfo=UTC)),
        (
            "2024-01-02T16:00:00.123456+00:00:00.000001",
            datetime(2024, 1, 2, 16, 0, 0, 123455, tzinfo=UTC),
        ),
        (
            "2024-01-02T16:00:00.123456-00:00:00.000001",
            datetime(2024, 1, 2, 16, 0, 0, 123457, tzinfo=UTC),
        ),
        (
            "2024-01-02T16:00:00+01:02:03.123456000",
            datetime(2024, 1, 2, 14, 57, 56, 876544, tzinfo=UTC),
        ),
        ("2024-01-02T00:30:00+08:00", datetime(2024, 1, 1, 16, 30, tzinfo=UTC)),
        (
            "2024-01-02 16:00:00,123456+00:00:00,000000000",
            datetime(2024, 1, 2, 16, 0, 0, 123456, tzinfo=UTC),
        ),
    ],
)
def test_work_p1_009_exact_offset_and_zero_tails(value, expected):
    assert utc(value) == expected


@pytest.mark.parametrize("suffix", ["+00:99", "+00:00:99", "+24:00", "+00.1", "+00:00.1"])
def test_work_p1_009_unsupported_offset_grammar(suffix):
    with pytest.raises(ContractError, match="INVALID_TIMESTAMP"):
        utc("2024-01-02T16:00:00" + suffix)
