"""Thin component interactions; all tasks and ledger evidence are real."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import aqrp
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService

APP = Path(aqrp.__file__).parent / "ui/app.py"


@pytest.fixture(scope="module")
def workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("interactive-view")
    initialize(root, "a" * 40)
    s = TaskService(root)
    d = {
        "kind": "engineering_pipeline",
        "start": "2024-01-06",
        "end": "2024-01-06",
        "horizons": [1],
    }
    for i, kind in enumerate(["research", "engineering_pipeline"]):
        row = s.submit(s.freeze({**d, "kind": kind}), str(i))
        r = s.work(row["task_id"])
        assert r["status"] == "SUCCEEDED", r
    row = s.submit(s.freeze({**d, "constraints": {"gross_max": "0"}}), "risk-reject")
    assert s.work(row["task_id"])["status"] == "FAILED"
    return root


def app(root, monkeypatch, page):
    monkeypatch.setenv("AQRP_WORKSPACE", str(root))
    a = AppTest.from_file(str(APP), default_timeout=60).run()
    a.sidebar.radio[0].set_value(page).run()
    assert not a.exception
    return a


def press(a, label):
    next(x for x in a.button if x.label == label).click().run()
    assert not a.exception


def test_recent_run_buttons_open_actual_run_and_original_artifacts(workspace, monkeypatch):
    a = app(workspace, monkeypatch, "Dashboard")
    label = next(x.label for x in a.button if x.label.startswith("Open backtest run"))
    press(a, label)
    assert a.title[0].value == "Strategy Backtest"
    assert any("REQUIRED_STAGE_REJECTED" in x.value for x in a.error)
    assert a.get("download_button")
    next(x for x in a.selectbox if x.label == "Child stage").set_value("R").run()
    next(x for x in a.selectbox if x.label == "Manifest artifact").set_value("report.html").run()
    assert not a.exception
    press(a, "Refresh task")
    a.sidebar.radio[0].set_value("Dashboard").run()
    label = next(x.label for x in a.button if x.label.startswith("Open research run"))
    press(a, label)
    assert a.title[0].value == "Alpha Research"


def test_experiment_filters_and_frozen_configuration_comparison(workspace, monkeypatch):
    a = app(workspace, monkeypatch, "Experiment Manager")
    next(x for x in a.multiselect if x.label == "Task states").set_value(["SUCCEEDED"]).run()
    assert not a.exception
    press(a, "Compare declared results")
    text = json.dumps([x.value for x in a.json])
    assert "projection_fields" in text
    a.sidebar.radio[0].set_value("Factor Library").run()
    press(a, "Compare frozen factor configurations")
    assert a.json
    a.sidebar.radio[0].set_value("Experiment Manager").run()
    next(x for x in a.text_input if x.label == "Task / run ID contains").set_value("no-match").run()
    assert any("No matching tasks" in x.value for x in a.info)


def test_settings_rollback_and_actual_queue_cancellation(workspace, monkeypatch):
    s = TaskService(workspace)
    s.save_defaults(s.defaults()["revision"], {"lookback": 2})
    a = app(workspace, monkeypatch, "Settings")
    press(a, "Rollback by adding a revision")
    assert s.defaults()["revision"] == 2
    queued = s.submit(s.freeze({"kind": "research"}), "queued-cancel")
    a.sidebar.radio[0].set_value("Experiment Manager").run()
    next(x for x in a.selectbox if x.label == "Task").set_value(queued["task_id"]).run()
    press(a, "Cancel safely")
    assert s.status(queued["task_id"])["status"] == "CANCELLED"


@pytest.mark.parametrize(
    "values",
    [
        [None, "1.25", "-0.50"],
        ["9007199254740993"],
        ["0." + "0" * 400 + "1"],
        ["NaN"],
        ["not-number"],
    ],
)
def test_chart_raw_values_and_explicit_precision_refusal(workspace, monkeypatch, values):
    monkeypatch.setenv("AQRP_WORKSPACE", str(workspace))
    script = (
        "from aqrp.ui.app import chart, table\nchart("
        + repr(list(range(len(values))))
        + ","
        + repr(values)
        + ",'precision-control')\ntable([{'value':None},{'value':float('nan')}])"
    )
    a = AppTest.from_string(script, default_timeout=60).run()
    assert not a.exception
    if values == [None, "1.25", "-0.50"]:
        assert a.get("plotly_chart")
    else:
        assert any("Chart precision unavailable" in w.value for w in a.warning)


def test_corrupt_catalogue_is_visible_error_and_never_an_empty_success(workspace, monkeypatch):
    path = workspace / "catalog.json"
    raw = path.read_bytes()
    try:
        x = json.loads(raw)
        x["code_bundle"] = "0" * 64
        path.write_text(json.dumps(x))
        monkeypatch.setenv("AQRP_WORKSPACE", str(workspace))
        a = AppTest.from_file(str(APP), default_timeout=60).run()
        assert a.error and not a.metric and not a.exception
    finally:
        path.write_bytes(raw)


def test_chart_precision_threshold_is_independent_of_decimal_context(workspace, monkeypatch):
    monkeypatch.setenv("AQRP_WORKSPACE", str(workspace))
    source = "from decimal import localcontext\nfrom aqrp.ui.app import chart\nwith localcontext() as ctx:\n    ctx.prec=16\n    chart([0],['9007199254740992.00000001'],'threshold-control')"
    a = AppTest.from_string(source, default_timeout=60).run()
    assert not a.exception
    assert any("Chart precision unavailable" in w.value for w in a.warning)
