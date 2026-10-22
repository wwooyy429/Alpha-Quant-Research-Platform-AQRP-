"""Developer receipt: official ZIP/byte manifests, actual wheel, snapshots and ledgers."""
import argparse
import hashlib
import io
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath

REPO = Path(r"C:\Users\11638\AppData\Local\AQRP\checkouts\phase1-57461d5d-5de2-4c78-9b4e-5fad2b5ccb29")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO).decode().strip()


def verify(path, head, expected_tests, *, official_sha=None, official_size=None):
    assert re.fullmatch("[0-9a-f]{40}", head)
    source_identity = json.loads(subprocess.check_output(["git", "show", head+":docs/audits/phase-3/IMPLEMENTATION_IDENTITY.json"], cwd=REPO))
    lock = subprocess.check_output(["git", "show", head+":requirements.lock"], cwd=REPO)
    archive = None
    if path.is_file():
        raw = path.read_bytes()
        assert sha(raw) == official_sha and len(raw) == official_size
        archive = zipfile.ZipFile(path)
        assert archive.testzip() is None
        names = [r.filename for r in archive.infolist() if not r.is_dir()]
        assert len(names) == len(set(names))
        for name in names:
            p = PurePosixPath(name)
            assert not p.is_absolute() and ".." not in p.parts and "\\" not in name
        env_paths = [n for n in names if PurePosixPath(n).name == "environment.json"]
        assert len(env_paths) == 1
        prefix = env_paths[0][:-len("environment.json")]
        assert all(n.startswith(prefix) for n in names)
        files = {n[len(prefix):] for n in names}
        read = lambda name: archive.read(prefix+name)
    else:
        files = {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()}
        read = lambda name: (path/name).read_bytes()
    selection = json.loads(read("upload-selection.json"))
    selected = {r["path"] for r in selection["files"]}
    if archive:
        assert files == selected | {"upload-selection.json"}, sorted((files ^ selected)-{"upload-selection.json"})
    for item in selection["files"]:
        assert sha(read(item["path"])) == item["sha256"], item["path"]
    for row in json.loads(read("artifacts.json")):
        if row["uploaded"]:
            assert sha(read(row["path"])) == row["sha256"]
    env = json.loads(read("environment.json"))
    assert env["complete"] and not env["dirty"] and env["lock_sha256"] == sha(lock)
    executed = env["code_commit"]
    assert re.fullmatch("[0-9a-f]{40}", executed)
    if subprocess.run(["git", "cat-file", "-e", executed+"^{commit}"], cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        subprocess.run(["git", "fetch", "origin", executed], cwd=REPO, check=True, capture_output=True)
    tree = git("rev-parse", executed+"^{tree}")
    assert tree == git("rev-parse", head+"^{tree}"), "CI source tree differs from fixed head"
    xml = ET.fromstring(read("junit.xml"))
    suites = [xml] if xml.tag == "testsuite" else list(xml.iter("testsuite"))
    stats = {k: sum(int(s.get(k, 0)) for s in suites) for k in ("tests", "failures", "errors", "skipped")}
    assert stats == {"tests": expected_tests, "failures": 0, "errors": 0, "skipped": 0}, stats
    coverage = json.loads(read("coverage.json"))
    gate_failures = []
    for name, value in coverage["files"].items():
        s = value["summary"]
        normalized = name.replace("\\", "/")
        critical = normalized.split("/")[-1] in {"time.py", "units.py", "pit.py", "actions.py", "snapshot.py", "environment.py", "exposures.py", "numerics.py", "pipeline.py", "ledger.py", "reproduction.py"} or "/validation/" in normalized or "/core/security/" in normalized or normalized.endswith("/services/research.py") or ("/factors/" in normalized and normalized.split("/")[-1] in {"contracts.py", "input.py", "admission.py", "builtins.py", "engine.py"})
        minimum = (95, 90) if critical else (90, 85)
        line = 100*s["covered_lines"]/s["num_statements"] if s["num_statements"] else 100
        branch = 100*s["covered_branches"]/s["num_branches"] if s["num_branches"] else 100
        if line < minimum[0] or branch < minimum[1]:
            gate_failures.append([name, line, branch, minimum])
    assert not gate_failures, gate_failures
    wheel_names = [n for n in files if n.startswith("wheel/aqrp-") and n.endswith(".whl")]
    assert len(wheel_names) == 1
    wheel_bytes = read(wheel_names[0])
    assert sha(wheel_bytes) == env["wheel_sha256"]
    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as wheel:
        expected = {"aqrp/"+r["path"]: r["sha256"] for r in source_identity["code_bundle_manifest"]["files"]}
        assert {n for n in wheel.namelist() if n.startswith("aqrp/") and n.endswith(".py")} == set(expected)
        for name, checksum in expected.items():
            assert sha(wheel.read(name)) == checksum, name
        assert sha(wheel.read("aqrp/factors/reviewed_code.json")) == source_identity["receipt_sha256"]
        receipt = json.loads(wheel.read("aqrp/factors/reviewed_code.json"))
        assert receipt["bundle_sha256"] == source_identity["code_bundle_sha256"] == sha(canonical(source_identity["code_bundle_manifest"]))
        assert receipt["financial_approval"] == "NONE" and receipt["environment"] == "TEST_ONLY"
    allowed_wheels = set(re.findall(rb"--hash=sha256:([0-9a-f]{64})", lock))
    dep_wheels = [n for n in selected if n.startswith("reproduction/wheelhouse/") and n.endswith(".whl")]
    for name in dep_wheels:
        assert sha(read(name)).encode() in allowed_wheels, name
    assert len(dep_wheels) == (22 if "Windows" in env["os"] else 21)
    original = json.loads(read("reproduction/published-original-replay.json"))
    assert original["status"] == "ALL_ORIGINAL_BYTES_VERIFIED_AND_THREE_RUNS_REPLAYED"
    assert len(original["verified_original_files"]) == 66 and len(original["runs"]) == 3
    assert {r["status"] for r in original["runs"]} == {"DECLARED_PROJECTION_MATCH"}
    rebase = Path(__file__).parent/"verification-extracted"/(path.stem if archive else path.name)
    rebase.mkdir(parents=True, exist_ok=True)
    def extract(name):
        target = rebase/name
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = read(name)
        if target.exists():
            assert target.read_bytes() == raw
        else:
            target.write_bytes(raw)
        return target
    # Preserve originals; only the independent verification copy is rebased.
    from aqrp.core.contracts import SnapshotRef
    from aqrp.data.snapshot import verify_snapshot
    from aqrp.experiments.ledger import ExperimentLedger
    snapshots, runs, engines, factors, reports = [], [], 0, 0, 0
    for name in sorted(selected):
        if name.startswith("research/"):
            extract(name)
        if name.endswith("/manifest.json"):
            m = json.loads(read(name))
            if m.get("schema_version") == "snapshot/1.0.0":
                base = PurePosixPath(name).parent
                extract(name)
                for row in m["tables"].values():
                    extract(str(base/row["path"]))
                ref = SnapshotRef(rebase/base.parent, m["snapshot_id"], m["manifest_hash"])
                verify_snapshot(ref)
                snapshots.append({"path": str(base), "hash": m["manifest_hash"]})
            elif "artifacts" in m and m.get("mode") == "TEST_ONLY":
                base = PurePosixPath(name).parent
                for row in m["artifacts"]:
                    assert sha(read(str(base/row["path"]))) == row["sha256"]
                raw_config = read(str(base/"config.json"))
                signals = json.loads(read(str(base/"signals.json")))
                assert sha(canonical({"rows": signals, "config": raw_config.decode()})) == m["content_hash"]
                factors += 1
    for name in sorted(selected):
        if name.startswith("research/") and name.endswith("/manifest.json"):
            m = json.loads(read(name))
            if "run_id" in m:
                parent = (rebase/name).parent.parent
                ExperimentLedger(parent).verify(m["run_id"])
                runs.append(m["run_id"])
        if name.startswith("research/") and name.endswith("/engine.json"):
            for e in json.loads(read(name)):
                assert sha(e["config_snapshot_utf8"].encode()) == e["config_snapshot_sha256"]
                assert sha(canonical({"rows": e["signals"], "config": e["config_snapshot_utf8"]})) == e["content_hash"]
                engines += 1
        if name.startswith("research/") and name.endswith("/report.json"):
            r = json.loads(read(name))
            assert not r["independence_verified"] and r["financial_approval"] == "NONE" and r["formal_test_status"] == "NOT_DEPLOYED_NOT_EXECUTED"
            reports += 1
    assert snapshots and len(runs) == 3 and engines and factors == 3 and reports == 3
    result = {"scope": "Developer byte/contract verification; not independent audit or OS deployment", "path": str(path),
              "head_sha": head, "executed_sha": executed, "source_tree": tree, "executed_parents": git("show", "-s", "--format=%P", executed).split(),
              "source_binding": "EXACT_COMMIT" if head == executed else "GITHUB_PR_MERGE_TREE_EQUALS_FIXED_HEAD", "environment": env,
              "zip_sha256": official_sha, "zip_bytes": official_size, "crc": "PASS" if archive else "NOT_APPLICABLE_DIRECTORY",
              "selected_files": len(selected), "upload_selection_sha256": sha(read("upload-selection.json")), "junit": stats,
              "coverage_gates": "PASS", "wheel_sha256": sha(wheel_bytes), "python_modules": len(expected), "dependency_wheels": len(dep_wheels),
              "snapshots": snapshots, "verified_runs": runs, "engine_batches": engines, "factor_runs": factors, "engineering_reports": reports,
              "original_published_files": 66, "original_runs_replayed": 3, "result": "PASS"}
    if archive:
        archive.close()
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("path", type=Path); p.add_argument("--head", required=True); p.add_argument("--tests", type=int, required=True)
    p.add_argument("--sha"); p.add_argument("--size", type=int); p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = verify(a.path, a.head, a.tests, official_sha=a.sha, official_size=a.size)
    a.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("result", "head_sha", "executed_sha", "selected_files", "python_modules", "engine_batches", "junit")}))
