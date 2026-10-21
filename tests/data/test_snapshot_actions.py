import hashlib
import json
from copy import deepcopy
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from aqrp.core.errors import ContractError, DataQualityError, SnapshotMismatch
from aqrp.core.time import utc
from aqrp.data.actions import action_view
from aqrp.data.quality import validate_table
from aqrp.data.query import query
from aqrp.data.schemas import SCHEMAS
from aqrp.data.snapshot import publish_snapshot, safe_path, verify_snapshot
from aqrp.data.store import read_snapshot
from aqrp.data.synthetic import PROVENANCE, record


def test_data_007_008_roundtrip_and_rebuild(tables, make_snapshot, spec):
    tables["bars_daily"][0]["close"] = None
    ref = make_snapshot(tables)
    manifest, raw = verify_snapshot(ref)
    _, index1 = read_snapshot(ref)
    _, index2 = read_snapshot(ref)
    for name in SCHEMAS:
        assert raw[name].equals(index1[name]) and raw[name].equals(index2[name])
        assert raw[name].schema == SCHEMAS[name]
    assert manifest["tables"]["bars_daily"]["rows"] == 4
    assert manifest["provenance"] == PROVENANCE
    assert query(spec, "2024-01-03T12:05:00Z", ref).table["close"].to_pylist() == [
        None,
        Decimal(100),
    ]
    with pytest.raises(SnapshotMismatch, match="IMMUTABLE"):
        publish_snapshot(tables, PROVENANCE, ref.root, snapshot_id=ref.snapshot_id)
    assert verify_snapshot(ref)[0] == manifest


def test_data_007_hash_tamper(tables, make_snapshot):
    ref = make_snapshot(tables)
    path = ref.root / ref.snapshot_id / "bars_daily.parquet"
    original = path.read_bytes()
    path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    with pytest.raises(SnapshotMismatch, match="HASH"):
        verify_snapshot(ref)
    path.write_bytes(original)
    with pytest.raises(SnapshotMismatch, match="MANIFEST"):
        verify_snapshot(replace(ref, manifest_hash="0" * 64))
    with pytest.raises(SnapshotMismatch):
        verify_snapshot(None)
    manifest_path = ref.root / ref.snapshot_id / "manifest.json"
    manifest_path.write_text("invalid json", encoding="utf-8")
    with pytest.raises(SnapshotMismatch):
        verify_snapshot(ref)


@pytest.mark.parametrize(
    "bad",
    [
        "../outside",
        "/outside",
        "C:/outside",
        "C:outside",
        "\\outside",
        ".",
        "",
        None,
        "a/../b",
        "a//b",
    ],
)
def test_data_007_path_traversal(tmp_path, bad):
    with pytest.raises(SnapshotMismatch):
        safe_path(tmp_path, bad)


def test_data_007_symlink_escape(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (tmp_path / "outside").mkdir()
    link = root / "escape"
    try:
        link.symlink_to(tmp_path / "outside", target_is_directory=True)
    except OSError:
        # Windows directory junctions exercise the same resolve/reparse escape check.
        import subprocess

        if __import__("os").name != "nt":
            raise
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(tmp_path / "outside")],
            check=True,
            capture_output=True,
        )
    with pytest.raises(SnapshotMismatch, match="ESCAPE"):
        safe_path(root, "escape/file")


def rewrite_manifest(ref, mutate):
    path = ref.root / ref.snapshot_id / "manifest.json"
    m = json.loads(path.read_bytes())
    mutate(m)
    # Independent canonical hash calculation, not the function under test.
    h = hashlib.sha256(
        json.dumps(
            {k: v for k, v in m.items() if k not in ("snapshot_id", "manifest_hash")},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    ).hexdigest()
    m["manifest_hash"] = h
    path.write_bytes(
        json.dumps(
            m, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
    )
    return replace(ref, manifest_hash=h)


@pytest.mark.parametrize(
    "change",
    [
        lambda m: m["tables"]["bars_daily"].update(path="../outside.parquet"),
        lambda m: m["tables"]["bars_daily"].update(rows=99),
        lambda m: m.update(schema_version="bad"),
        lambda m: m.update(data_schema_version="bad"),
        lambda m: m.update(snapshot_id="wrong"),
        lambda m: m.update(pit_status="bad"),
        lambda m: m["tables"].pop("calendar"),
        lambda m: m["provenance"].pop("unit_version"),
        lambda m: m["tables"]["bars_daily"].update(event_min=None),
        lambda m: m["tables"]["bars_daily"]["quality"].update(input=-1),
        lambda m: m["tables"]["bars_daily"]["quality"].update(input=99),
        lambda m: m["provenance"].update(calendar_version="wrong"),
    ],
)
def test_data_007_forged_manifest_semantics(tables, make_snapshot, change):
    ref = rewrite_manifest(make_snapshot(tables), change)
    with pytest.raises(SnapshotMismatch):
        verify_snapshot(ref)


def test_data_007_row_identity_schema_and_cleanup(tables, make_snapshot, tmp_path, monkeypatch):
    ref = make_snapshot(tables)
    path = ref.root / ref.snapshot_id / "bars_daily.parquet"
    table = pq.read_table(path)
    rows = table.to_pylist()
    rows[0]["snapshot_id"] = "wrong"
    pq.write_table(pa.Table.from_pylist(rows, schema=table.schema), path)
    ref = rewrite_manifest(
        ref,
        lambda m: m["tables"]["bars_daily"].update(
            sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        ),
    )
    with pytest.raises(SnapshotMismatch, match="MIXED"):
        verify_snapshot(ref)
    pq.write_table(table.drop(["close"]), path)
    ref = rewrite_manifest(
        ref,
        lambda m: m["tables"]["bars_daily"].update(
            sha256=hashlib.sha256(path.read_bytes()).hexdigest()
        ),
    )
    with pytest.raises(SnapshotMismatch, match="SCHEMA"):
        verify_snapshot(ref)
    for sid in ("../bad", "", 123):
        with pytest.raises(SnapshotMismatch):
            publish_snapshot(tables, PROVENANCE, tmp_path / "root", snapshot_id=sid)
    with pytest.raises(ContractError):
        publish_snapshot(tables, {}, tmp_path)
    invalid = dict(PROVENANCE)
    invalid["source_license"] = ""
    with pytest.raises(ContractError):
        publish_snapshot(tables, invalid, tmp_path)

    def failing_write(*args, **kwargs):
        raise OSError("Simulated failed write; must not publish partial snapshot")

    monkeypatch.setattr(pq, "write_table", failing_write)
    with pytest.raises(OSError):
        publish_snapshot(tables, PROVENANCE, tmp_path / "atomic", snapshot_id="atomic-test")
    assert list((tmp_path / "atomic").iterdir()) == []


def test_data_004_action_edges(tables):
    bars = deepcopy(tables["bars_daily"][:2])
    sessions = [date(2024, 1, 2), date(2024, 1, 3)]
    action = record(
        "corporate_actions",
        action_id="s1",
        revision_id=1,
        security_id="SYN_A:001",
        type="SPLIT",
        effective_at=utc("2024-01-03T00:00:00Z"),
        announcement_at=utc("2024-01-01T00:00:00Z"),
        split_ratio=Decimal(2),
        ex_date=date(2024, 1, 3),
        currency="SYNCCY",
    )
    assert validate_table("corporate_actions", [action]).report.valid == 1
    for field, bad in [
        ("type", "UNKNOWN"),
        ("split_ratio", None),
        ("split_ratio", Decimal(0)),
        ("announcement_at", None),
        ("effective_at", None),
        ("event_time", utc("2024-01-02T00:00:00Z")),
        ("available_at", utc("2023-12-31T00:00:00Z")),
    ]:
        changed = deepcopy(action)
        changed[field] = bad
        assert validate_table("corporate_actions", [changed]).report.rejected == 1
    div = deepcopy(action)
    div.update(
        type="CASH_DIVIDEND",
        split_ratio=None,
        cash_per_share=Decimal(2),
        dividend_basis="PER_OLD_SHARE",
    )
    for field, bad in [
        ("cash_per_share", None),
        ("cash_per_share", Decimal(-1)),
        ("dividend_basis", "PER_NEW_SHARE"),
    ]:
        changed = deepcopy(div)
        changed[field] = bad
        assert validate_table("corporate_actions", [changed]).report.rejected == 1
    broken = deepcopy(div)
    broken["dividend_basis"] = "UNKNOWN"
    with pytest.raises(DataQualityError, match="BASIS"):
        action_view(bars, [broken], "total_return", sessions)
    assert validate_table("corporate_actions", [div]).report.valid == 1
    with pytest.raises(DataQualityError, match="UNKNOWN_PRICE_BASIS"):
        action_view(bars, [], "bad", sessions)
    null = deepcopy(bars)
    null[0]["close"] = None
    null[0]["volume"] = None
    adjusted = action_view(null, [action], "split_adjusted", sessions)
    assert adjusted[0]["close"] is None and adjusted[0]["volume"] is None
    with pytest.raises(DataQualityError, match="RETURN_GAP"):
        action_view(null, [], "total_return", sessions)
    gap = deepcopy(bars)
    gap[1]["session_date"] = date(2024, 1, 4)
    with pytest.raises(DataQualityError, match="SESSION_GAP"):
        action_view(
            gap,
            [],
            "total_return",
            [date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)],
        )
    multi = deepcopy(action)
    multi["effective_at"] += timedelta(hours=1)
    with pytest.raises(DataQualityError, match="MULTI_SPLIT"):
        action_view(bars, [action, multi], "total_return", sessions)
