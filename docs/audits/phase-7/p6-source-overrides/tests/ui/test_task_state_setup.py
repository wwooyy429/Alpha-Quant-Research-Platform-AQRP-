"""Real rollback-journal contention and fail-closed transaction admission."""

import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from types import SimpleNamespace

import pytest

from aqrp.core.errors import ContractError
from aqrp.services import task_state
from aqrp.services.task_state import TaskState


def held_reader(root):
    db = root / "task-control" / "tasks.sqlite"
    db.parent.mkdir(parents=True)
    c = sqlite3.connect(db, timeout=0, isolation_level=None)
    c.execute("CREATE TABLE sentinel (value INTEGER)")
    c.execute("INSERT INTO sentinel VALUES (17)")
    c.execute("BEGIN")
    assert c.execute("SELECT value FROM sentinel").fetchone() == (17,)
    return c, db


def test_real_reader_blocks_wal_then_released_setup_succeeds_once(tmp_path, monkeypatch):
    holder, db = held_reader(tmp_path)
    connect = sqlite3.connect
    busy = threading.Event()
    observed = []

    class Observed(sqlite3.Connection):
        closed = False

        def execute(self, sql, *a):
            try:
                return super().execute(sql, *a)
            except sqlite3.OperationalError as e:
                if sql == "PRAGMA journal_mode=WAL":
                    assert e.sqlite_errorcode & 0xFF in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)
                    busy.set()
                raise

        def close(self):
            self.closed = True
            super().close()

    def factory(*a, **k):
        # Model the immediate native BUSY already observed with timeout30 in
        # C5: SQLite may bypass its native handler. A zero handler timeout
        # deterministically produces that same native error for both versions.
        k["timeout"] = 0
        c = connect(*a, **k, factory=Observed)
        observed.append(c)
        return c

    monkeypatch.setattr(task_state.sqlite3, "connect", factory)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(TaskState, tmp_path)
        try:
            assert busy.wait(5), "No actual native WAL contention observed"
        finally:
            holder.rollback()
            holder.close()
        state = future.result(timeout=5)
    assert state.workspace_id and len(observed) == 1 and observed[0].closed
    with closing(connect(db)) as c:
        assert c.execute("SELECT value FROM sentinel").fetchone() == (17,)
        assert c.execute("SELECT count(*) FROM workspace").fetchone() == (1,)
        assert c.execute("PRAGMA journal_mode").fetchone() == ("wal",)
    with state.transaction() as c:
        assert c.execute("PRAGMA synchronous").fetchone()[0] == 2


def test_real_reader_exhausts_finite_setup_without_allocating_workspace(tmp_path, monkeypatch):
    holder, db = held_reader(tmp_path)
    monkeypatch.setattr(task_state, "SETUP_TIMEOUT_SECONDS", 0.025)
    try:
        with pytest.raises(sqlite3.OperationalError) as result:
            TaskState(tmp_path)
        assert result.value.sqlite_errorcode & 0xFF in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED)
    finally:
        holder.rollback()
        holder.close()
    with closing(sqlite3.connect(db)) as c:
        assert c.execute("SELECT value FROM sentinel").fetchone() == (17,)
        assert c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == [
            ("sentinel",)
        ]


@pytest.mark.parametrize("code", [None, sqlite3.SQLITE_IOERR])
def test_unrelated_setup_error_propagates_once_and_closes(tmp_path, monkeypatch, code):
    connect = sqlite3.connect
    calls, observed = [], []
    original = sqlite3.OperationalError("controlled I/O failure")
    if code is not None:
        original.sqlite_errorcode = code

    class Observed(sqlite3.Connection):
        closed = False

        def execute(self, sql, *a):
            calls.append(sql)
            raise original

        def close(self):
            self.closed = True
            super().close()

    def factory(*a, **k):
        c = connect(*a, **k, factory=Observed)
        observed.append(c)
        return c

    monkeypatch.setattr(task_state.sqlite3, "connect", factory)
    with pytest.raises(sqlite3.OperationalError) as result:
        TaskState(tmp_path)
    assert result.value is original and calls == ["PRAGMA journal_mode=WAL"]
    assert len(observed) == 1 and observed[0].closed


@pytest.mark.parametrize("mode", [None, ("delete",)])
def test_wal_not_confirmed_never_admits_transaction(tmp_path, monkeypatch, mode):
    connect = sqlite3.connect
    calls, observed = [], []

    class Observed(sqlite3.Connection):
        closed = False

        def execute(self, sql, *a):
            calls.append(sql)
            return SimpleNamespace(fetchone=lambda: mode)

        def close(self):
            self.closed = True
            super().close()

    def factory(*a, **k):
        c = connect(*a, **k, factory=Observed)
        observed.append(c)
        return c

    monkeypatch.setattr(task_state.sqlite3, "connect", factory)
    with pytest.raises(ContractError, match="TASK_JOURNAL_MODE_UNVERIFIED"):
        TaskState(tmp_path)
    assert calls == ["PRAGMA journal_mode=WAL"] and observed[0].closed


def test_busy_in_body_rolls_back_without_replaying_body(tmp_path):
    state = TaskState(tmp_path)
    attempts = []
    error = sqlite3.OperationalError("controlled body contention")
    error.sqlite_errorcode = sqlite3.SQLITE_BUSY
    with pytest.raises(sqlite3.OperationalError) as result:
        with state.transaction() as c:
            attempts.append(1)
            c.execute("INSERT INTO defaults VALUES(1,'{}','not-a-real-hash')")
            raise error
    assert result.value is error and attempts == [1]
    with state.transaction() as c:
        assert c.execute("SELECT count(*) FROM defaults").fetchone()[0] == 0
