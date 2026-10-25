"""Task-specific campaign diagnosis retains full shared fail-closed verification."""

import sqlite3
import uuid

import pytest

from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import append_chain
from aqrp.services.task_requests import initialize
from aqrp.services.tasks import TaskService


def rows(state):
    with sqlite3.connect(state.db) as c:
        names = [
            r[0]
            for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        ]
        return {
            name: list(c.execute('SELECT * FROM "' + name + '" ORDER BY rowid')) for name in names
        }


def files(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file() and p.suffix in (".json", ".jsonl")
    }


@pytest.mark.parametrize("entry", ["service", "state"])
@pytest.mark.parametrize("fault", ["missing-campaign", "authority-hash", "unowned-trial"])
def test_task_campaign_error_translation_is_specific_and_read_only(tmp_path, entry, fault):
    initialize(tmp_path, "a" * 40)
    service = TaskService(tmp_path)
    frozen = service.freeze(
        {"factor_ids": ["momentum"], "start": "2024-01-06", "end": "2024-01-06", "horizons": [1]}
    )
    task = service.submit(frozen, "original")["task_id"]
    if fault == "unowned-trial":
        # Explicit foreign-writer fault; it is never an admitted/executed trial.
        append_chain(
            tmp_path / "research-runs/trials.jsonl",
            "TRIAL_ATTEMPT",
            {"run_id": str(uuid.uuid4()), "hypothesis": "unowned-negative-probe"},
        )
    else:
        with service.state.transaction() as c:
            if fault == "missing-campaign":
                c.execute("DELETE FROM campaign_attempts WHERE task=?", (task,))
            else:
                c.execute("UPDATE admissions SET hash=?", ("0" * 64,))
    original_rows, original_files = rows(service.state), files(tmp_path)
    expected = (
        "CAMPAIGN_ATTEMPT_HISTORY_INCOMPLETE"
        if fault == "missing-campaign"
        else "ADMISSION_HISTORY_UNVERIFIED"
    )
    with pytest.raises(ContractError) as raised:
        if entry == "service":
            service.submit(frozen, "must-not-be-created")
        else:
            service.state.submit(frozen.raw, "must-not-be-created")
    assert raised.value.code == expected
    assert rows(service.state) == original_rows
    assert files(tmp_path) == original_files
    assert len(original_rows["tasks"]) == len(original_rows["admissions"]) == 1
    assert original_rows["trial_claims"] == []
