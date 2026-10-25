"""Literal selection boundaries; omitted wire layout stays unchanged."""

import hashlib
from copy import deepcopy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import aqrp
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import advance_actor, install_execution_plan, open_protocol_driver
from aqrp.portfolio.contracts import load
from aqrp.services.task_cli import main
from aqrp.services.task_requests import catalogue, execution_selection, initialize, validate_draft
from aqrp.services.tasks import TaskService


def payload(sessions=None):
    original = [
        {"session": f"2024-01-{n:02d}", "decision_time": f"2024-01-{n:02d}T12:05:00Z"}
        for n in range(4, 23)
    ]
    return {
        "research": {"decisions": original},
        "raw_draft": {} if sessions is None else {"execution_sessions": sessions},
        "execution": {},
    }


def test_selection_keeps_all19_research_points_and_maps_original_ordinals():
    source = payload([f"2024-01-{n:02d}" for n in range(4, 23, 2)])
    before = canonical(source)
    selection = execution_selection(source)
    assert len(source["research"]["decisions"]) == 19
    assert [r["research_ordinal"] for r in selection["resolved"]] == [
        0,
        2,
        4,
        6,
        8,
        10,
        12,
        14,
        16,
        18,
    ]
    assert selection["resolved"][1] == {
        "research_ordinal": 2,
        "session": "2024-01-06",
        "decision_time": "2024-01-06T12:05:00Z",
    }
    assert before == canonical(source)
    assert selection["research_decisions_sha256"] == digest(source["research"]["decisions"])


def test_omission_is_derived_all_view_without_changing_old_wire():
    source = payload()
    before = canonical(source)
    selection = execution_selection(source)
    assert selection["mode"] == "ALL_RESEARCH_DECISIONS"
    assert len(selection["resolved"]) == 19
    assert canonical(source) == before and source["execution"] == {}


@pytest.mark.parametrize(
    "sessions",
    [
        [],
        (),
        None,
        "2024-01-04",
        [1],
        [True],
        ["２０２４-01-04"],
        ["2024-1-04"],
        ["2024-01-4"],
        ["2024-02-30"],
        ["2024-01-04T12:05:00Z"],
        ["2024-01-04 "],
        ["2024-01-05", "2024-01-04"],
        ["2024-01-04", "2024-01-04"],
        ["2024-01-03"],
        ["2024-01-23"],
    ],
)
def test_invalid_selection_is_never_sorted_filtered_or_defaulted(sessions):
    with pytest.raises(ContractError):
        validate_draft({"kind": "engineering_pipeline", "execution_sessions": sessions})
        execution_selection(payload(sessions))


@pytest.mark.parametrize("kind", ["research", "replay", None])
def test_selection_not_allowed_outside_engineering_pipeline(kind):
    draft = {"execution_sessions": ["2024-01-04"]}
    if kind is not None:
        draft["kind"] = kind
    with pytest.raises(ContractError, match="EXECUTION_SELECTION_PIPELINE_ONLY"):
        validate_draft(draft)


@pytest.mark.parametrize("key", ["decision_time", "research_ordinal", "session"])
def test_valid_looking_resolution_tamper_is_rederived(key):
    source = payload(["2024-01-04", "2024-01-06"])
    selection = execution_selection(source)
    source["execution"]["selection"] = deepcopy(selection)
    source["execution"]["selection"]["resolved"][0][key] = {
        "session": "2024-01-05",
        "decision_time": "2024-01-05T12:05:00Z",
        "research_ordinal": 1,
    }[key]
    with pytest.raises(ContractError, match="EXECUTION_SELECTION_CHANGED"):
        execution_selection(source)


def test_research_default_does_not_accept_injected_default_selection():
    source = payload()
    source["execution"]["selection"] = execution_selection(source)
    with pytest.raises(ContractError, match="UNEXPECTED_EXECUTION_SELECTION"):
        execution_selection(source)


@pytest.fixture(scope="module")
def builder(tmp_path_factory):
    root = tmp_path_factory.mktemp("p7-builder")
    initialize(root, "a" * 40)
    return TaskService(root)


def test_shared_builder_default_and_cli_explicit(builder, tmp_path):
    draft = {
        "kind": "engineering_pipeline",
        "factor_ids": ["momentum"],
        "start": "2024-01-04",
        "end": "2024-01-22",
        "horizons": [1],
    }
    original = builder.freeze(draft)
    x = load(original.raw)
    assert set(x["payload"]["execution"]) == {
        "initial_cash",
        "fee_budget",
        "factor_weights",
        "policy",
        "constraints",
    }
    assert x["payload"]["raw_draft"] == draft
    assert builder.validate_effective(original.raw) == x
    selected = {**draft, "execution_sessions": ["2024-01-04", "2024-01-06"]}
    direct = builder.freeze(selected)
    source, output = tmp_path / "draft.json", tmp_path / "frozen.json"
    source.write_bytes(canonical(draft))
    assert (
        main(
            [
                "freeze",
                "--workspace",
                str(builder.root),
                "--request",
                str(source),
                "--output",
                str(output),
                "--execution-sessions",
                "2024-01-04",
                "2024-01-06",
            ]
        )
        == 0
    )
    assert output.read_bytes() == direct.raw
    assert len(load(direct.raw)["payload"]["research"]["decisions"]) == 19
    changed = load(direct.raw)
    changed["payload"]["execution"]["selection"]["sessions"] = ["2024-01-06"]
    with pytest.raises(ContractError, match="EFFECTIVE_REQUEST_CHANGED"):
        builder.validate_effective(canonical(changed))


def test_cli_cannot_override_frozen_or_duplicate_selection(builder, tmp_path):
    source = tmp_path / "original.json"
    source.write_bytes(builder.freeze({"kind": "engineering_pipeline"}).raw)
    assert (
        main(
            [
                "freeze",
                "--workspace",
                str(builder.root),
                "--request",
                str(source),
                "--execution-sessions",
                "2024-01-06",
            ]
        )
        == 2
    )


def test_ui_form_uses_same_builder_without_cropping_research(tmp_path, monkeypatch):
    root = tmp_path / "web-selection"
    initialize(root, "a" * 40)
    monkeypatch.setenv("AQRP_WORKSPACE", str(root))
    # This is a form/queued-request test; no simulated browser or worker claim.
    monkeypatch.setattr(
        "aqrp.services.task_worker.start_worker", lambda *args: {"status": "QUEUED_FORM_TEST"}
    )
    app = AppTest.from_file(str(Path(aqrp.__file__).parent / "ui/app.py"), default_timeout=90).run()
    app.sidebar.radio[0].set_value("Strategy Backtest").run()
    fields = {x.label: x for x in app.text_input}
    fields["First decision session (YYYY-MM-DD)"].set_value("2024-01-04")
    fields["Last decision session (YYYY-MM-DD)"].set_value("2024-01-06")
    fields["Prediction horizons (session counts)"].set_value("1")
    fields["Execution sessions (optional comma-separated YYYY-MM-DD)"].set_value("2024-01-06")
    next(x for x in app.button if x.label == "Submit engineering pipeline").click().run()
    assert not app.exception
    service = TaskService(root)
    request = service.request(app.session_state["engineering_pipelinetask"])
    assert [d["session"] for d in request["payload"]["research"]["decisions"]] == [
        "2024-01-04",
        "2024-01-05",
        "2024-01-06",
    ]
    assert request["payload"]["execution"]["selection"]["resolved"] == [
        {"research_ordinal": 2, "session": "2024-01-06", "decision_time": "2024-01-06T12:05:00Z"}
    ]
    assert request == load(service.freeze(request["payload"]["raw_draft"]).raw)


def test_ui_cannot_claim_new_trusted_activation_from_old_session(tmp_path, monkeypatch):
    root = tmp_path / "web-activation"
    cat = initialize(root, "a" * 40)
    monkeypatch.setenv("AQRP_WORKSPACE", str(root))
    app = AppTest.from_file(str(Path(aqrp.__file__).parent / "ui/app.py"), default_timeout=90).run()
    service = TaskService(root)
    request = service.freeze(
        {"kind": "research", "start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}
    )
    runner = Path(__file__).resolve()
    identity = {
        "runner_path": str(runner),
        "runner_sha256": hashlib.sha256(runner.read_bytes()).hexdigest(),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }
    plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "UI_ACTIVATION_REGRESSION_FIXTURE",
        **identity,
        "catalogue_hash": digest(cat),
        "data_hash": cat["snapshot"]["manifest_hash"],
        "slots": [
            {
                "slot_id": "only-original-owner",
                "service_kind": "TASK",
                "request_hash": request.config_hash,
                "output_root": str(root / "research-runs"),
                "requested_units": 1,
                "grant_capacity": 1,
                "max_admitted_owners": 1,
                "expected_status": "CANCELLED",
            }
        ],
    }
    plan_hash = install_execution_plan(root, plan, identity)
    driver = open_protocol_driver(root, plan_hash, identity)
    advance_actor(driver, -1)
    app.run()
    assert not app.exception
    assert any(x.value == "EXECUTION_PLAN_ACTIVATION_STALE" for x in app.error)
    assert not service.list()


def test_cli_init_validates_catalogue_before_constructing_service(tmp_path, monkeypatch):
    def forbidden(*args):
        raise AssertionError("CLI must let trusted initialize create authority after catalogue")

    monkeypatch.setattr("aqrp.services.task_cli.TaskService", forbidden)
    root = tmp_path / "cli-initialization"
    assert main(["init", "--workspace", str(root), "--commit", "a" * 40]) == 0
    assert catalogue(root)["code_commit"] == "a" * 40
    assert (root / "task-control/admission-anchor.json").is_file()
