import hashlib
import io
import json
import os
import runpy
import sys
import zipfile
from dataclasses import asdict
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec
from aqrp.core.errors import ContractError
from aqrp.data.synthetic import load_synthetic
from aqrp.experiments import replay_worker, reproduction
from aqrp.experiments.reproduction import ORIGINAL_BUNDLE, archive_environment, replay_original

ROOT = Path(__file__).resolve().parents[2]
WHEEL = ROOT / "docs/audits/phase-2/publication/sdk/wheel/aqrp-0.2.0-py3-none-any.whl"


@pytest.fixture(scope="module")
def original_archive():
    path = os.environ.get("AQRP_ORIGINAL_ENV_ARCHIVE")
    if not path:
        pytest.fail(
            "Complete SDK tests require tools/original_replay_smoke.py output via AQRP_ORIGINAL_ENV_ARCHIVE (tools/ci.py configures it)"
        )
    stored = json.loads(Path(path).read_bytes())
    return archive_environment(stored["interpreter"], WHEEL, ROOT / "requirements.lock")


def replay_request(snapshot, *, factor="momentum", implementation=ORIGINAL_BUNDLE, version="1.0.0"):
    query = QuerySpec(
        ("SYN_A:001",),
        "SYN_A",
        "SYN_A_CAL",
        (date(2024, 1, 2), date(2024, 1, 4)),
        ("close", "volume"),
        "split_adjusted",
    )
    return json.loads(
        canonical(
            {
                "snapshot": {**asdict(snapshot), "root": str(snapshot.root)},
                "query": asdict(query),
                "ref": {
                    "factor_id": factor,
                    "factor_version": version,
                    "implementation_hash": implementation,
                },
                "decision_time": "2024-01-04T12:05:00Z",
                "parameters": {"lookback": 2},
                "seed": 17,
            }
        )
    )


@pytest.mark.parametrize("factor", ["momentum", "reversal", "volume"])
def test_three_real_original_factor_refs(original_archive, make_snapshot, factor):
    from decimal import Decimal

    tables = load_synthetic(sessions=[(date(2024, 1, i), "12:00:00") for i in (2, 3, 4)])
    for row in tables["bars_daily"]:
        i = row["session_date"].day - 2
        price, volume = Decimal([100, 110, 121][i]), Decimal([100, 150, 200][i])
        row.update({k: price for k in ("open", "high", "low", "close")})
        row.update(
            volume=volume,
            source_volume=str(volume),
            amount=price * volume,
            source_amount=str(price * volume),
        )
    result = replay_original(original_archive, replay_request(make_snapshot(tables), factor=factor))
    assert result["status"] == "ORIGINAL_ARTIFACT_EXECUTED"
    assert (
        result["result"]["rows"][0]["factor_value"]
        == {"momentum": 0.21, "reversal": -0.21, "volume": 0.6}[factor]
    )


def test_archive_integrity_and_invalid_replay(original_archive, tmp_path, monkeypatch):
    with pytest.raises(ContractError, match="UNAPPROVED_REPRODUCTION_ARCHIVE"):
        archive_environment(sys.executable, Path(__file__), ROOT / "requirements.lock")
    with pytest.raises(ContractError, match="REPRODUCTION_ARCHIVE_CHANGED"):
        replay_original({**original_archive, "interpreter_hash": "0" * 64}, {})
    with pytest.raises(ContractError, match="UNAPPROVED_REPRODUCTION_ARCHIVE"):
        replay_original({**original_archive, "worker_hash": "0" * 64}, {})
    with pytest.raises(ContractError, match="INVALID_REPLAY_REQUEST"):
        replay_original(original_archive, {"command": "arbitrary"})
    monkeypatch.setattr(
        reproduction,
        "_invoke",
        lambda *a: {**original_archive["inspection"], "unexpected_drift": True},
    )
    fields = {k: {} for k in ("snapshot", "query", "ref", "decision_time", "parameters", "seed")}
    with pytest.raises(ContractError, match="ORIGINAL_ENVIRONMENT_DRIFT"):
        replay_original(original_archive, fields)
    monkeypatch.setattr(
        reproduction, "_invoke", lambda *a: {**original_archive["inspection"], "inventory": {}}
    )
    with pytest.raises(ContractError, match="ORIGINAL_ENVIRONMENT_LOCK_MISMATCH"):
        archive_environment(original_archive["interpreter"], WHEEL, ROOT / "requirements.lock")


def test_subprocess_failure_is_not_cached_success(tmp_path, monkeypatch):
    monkeypatch.setattr(
        reproduction.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=1, stdout=b"", stderr=b"fixture"),
    )
    with pytest.raises(ContractError, match="ORIGINAL_ENVIRONMENT_REPLAY_FAILED"):
        reproduction._invoke(sys.executable, WHEEL, {})


def test_real_published_original_bytes_and_runs(original_archive):
    result = reproduction.replay_published_runs(
        original_archive, ROOT / "docs/audits/phase-2/publication"
    )
    assert result["status"] == "ALL_ORIGINAL_BYTES_VERIFIED_AND_THREE_RUNS_REPLAYED"
    assert len(result["verified_original_files"]) == 66
    assert {r["status"] for r in result["runs"]} == {"DECLARED_PROJECTION_MATCH"}


@pytest.mark.parametrize(
    "fault,code",
    [
        ("manifest", "ORIGINAL_PUBLICATION_MANIFEST_CHANGED"),
        ("file", "ORIGINAL_PUBLICATION_ARTIFACT_CHANGED"),
        ("nested-artifact", "ORIGINAL_RUN_ARTIFACT_CHANGED"),
        ("content", "ORIGINAL_CONTENT_HASH_CHANGED"),
        ("projection", "ORIGINAL_RUN_PROJECTION_MISMATCH"),
        ("set", "ORIGINAL_PUBLISHED_RUN_SET_INCOMPLETE"),
    ],
)
def test_published_run_guards_with_explicit_non_authoritative_fixture(
    tmp_path, monkeypatch, fault, code
):
    import shutil

    source = next((ROOT / "docs/audits/phase-2/publication/sdk/factor-runs").iterdir())
    run = tmp_path / "sdk/factor-runs" / source.name
    shutil.copytree(source, run)
    m = json.loads((run / "manifest.json").read_bytes())
    original = json.loads((run / "config.json").read_bytes())
    rows = json.loads((run / "signals.json").read_bytes())
    if fault == "nested-artifact":
        m["artifacts"][0]["sha256"] = "0" * 64
    if fault == "content":
        m["content_hash"] = "0" * 64
    (run / "manifest.json").write_bytes(canonical(m))
    entries = [
        {
            "path": p.relative_to(tmp_path).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in run.iterdir()
    ]
    manifest = tmp_path / "FILE_MANIFEST.json"
    manifest.write_bytes(canonical({"files": entries}))
    # Fixture key is intentionally different from the actual immutable P2 anchor.
    monkeypatch.setattr(
        reproduction, "ORIGINAL_PUBLICATION", hashlib.sha256(manifest.read_bytes()).hexdigest()
    )
    if fault == "manifest":
        manifest.write_bytes(b"{}")
    if fault == "file":
        (run / "config.json").write_bytes(b"{}")
    result = {"rows": rows, "config": original, "logical_hash": m["logical_hash"]}
    if fault == "projection":
        result["rows"][0]["factor_value"] = 999
    monkeypatch.setattr(reproduction, "replay_original", lambda *a: {"result": result})
    with pytest.raises(ContractError, match=code):
        reproduction.replay_published_runs({}, tmp_path)


@pytest.fixture
def worker_fixture(tmp_path, monkeypatch):
    """In-process worker guard tests with explicit fake distribution metadata.

    Separate tests above really execute the archived wheel. This fake fixture
    covers transport failure branches; it is not old-environment evidence.
    """
    import aqrp

    package_root = Path(aqrp.__file__).resolve().parent.parent
    wheel = tmp_path / "fixture.whl"
    with zipfile.ZipFile(wheel, "w") as z:
        z.write(package_root / "aqrp/__init__.py", "aqrp/__init__.py")
    dist = SimpleNamespace(version="0.2.0", locate_file=lambda name: package_root / name)
    monkeypatch.setattr(replay_worker.importlib.metadata, "distribution", lambda name: dist)
    payload = {
        "schema": "replay/1",
        "mode": "inspect",
        "wheel": str(wheel),
        "wheel_hash": hashlib.sha256(wheel.read_bytes()).hexdigest(),
    }

    def stdin(p):
        data = p if isinstance(p, bytes) else canonical(p)
        monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(data)))

    return payload, dist, stdin, wheel


def test_worker_inspect_compute_and_entrypoint(worker_fixture, make_snapshot, capsys):
    from aqrp.factors.admission import builtin_spec

    payload, dist, stdin, _ = worker_fixture
    stdin(payload)
    replay_worker.main()
    assert json.loads(capsys.readouterr().out)["python"] == "3.13.16"
    s = make_snapshot(load_synthetic(sessions=[(date(2024, 1, i), "12:00:00") for i in (2, 3, 4)]))
    ref = builtin_spec("momentum").ref
    compute = {
        **payload,
        **replay_request(s, implementation=ref.implementation_hash, version=ref.factor_version),
        "mode": "compute",
    }
    stdin(compute)
    replay_worker.main()
    assert json.loads(capsys.readouterr().out)["rows"]
    compute["ref"]["implementation_hash"] = "0" * 64
    stdin(compute)
    with pytest.raises(ValueError, match="exact original FactorRef"):
        replay_worker.main()
    stdin(payload)
    runpy.run_path(str(Path(replay_worker.__file__)), run_name="__main__")
    assert json.loads(capsys.readouterr().out)["inventory"]


def test_worker_transport_and_archive_rejections(worker_fixture):
    payload, dist, stdin, wheel = worker_fixture
    for request, reason in (
        (b"x" * 1_048_577, "input size"),
        ({**payload, "schema": "wrong"}, "schema"),
        ({**payload, "wheel_hash": "0" * 64}, "wheel changed"),
    ):
        stdin(request)
        with pytest.raises(ValueError, match=reason):
            replay_worker.main()
    dist.version = "0.3.0"
    stdin(payload)
    with pytest.raises(ValueError, match="original interpreter/wheel"):
        replay_worker.main()
    dist.version = "0.2.0"
    with zipfile.ZipFile(wheel, "w") as z:
        z.writestr("aqrp/__init__.py", b"changed")
    stdin({**payload, "wheel_hash": hashlib.sha256(wheel.read_bytes()).hexdigest()})
    with pytest.raises(ValueError, match="installed archive byte mismatch"):
        replay_worker.main()
