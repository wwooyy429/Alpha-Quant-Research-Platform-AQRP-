"""Read-only three-token engineering probe. Does not enable users or mutate ACL/data.

Run separately under each real, non-elevated subject AFTER independent review and
execution authorization. Config is an operator-published, SHA-pinned inventory of
the actual inputs, publication sidecar and all dynamic products. Canary-only or
missing-file denials do not pass. Never imports/calls FINAL_TEST evaluation.
"""

import argparse
import ctypes
import hashlib
import json
import os
import stat
import uuid
from datetime import UTC, datetime
from pathlib import Path

from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import SnapshotRef
from aqrp.experiments.ledger import immutable_write
from aqrp.validation.engineering_input import verify_engineering_input
from aqrp.validation.windows_acl import WindowsTreePolicy


def token():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    adv = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    adv.OpenProcessToken.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    adv.GetTokenInformation.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    adv.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
    handle = ctypes.c_void_p()
    if not adv.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(handle)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        size = ctypes.c_uint32()
        adv.GetTokenInformation(handle, 1, None, 0, ctypes.byref(size))
        buf = ctypes.create_string_buffer(size.value)
        if not adv.GetTokenInformation(handle, 1, buf, len(buf), ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        pointer = ctypes.c_void_p()
        sid = ctypes.cast(buf, ctypes.POINTER(ctypes.c_void_p))[0]
        if not adv.ConvertSidToStringSidW(sid, ctypes.byref(pointer)):
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            actual_sid = ctypes.wstring_at(pointer)
        finally:
            kernel.LocalFree(pointer)
        elevated = ctypes.c_uint32()
        if not adv.GetTokenInformation(
            handle, 20, ctypes.byref(elevated), ctypes.sizeof(elevated), ctypes.byref(size)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return {
            "sid": actual_sid,
            "elevated": bool(elevated.value),
            "source": "OpenProcessToken/GetTokenInformation",
        }
    finally:
        kernel.CloseHandle(handle)


def access(path, mask):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    ctypes.set_last_error(0)
    h = kernel.CreateFileW(str(path), mask, 7, None, 3, 0x02000000, None)
    err = ctypes.get_last_error()
    if h == ctypes.c_void_p(-1).value:
        return {"opened": False, "winerror": err, "mask": mask, "disposition": "OPEN_EXISTING"}
    if not kernel.CloseHandle(h):
        raise ctypes.WinError(ctypes.get_last_error())
    return {"opened": True, "winerror": 0, "mask": mask, "disposition": "OPEN_EXISTING"}


def inventory_document(raw, expected_sha256):
    if raw is None or hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("AUTHORITATIVE_INVENTORY_HASH_MISMATCH")
    inv = json.loads(raw)
    if canonical(inv) != raw or inv["schema"] != "windows-probe-inventory/2":
        raise ValueError("NONCANONICAL_OR_OLD_INVENTORY")
    root = Path(inv["root"])
    rows = inv["objects"]
    paths = {r["path"] for r in rows}
    if (
        not root.is_absolute()
        or ".." in root.parts
        or len(paths) != len(rows)
        or str(root) not in paths
        or inv["phase"] not in ("before", "after")
        or inv["scope"] != "ENGINEERING_DEMO_ONLY"
        or inv["gate_before_sha256"] != inv["gate_after_sha256"]
        or inv["enumeration_complete"] is not True
        or inv["enumeration_passes"] != 2
    ):
        raise ValueError("INCOMPLETE_AUTHORITATIVE_INVENTORY")
    uuid.UUID(inv["attempt_id"])
    policy = WindowsTreePolicy(**inv["policy"])
    gate = inv["gate"]
    if (
        policy.binding != inv["policy_binding"]
        or str(policy.root) != inv["root"]
        or digest(gate) != inv["gate_before_sha256"]
        or gate["enumeration_complete"] is not True
        or gate["enumeration_passes"] != 2
        or gate["policy_binding"] != policy.binding
        or gate["tree_objects"]
        != [{k: r[k] for k in ("path", "object_type", "identity")} for r in rows]
        or gate["objects"] != len(rows)
    ):
        raise ValueError("INVENTORY_GATE_OBJECT_MISMATCH")
    policy.verify_rows(
        gate["descriptors"], {Path(r["path"]): r["object_type"] == "directory" for r in rows}
    )
    policy.verify_ancestors(gate["ancestor_descriptors"])
    s = inv["snapshot"]
    publication = inv["publication"]
    source = Path(s["root"]) / s["snapshot_id"]
    inputs = {str(source / r["path"]): r for r in publication["files"]}
    sidecar = str(Path(s["root"]) / (s["snapshot_id"] + ".publication.json"))
    if (
        inv["principals"]
        != {
            "operator": policy.owner,
            "research": policy.research,
            "evaluator": policy.evaluator,
            "auditor": policy.auditor,
        }
        or s["manifest_hash"] != inv["snapshot_manifest_hash"]
        or s["manifest_hash"] != publication["snapshot_manifest_hash"]
        or s["snapshot_id"] != publication["snapshot_id"]
        or len(inputs) != 9
    ):
        raise ValueError("INVENTORY_SOURCE_OR_PRINCIPALS_MISMATCH")
    for r in rows:
        p = Path(r["path"])
        if not p.is_absolute() or ".." in p.parts or not p.is_relative_to(root):
            raise ValueError("INVENTORY_PATH_OUTSIDE_ROOT")
        if r["object_type"] not in ("file", "directory"):
            raise ValueError("INVENTORY_OBJECT_TYPE")
        if r["object_type"] == "directory":
            if r["kind"] != "directory_boundary" or r["members"] != sorted(
                Path(s).name for s in paths if Path(s).parent == p and Path(s) != p
            ):
                raise ValueError("INVENTORY_DIRECTORY_MEMBERSHIP")
        elif r["kind"] not in (
            "snapshot_input",
            "publication_sidecar",
            "operator_key",
            "dynamic_product",
        ):
            raise ValueError("INVENTORY_FILE_KIND")
        if p != root and str(p.parent) not in paths:
            raise ValueError("INVENTORY_MISSING_DIRECTORY")
        if r["evaluator_writable"] != (not policy.is_readonly(p) and p != policy.key_file):
            raise ValueError("INVENTORY_ACCESS_CLASS_MISMATCH")
        if r["object_type"] == "file":
            kind = (
                "snapshot_input"
                if str(p) in inputs
                else (
                    "publication_sidecar"
                    if str(p) == sidecar
                    else ("operator_key" if p == policy.key_file else "dynamic_product")
                )
            )
            if kind != r["kind"]:
                raise ValueError("INVENTORY_FILE_KIND")
            if kind == "snapshot_input" and (r["bytes"], r["sha256"]) != (
                inputs[str(p)]["bytes"],
                inputs[str(p)]["sha256"],
            ):
                raise ValueError("INVENTORY_INPUT_HASH_MISMATCH")
            if kind == "publication_sidecar" and (r["bytes"], r["sha256"]) != (
                len(canonical(publication)),
                digest(publication),
            ):
                raise ValueError("INVENTORY_SIDECAR_HASH_MISMATCH")
    if (
        sum(r["kind"] == "snapshot_input" for r in rows) != 9
        or sum(r["kind"] == "publication_sidecar" for r in rows) != 1
        or sum(r["kind"] == "operator_key" for r in rows) != 1
    ):
        raise ValueError("ACTUAL_INPUT_SIDECAR_KEY_INVENTORY_REQUIRED")
    if (
        digest({k: v for k, v in inv.items() if k != "tree_state_sha256"})
        != inv["tree_state_sha256"]
    ):
        raise ValueError("INVENTORY_STATE_HASH_MISMATCH")
    return inv


def freeze_inventory(
    policy, snapshot, attempt_id, phase, *, get_token=token, before_raw=None, before_sha256=None
):
    """Trusted operator only; complete two-gate capture, no ACL writes or role enablement."""
    actual = get_token()
    if actual["sid"] != policy.owner or actual["elevated"]:
        raise ValueError("TRUSTED_NON_ELEVATED_OPERATOR_REQUIRED")
    uuid.UUID(attempt_id)
    if phase not in ("before", "after") or policy.key_file is None:
        raise ValueError("INVALID_PHASE_OR_MISSING_KEY")
    if not Path(snapshot.root).is_absolute() or ".." in Path(snapshot.root).parts:
        raise ValueError("ABSOLUTE_SNAPSHOT_ROOT_REQUIRED")
    publication = verify_engineering_input(snapshot, tree_policy=policy)
    input_root = Path(snapshot.root) / snapshot.snapshot_id
    inputs = {str(input_root / r["path"]) for r in publication["files"]}
    sidecar = str(Path(snapshot.root) / (snapshot.snapshot_id + ".publication.json"))
    first = policy.verify()
    if not first["enumeration_complete"] or first["enumeration_passes"] != 2:
        raise ValueError("INCOMPLETE_GATE_CAPTURE")
    rows = []
    paths = {r["path"] for r in first["tree_objects"]}
    for obj in first["tree_objects"]:
        p = Path(obj["path"])
        r = {**obj, "evaluator_writable": not policy.is_readonly(p) and p != policy.key_file}
        if obj["object_type"] == "directory":
            r.update(
                kind="directory_boundary",
                members=sorted(Path(s).name for s in paths if Path(s).parent == p and Path(s) != p),
            )
        else:
            with p.open("rb") as stream:
                start = os.fstat(stream.fileno())
                raw = stream.read()
                end = os.fstat(stream.fileno())
            if (
                [start.st_dev, start.st_ino, stat.S_IFMT(start.st_mode)] != obj["identity"]
                or (start.st_size, start.st_mtime_ns) != (end.st_size, end.st_mtime_ns)
                or len(raw) != end.st_size
            ):
                raise ValueError("INVENTORY_BYTES_CHANGED")
            kind = (
                "snapshot_input"
                if str(p) in inputs
                else (
                    "publication_sidecar"
                    if str(p) == sidecar
                    else ("operator_key" if p == policy.key_file else "dynamic_product")
                )
            )
            r.update(kind=kind, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        rows.append(r)
    last = policy.verify()
    if first != last:
        raise ValueError("TREE_CHANGED_DURING_INVENTORY")
    inv = {
        "schema": "windows-probe-inventory/2",
        "scope": "ENGINEERING_DEMO_ONLY",
        "attempt_id": attempt_id,
        "phase": phase,
        "root": str(policy.root),
        "principals": {
            "operator": policy.owner,
            "research": policy.research,
            "evaluator": policy.evaluator,
            "auditor": policy.auditor,
        },
        "policy_binding": policy.binding,
        "snapshot_manifest_hash": snapshot.manifest_hash,
        "snapshot": {
            "root": str(snapshot.root),
            "snapshot_id": snapshot.snapshot_id,
            "manifest_hash": snapshot.manifest_hash,
        },
        "publication": publication,
        "policy": {
            "root": str(policy.root),
            "owner": policy.owner,
            "evaluator": policy.evaluator,
            "research": policy.research,
            "auditor": policy.auditor,
            "inherited_roots": sorted(map(str, policy.inherited_roots)),
            "readonly_roots": sorted(map(str, policy.readonly_roots)),
            "key_file": str(policy.key_file),
        },
        "gate": first,
        "gate_before_sha256": digest(first),
        "gate_after_sha256": digest(last),
        "enumeration_complete": True,
        "enumeration_passes": 2,
        "objects": rows,
        "predecessor_sha256": None,
        "added_paths": [],
        "removed_paths": [],
    }
    if phase == "after":
        before = inventory_document(before_raw, before_sha256)
        if before["phase"] != "before" or any(
            before[k] != inv[k]
            for k in (
                "attempt_id",
                "root",
                "principals",
                "policy_binding",
                "snapshot_manifest_hash",
            )
        ):
            raise ValueError("BEFORE_AFTER_BINDING_MISMATCH")
        old = {r["path"]: r for r in before["objects"]}
        new = {r["path"]: r for r in rows}
        if any(
            new.get(p) != r
            for p, r in old.items()
            if r["kind"] in ("snapshot_input", "publication_sidecar", "operator_key")
        ):
            raise ValueError("IMMUTABLE_INPUT_SIDECAR_KEY_CHANGED")
        inv.update(
            predecessor_sha256=before_sha256,
            added_paths=sorted(new.keys() - old.keys()),
            removed_paths=sorted(old.keys() - new.keys()),
        )
    inv["tree_state_sha256"] = digest(inv)
    raw = canonical(inv)
    inventory_document(raw, hashlib.sha256(raw).hexdigest())
    return raw


def operations(item, role):
    directory = item["object_type"] == "directory"
    read = role != "research" and (role != "auditor" or item["kind"] != "operator_key")
    write = role == "evaluator" and item["evaluator_writable"]
    result = {
        "list_directory" if directory else "read": (1, read),
        "create_file" if directory else "write_data": (2, write),
        "create_directory" if directory else "append": (4, write),
        "change_dacl": (0x40000, False),
        "take_ownership": (0x80000, False),
        "delete": (0x10000, write),
    }
    if directory:
        # The closed MODIFY mask grants DELETE on the object, NOT FILE_DELETE_CHILD.
        result["delete_child"] = (0x40, False)
    return result


def validate_binding(config, raw, sha256):
    inv = inventory_document(raw, sha256)
    if config.get("operator_inventory_sha256") != sha256 or any(
        config.get(k) != inv[k]
        for k in ("scope", "principals", "objects", "attempt_id", "phase", "root", "policy_binding")
    ):
        raise ValueError("PROBE_INVENTORY_SET_OR_BINDING_MISMATCH")
    return inv


def probe_config(inventory_raw, inventory_sha256):
    inv = inventory_document(inventory_raw, inventory_sha256)
    return {
        **{
            k: inv[k]
            for k in (
                "scope",
                "principals",
                "objects",
                "attempt_id",
                "phase",
                "root",
                "policy_binding",
            )
        },
        "operator_inventory_sha256": inventory_sha256,
    }


def probe(
    config, role, *, inventory_raw=None, inventory_sha256=None, get_token=token, open_access=access
):
    inv = validate_binding(config, inventory_raw, inventory_sha256)
    actual = get_token()
    if (
        config["scope"] != "ENGINEERING_DEMO_ONLY"
        or actual["elevated"]
        or actual["sid"] != config["principals"][role]
        or len(set(config["principals"].values())) != 4
    ):
        raise ValueError("WRONG_REAL_SUBJECT_OR_ENGINEERING_SCOPE")
    objects = config["objects"]
    checks = []
    for item in objects:
        path = Path(item["path"])
        requests = operations(item, role)
        for name, (mask, allowed) in requests.items():
            observed = open_access(path, mask)
            passed = (
                observed["opened"]
                if allowed
                else not observed["opened"] and observed["winerror"] == 5
            )
            checks.append(
                {
                    "path": str(path),
                    "operation": name,
                    "expected_open": allowed,
                    "observed": observed,
                    "pass": passed,
                }
            )
        if requests["list_directory" if item["object_type"] == "directory" else "read"][1]:
            try:
                if item["object_type"] == "directory":
                    members = sorted(p.name for p in path.iterdir())
                    ok = path.is_dir() and members == item["members"]
                    detail = {"members": members}
                else:
                    raw = path.read_bytes()
                    observed_hash = hashlib.sha256(raw).hexdigest()
                    ok = (
                        path.is_file()
                        and len(raw) == item["bytes"]
                        and observed_hash == item["sha256"]
                    )
                    detail = {"bytes": len(raw), "sha256": observed_hash}
            except OSError as exc:
                ok, detail = (
                    False,
                    {"type": type(exc).__name__, "winerror": getattr(exc, "winerror", None)},
                )
            checks.append(
                {
                    "path": str(path),
                    "operation": "actual_members"
                    if item["object_type"] == "directory"
                    else "actual_bytes",
                    "pass": ok,
                    **detail,
                }
            )
    return {
        "scope": "ENGINEERING_DEMO_ONLY",
        "role": role,
        "token": actual,
        "attempt_id": config["attempt_id"],
        "phase": config["phase"],
        "checks": checks,
        "listed_checks_pass": all(c["pass"] for c in checks),
        "inventory_binding_verified": True,
        "inventory_sha256": inventory_sha256,
        "config_sha256": digest(config),
        "root": inv["root"],
        "policy_binding": inv["policy_binding"],
        "execution_mode": "NATIVE_WINDOWS_TOKEN"
        if get_token is token and open_access is access
        else "MODEL_ADAPTER",
        "coverage_verified": False,
        "all_pass": False,
        "status": "PARTIAL_REQUIRES_OPERATOR_RECONCILIATION",
        "formal_test_executed": False,
        "financial_approval": "NONE",
        "finished_at_UTC": datetime.now(UTC).isoformat(),
    }


def reconcile(
    config,
    inventory_raw,
    inventory_sha256,
    results,
    *,
    get_token=token,
    before_raw=None,
    before_sha256=None,
):
    """Mandatory phase coverage gate; never declares overall OS isolation or finance approved."""
    inv = validate_binding(config, inventory_raw, inventory_sha256)
    s = inv["snapshot"]
    current_raw = freeze_inventory(
        WindowsTreePolicy(**inv["policy"]),
        SnapshotRef(Path(s["root"]), s["snapshot_id"], s["manifest_hash"]),
        inv["attempt_id"],
        inv["phase"],
        get_token=get_token,
        before_raw=before_raw,
        before_sha256=before_sha256,
    )
    current_sha256 = hashlib.sha256(current_raw).hexdigest()
    current = inventory_document(current_raw, current_sha256)
    if (
        current != inv
        or len(results) != 3
        or {r["role"] for r in results} != {"research", "evaluator", "auditor"}
    ):
        raise ValueError("INVENTORY_DRIFT_OR_MISSING_ROLES")
    for r in results:
        if (
            r["config_sha256"] != digest(config)
            or r["inventory_sha256"] != inventory_sha256
            or r["token"]["sid"] != inv["principals"][r["role"]]
            or r["token"]["elevated"]
            or any(r[k] != inv[k] for k in ("attempt_id", "phase", "root", "policy_binding"))
        ):
            raise ValueError("ROLE_RESULT_BINDING_MISMATCH")
        expected = []
        for item in inv["objects"]:
            for op, (mask, allowed) in operations(item, r["role"]).items():
                expected.append((item["path"], op, mask, allowed))
            if operations(item, r["role"])[
                "list_directory" if item["object_type"] == "directory" else "read"
            ][1]:
                expected.append(
                    (
                        item["path"],
                        "actual_members" if item["object_type"] == "directory" else "actual_bytes",
                        None,
                        item,
                    )
                )
        if len(r["checks"]) != len(expected):
            raise ValueError("ROLE_CHECK_COVERAGE_MISMATCH")
        for c, (path, op, mask, want) in zip(r["checks"], expected):
            if (c["path"], c["operation"]) != (path, op):
                raise ValueError("ROLE_CHECK_COVERAGE_MISMATCH")
            if mask is not None:
                seen = c["observed"]
                ok = (
                    seen["mask"] == mask
                    and c["expected_open"] == want
                    and (
                        seen["opened"] and seen["winerror"] == 0
                        if want
                        else not seen["opened"] and seen["winerror"] == 5
                    )
                )
            else:
                ok = (
                    c.get("members") == want["members"]
                    if op == "actual_members"
                    else (c.get("bytes"), c.get("sha256")) == (want["bytes"], want["sha256"])
                )
            if not ok or not c["pass"]:
                raise ValueError("ROLE_ACCESS_OR_CONTENT_CHECK_FAILED")
    return {
        "scope": "PHASE_INVENTORY_COVERAGE_ONLY",
        "attempt_id": inv["attempt_id"],
        "phase": inv["phase"],
        "inventory_sha256": inventory_sha256,
        "listed_checks_pass": True,
        "coverage_verified": True,
        "all_pass": True,
        "post_probe_inventory_sha256": current_sha256,
        "result_sha256": [digest(r) for r in results],
        "real_token_claims": all(r["execution_mode"] == "NATIVE_WINDOWS_TOKEN" for r in results),
        "overall_windows_isolation": "NOT_VERIFIED",
        "formal_test_executed": False,
        "financial_approval": "NONE",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--mode", choices=("probe", "freeze", "reconcile"), default="probe")
    parser.add_argument("--role", choices=("research", "evaluator", "auditor"))
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--inventory-sha256")
    parser.add_argument("--before", type=Path)
    parser.add_argument("--before-sha256")
    parser.add_argument("--results", nargs=3, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--probe-config-output", type=Path)
    args = parser.parse_args()
    if os.name != "nt":
        raise SystemExit("Actual probe requires Windows NTFS; not executed")
    raw = args.config.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.sha256:
        raise SystemExit("OPERATOR_INVENTORY_HASH_MISMATCH")
    config = json.loads(raw)
    if args.mode == "freeze":
        if args.output is None or args.probe_config_output is None:
            parser.error(
                "freeze requires unused --output and --probe-config-output outside the sealed root"
            )
        policy = WindowsTreePolicy(**config["policy"])
        if (
            args.output.absolute().is_relative_to(policy.root)
            or args.probe_config_output.absolute().is_relative_to(policy.root)
            or args.output.absolute() == args.probe_config_output.absolute()
        ):
            parser.error("inventory output must be outside the sealed root")
        s = config["snapshot"]
        result_raw = freeze_inventory(
            policy,
            SnapshotRef(Path(s["root"]), s["snapshot_id"], s["manifest_hash"]),
            config["attempt_id"],
            config["phase"],
            before_raw=None if args.before is None else args.before.read_bytes(),
            before_sha256=args.before_sha256,
        )
        immutable_write(args.output, result_raw)
        config_raw = canonical(probe_config(result_raw, hashlib.sha256(result_raw).hexdigest()))
        immutable_write(args.probe_config_output, config_raw)
        print(
            json.dumps(
                {
                    "inventory": str(args.output),
                    "sha256": hashlib.sha256(result_raw).hexdigest(),
                    "probe_config": str(args.probe_config_output),
                    "probe_config_sha256": hashlib.sha256(config_raw).hexdigest(),
                    "overall_windows_isolation": "NOT_VERIFIED",
                }
            )
        )
        return
    if args.inventory is None or args.inventory_sha256 is None:
        parser.error("probe/reconcile require operator-pinned --inventory and --inventory-sha256")
    if args.mode == "reconcile":
        if args.results is None:
            parser.error(
                "reconcile requires three --results; must execute as trusted operator for fresh full-tree recapture"
            )
        result = reconcile(
            config,
            args.inventory.read_bytes(),
            args.inventory_sha256,
            [json.loads(p.read_bytes()) for p in args.results],
            before_raw=None if args.before is None else args.before.read_bytes(),
            before_sha256=args.before_sha256,
        )
    else:
        if args.role is None:
            parser.error("probe requires --role")
        result = probe(
            config,
            args.role,
            inventory_raw=args.inventory.read_bytes(),
            inventory_sha256=args.inventory_sha256,
        )
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    # Individual role probes are explicitly PARTIAL; zero is not overall isolation PASS.
    raise SystemExit(0 if result["listed_checks_pass"] else 2)


if __name__ == "__main__":
    main()
