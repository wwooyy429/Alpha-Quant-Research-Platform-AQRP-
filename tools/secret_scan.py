"""Pinned scanner, redacted logs, positive and negative controls; no real credentials."""

import hashlib
import io
import os
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    out = Path(sys.argv[1])
    windows = os.name == "nt"
    filename = "gitleaks_8.30.1_" + ("windows_x64.zip" if windows else "linux_x64.tar.gz")
    expected = (
        "d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e"
        if windows
        else "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
    )
    url = "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/" + filename
    binary = urllib.request.urlopen(url, timeout=90).read()
    assert hashlib.sha256(binary).hexdigest() == expected
    name = "gitleaks.exe" if windows else "gitleaks"
    exe = out / name
    if windows:
        with zipfile.ZipFile(io.BytesIO(binary)) as z:
            exe.write_bytes(z.read(name))
    else:
        with tarfile.open(fileobj=io.BytesIO(binary)) as t:
            exe.write_bytes(t.extractfile(name).read())
        exe.chmod(0o700)
    with (out / "secret-scan.log").open("w", encoding="utf-8") as log:
        version = subprocess.run([str(exe), "version"], capture_output=True, text=True, check=True)
        log.write(version.stdout)
        assert "8.30.1" in version.stdout
        for positive in (True, False):
            control = out / ("positive-control" if positive else "negative-control")
            control.mkdir()
            value = (
                ("gh" + "p_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                if positive
                else "SYNTHETIC_NO_CREDENTIAL"
            )
            (control / "control.txt").write_text("token = " + value, encoding="utf-8")
            result = subprocess.run(
                [str(exe), "dir", str(control), "--redact=100", "--no-banner"],
                stdout=log,
                stderr=log,
            )
            assert result.returncode == (1 if positive else 0), "Scanner control failed"
        result = subprocess.run(
            [str(exe), "dir", str(root), "--redact=100", "--no-banner"], stdout=log, stderr=log
        )
        assert result.returncode == 0, "Secret scan failed; inspect redacted evidence"
    print("Secret scan and positive/negative controls PASS")


if __name__ == "__main__":
    main()
