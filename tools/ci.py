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
from datetime import UTC, datetime
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
    started = datetime.now(UTC).isoformat()
    with (RUN / "commands.log").open("a", encoding="utf-8") as log:
        log.write(json.dumps([str(a) for a in args]) + "\n")
        log.flush()
        result = subprocess.run(args, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        with (RUN / "commands.jsonl").open("a", encoding="utf-8") as records:
            records.write(
                json.dumps(
                    {
                        "argv": [str(a) for a in args],
                        "cwd": str(cwd),
                        "started_utc": started,
                        "ended_utc": datetime.now(UTC).isoformat(),
                        "exit": result.returncode,
                        "combined_raw_log": "commands.log",
                    }
                )
                + "\n"
            )
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
        "started_utc": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "executable": sys.executable,
        "os": platform.platform(),
        "ImageOS": os.environ.get("ImageOS"),
        "ImageVersion": os.environ.get("ImageVersion"),
        "code_commit": commit,
        "dirty": bool(dirty),
        "complete": False,
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
    ui_lock = ROOT / (
        "requirements-ui-windows.lock" if os.name == "nt" else "requirements-ui-linux.lock"
    )
    ui_wheels = RUN / "ui-wheelhouse"
    command(
        [
            str(py),
            "-m",
            "pip",
            "download",
            "--index-url",
            "https://pypi.org/simple",
            "--require-hashes",
            "--only-binary=:all:",
            "--no-deps",
            "--dest",
            str(ui_wheels),
            "-r",
            str(ui_lock),
        ]
    )
    command(
        [
            str(py),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--require-hashes",
            "--find-links",
            str(ui_wheels),
            "-r",
            str(ui_lock),
        ]
    )
    allowed_ui = set(
        __import__("re").findall(rb"--hash=sha256:([0-9a-f]{64})", ui_lock.read_bytes())
    )
    wheel_rows = []
    for item in sorted(ui_wheels.glob("*.whl")):
        checksum = hashlib.sha256(item.read_bytes()).hexdigest()
        assert checksum.encode() in allowed_ui
        with zipfile.ZipFile(item) as archive:
            metadata = archive.read(
                next(n for n in archive.namelist() if n.endswith(".dist-info/METADATA"))
            ).decode()
        wheel_rows.append(
            {
                "path": item.relative_to(RUN).as_posix(),
                "bytes": item.stat().st_size,
                "sha256": checksum,
                "METADATA": metadata,
            }
        )
    assert len(wheel_rows) == 29
    (RUN / "ui-dependency-wheels.json").write_text(
        json.dumps(
            {"lock_sha256": hashlib.sha256(ui_lock.read_bytes()).hexdigest(), "wheels": wheel_rows},
            indent=2,
        ),
        encoding="utf-8",
    )
    env["ui_lock_sha256"] = hashlib.sha256(ui_lock.read_bytes()).hexdigest()
    command([str(py), "-m", "pip", "check"])
    archive = subprocess.check_output(["git", "archive", "--format=zip", commit], cwd=ROOT)
    env["source_git_archive_sha256"] = hashlib.sha256(archive).hexdigest()
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
    (RUN / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    command([str(py), "-m", "pip", "install", "--no-index", "--no-deps", str(project_wheel)])
    command([str(py), "-m", "ruff", "check", "src", "tests", "tools"], cwd=source)
    command([str(py), "-m", "ruff", "format", "--check", "src", "tests", "tools"], cwd=source)
    command([str(py), str(source / "tools/check_phase7_package.py")], cwd=source)
    # The protected historical base policy remains byte-exact. The child only
    # scopes independently recomputed public variant identifiers to exact files.
    os.environ["GITLEAKS_CONFIG"] = str(source / ".gitleaks-phase7.toml")
    env["secret_scan_policy"] = {
        "base_sha256": hashlib.sha256((source / ".gitleaks.toml").read_bytes()).hexdigest(),
        "effective_child_sha256": hashlib.sha256(
            (source / ".gitleaks-phase7.toml").read_bytes()
        ).hexdigest(),
        "effective_config": str(source / ".gitleaks-phase7.toml"),
        "timing": "Scan before expensive tests; exact entire scanned-source bytes rechecked before complete",
    }
    (RUN / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    command([str(py), str(source / "tools/secret_scan.py"), str(RUN)], cwd=source)
    command(
        [
            str(py),
            str(source / "tools/check_phase7_scan_policy.py"),
            str(RUN),
            "--operation",
            "capture",
        ],
        cwd=source,
    )
    command([str(py), str(source / "tools/original_replay_smoke.py"), str(RUN)], cwd=source)
    command([str(py), str(source / "tools/released_p6_smoke.py"), str(RUN)], cwd=source)
    os.environ["AQRP_ORIGINAL_ENV_ARCHIVE"] = str(RUN / "reproduction/environment-archive.json")
    command(
        [
            str(py),
            "-m",
            "pytest",
            "--hypothesis-seed=20261023",
            "-o",
            f"cache_dir={RUN / 'pytest-cache'}",
            f"--basetemp={RUN / 'tmp'}",
            "--cov="
            + subprocess.check_output(
                [str(py), "-c", "import aqrp,pathlib; print(pathlib.Path(aqrp.__file__).parent)"],
                text=True,
            ).strip(),
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
    command([str(py), str(source / "tools/independent_reference.py")], cwd=source)
    command([str(py), str(source / "tools/data_smoke.py"), str(RUN)], cwd=source)
    command([str(py), str(source / "tools/factor_smoke.py"), str(RUN)], cwd=source)
    command([str(py), str(source / "tools/research_smoke.py"), str(RUN)], cwd=source)
    command([str(py), str(source / "tools/portfolio_smoke.py"), str(RUN)], cwd=source)
    command([str(py), str(source / "tools/backtest_smoke.py"), str(RUN)], cwd=source)
    command(
        [str(py), str(source / "tools/backtest_reference.py"), str(RUN / "backtest")], cwd=source
    )
    for script in (
        "reference_arithmetic.py",
        "supplemental_reference.py",
        "recheck_reference_v2.py",
    ):
        command(
            [str(py), "-I", str(source / "docs/audits/phase-3" / script)],
            cwd=source / "docs/audits/phase-3",
        )
    for name in ("reference_check.py", "revision_reference.py"):
        command(
            [
                str(py),
                "-I",
                str(source / "docs/audits/phase-6" / name),
                str(RUN / ("p6-" + name.replace(".py", ".json"))),
            ],
            cwd=source,
        )
    command([str(py), str(source / "tools/ui_smoke.py"), str(RUN)], cwd=source)
    command([str(py), str(source / "tools/e2e_smoke.py"), str(RUN)], cwd=source)
    command([str(py), str(source / "tools/competition_smoke.py"), str(RUN)], cwd=source)
    command(
        [
            str(py),
            str(source / "tools/check_phase7_scan_policy.py"),
            str(RUN),
            "--operation",
            "verify",
        ],
        cwd=source,
    )
    env["complete_scope"] = (
        "Complete clean SDK and P7 non-browser protocol; actual browser and overall E2E recorded separately"
    )
    env["phase7_actual_browser_complete"] = False
    env["phase7_full_e2e_complete"] = False
    env["complete"] = True
    env["ended_utc"] = datetime.now(UTC).isoformat()
    (RUN / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    hashes = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in RUN.iterdir()
        if p.is_file() and p.name != "artifacts.json"
    }
    (RUN / "artifacts.json").write_text(
        json.dumps(
            [
                {
                    "path": k,
                    "sha256": v,
                    "uploaded": k not in ("gitleaks.exe", "gitleaks", bootstrap.name),
                }
                for k, v in sorted(hashes.items())
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    selected = []
    for path in sorted(RUN.rglob("*")):
        relative = path.relative_to(RUN)
        if path.is_file() and (
            (
                len(relative.parts) == 1
                and (path.suffix in (".log", ".json", ".jsonl", ".xml") or path.name == ".coverage")
            )
            or relative.parts[0]
            in (
                "dataset",
                "factor-dataset",
                "factor-runs",
                "wheel",
                "research",
                "portfolio",
                "backtest",
                "ui",
                "ui-wheelhouse",
                "e2e",
                "competition",
                "scan-policy",
                "tmp",
            )
            or (
                relative.parts[0] == "reproduction"
                and relative.parts[1] != "venv"
                and not (
                    relative.parts[1] == "p6"
                    and len(relative.parts) > 2
                    and relative.parts[2] in ("venv", "source", "pytest-cache")
                )
            )
        ):
            selected.append(
                {
                    "path": relative.as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    (RUN / "upload-selection.json").write_text(
        json.dumps(
            {
                "files": selected,
                "self_excluded": True,
                "omitted_local_tools": [
                    "gitleaks.exe" if os.name == "nt" else "gitleaks",
                    bootstrap.name,
                ],
                "policy": "Exact selected file hashes; omitted tools remain independently pinned and locally verified, not falsely claimed as uploaded",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"PASS: {RUN}")


if __name__ == "__main__":
    main()
