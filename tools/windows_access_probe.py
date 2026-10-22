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
from datetime import UTC, datetime
from pathlib import Path


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


def probe(config, role, *, get_token=token, open_access=access):
    actual = get_token()
    if (
        config["scope"] != "ENGINEERING_DEMO_ONLY"
        or actual["elevated"]
        or actual["sid"] != config["principals"][role]
        or len(set(config["principals"].values())) != 4
    ):
        raise ValueError("WRONG_REAL_SUBJECT_OR_ENGINEERING_SCOPE")
    objects = config["objects"]
    inputs = [r for r in objects if r["kind"] == "snapshot_input"]
    if (
        len(inputs) != 9
        or len({r["path"] for r in objects}) != len(objects)
        or not any(r["kind"] == "publication_sidecar" for r in objects)
        or not config.get("operator_inventory_sha256")
    ):
        raise ValueError("ACTUAL_INPUT_SIDECAR_INVENTORY_REQUIRED")
    checks = []
    for item in objects:
        path = Path(item["path"])
        expected_read = role != "research"
        requests = {
            "read": 1,
            "write_data": 2,
            "append": 4,
            "change_dacl": 0x40000,
            "take_ownership": 0x80000,
            "delete": 0x10000,
        }
        for name, mask in requests.items():
            allowed = (
                expected_read
                if name == "read"
                else (
                    role == "evaluator"
                    and item["kind"] == "dynamic_product"
                    and name in ("write_data", "append", "delete")
                )
            )
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
        if expected_read:
            try:
                raw = path.read_bytes()
                observed_hash = hashlib.sha256(raw).hexdigest()
                ok = len(raw) == item["bytes"] and observed_hash == item["sha256"]
                detail = {"bytes": len(raw), "sha256": observed_hash}
            except OSError as exc:
                ok, detail = (
                    False,
                    {"type": type(exc).__name__, "winerror": getattr(exc, "winerror", None)},
                )
            checks.append({"path": str(path), "operation": "actual_bytes", "pass": ok, **detail})
    return {
        "scope": "ENGINEERING_DEMO_ONLY",
        "role": role,
        "token": actual,
        "attempt_id": config["attempt_id"],
        "phase": config["phase"],
        "checks": checks,
        "all_pass": all(c["pass"] for c in checks),
        "formal_test_executed": False,
        "financial_approval": "NONE",
        "finished_at_UTC": datetime.now(UTC).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--role", choices=("research", "evaluator", "auditor"), required=True)
    args = parser.parse_args()
    if os.name != "nt":
        raise SystemExit("Actual probe requires Windows NTFS; not executed")
    raw = args.config.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.sha256:
        raise SystemExit("OPERATOR_INVENTORY_HASH_MISMATCH")
    result = probe(json.loads(raw), args.role)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    raise SystemExit(0 if result["all_pass"] else 2)


if __name__ == "__main__":
    main()
