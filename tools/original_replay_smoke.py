"""Real original three Ref executions in an isolated original-wheel environment."""

import hashlib
import json
import os
import subprocess
import sys
import venv
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from aqrp.core.canonical import canonical
from aqrp.core.contracts import QuerySpec
from aqrp.data.snapshot import publish_snapshot
from aqrp.data.synthetic import PROVENANCE, load_synthetic
from aqrp.experiments.reproduction import (
    ORIGINAL_BUNDLE,
    archive_environment,
    replay_original,
    replay_published_runs,
)


def main():
    output = Path(sys.argv[1]) / "reproduction"
    source = Path(__file__).resolve().parents[1]
    wheel = source / "docs/audits/phase-2/publication/sdk/wheel/aqrp-0.2.0-py3-none-any.whl"
    output.mkdir(parents=True, exist_ok=True)
    lock = source / "requirements.lock"
    wheelhouse = output / "wheelhouse"
    wheelhouse.mkdir()

    def command(args, env=None):
        with (output / "commands.log").open("ab") as f:
            f.write(canonical([str(a) for a in args]) + b"\n")
            f.flush()
            subprocess.run(args, check=True, stdout=f, stderr=subprocess.STDOUT, env=env)

    command(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--index-url",
            "https://pypi.org/simple",
            "--require-hashes",
            "--only-binary=:all:",
            "--dest",
            str(wheelhouse),
            "-r",
            str(lock),
        ]
    )
    original_env = output / "venv"
    venv.create(original_env, with_pip=False)
    python = original_env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    env = dict(os.environ, PYTHONPATH=str(next(wheelhouse.glob("pip-*.whl"))))
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
            str(lock),
        ],
        env=env,
    )
    command([str(python), "-I", "-m", "pip", "install", "--no-index", "--no-deps", str(wheel)])
    archive = archive_environment(python, wheel, lock)
    archive["dependency_wheels"] = [
        {"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(wheelhouse.iterdir())
    ]
    (output / "environment-archive.json").write_bytes(canonical(archive))
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
    s = publish_snapshot(tables, PROVENANCE, output / "dataset")
    q = QuerySpec(
        ("SYN_A:001",),
        "SYN_A",
        "SYN_A_CAL",
        (date(2024, 1, 2), date(2024, 1, 4)),
        ("close", "volume"),
        "split_adjusted",
    )
    results = {}
    for factor, answer in (("momentum", 0.21), ("reversal", -0.21), ("volume", 0.6)):
        request = {
            "snapshot": {**asdict(s), "root": str(s.root)},
            "query": asdict(q),
            "ref": {
                "factor_id": factor,
                "factor_version": "1.0.0",
                "implementation_hash": ORIGINAL_BUNDLE,
            },
            "decision_time": "2024-01-04T12:05:00Z",
            "parameters": {"lookback": 2},
            "seed": 17,
        }
        # Transport dates are JSON strings, never Python objects/pickles across envs.
        request = json.loads(canonical(request))
        result = replay_original(archive, request)
        assert result["result"]["rows"][0]["factor_value"] == answer
        results[factor] = result
        (output / (factor + "-request.json")).write_bytes(canonical(request))
        (output / (factor + "-result.json")).write_bytes(canonical(result))
    (output / "result.json").write_bytes(
        canonical(
            {
                "status": "THREE_ORIGINAL_REFS_EXECUTED",
                "results": results,
                "environment_claim": "ORIGINAL_WHEEL_AND_LOCK_VERIFIED; not identical installer or host bytes",
            }
        )
    )
    (output / "published-original-replay.json").write_bytes(
        canonical(replay_published_runs(archive, source / "docs/audits/phase-2/publication"))
    )
    print(
        "Original 0.2.0 wheel / isolated locked venv / three exact old Refs and original published runs PASS"
    )


if __name__ == "__main__":
    main()
