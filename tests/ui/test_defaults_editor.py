"""Independent literal regression for the observed browser lost-edit defect."""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

import aqrp
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService


def test_two_consecutive_editor_saves_retain_second_exact_input(tmp_path, monkeypatch):
    initialize(tmp_path, "a" * 40)
    monkeypatch.setenv("AQRP_WORKSPACE", str(tmp_path))
    app = AppTest.from_file(str(Path(aqrp.__file__).parent / "ui/app.py"), default_timeout=60).run()
    app.sidebar.radio[0].set_value("Settings").run()
    for value in [3, 2]:
        app.text_area[0].set_value(json.dumps({"lookback": value}))
        next(b for b in app.button if b.label == "Save defaults revision").click().run()
        assert not app.exception
    s = TaskService(tmp_path)
    with s.state.transaction() as c:
        rows = [dict(v) for v in c.execute("SELECT * FROM defaults ORDER BY revision")]
    (tmp_path / "consecutive-save-actual.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    assert [json.loads(r["payload"]) for r in rows] == [{"lookback": 3}, {"lookback": 2}]


def settings(root, monkeypatch):
    initialize(root, "a" * 40)
    monkeypatch.setenv("AQRP_WORKSPACE", str(root))
    a = AppTest.from_file(str(Path(aqrp.__file__).parent / "ui/app.py"), default_timeout=60).run()
    a.sidebar.radio[0].set_value("Settings").run()
    assert not a.exception
    return a


def press(a, label):
    next(x for x in a.button if x.label == label).click().run()
    assert not a.exception


def test_successful_saves_and_rollback_immediately_show_own_snapshot(tmp_path, monkeypatch):
    a = settings(tmp_path, monkeypatch)
    s = TaskService(tmp_path)
    old = s.freeze({"kind": "research"})
    old_bytes = old.raw
    for revision, value in [(1, 3), (2, 2)]:
        a.text_area[0].set_value(json.dumps({"lookback": value}))
        press(a, "Save defaults revision")
        assert any("Current revision" in m.value and str(revision) in m.value for m in a.markdown)
        assert a.session_state["settings-defaults-editor-base"] == revision
        assert json.loads(a.text_area[0].value) == {"lookback": value}
    next(x for x in a.selectbox if x.label == "Rollback target revision").set_value(1).run()
    press(a, "Rollback by adding a revision")
    assert s.defaults()["revision"] == 3
    assert json.loads(a.text_area[0].value) == {"lookback": 3}
    assert a.session_state["settings-defaults-editor-base"] == 3
    assert [json.loads(s.defaults(r)["payload"]) for r in [1, 2, 3]] == [
        {"lookback": 3},
        {"lookback": 2},
        {"lookback": 3},
    ]
    assert old.raw == old_bytes
    t = s.submit(old, "old-request-after-editor-changes")
    assert s.cancel(t["task_id"]) == "CANCELLED"


def test_two_sessions_stale_editor_cannot_overwrite_new_defaults(tmp_path, monkeypatch):
    a = settings(tmp_path, monkeypatch)
    b = settings(tmp_path, monkeypatch)
    a.text_area[0].set_value('{"lookback":3}')
    press(a, "Save defaults revision")
    b.text_area[0].set_value('{"lookback":2}')
    press(b, "Save defaults revision")
    assert any(e.value == "DEFAULTS_REVISION_CONFLICT" for e in b.error)
    assert json.loads(b.text_area[0].value) == {"lookback": 2}
    assert b.session_state["settings-defaults-editor-base"] == 0
    assert TaskService(tmp_path).defaults()["revision"] == 1
    press(b, "Reload latest defaults")
    assert b.session_state["settings-defaults-editor-base"] == 1
    assert json.loads(b.text_area[0].value) == {"lookback": 3}
    b.text_area[0].set_value('{"lookback":2}')
    press(b, "Save defaults revision")
    assert TaskService(tmp_path).defaults()["revision"] == 2
    assert json.loads(TaskService(tmp_path).defaults()["payload"]) == {"lookback": 2}


def test_rejected_editor_draft_is_preserved_and_never_saved(tmp_path, monkeypatch):
    a = settings(tmp_path, monkeypatch)
    draft = '{"untrusted_field":"no-execution"}'
    a.text_area[0].set_value(draft)
    press(a, "Save defaults revision")
    assert any(e.value == "UNKNOWN_TASK_DRAFT_FIELD" for e in a.error)
    assert a.text_area[0].value == draft
    assert TaskService(tmp_path).defaults()["revision"] == 0


def test_factor_selection_preserves_unrelated_defaults_and_rollback_updates_selection(
    tmp_path, monkeypatch
):
    a = settings(tmp_path, monkeypatch)
    a.text_area[0].set_value('{"lookback":3,"fee_budget":"20"}')
    press(a, "Save defaults revision")
    a.sidebar.radio[0].set_value("Factor Library").run()
    a.multiselect[0].set_value(["reversal"])
    press(a, "Save factor selection as a defaults revision")
    s = TaskService(tmp_path)
    assert json.loads(s.defaults()["payload"]) == {
        "lookback": 3,
        "fee_budget": "20",
        "factor_ids": ["reversal"],
        "weights_percent": {"reversal": "100"},
    }
    next(x for x in a.selectbox if x.label == "Factor configuration rollback revision").set_value(
        1
    ).run()
    press(a, "Rollback factor configuration")
    assert s.defaults()["revision"] == 3
    assert json.loads(s.defaults()["payload"]) == {"lookback": 3, "fee_budget": "20"}
    assert a.session_state["selected_factors"] == ["momentum"]
