"""Explicit local engineering worker. No shell, arbitrary argv, service or scheduler."""

import os
import subprocess
import sys

from aqrp.backtest.transactions import guard_path


def start_worker(service, task):
    row = service.status(task)
    if row["status"] != "QUEUED":
        return {"status": "ALREADY_SUBMITTED", "task_id": task}
    path = guard_path(service.root / "tasks" / task / "worker.log")
    env = {
        k: v
        for k, v in os.environ.items()
        if k.upper() in {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "LANG", "LC_ALL"}
    }
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    args = [
        sys.executable,
        "-m",
        "aqrp.services.task_cli",
        "work",
        "--workspace",
        str(service.root),
        "--task",
        task,
    ]
    with path.open("ab") as log:
        p = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=service.root,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    return {"task_id": task, "pid": p.pid, "argv": args, "scope": "LOCAL_ENGINEERING_WORKER"}
