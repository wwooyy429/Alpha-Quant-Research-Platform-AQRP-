"""Execute the unchanged P6 gate in its released source and original wheel.

Dependencies come from the already hash-checked SDK wheelhouses. This is the
declared original-package/lock boundary, not identical historical host recovery.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "docs/audits/phase-7"
P6 = "d563347ad11e1f26e131dc06e343250282c05c33"
P6_INPUTS_SHA256 = "afab44eb186a2c569840ec3dada3acaf004dd2fbfab6f7710c3ac9d63df5ecb1"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    run = Path(sys.argv[1])
    output = run / "reproduction/p6"
    output.mkdir()
    source = output / "source"
    raw = (D / "P6_BASELINE_INPUTS.json").read_bytes()
    assert sha(raw) == P6_INPUTS_SHA256
    baseline = json.loads(raw)
    assert baseline["phase6_release_sha"] == P6
    for row in baseline["files"]:
        original = ROOT / row["path"]
        if sha(original.read_bytes()) != row["sha256"]:
            original = D / "p6-source-overrides" / row["path"]
        data = original.read_bytes()
        assert len(data) == row["bytes"] and sha(data) == row["sha256"], row["path"]
        path = source / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    old_wheel = next((source / "docs/audits/phase-6/publication/sdk/wheel").glob("aqrp-*.whl"))
    wheel_root = output / "wheel"
    wheel_root.mkdir()
    wheel = wheel_root / old_wheel.name
    shutil.copyfile(old_wheel, wheel)
    environment = output / "venv"
    venv.create(environment, with_pip=False)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    wheelhouse = run / "reproduction/wheelhouse"
    bootstrap = next(wheelhouse.glob("pip-*.whl"))
    commands = []

    def command(args, env=None):
        with (output / "commands.log").open("ab") as stream:
            stream.write((json.dumps([str(a) for a in args]) + "\n").encode())
            stream.flush()
            result = subprocess.run(
                args, cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT
            )
        commands.append(
            {"argv": [str(a) for a in args], "cwd": str(source), "exit": result.returncode}
        )
        (output / "commands.json").write_text(json.dumps(commands, indent=2), encoding="utf-8")
        assert result.returncode == 0, output / "commands.log"

    command(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            str(wheelhouse),
            "--require-hashes",
            "-r",
            str(source / "requirements.lock"),
        ],
        env=dict(os.environ, PYTHONPATH=str(bootstrap)),
    )
    lock_name = "requirements-ui-windows.lock" if os.name == "nt" else "requirements-ui-linux.lock"
    command(
        [
            str(python),
            "-I",
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            "--find-links",
            str(run / "ui-wheelhouse"),
            "--require-hashes",
            "-r",
            str(source / lock_name),
        ]
    )
    command([str(python), "-I", "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)])
    command([str(python), "-I", str(source / "tools/check_phase6_package.py")])
    command(
        [
            str(python),
            "-I",
            "-m",
            "pytest",
            "tests/environment/test_installation.py",
            "--junitxml=" + str(output / "installation.junit.xml"),
            "-o",
            "cache_dir=" + str(output / "pytest-cache"),
        ]
    )
    command(
        [
            str(python),
            "-I",
            "-m",
            "pytest",
            "tests/ui/test_g2_cancel_proof_controls.py::test_legacy_data_attempts_consume_shared_quota_without_automatic_registration",
            "tests/ui/test_task_state_setup.py",
            "--junitxml=" + str(output / "legacy-history.junit.xml"),
            "-o",
            "cache_dir=" + str(output / "pytest-cache"),
        ]
    )
    # The probe executes only the original installed package, never the P7 source.
    probe = ROOT / "tools/released_p6_probe.py"
    result = subprocess.run(
        [str(python), "-I", str(probe), str(output)], cwd=output, capture_output=True
    )
    (output / "identity.stdout.log").write_bytes(result.stdout)
    (output / "identity.stderr.log").write_bytes(result.stderr)
    assert result.returncode == 0
    identity = json.loads(result.stdout)
    assert identity["version"] == "0.6.0.dev5"
    assert identity["bundle"] == "28c3cc049efcce8fc3e55b4056e8e116f98deca39eeb1d2c8822799c8e98855b"
    assert len(identity["modules"]["files"]) == 83
    assert all(x["factor_version"] == "1.2.1" for x in identity["factor_refs"].values())
    report = {
        "scope": "Original P6 package/lock/source/gate and four actual old Refs; not historical host equivalence",
        "source_commit": P6,
        "source_files": len(baseline["files"]),
        "source_manifest_sha256": sha(raw),
        "wheel_sha256": sha(wheel.read_bytes()),
        "probe_sha256": sha(probe.read_bytes()),
        "python": str(python),
        "original_identity": identity,
        "source_and_venv_upload": "Excluded explicitly; source reconstructable from fixed P6 Git plus frozen manifest/overrides; original wheel and execution evidence included",
        "result": "PASS",
    }
    (output / "RESULT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"original_P6_fixed_source": P6, "result": "PASS"}))


if __name__ == "__main__":
    main()
