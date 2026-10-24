"""Test-only abrupt self-termination, never a business/runtime API."""

import json

CHILD_CRASH_SUPPORT = r"""
import ctypes, faulthandler, json, os, sys
from pathlib import Path
faulthandler.enable(all_threads=True)
def hard_exit(code, point):
    marker = Path(sys.argv[1]) / "injected-crash-boundary.json"
    with marker.open("x", encoding="utf-8") as f:
        json.dump({"point": point, "pid": os.getpid(), "task_id": sys.argv[2],
                   "exit_code": code, "method": "self-TerminateProcess" if os.name == "nt" else "os._exit"}, f)
        f.flush()
        os.fsync(f.fileno())
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.TerminateProcess.argtypes = (ctypes.c_void_p, ctypes.c_uint)
        kernel.TerminateProcess.restype = ctypes.c_int
        kernel.TerminateProcess(kernel.GetCurrentProcess(), code)
        raise RuntimeError("TerminateProcess returned: " + str(ctypes.get_last_error()))
    os._exit(code)
"""


def assert_crash_marker(root, task, point, code):
    marker = json.loads((root / "injected-crash-boundary.json").read_bytes())
    assert marker["point"] == point and marker["task_id"] == task
    assert marker["exit_code"] == code
    assert isinstance(marker["pid"], int) and marker["pid"] > 0
    assert marker["method"] in ("self-TerminateProcess", "os._exit")
