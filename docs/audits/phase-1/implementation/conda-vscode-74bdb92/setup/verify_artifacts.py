"""Developer evidence verification; does not attest Gemini SDK execution.
Usage: verify_artifacts.py REPOSITORY ZIP_DIRECTORY EXTERNAL_OUTPUT_DIRECTORY
Requires the locked Phase 1 Python environment. Does not modify source or ZIPs.
"""
import hashlib
import json
import platform
import stat
import subprocess
import sys
import zipfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path, PureWindowsPath
from xml.etree import ElementTree

TARGET = "74bdb9216c585d27de91123605aff0266ca028cc"
MERGE = "f093faca9a9dd4977caa1142267ff494766d3c7e"
EXPECTED = {
    12288989083: "73385602dad830f3157dba8f5629616127777511830b02675fd06df517f93e7c",
    12288679676: "8f092b7214202292995276a4dab3187063cd481d8a6556ac342e450738b64ea5",
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(v):
    if isinstance(v, datetime):
        return v.isoformat(timespec="microseconds")
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, Decimal):
        return format(v, "f")
    raise TypeError(type(v).__name__)

def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False, default=encode).encode()

def extract(z, destination):
    destination.mkdir(parents=True, exist_ok=False)
    names = set()
    assert len(z.infolist()) < 5000
    assert sum(i.file_size for i in z.infolist()) < 20_000_000
    for item in z.infolist():
        name = item.filename
        assert name not in names
        names.add(name)
        p = Path(name)
        assert "\\" not in name and not p.is_absolute() and not PureWindowsPath(name).drive
        assert ".." not in p.parts and not stat.S_ISLNK(item.external_attr >> 16)
        target = (destination / p).resolve()
        assert target.is_relative_to(destination.resolve())
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(item))

def main():
    repo, archives, out = (Path(p).resolve() for p in sys.argv[1:])
    out.mkdir(parents=True, exist_ok=False)
    assert sys.version_info[:3] == (3, 13, 16)
    assert sys.maxsize > 2**32 and not sysconfig_free_threaded()
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()
    assert git("rev-parse", TARGET + "^{tree}") == git("rev-parse", MERGE + "^{tree}")
    assert git("show", "-s", "--format=%P", MERGE).split() == [
        "502c6931dcfce50bee2f71a80524475fae6396bf", TARGET]
    export = out / "fixed-source.zip"
    subprocess.run(["git", "archive", "--format=zip", "--output=" + str(export), TARGET],
                   cwd=repo, check=True)
    source = out / "source"
    with zipfile.ZipFile(export) as z:
        extract(z, source)
    sys.path.insert(0, str(source / "src"))
    import pyarrow
    import pyarrow.parquet as pq
    from aqrp.core.contracts import QuerySpec, SnapshotRef
    from aqrp.data.query import query
    from aqrp.data.schemas import SCHEMAS
    from aqrp.data.snapshot import verify_snapshot
    result = {
        "performed_by": "Codex developer; not independent Gemini execution",
        "python": sys.version, "platform": platform.platform(), "pyarrow": pyarrow.__version__,
        "execution_target": TARGET, "ci_checkout_commit": MERGE,
        "ci_checkout_parents": git("show", "-s", "--format=%P", MERGE).split(),
        "ci_checkout_tree": git("rev-parse", MERGE + "^{tree}"),
        "ci_checkout_tree_matches_target": True,
        "artifacts": [], "gemini_sdk_execution": "NOT RUN",
    }
    rows_by_os, tables_by_os, configs = [], [], []
    fixture_hash = sha((source / "tests/golden/phase1_input.json").read_bytes())
    lock_hash = sha((source / "requirements.lock").read_bytes())
    for aid, expected in EXPECTED.items():
        raw = (archives / f"{aid}.zip").read_bytes()
        assert sha(raw) == expected
        dest = out / str(aid)
        with zipfile.ZipFile(archives / f"{aid}.zip") as z:
            assert z.testzip() is None
            extract(z, dest)
        base = next(dest.glob("*/artifacts.json")).parent
        env = json.loads((base / "environment.json").read_bytes())
        assert env["complete"] and not env["dirty"]
        assert env["code_commit"] == env["github_sha"] == MERGE
        assert env["github_run_id"] == "39476825340" and env["github_run_attempt"] == "1"
        assert env["python"].startswith("3.13.16 ") and env["lock_sha256"] == lock_hash
        listed = json.loads((base / "artifacts.json").read_bytes())
        checks = []
        for item in listed:
            path = base / item["path"]
            assert path.resolve().is_relative_to(base.resolve())
            actual = sha(path.read_bytes()) if path.is_file() else None
            assert actual is None or actual == item["sha256"]
            checks.append({"path": item["path"], "expected_sha256": item["sha256"],
                           "actual_sha256": actual, "status": "PASS" if actual else "NOT UPLOADED"})
        missing = {c["path"] for c in checks if c["actual_sha256"] is None}
        assert missing == {".coverage", "pip-26.2.1-py3-none-any.whl",
                           "gitleaks.exe" if aid == 12288679676 else "gitleaks"}
        listed_paths = {c["path"] for c in checks}
        unlisted = [p.relative_to(base).as_posix() for p in base.rglob("*")
                    if p.is_file() and p.relative_to(base).as_posix() not in listed_paths]
        assert set(unlisted) == {"artifacts.json"} | {
            p.relative_to(base).as_posix() for p in (base / "dataset").rglob("*") if p.is_file()}
        run = json.loads((base / "smoke-run.json").read_bytes())
        config = json.loads((base / "smoke-config.json").read_bytes())
        rows = json.loads((base / "smoke-result.json").read_bytes())
        manifest = json.loads((base / "smoke-snapshot.json").read_bytes())
        assert sha(canonical(config)) == run["config_hash"]
        assert sha(canonical(rows)) == run["result_hash"] == sha((base / "smoke-result.json").read_bytes())
        assert run["fixture_sha256"] == fixture_hash and run["rows"] == len(rows) == 2
        assert [r["close"] for r in rows] == ["100.00000000"] * 2
        assert config["snapshot_id"] == run["snapshot_id"] == manifest["snapshot_id"]
        assert config["manifest_hash"] == run["manifest_hash"] == manifest["manifest_hash"]
        assert sha(canonical({k: v for k, v in manifest.items()
                              if k not in ("snapshot_id", "manifest_hash")})) == run["manifest_hash"]
        sealed = base / "dataset" / run["snapshot_id"]
        assert (sealed / "manifest.json").read_bytes() == (base / "smoke-snapshot.json").read_bytes()
        table_checks, normalized = [], {}
        for name, entry in manifest["tables"].items():
            data = (sealed / entry["path"]).read_bytes()
            assert sha(data) == entry["sha256"]
            table = pq.read_table(sealed / entry["path"])
            assert table.schema == SCHEMAS[name] and table.num_rows == entry["rows"]
            records = table.to_pylist()
            assert all(r["snapshot_id"] == run["snapshot_id"] for r in records)
            normalized[name] = [{k: v for k, v in r.items() if k != "snapshot_id"} for r in records]
            table_checks.append({"table": name, "rows": table.num_rows,
                                 "sha256": sha(data), "schema": str(table.schema), "status": "PASS"})
        ref = SnapshotRef(base / "dataset", run["snapshot_id"], run["manifest_hash"])
        verify_snapshot(ref)
        spec = QuerySpec(tuple(config["security_ids"]), config["market_id"], config["calendar_id"],
                         tuple(date.fromisoformat(v) for v in config["session_range"]))
        view = query(spec, config["as_of"], ref)
        assert canonical(view.table.to_pylist()) == canonical(rows)
        suites = list(ElementTree.fromstring((base / "junit.xml").read_bytes()).iter("testsuite"))
        junit = {k: sum(int(s.attrib.get(k, 0)) for s in suites)
                 for k in ("tests", "failures", "errors", "skipped")}
        assert junit == {"tests": 102, "failures": 0, "errors": 0, "skipped": 0}
        assert json.loads((base / "scan-findings.json").read_bytes()) == []
        coverage = subprocess.run([sys.executable, str(source / "tools/check_coverage.py"),
                                   str(base / "coverage.json")], capture_output=True, text=True)
        (out / f"coverage-{aid}.log").write_text(coverage.stdout + coverage.stderr, encoding="utf-8")
        assert coverage.returncode == 0
        rows_by_os.append(canonical(rows))
        tables_by_os.append(canonical(normalized))
        configs.append({k: v for k, v in config.items() if k not in ("snapshot_id", "manifest_hash")})
        result["artifacts"].append({
            "id": aid, "zip_sha256": sha(raw), "zip_bytes": len(raw),
            "zip_hash_status": "PASS", "environment": env, "file_checks": checks,
            "unlisted_members": sorted(unlisted), "tables": table_checks, "junit": junit,
            "coverage_gate": "PASS", "snapshot_sdk_verify": "PASS",
            "downloaded_snapshot_query_replay": "PASS", "result_hash": run["result_hash"],
            "query_hash_original": run["query_hash"], "query_hash_relocated": view.query_hash,
            "root_hash_coverage": "11/14 referenced root files verified; 3 not uploaded",
            "project_wheel_binary_rehash": "NOT VERIFIED; wheel bytes not uploaded",
        })
    assert rows_by_os[0] == rows_by_os[1]
    assert tables_by_os[0] == tables_by_os[1]
    assert configs[0] == configs[1]
    result["cross_platform"] = {
        "smoke_bytes_and_result_hash": "PASS",
        "all_8_table_schemas_and_logical_records": "PASS",
        "only_ignored_table_field": "snapshot_id",
        "equivalent_query_config": "PASS",
        "whole_zip_or_parquet_or_wheel_equality_required": False,
    }
    local = out / "developer-smoke"
    local.mkdir()
    import os
    smoke_env = dict(os.environ, PYTHONPATH=str(source / "src"), PYTHONDONTWRITEBYTECODE="1")
    smoke = subprocess.run([sys.executable, str(source / "tools/data_smoke.py"), str(local)],
                           env=smoke_env, capture_output=True, text=True)
    (out / "developer-smoke.log").write_text(smoke.stdout + smoke.stderr, encoding="utf-8")
    assert smoke.returncode == 0
    assert (local / "smoke-result.json").read_bytes() == rows_by_os[0]
    result["developer_fresh_sdk_smoke"] = {"exit_code": smoke.returncode,
        "result_matches_both_ci_platforms": True, "full_ci_entry_rerun": False,
        "source": TARGET, "not_gemini": True}
    (out / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8")
    print("Developer ZIP hashes, available file hashes, snapshots, SDK replay, coverage,")
    print("102-test JUnit per platform, cross-OS data and fresh smoke: PASS.")
    print("Unuploaded .coverage/scanner/bootstrap wheel and project wheel remain unavailable.")
    print("Gemini SDK and binary hash execution remain BLOCKED / NOT RUN.")

def sysconfig_free_threaded():
    import sysconfig
    return bool(sysconfig.get_config_var("Py_GIL_DISABLED"))

if __name__ == "__main__":
    main()
