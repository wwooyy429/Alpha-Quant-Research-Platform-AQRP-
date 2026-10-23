"""Installed SDK/legacy CLI/task CLI/component execution; real browser recorded separately."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from streamlit.testing.v1 import AppTest
from ui_reference import actor, compare

import aqrp
from aqrp.core.canonical import canonical
from aqrp.services.task_history import register_history
from aqrp.services.task_requests import catalogue, initialize
from aqrp.services.tasks import TaskService
from aqrp.ui.environment import ui_environment


def main():
    output = Path(sys.argv[1]) / "ui"
    output.mkdir()
    environment = json.loads((output.parent / "environment.json").read_bytes())
    workspace = output / "workspace"
    initialize(workspace, environment["code_commit"])
    service = TaskService(workspace)
    records = {}
    comparisons = {}
    (output / "ui-environment.json").write_bytes(canonical(ui_environment()))

    def command(name, args):
        p = subprocess.run([sys.executable, *args], capture_output=True, cwd=workspace)
        (output / (name + ".stdout.log")).write_bytes(p.stdout)
        (output / (name + ".stderr.log")).write_bytes(p.stderr)
        (output / (name + ".command.json")).write_bytes(
            canonical(
                {
                    "argv": [sys.executable, *args],
                    "cwd": str(workspace),
                    "exit": p.returncode,
                    "scope": "Actual installed application execution",
                }
            )
        )
        assert p.returncode == 0, (name, p.stderr[-2000:])
        return json.loads(p.stdout)

    os.environ["AQRP_WORKSPACE"] = str(workspace)
    for factor in ["momentum", "reversal"]:
        draft = {
            "kind": "engineering_pipeline",
            "factor_ids": [factor],
            "start": "2024-01-06",
            "end": "2024-01-06",
            "lookback": 2,
            "horizons": [1],
            "neutralize": True,
            "weights_percent": {factor: "100"},
            "initial_cash": "1000",
            "fee_budget": "10",
            "policy": {"top_k": 1},
            "constraints": {},
        }
        effective = service.freeze(draft)
        request_path = output / (factor + "-draft.json")
        request_path.write_bytes(canonical(draft))
        (output / (factor + "-effective.json")).write_bytes(effective.raw)
        sdk = service.submit(effective, "sdk-" + factor)
        sdk = service.work(sdk["task_id"])
        assert sdk["status"] == "SUCCEEDED", sdk
        sdk_actor = actor(
            workspace / "research-runs",
            sdk["result"]["research_run_id"],
            workspace / "backtest-runs",
            sdk["result"]["backtest_run_id"],
        )
        cat = catalogue(workspace)
        coverage = json.loads(cat["coverage"]["payload"])
        legacy_request = {
            "config": json.loads(effective.raw)["payload"]["research"],
            "snapshot": cat["snapshot"],
            "exposures": cat["exposures"],
            "coverage": coverage,
            "code_commit": environment["code_commit"],
        }
        legacy_path = output / (factor + "-legacy-research.json")
        legacy_path.write_bytes(canonical(legacy_request))
        old_r = command(
            factor + "-legacy-research",
            [
                "-m",
                "aqrp.services.cli",
                str(legacy_path),
                "--output",
                str(workspace / "research-runs"),
            ],
        )
        assert old_r["status"] == "SUCCEEDED"
        legacy_backtest = service._pipeline_request(
            json.loads(effective.raw), {"run_id": old_r["run_id"]}
        )
        old_b_path = output / (factor + "-legacy-backtest.json")
        old_b_path.write_bytes(legacy_backtest.raw)
        old_b = command(
            factor + "-legacy-backtest",
            [
                "-c",
                "from aqrp.services.backtest_cli import main; raise SystemExit(main())",
                "simulate",
                "--root",
                str(output / (factor + "-legacy-p5")),
                "--request",
                str(old_b_path),
                "--commit",
                environment["code_commit"],
            ],
        )
        assert old_b["status"] == "SUCCEEDED"
        # Each legacy CLI chain consumes its own actual P3 parent, mapped only after byte proofs.
        legacy_actor = actor(
            workspace / "research-runs",
            old_r["run_id"],
            output / (factor + "-legacy-p5"),
            old_b["run_id"],
        )
        old_metrics = json.loads(
            (workspace / "research-runs" / old_r["run_id"] / "metrics.json").read_bytes()
        )
        assert canonical(old_metrics) == canonical(sdk_actor["research_metrics"])
        cli = command(
            factor + "-task-cli",
            [
                "-m",
                "aqrp.services.task_cli",
                "submit",
                "--workspace",
                str(workspace),
                "--request",
                str(request_path),
                "--key",
                "cli-" + factor,
                "--wait",
            ],
        )
        assert cli["status"] == "SUCCEEDED" and cli["config_hash"] == sdk["config_hash"]
        cli_actor = actor(
            workspace / "research-runs",
            cli["result"]["research_run_id"],
            workspace / "backtest-runs",
            cli["result"]["backtest_run_id"],
        )
        component = AppTest.from_file(
            str(Path(aqrp.__file__).parent / "ui/app.py"), default_timeout=90
        ).run()
        component.sidebar.radio[0].set_value("Strategy Backtest").run()
        component.multiselect[0].set_value([factor])
        next(v for v in component.text_area if v.label.startswith("Factor weights")).set_value(
            json.dumps({factor: "100"})
        )
        next(
            v for v in component.text_input if v.label.startswith("Prediction horizons")
        ).set_value("1")
        next(v for v in component.button if v.label == "Submit engineering pipeline").click().run()
        assert not component.exception
        task = component.session_state["engineering_pipelinetask"]
        deadline = time.monotonic() + 240
        while service.state.get(task)["status"] not in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            assert time.monotonic() < deadline
            time.sleep(0.1)
        ui = service.status(task)
        assert ui["status"] == "SUCCEEDED", ui
        assert ui["config_hash"] == sdk["config_hash"]
        component.run()
        assert not component.exception
        component_actor = actor(
            workspace / "research-runs",
            ui["result"]["research_run_id"],
            workspace / "backtest-runs",
            ui["result"]["backtest_run_id"],
        )
        records[factor] = {
            "sdk": sdk,
            "task_cli": cli,
            "component": ui,
            "old_research_cli": old_r,
            "old_backtest_cli": {"run_id": old_b["run_id"], "status": old_b["status"]},
            "input_config_hash": sdk["config_hash"],
        }
        comparisons[factor] = {
            name: compare(sdk_actor, value)
            for name, value in [
                ("legacy-cli", legacy_actor),
                ("task-cli", cli_actor),
                ("component", component_actor),
            ]
        }
        assert all(
            c["research_equal"] and c["financial_exact_equal"] for c in comparisons[factor].values()
        ), comparisons[factor]
        for name, value in [
            ("sdk", sdk_actor),
            ("legacy-cli", legacy_actor),
            ("task-cli", cli_actor),
            ("component", component_actor),
        ]:
            (output / (factor + "-" + name + "-projection.json")).write_bytes(canonical(value))
        before = len(service.list())
        for page in [
            "Dashboard",
            "Factor Library",
            "Alpha Research",
            "Strategy Backtest",
            "Experiment Manager",
            "Settings",
        ]:
            component.sidebar.radio[0].set_value(page).run()
            assert not component.exception
        assert len(service.list()) == before
    momentum = json.loads((output / "momentum-sdk-projection.json").read_bytes())
    reversal = json.loads((output / "reversal-sdk-projection.json").read_bytes())
    assert {f["security_id"] for f in momentum["financial"]["fills"]} != {
        f["security_id"] for f in reversal["financial"]["fills"]
    }
    archive = json.loads(Path(os.environ["AQRP_ORIGINAL_ENV_ARCHIVE"]).read_bytes())
    publication = Path(__file__).resolve().parents[1] / "docs/audits/phase-2/publication"
    register_history(workspace, archive, publication)
    historical = service.submit(
        service.freeze(
            {
                "kind": "replay",
                "profile": "PUBLISHED_REF_PROJECTION",
                "source_task": "published-original",
            }
        ),
        "original-ref-replay",
    )
    historical = service.work(historical["task_id"])
    assert historical["status"] == "SUCCEEDED", historical
    summary = {
        "scope": "Actual installed SDK/oldCLI/taskCLI/AppTest components; real browser separately required",
        "real_browser_executed_here": False,
        "financial_approval": "NONE",
        "formal_Test": False,
        "records": records,
        "comparisons": comparisons,
        "registered_original_Ref_replay": historical,
        "ui_environment": ui_environment(),
        "Windows_R2": "DEFERRED / NOT VERIFIED",
    }
    (output / "summary.json").write_bytes(canonical(summary))
    print(
        "P6 installed application SDK/legacyCLI/taskCLI/component parity, six pages, factor replacement and original-Ref execution PASS; real browser not claimed here"
    )


if __name__ == "__main__":
    main()
