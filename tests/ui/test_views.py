"""AppTest component execution, explicitly separate from real-browser evidence."""

import json
import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import aqrp
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService

APP = Path(aqrp.__file__).parent / "ui/app.py"
PAGES = [
    "Dashboard",
    "Factor Library",
    "Alpha Research",
    "Strategy Backtest",
    "Experiment Manager",
    "Settings",
]


@pytest.fixture(scope="module")
def view_workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("component-views")
    initialize(root, "a" * 40)
    return root


def app(root, monkeypatch):
    monkeypatch.setenv("AQRP_WORKSPACE", str(root))
    value = AppTest.from_file(str(APP), default_timeout=45).run()
    assert not value.exception
    return value


@pytest.mark.parametrize("page", PAGES)
def test_six_pages_render_real_catalogue_and_empty_state(view_workspace, monkeypatch, page):
    a = app(view_workspace, monkeypatch)
    a.sidebar.radio[0].set_value(page).run()
    assert not a.exception
    assert a.title[0].value == page
    assert any("Financial approval: NONE" in c.value for c in a.sidebar.caption)


def test_factor_selection_revision_save_and_rollback(view_workspace, monkeypatch):
    a = app(view_workspace, monkeypatch)
    a.sidebar.radio[0].set_value("Factor Library").run()
    a.multiselect[0].set_value(["reversal"])
    next(b for b in a.button if b.label == "Apply selection to new forms").click().run()
    assert a.session_state["selected_factors"] == ["reversal"]
    next(
        b for b in a.button if b.label == "Save factor selection as a defaults revision"
    ).click().run()
    a.run()
    assert TaskService(view_workspace).state.defaults()["revision"] == 1
    next(b for b in a.button if b.label == "Rollback factor configuration").click().run()
    assert TaskService(view_workspace).state.defaults()["revision"] == 2
    assert not a.exception


def test_settings_default_cas_and_invalid_input_exposed(view_workspace, monkeypatch):
    a = app(view_workspace, monkeypatch)
    a.sidebar.radio[0].set_value("Settings").run()
    a.text_area[0].set_value('{"lookback":3,"initial_cash":"2000"}')
    next(b for b in a.button if b.label == "Save defaults revision").click().run()
    assert not a.exception
    s = TaskService(view_workspace)
    assert json.loads(s.state.defaults()["payload"])["lookback"] == 3
    a.run()
    a.text_area[0].set_value('{"api_key":"synthetic-negative-control"}')
    next(b for b in a.button if b.label == "Save defaults revision").click().run()
    assert a.error and a.error[-1].value == "UNKNOWN_TASK_DRAFT_FIELD"
    assert not a.exception


def test_formal_gate_is_real_backend_refusal(view_workspace, monkeypatch):
    a = app(view_workspace, monkeypatch)
    a.sidebar.radio[0].set_value("Strategy Backtest").run()
    next(b for b in a.button if b.label == "Check formal-entry gate").click().run()
    assert any(e.value == "APPROVAL_REQUIRED" for e in a.error)
    assert not a.exception


def test_component_form_submits_actual_worker_and_preserves_effective_values(tmp_path, monkeypatch):
    initialize(tmp_path, "a" * 40)
    a = app(tmp_path, monkeypatch)
    a.sidebar.radio[0].set_value("Strategy Backtest").run()
    next(t for t in a.text_input if t.label == "Prediction horizons (session counts)").set_value(
        "1"
    )
    next(b for b in a.button if b.label == "Submit engineering pipeline").click().run()
    assert not a.exception

    task = a.session_state["engineering_pipelinetask"]
    s = TaskService(tmp_path)
    deadline = time.monotonic() + 180
    while s.state.get(task)["status"] not in ("SUCCEEDED", "FAILED", "CANCELLED"):
        assert time.monotonic() < deadline
        time.sleep(0.1)
    row = s.status(task)
    assert row["status"] == "SUCCEEDED", row
    a.run()
    assert not a.exception
    assert any(m.label == "Maximum drawdown (core result)" for m in a.metric)
    assert a.get("plotly_chart")
    frozen = json.loads(s.state.get(task)["raw"])
    assert frozen["payload"]["execution"]["factor_weights"] == {"momentum": "1"}
    assert frozen["payload"]["research"]["horizons"] == [1]
    next(b for b in a.button if b.label == "New experiment key").click().run()
    a.sidebar.radio[0].set_value("Alpha Research").run()
    assert not a.exception
    a.sidebar.radio[0].set_value("Experiment Manager").run()
    next(b for b in a.button if b.label == "Compare declared results").click().run()
    assert not a.exception


def test_corrupt_actual_transaction_hides_trusted_financial_widgets(tmp_path, monkeypatch):
    initialize(tmp_path, "a" * 40)
    service = TaskService(tmp_path)
    row = service.submit(
        service.freeze(
            {
                "kind": "engineering_pipeline",
                "factor_ids": ["momentum"],
                "start": "2024-01-06",
                "end": "2024-01-06",
                "horizons": [1],
            }
        ),
        "damaged-view",
    )
    result = service.work(row["task_id"])
    assert result["status"] == "SUCCEEDED", result
    binding = result["slots"]["B"]["binding"]
    root = Path(binding["physical_ledger_root"]) / binding["child_run_id"]
    path = next((root / "transactions").glob("commit-*.json"))
    raw = path.read_bytes()
    try:
        path.write_bytes(raw + b" ")
        a = app(tmp_path, monkeypatch)
        a.sidebar.radio[0].set_value("Strategy Backtest").run()
        assert not a.exception
        assert not a.metric
        assert any("No trusted financial results" in e.value for e in a.error)
    finally:
        path.write_bytes(raw)
    assert service.status(row["task_id"])["status"] == "SUCCEEDED"
