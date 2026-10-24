"""CLI uses the real shared service; launcher tests constrain subprocess argv/env."""

import json
import os
import runpy
import sys
from pathlib import Path

import pytest

from aqrp.services.task_cli import main
from aqrp.services.task_requests import initialize
from aqrp.services.task_worker import start_worker
from aqrp.services.tasks import TaskService


@pytest.fixture(scope="module")
def workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("task-cli")
    initialize(root, "a" * 40)
    return root


def invoke(root, capsys, op, *args, code=0):
    exit_code = main([op, "--workspace", str(root), *map(str, args)])
    output = capsys.readouterr().out
    assert exit_code == code, output
    return json.loads(output)


def test_cli_catalogue_freeze_submit_cancel_defaults_and_error_outputs(workspace, tmp_path, capsys):
    r = workspace
    assert invoke(r, capsys, "init", "--commit", "a" * 40)["financial_approval"] == "NONE"
    assert invoke(r, capsys, "catalogue")["scope"] == "ENGINEERING_TEST_ONLY"
    request = tmp_path / "draft.json"
    request.write_text('{"kind":"research","start":"2024-01-06","end":"2024-01-06","horizons":[1]}')
    frozen = tmp_path / "frozen.json"
    invoke(r, capsys, "freeze", "--request", request, "--output", frozen)
    t = invoke(r, capsys, "submit", "--request", frozen, "--key", "queue")["task_id"]
    assert invoke(r, capsys, "status", "--task", t)["status"] == "QUEUED"
    assert invoke(r, capsys, "list")[0]["task_id"] == t
    assert invoke(r, capsys, "logs", "--task", t)[0]["kind"] == "SUBMITTED"
    assert invoke(r, capsys, "cancel", "--task", t)["status"] == "CANCELLED"
    assert invoke(r, capsys, "work", "--task", t)["status"] == "CANCELLED"
    assert start_worker(TaskService(r), t)["status"] == "ALREADY_SUBMITTED"
    assert invoke(r, capsys, "defaults")["revision"] == 0
    patch = tmp_path / "patch.json"
    patch.write_text('{"lookback":3}')
    assert invoke(r, capsys, "defaults", "--revision", 0, "--request", patch)["revision"] == 1
    assert invoke(r, capsys, "rollback", "--revision", 1, "--target", 1)["revision"] == 2
    assert invoke(r, capsys, "status", "--task", "bad", code=2)["code"] == "UNKNOWN_TASK"
    assert (
        invoke(r, capsys, "freeze", "--request", tmp_path / "missing", code=2)["code"]
        == "FileNotFoundError"
    )


def test_cli_real_pipeline_artifacts_replay_and_comparison(tmp_path, capsys):
    initialize(tmp_path, "a" * 40)
    request = tmp_path / "draft.json"
    request.write_text(
        '{"kind":"engineering_pipeline","start":"2024-01-06","end":"2024-01-06","horizons":[1]}'
    )
    r = invoke(tmp_path, capsys, "submit", "--request", request, "--key", "pipeline", "--wait")
    assert r["status"] == "SUCCEEDED", r
    t = r["task_id"]
    assert invoke(tmp_path, capsys, "compare", "--task", t, "--right", t)["numeric_equal"]
    assert (
        invoke(
            tmp_path,
            capsys,
            "artifact",
            "--task",
            t,
            "--slot",
            "B",
            "--name",
            "result.json",
            code=2,
        )["code"]
        == "ARTIFACT_OUTPUT_REQUIRED"
    )
    output = tmp_path / "download.json"
    assert (
        invoke(
            tmp_path,
            capsys,
            "artifact",
            "--task",
            t,
            "--slot",
            "B",
            "--name",
            "result.json",
            "--output",
            output,
        )["status"]
        == "VERIFIED_ARTIFACT_SAVED"
    )
    assert json.loads(output.read_bytes())["account"]["cash_total"] == "98.1"
    replay = invoke(tmp_path, capsys, "replay", "--task", t, "--key", "cli-replay", "--wait")
    assert replay["status"] == "SUCCEEDED", replay
    assert (
        invoke(tmp_path, capsys, "submit", "--request", request, "--key", "pipeline")["task_id"]
        == t
    )


def test_launcher_is_loopback_fixed_argv_no_shell_and_keeps_home_identity(tmp_path, monkeypatch):
    import aqrp.ui.launch as launcher

    calls = []

    def call(args, **kw):
        calls.append((args, kw))
        return 0

    monkeypatch.setattr(launcher.subprocess, "call", call)
    monkeypatch.setenv("AQRP_DO_NOT_FORWARD", "test-value")
    assert (
        launcher.main(["--workspace", str(tmp_path), "--commit", "a" * 40, "--port", "19324"]) == 0
    )
    argv, kw = calls[-1]
    assert "--server.address=127.0.0.1" in argv and "--server.port=19324" in argv
    assert kw["shell"] is False and "AQRP_DO_NOT_FORWARD" not in kw["env"]
    if "USERPROFILE" in os.environ:
        assert kw["env"]["USERPROFILE"] == os.environ["USERPROFILE"]
    monkeypatch.setattr(
        sys, "argv", ["aqrp-ui", "--workspace", str(tmp_path), "--commit", "a" * 40]
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("aqrp.ui.launch", run_name="__main__")
    assert exc.value.code == 0


def test_task_cli_module_entry_keeps_structured_failure(workspace, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv", ["aqrp-tasks", "status", "--workspace", str(workspace), "--task", "missing"]
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("aqrp.services.task_cli", run_name="__main__")
    assert exc.value.code == 2
    assert json.loads(capsys.readouterr().out)["code"] == "UNKNOWN_TASK"


@pytest.mark.parametrize("failure", ["missing", "version", "record", "lock"])
def test_ui_environment_refuses_missing_or_modified_distribution(monkeypatch, failure):
    import importlib.metadata

    from aqrp.core.errors import ContractError
    from aqrp.ui.environment import ui_environment

    distribution = importlib.metadata.distribution

    class Changed:
        version = "0"

        def read_text(self, name):
            return None if failure == "record" else "original"

    def dist(name):
        if failure == "missing":
            raise importlib.metadata.PackageNotFoundError(name)
        d = distribution(name)
        if failure in ("version", "record"):
            c = Changed()
            c.version = d.version if failure == "record" else "0"
            return c
        return d

    monkeypatch.setattr(importlib.metadata, "distribution", dist)
    if failure == "lock":
        old = Path.read_text
        monkeypatch.setattr(
            Path,
            "read_text",
            lambda p, *a, **kw: "" if p.name.startswith("requirements-") else old(p, *a, **kw),
        )
    with pytest.raises(ContractError):
        ui_environment()
