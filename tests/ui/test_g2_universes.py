"""Trusted universe selection binds P1 history and drives actual research/execution."""

import json
import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import aqrp
from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.data.query import universe_at
from aqrp.services.task_cli import main
from aqrp.services.task_inputs import execution_requests
from aqrp.services.task_requests import catalogue, initialize, references
from aqrp.services.tasks import TaskService

SINGLE = {"start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}


@pytest.fixture(scope="module")
def workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("universe-selection")
    initialize(root, "a" * 40)
    return root


@pytest.mark.parametrize(
    "pool,ids", [("SYN_U", range(1, 7)), ("SYN_CORE4", range(1, 5)), ("SYN_TAIL4", range(3, 7))]
)
def test_real_selected_pool_membership_and_p5_sidecar(workspace, pool, ids):
    s = TaskService(workspace)
    c = catalogue(workspace)
    frozen = s.freeze({**SINGLE, "universe_id": pool})
    config = json.loads(frozen.raw)["payload"]["research"]
    assert config["universe_id"] == pool
    assert config["universe_ref"] == c["universes"][pool]
    assert config["universe_ref"]["membership_history_sha256"]
    t = s.submit(frozen, pool)["task_id"]
    r = s.work(t)
    assert r["status"] == "SUCCEEDED", r
    rows = json.loads(s.artifact(t, "R", "raw.json"))["rows"]
    assert {x["security_id"] for x in rows} == {f"SYN_A:{i:03d}" for i in ids}
    ref, _, _ = references(workspace, c)
    req = execution_requests(
        config, ref, workspace / "research-runs", {"run_id": r["result"]["research_run_id"]}
    )["momentum"]
    raw = json.loads(req.raw)
    for quote_time in sorted({row["event_time"] for row in raw["sidecar"]["rows"]}):
        allowed = {x["security_id"] for x in universe_at(pool, quote_time, ref)}
        assert all(
            x["in_universe"] == (x["security_id"] in allowed)
            for x in raw["sidecar"]["rows"]
            if x["event_time"] == quote_time
        )
    assert raw["sidecar"]["snapshot_sha256"] == c["snapshot"]["manifest_hash"]


@pytest.mark.parametrize("pool", ["arbitrary", "../SYN_U", "SYN_B", 1, None, []])
def test_unknown_or_nonregistered_pool_is_refused(workspace, pool):
    with pytest.raises(ContractError, match="UNKNOWN_ENGINEERING_UNIVERSE"):
        TaskService(workspace).freeze({**SINGLE, "universe_id": pool})


def test_cli_sdk_canonical_pool_identity_and_registration(workspace, tmp_path, capsys):
    s = TaskService(workspace)
    draft = {**SINGLE, "universe_id": "SYN_CORE4"}
    path = tmp_path / "draft.json"
    path.write_text(json.dumps(draft))
    assert main(["freeze", "--workspace", str(workspace), "--request", str(path)]) == 0
    raw = json.loads(capsys.readouterr().out)
    assert raw == json.loads(s.freeze(draft).raw)
    variants = tmp_path / "variants.json"
    variants.write_text(json.dumps([{**SINGLE, "universe_id": "SYN_TAIL4", "lookback": 3}]))
    assert (
        main(
            [
                "campaign-register",
                "--workspace",
                str(workspace),
                "--request",
                str(variants),
                "--campaign",
                "cli-study",
            ]
        )
        == 0
    )
    registered = json.loads(capsys.readouterr().out)
    assert registered["registration_history"]["contaminated_before_registration"]
    assert main(["campaigns", "--workspace", str(workspace)]) == 0
    assert registered in json.loads(capsys.readouterr().out)


@pytest.mark.parametrize("page", ["Alpha Research", "Strategy Backtest"])
def test_both_web_forms_render_trusted_selector(workspace, monkeypatch, page):
    monkeypatch.setenv("AQRP_WORKSPACE", str(workspace))
    a = AppTest.from_file(str(Path(aqrp.__file__).parent / "ui/app.py"), default_timeout=90).run()
    a.sidebar.radio[0].set_value(page).run()
    selector = next(x for x in a.selectbox if x.label == "Stock universe")
    assert set(selector.options) == {"SYN_U", "SYN_CORE4", "SYN_TAIL4"}
    # Form fields reach the backend on submit, rather than an artificial
    # rerun without a form submission (which discards unsubmitted form state).
    selector.set_value("SYN_TAIL4")
    next(x for x in a.text_input if x.label == "Prediction horizons (session counts)").set_value(
        "1"
    )
    label = "Submit research" if page == "Alpha Research" else "Submit engineering pipeline"
    next(x for x in a.button if x.label == label).click().run()
    assert not a.exception
    kind = "research" if page == "Alpha Research" else "engineering_pipeline"
    task = a.session_state[kind + "task"]
    service = TaskService(workspace)
    assert service.request(task)["payload"]["research"]["universe_id"] == "SYN_TAIL4"
    deadline = time.monotonic() + 180
    while service.state.get(task)["status"] not in ("SUCCEEDED", "FAILED", "CANCELLED"):
        assert time.monotonic() < deadline
        time.sleep(0.1)
    assert service.status(task)["status"] == "SUCCEEDED"
    rows = json.loads(service.artifact(task, "R", "raw.json"))["rows"]
    assert {row["security_id"] for row in rows} == {f"SYN_A:{i:03d}" for i in range(3, 7)}


def test_membership_identity_changes_configuration_hash(workspace):
    s = TaskService(workspace)
    requests = [
        json.loads(s.freeze({**SINGLE, "universe_id": p}).raw)
        for p in ("SYN_U", "SYN_CORE4", "SYN_TAIL4")
    ]
    assert len({digest(x) for x in requests}) == 3
    assert len({x["payload"]["universe"]["membership_history_sha256"] for x in requests}) == 3


def test_actual_subset_pipeline_retains_exact_financial_answer(workspace):
    s = TaskService(workspace)
    task = s.submit(
        s.freeze({**SINGLE, "kind": "engineering_pipeline", "universe_id": "SYN_CORE4"}),
        "subset-pipeline",
    )["task_id"]
    actual = s.work(task)
    assert actual["status"] == "SUCCEEDED", actual
    result = s.financial_result(task)
    assert result["account"]["cash_total"] == "98.1"
    assert result["account"]["equity"] == "998.1"
    assert {f["security_id"] for f in result["fills"]} <= {f"SYN_A:{i:03d}" for i in range(1, 5)}
    request = json.loads(s.artifact(task, "B", "config.json"))
    raw = json.loads(bytes.fromhex(request["raw_request_hex"]))
    assert all(
        not row["in_universe"]
        for row in raw["sidecar"]["rows"]
        if row["security_id"] in ("SYN_A:005", "SYN_A:006")
    )
