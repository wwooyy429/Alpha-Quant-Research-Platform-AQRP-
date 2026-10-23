"""Loopback-only development UI launcher; no deployment or permissions changes."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from aqrp.services.task_requests import initialize


def main(argv=None):
    p = argparse.ArgumentParser(description="AQRP local engineering UI")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--commit", required=True)
    p.add_argument("--port", type=int, default=8501)
    p.add_argument("--history-registration", type=Path)
    a = p.parse_args(argv)
    initialize(a.workspace, a.commit)
    if a.history_registration is not None:
        import json

        from aqrp.services.task_history import register_history

        history = json.loads(a.history_registration.read_bytes())
        register_history(a.workspace, history["archive"], history["publication_root"])

    env = {
        k: v
        for k, v in os.environ.items()
        if k.upper()
        in {
            "SYSTEMROOT",
            "WINDIR",
            "PATH",
            "TEMP",
            "TMP",
            "LANG",
            "LC_ALL",
            "USERPROFILE",
            "HOMEDRIVE",
            "HOMEPATH",
        }
    }
    env.update(
        AQRP_WORKSPACE=str(a.workspace.absolute()), PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"
    )
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(Path(__file__).with_name("app.py")),
            "--server.address=127.0.0.1",
            f"--server.port={a.port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.runOnSave=false",
        ],
        env=env,
        shell=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
