"""Real P1 bytes/publication lifecycle; fake ACL adapter never counts as OS proof."""

import hashlib
import json

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.validation import engineering_input as m
from aqrp.validation import evaluator
from aqrp.validation.windows_acl import WindowsTreePolicy


def operator(tmp_path, monkeypatch):
    dest = tmp_path / "prebuilt-inputs"
    dest.mkdir()
    proof = WindowsTreePolicy(
        dest,
        owner="operator",
        evaluator="eval",
        research="research",
        auditor="audit",
        readonly_roots=(dest,),
    )
    monkeypatch.setattr(proof, "verify", lambda: {"profile": "WI-NTFS-CHAIN-1"})
    monkeypatch.setattr(evaluator, "identity", lambda: "operator")
    return dest, proof


def test_untrusted_policy_object_rejected(tmp_path):
    with pytest.raises(ContractError, match="TRUSTED_WINDOWS_TREE_POLICY_REQUIRED"):
        m.publish_engineering_input(None, tmp_path, tree_policy=None)
    with pytest.raises(ContractError, match="TRUSTED_WINDOWS_TREE_POLICY_REQUIRED"):
        m.verify_engineering_input(None, tree_policy=None)


def test_publish_actual_nine_bytes_sidecar_and_source_unchanged(
    tmp_path, monkeypatch, tables, make_snapshot
):
    source = make_snapshot(tables)
    original = m.input_inventory(source)
    dest, p = operator(tmp_path, monkeypatch)
    ref = m.publish_engineering_input(source, dest, tree_policy=p)
    receipt = m.verify_engineering_input(ref, tree_policy=p)
    assert len(receipt["files"]) == 9 and receipt["formal_test"] is False
    assert receipt["publisher"] == "operator" and receipt["financial_approval"] == "NONE"
    assert m.input_inventory(source) == original == m.input_inventory(ref)
    for row in receipt["files"]:
        raw = (dest / ref.snapshot_id / row["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]
    with pytest.raises(FileExistsError):
        m.publish_engineering_input(source, dest, tree_policy=p)
    # Actual unknown file is rejected, not omitted from the audit inventory.
    (dest / ref.snapshot_id / "unknown").write_bytes(b"unknown")
    with pytest.raises(ContractError, match="MEMBERSHIP"):
        m.input_inventory(ref)


@pytest.mark.parametrize(
    "field,value",
    [
        ("publisher", "eval"),
        ("financial_approval", "yes"),
        ("formal_test", True),
        ("inventory_hash", "0" * 64),
        ("acl_profile", "old"),
        ("files", []),
        ("scope", "FINAL_TEST"),
        ("extra", "posthoc"),
    ],
)
def test_publication_tampering(tmp_path, monkeypatch, tables, make_snapshot, field, value):
    src = make_snapshot(tables)
    dest, p = operator(tmp_path, monkeypatch)
    ref = m.publish_engineering_input(src, dest, tree_policy=p)
    path = dest / (ref.snapshot_id + ".publication.json")
    obj = json.loads(path.read_bytes())
    obj[field] = value
    path.write_bytes(canonical(obj))
    with pytest.raises(ContractError, match="PUBLICATION_MISMATCH"):
        m.verify_engineering_input(ref, tree_policy=p)


def test_operator_and_prebuilt_acl_gate_fail_before_write(
    tmp_path, monkeypatch, tables, make_snapshot
):
    src = make_snapshot(tables)
    dest, p = operator(tmp_path, monkeypatch)
    monkeypatch.setattr(evaluator, "identity", lambda: "eval")
    with pytest.raises(ContractError, match="TRUSTED_INPUT_OPERATOR"):
        m.publish_engineering_input(src, dest, tree_policy=p)
    assert not list(dest.iterdir())
    monkeypatch.setattr(evaluator, "identity", lambda: "operator")
    with pytest.raises(ContractError, match="PREBUILT"):
        m.publish_engineering_input(src, tmp_path / "not-approved", tree_policy=p)
    with pytest.raises(ContractError, match="PREBUILT"):
        m.verify_engineering_input(src, tree_policy=p)

    def deny():
        raise ContractError("UNPROVEN_WINDOWS_EFFECTIVE_ACL")

    p.verify = deny
    with pytest.raises(ContractError, match="UNPROVEN_WINDOWS"):
        m.publish_engineering_input(src, dest, tree_policy=p)
    assert not list(dest.iterdir())


def test_partial_failure_has_no_commit_marker_or_repair(
    tmp_path, monkeypatch, tables, make_snapshot
):
    src = make_snapshot(tables)
    dest, p = operator(tmp_path, monkeypatch)
    calls = 0

    def changed():
        nonlocal calls
        calls += 1
        if calls > 1:
            raise ContractError("ACL_TREE_CHANGED")
        return {"profile": "WI-NTFS-CHAIN-1"}

    p.verify = changed
    with pytest.raises(ContractError, match="ACL_TREE_CHANGED"):
        m.publish_engineering_input(src, dest, tree_policy=p)
    assert len(list((dest / src.snapshot_id).iterdir())) == 9
    assert not (dest / (src.snapshot_id + ".publication.json")).exists()
    p.verify = lambda: {"profile": "WI-NTFS-CHAIN-1"}
    from aqrp.core.contracts import SnapshotRef

    with pytest.raises(FileNotFoundError):
        m.verify_engineering_input(
            SnapshotRef(dest, src.snapshot_id, src.manifest_hash), tree_policy=p
        )


def test_source_changes_and_private_temp_never_renamed(
    tmp_path, monkeypatch, tables, make_snapshot
):
    source = make_snapshot(tables)
    dest, p = operator(tmp_path, monkeypatch)
    inventory = m.input_inventory

    def change_after_inventory(ref):
        result = inventory(ref)
        file = source.root / source.snapshot_id / result["files"][0]["path"]
        file.write_bytes(file.read_bytes() + b"changed")
        return result

    monkeypatch.setattr(m, "input_inventory", change_after_inventory)
    with pytest.raises(ContractError, match="ENGINEERING_SOURCE_CHANGED"):
        m.publish_engineering_input(source, dest, tree_policy=p)
    assert not (dest / (source.snapshot_id + ".publication.json")).exists()
