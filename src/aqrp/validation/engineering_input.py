"""Operator-prebuilt engineering inputs; P1 private temp semantics stay unchanged."""

import hashlib
import uuid
from pathlib import Path

from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import SnapshotRef
from aqrp.core.errors import ContractError
from aqrp.data.snapshot import verify_snapshot
from aqrp.experiments.ledger import immutable_write

from .windows_acl import WindowsTreePolicy


def input_inventory(ref):
    manifest, _ = verify_snapshot(ref)
    directory = Path(ref.root) / ref.snapshot_id
    names = {"manifest.json", *(r["path"] for r in manifest["tables"].values())}
    if len(names) != 9 or {p.name for p in directory.iterdir()} != names:
        raise ContractError("ENGINEERING_INPUT_MEMBERSHIP_MISMATCH")
    files = []
    for name in sorted(names):
        p = directory / name
        if p.is_symlink() or p.is_junction() or p.stat().st_nlink != 1 or not p.is_file():
            raise ContractError("ENGINEERING_INPUT_LINK")
        raw = p.read_bytes()
        files.append({"path": name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    return {
        "scope": "ENGINEERING_DEMO_ONLY",
        "snapshot_id": ref.snapshot_id,
        "snapshot_manifest_hash": ref.manifest_hash,
        "files": files,
    }


def publish_engineering_input(source, destination, *, tree_policy):
    """No ACL repair: destination must ALREADY be operator-owned and role-readonly.

    Operator-only preparation, before evaluator launch. Copies bytes (never renames
    the P1 private directory) into fresh default-inheriting objects. The published
    sidecar is the final commit marker; consumers reject until it exists and the
    full gate/inventory matches. Failed partial output is retained, never repaired.
    """
    from .evaluator import identity

    if not isinstance(tree_policy, WindowsTreePolicy):
        raise ContractError("TRUSTED_WINDOWS_TREE_POLICY_REQUIRED")
    destination = Path(destination).absolute()
    if identity() != tree_policy.owner:
        raise ContractError("TRUSTED_INPUT_OPERATOR_REQUIRED")
    if destination not in tree_policy.readonly_roots or not destination.is_dir():
        raise ContractError("PREBUILT_READONLY_INPUT_ANCHOR_REQUIRED")
    tree_policy.verify()
    original = input_inventory(source)
    attempt = str(uuid.uuid4())
    target = destination / source.snapshot_id
    # mode 0777 inherits the pre-reviewed DACL; never use P1's mkdtemp here.
    target.mkdir(mode=0o777, exist_ok=False)
    for row in original["files"]:
        raw = (Path(source.root) / source.snapshot_id / row["path"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ContractError("ENGINEERING_SOURCE_CHANGED")
        immutable_write(target / row["path"], raw)
    published = SnapshotRef(destination, source.snapshot_id, source.manifest_hash)
    if input_inventory(source) != original or input_inventory(published) != original:
        raise ContractError("ENGINEERING_SOURCE_CHANGED")
    proof = tree_policy.verify()
    payload = {
        **original,
        "attempt_id": attempt,
        "publisher": identity(),
        "acl_profile": proof["profile"],
        "formal_test": False,
        "financial_approval": "NONE",
        "inventory_hash": digest(original),
    }
    immutable_write(destination / (source.snapshot_id + ".publication.json"), canonical(payload))
    tree_policy.verify()
    return published


def verify_engineering_input(ref, *, tree_policy):
    import json

    if not isinstance(tree_policy, WindowsTreePolicy):
        raise ContractError("TRUSTED_WINDOWS_TREE_POLICY_REQUIRED")
    root = Path(ref.root).absolute()
    if root not in tree_policy.readonly_roots:
        raise ContractError("PREBUILT_READONLY_INPUT_ANCHOR_REQUIRED")
    tree_policy.verify()
    inventory = input_inventory(ref)
    path = root / (ref.snapshot_id + ".publication.json")
    raw = path.read_bytes()
    receipt = json.loads(raw)
    expected_keys = set(inventory) | {
        "attempt_id",
        "publisher",
        "acl_profile",
        "formal_test",
        "financial_approval",
        "inventory_hash",
    }
    if (
        canonical(receipt) != raw
        or set(receipt) != expected_keys
        or any(receipt[k] != v for k, v in inventory.items())
        or receipt["publisher"] != tree_policy.owner
        or receipt["inventory_hash"] != digest(inventory)
        or receipt["formal_test"] is not False
        or receipt["financial_approval"] != "NONE"
        or receipt["acl_profile"] != "WI-NTFS-CHAIN-1"
    ):
        raise ContractError("ENGINEERING_PUBLICATION_MISMATCH")
    uuid.UUID(receipt["attempt_id"])
    return receipt
