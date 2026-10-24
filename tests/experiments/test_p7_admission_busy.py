"""Distinguish transient lock contention from corrupted authority history."""

import sqlite3
from types import SimpleNamespace

import pytest

from aqrp.core.errors import ContractError
from aqrp.experiments import admission


@pytest.fixture
def budget(tmp_path):
    control = tmp_path / "task-control"
    control.mkdir()
    c = sqlite3.connect(control / "tasks.sqlite", isolation_level=None)
    c.execute("CREATE TABLE workspace(id TEXT)")
    c.execute("INSERT INTO workspace VALUES ('literal-busy-fixture')")
    c.execute("BEGIN IMMEDIATE")
    authority = admission.BudgetAuthority(tmp_path)
    authority.initialize(c, "literal-busy-fixture")
    c.commit()
    c.close()
    return authority


def busy_error():
    error = sqlite3.OperationalError("literal SQLITE_BUSY injection")
    error.sqlite_errorcode = sqlite3.SQLITE_BUSY
    return error


def test_only_pretransaction_setup_retries_then_body_runs_once(budget, monkeypatch):
    original_connect = sqlite3.connect
    attempts, body = [], []

    class OnceBusy(sqlite3.Connection):
        def execute(self, sql, *args, **kwargs):
            if sql == "BEGIN IMMEDIATE":
                attempts.append(sql)
                if len(attempts) == 1:
                    raise busy_error()
            return super().execute(sql, *args, **kwargs)

    monkeypatch.setattr(
        admission.sqlite3, "connect", lambda *a, **k: original_connect(*a, **k, factory=OnceBusy)
    )
    with budget.transaction() as c:
        body.append("one actual body")
        assert c.in_transaction
        assert c.execute("SELECT count(*) FROM admissions").fetchone()[0] == 0
    assert len(attempts) == 2
    assert body == ["one actual body"]


def test_busy_deadline_is_explicit_retryable_and_does_not_enter_body(budget, monkeypatch):
    original_connect = sqlite3.connect

    class AlwaysBusy(sqlite3.Connection):
        def execute(self, sql, *args, **kwargs):
            if sql == "BEGIN IMMEDIATE":
                raise busy_error()
            return super().execute(sql, *args, **kwargs)

    ticks = iter([0, 31])
    monkeypatch.setattr(
        admission, "time", SimpleNamespace(monotonic=lambda: next(ticks), sleep=lambda _: None)
    )
    monkeypatch.setattr(
        admission.sqlite3, "connect", lambda *a, **k: original_connect(*a, **k, factory=AlwaysBusy)
    )
    with pytest.raises(ContractError, match="ADMISSION_BUSY") as error:
        with budget.transaction():
            pytest.fail("a timed-out setup may not execute the business body")
    assert error.value.retryable is True


def test_busy_inside_body_rolls_back_without_automatic_body_retry(budget):
    entered = []
    with pytest.raises(ContractError, match="ADMISSION_BUSY") as error:
        with budget.transaction() as c:
            entered.append("one body")
            c.execute("CREATE TABLE body_transaction_probe(value TEXT)")
            c.execute("INSERT INTO body_transaction_probe VALUES ('must roll back')")
            raise busy_error()
    assert error.value.retryable is True
    assert entered == ["one body"]
    with budget.transaction() as c:
        assert (
            c.execute(
                "SELECT count(*) FROM sqlite_master WHERE name='body_transaction_probe'"
            ).fetchone()[0]
            == 0
        )
