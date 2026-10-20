"""Clean hashed installation and wheel tests; all writable artifacts outside source tree."""

import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import tempfile
import urllib.request
import uuid
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = Path(os.environ.get("AQRP_RUN_ROOT", tempfile.gettempdir())) / f"aqrp-{uuid.uuid4()}"
RUN.mkdir(parents=True)
os.environ["AQRP_ARTIFACT_DIR"] = str(RUN)
os.environ["PYTHONPYCACHEPREFIX"] = str(RUN / "bytecode")
os.environ["PIP_CACHE_DIR"] = str(RUN / "pip-cache")
os.environ["UV_CACHE_DIR"] = str(RUN / "uv-cache")
os.environ["HYPOTHESIS_STORAGE_DIRECTORY"] = str(RUN / "hypothesis")
os.environ["RUFF_CACHE_DIR"] = str(RUN / "ruff-cache")
os.environ["PYTHONUTF8"] = "1"
os.environ["COVERAGE_FILE"] = str(RUN / ".coverage")


def command(args, cwd=ROOT):
    with (RUN / "commands.log").open("a", encoding="utf-8") as log:
        log.write(json.dumps([str(a) for a in args]) + "\n")
        log.flush()
        result = subprocess.run(args, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            print((RUN / "commands.log").read_text(encoding="utf-8", errors="replace")[-12000:])
            raise SystemExit(result.returncode)


def main():
    assert sys.version_info[:3] == (3, 13, 16)
    print(f"Artifacts: {RUN}", flush=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    env = {
        "run_id": RUN.name,
        "python": sys.version,
        "executable": sys.executable,
        "os": platform.platform(),
        "ImageOS": os.environ.get("ImageOS"),
        "ImageVersion": os.environ.get("ImageVersion"),
        "code_commit": commit,
        "dirty": bool(dirty),
        "workspace": str(ROOT),
        "run_root": str(RUN.resolve()),
        "lock_sha256": hashlib.sha256((ROOT / "requirements.lock").read_bytes()).hexdigest(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "github_sha": os.environ.get("GITHUB_SHA"),
    }
    (RUN / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    if dirty:
        raise SystemExit("Formal clean install requires a committed clean source tree")
    venv.create(RUN / "venv", with_pip=False)
    py = RUN / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    candidates = json.loads((ROOT / "docs/audits/phase-1/DEPENDENCY_CANDIDATES.json").read_bytes())
    package = next(p for p in candidates["packages"] if p["name"] == "pip")
    wheel = package["candidate_wheels"][0]
    binary = urllib.request.urlopen(wheel["url"], timeout=90).read()
    assert hashlib.sha256(binary).hexdigest() == wheel["sha256"]
    bootstrap = RUN / wheel["filename"]
    bootstrap.write_bytes(binary)
    os.environ["PYTHONPATH"] = str(bootstrap)
    command(
        [
            str(py),
            "-m",
            "pip",
            "install",
            "--index-url",
            "https://pypi.org/simple",
            "--require-hashes",
            "--only-binary=:all:",
            "-r",
            str(ROOT / "requirements.lock"),
        ]
    )
    del os.environ["PYTHONPATH"]
    command([str(py), "-m", "pip", "check"])
    archive = subprocess.check_output(["git", "archive", "--format=zip", commit], cwd=ROOT)
    source = RUN / "source"
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        z.extractall(source)
    command(
        [
            str(py),
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--no-index",
            "--wheel-dir",
            str(RUN / "wheel"),
            str(source),
        ]
    )
    project_wheel = next((RUN / "wheel").glob("aqrp-*.whl"))
    env["wheel_sha256"] = hashlib.sha256(project_wheel.read_bytes()).hexdigest()
    command([str(py), "-m", "pip", "install", "--no-index", "--no-deps", str(project_wheel)])
    command([str(py), "-m", "ruff", "check", "src", "tests", "tools"], cwd=source)
    command([str(py), "-m", "ruff", "format", "--check", "src", "tests", "tools"], cwd=source)
    command(
        [
            str(py),
            "-m",
            "pytest",
            "-o",
            f"cache_dir={RUN / 'pytest-cache'}",
            f"--basetemp={RUN / 'tmp'}",
            "--cov=aqrp",
            "--cov-branch",
            f"--cov-report=json:{RUN / 'coverage.json'}",
            f"--cov-report=xml:{RUN / 'coverage.xml'}",
            f"--junitxml={RUN / 'junit.xml'}",
        ],
        cwd=source,
    )
    command(
        [str(py), str(source / "tools/check_coverage.py"), str(RUN / "coverage.json")], cwd=source
    )
    command([str(py), str(source / "tools/secret_scan.py"), str(RUN)], cwd=source)
    env["complete"] = True
    (RUN / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in RUN.iterdir()
        if p.is_file() and p.name != "artifacts.json"
    }
    (RUN / "artifacts.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
    print(f"PASS: {RUN}")


if __name__ == "__main__":
    main()
