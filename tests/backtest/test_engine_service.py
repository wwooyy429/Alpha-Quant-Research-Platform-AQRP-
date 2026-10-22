"""Production queue, serialized outputs, fixed inputs and fail-closed boundaries."""

import json
import subprocess
import sys
import uuid
from copy import deepcopy
from datetime import timedelta

import pytest

from aqrp.backtest.contracts import EngineeringBacktestRequest, validate
from aqrp.backtest.engine import Simulator
from aqrp.backtest.exact import F
from aqrp.backtest.ledger import account
from aqrp.backtest.provider import SignalProvider
from aqrp.backtest.synthetic import fixture_request, seal_sidecar
from aqrp.backtest.transactions import TransactionStore
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.portfolio.contracts import load
from aqrp.services.backtest import (
    audit_bytes,
    replay_engineering,
    result_engineering,
    simulate_approved,
    simulate_engineering,
)
from aqrp.services.backtest_cli import main as cli


def data():
    return load(fixture_request().raw)


def reseal_portfolio(x, index=0):
    p = load(x["decisions"][index]["portfolio_request_utf8"])
    return p


def put_portfolio(x, p, index=0):
    entries = [v for k, v in p["inputs"].items() if k != "scores"] + p["inputs"]["scores"]
    for e in entries:
        e["content_sha256"] = digest({k: v for k, v in e.items() if k != "content_sha256"})
    p["source"]["fixture_manifest"] = {e["ref"]: e["content_sha256"] for e in entries}
    x["decisions"][index]["portfolio_request_utf8"] = canonical(p).decode()
    return x


def run(x, path):
    return simulate_engineering(seal_sidecar(x), path, "a" * 40).read()


def test_full_simulation_literal_answer_and_actual_numerical_replay(tmp_path):
    r = run(data(), tmp_path / "runs")
    assert r["status"] == "SUCCEEDED", r
    assert r["account"]["cash_total"] == "98.1" and r["account"]["equity"] == "998.1"
    assert r["positions"]["SYNTH:0"]["quantity"] == "9"
    assert len(r["fills"]) == 1 and r["fills"][0]["fee"] == "1"
    assert list(r["orders"].values())[0]["status"] == "FILLED"
    assert r["financial_approval"] == "NONE" and not r["executable"]
    assert (
        replay_engineering(tmp_path / "runs", r["run_id"], tmp_path / "replay")["status"]
        == "NUMERICAL_REPLAY_VERIFIED"
    )
    assert result_engineering(tmp_path / "runs", r["run_id"])["state_sha256"] == r["state_sha256"]
    m = ExperimentLedger(tmp_path / "runs").verify(r["run_id"])
    assert {
        "state.json",
        "transactions.json",
        "trace.json",
        "transaction-files.json",
        "published-byte-audit.json",
    } <= {e["path"] for e in m["files"]}


@pytest.mark.parametrize("mode", ["LATE", "GAP", "SUSPENDED", "NO_CAPACITY_LOT", "BUDGET"])
def test_no_fill_and_no_fee_for_invalid_or_ineligible_execution(tmp_path, mode):
    x = data()
    if mode == "BUDGET":
        x["fee_budget"] = "2"
    elif mode == "NO_CAPACITY_LOT":
        for a in x["assets"]:
            a["lot"] = "12"
        p = reseal_portfolio(x)
        for row in p["inputs"]["prices"]["data"]:
            row["lot"] = "12"
        # Enough capital to create one whole lot, but slice capacity is ten shares.
        x["initial_cash"] = "2000"
        x["fee_budget"] = "20"
        put_portfolio(x, p)
    else:
        for row in x["sidecar"]["rows"]:
            if row["session_id"] == x["sessions"][1]["session_id"] and row["kind"] == "OPEN":
                if mode == "LATE":
                    row["available_at"] = (
                        utc(row["event_time"]) + timedelta(microseconds=1)
                    ).isoformat()
                elif mode == "GAP":
                    row["price"] = "200400.41"
                else:
                    row["tradable"] = False
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    assert r["fills"] == [] and r["performance"]["commission"] == "0"
    assert all(o["status"] in ("EXPIRED", "REJECTED") for o in r["orders"].values())


@pytest.mark.parametrize("kind,side", [("LIMIT", "BUY"), ("MARKET", "SELL"), ("LIMIT", "SELL")])
def test_order_types_long_short_and_frozen_sell_gap(tmp_path, kind, side):
    x = data()
    if side == "SELL":
        p = reseal_portfolio(x)
        p["policy"].update(mode="LONG_SHORT", gross="0.4", net="0")
        put_portfolio(x, p)
    if kind == "LIMIT":
        x["decisions"][0].update(
            order_type="LIMIT",
            limit_prices={
                a["security_id"]: "99"
                if side == "SELL" and a["security_id"] == "SYNTH:1"
                else "101"
                for a in x["assets"]
            },
        )
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    if side == "BUY":
        assert r["fills"] and all(F(f["price"]) <= 101 for f in r["fills"])
    else:
        assert any(F(f["signed_qty"]) < 0 for f in r["fills"])
        assert r["account"]["U_short"] == "0"  # Full T+1 lifecycle ran.


def test_signal_at_open_is_not_executable_at_same_open(tmp_path):
    x = data()
    p = reseal_portfolio(x)
    t = x["sessions"][1]["open"]
    p["context"]["decision_time"] = t
    p["context"]["session_index"] = 1
    for name, e in p["inputs"].items():
        for item in e if name == "scores" else [e]:
            item["context"] = p["context"]
            item.update(event_time=t, available_at=t, as_of=t)
            if name == "account":
                item["data"]["valuation_time"] = t
            else:
                for row in item["data"]["rows"] if name == "scores" else item["data"]:
                    row.update(event_time=t, available_at=t, as_of=t)
                    if name == "scores":
                        row.update(signal_time=t, session_index=1)
    put_portfolio(x, p)
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    assert r["fills"][0]["at"] == "2024-02-03T09:00:00.000000+00:00"


def test_gtc_waits_for_next_visible_slice_day_does_not(tmp_path):
    x = data()
    x["decisions"][0]["time_in_force"] = "GTC"
    for r in x["sidecar"]["rows"]:
        if r["session_id"] == x["sessions"][1]["session_id"] and r["kind"] == "OPEN":
            r["available_at"] = (utc(r["event_time"]) + timedelta(microseconds=1)).isoformat()
    result = run(x, tmp_path)
    assert result["status"] == "SUCCEEDED", result
    assert result["fills"][0]["at"].startswith("2024-02-03T09:00")


@pytest.mark.parametrize("phase,expected_fills", [(60, 0), (70, 1)])
def test_cancel_before_and_during_match_obeys_ack_clock(tmp_path, phase, expected_fills):
    x = data()
    oid = str(uuid.uuid5(uuid.UUID(x["request_id"]), "order:0:SYNTH:0"))
    t = x["sessions"][1]["open"]
    x["cancellations"] = [
        {
            "control_id": str(uuid.uuid4()),
            "order_id": oid,
            "requested_at": t,
            "available_at": t,
            "received_at": t,
            "received_phase": phase,
        }
    ]
    r = run(x, tmp_path)
    assert r["status"] == "SUCCEEDED", r
    assert len(r["fills"]) == expected_fills
    trace = json.loads((tmp_path / r["run_id"] / "trace.json").read_bytes())
    c = [t for t in trace if t["kind"] == "CANCELLATION"][0]
    assert c["dispatch_key"][0].endswith("000001+00:00") == (phase == 70)


def test_stale_cancellation_fails_and_retains_actual_commits(tmp_path):
    x = data()
    t = x["sessions"][1]["open"]
    x["cancellations"] = [
        {
            "control_id": str(uuid.uuid4()),
            "order_id": str(uuid.uuid4()),
            "requested_at": x["sessions"][0]["close"],
            "available_at": x["sessions"][0]["close"],
            "received_at": t,
            "received_phase": 60,
        }
    ]
    r = run(x, tmp_path)
    assert r["status"] == "FAILED" and r["reasons"] == ["STALE_CANCELLATION_TIME"]
    assert "performance" not in r and "last_committed_account" in r
    with pytest.raises(ContractError, match="FAILED_SIMULATION_NOT_REPLAYABLE"):
        replay_engineering(tmp_path, r["run_id"], tmp_path / "replay")


@pytest.mark.parametrize("kind", ["SPLIT", "DIVIDEND", "LATE_ACTION", "FRACTIONAL_SPLIT"])
def test_actual_action_queue_and_failure_evidence(tmp_path, kind):
    x = data()
    t = x["sessions"][2]["open"]
    x["actions"] = [
        {
            "action_id": str(uuid.uuid4()),
            "kind": "DIVIDEND" if kind == "DIVIDEND" else "SPLIT",
            "security_id": "SYNTH:0",
            "effective_at": t,
            "available_at": x["sessions"][2]["close"] if kind == "LATE_ACTION" else t,
            "value": "0.5" if kind == "FRACTIONAL_SPLIT" else "1" if kind == "DIVIDEND" else "2",
            "unit": "PER_OLD_SHARE" if kind == "DIVIDEND" else "RATIO",
            "pay_at": x["sessions"][3]["open"] if kind == "DIVIDEND" else None,
        }
    ]
    if kind == "SPLIT":
        for row in x["sidecar"]["rows"]:
            if (
                row["security_id"] == "SYNTH:0"
                and row["session_id"] >= x["sessions"][2]["session_id"]
            ):
                row["price"] = "50"
    r = run(x, tmp_path)
    if kind in ("LATE_ACTION", "FRACTIONAL_SPLIT"):
        assert r["status"] == "FAILED"
        assert r["reasons"] == [
            "DATA_REVISION_REQUIRES_RERUN"
            if kind == "LATE_ACTION"
            else "UNDEFINED_FRACTIONAL_SPLIT"
        ]
    else:
        assert r["status"] == "SUCCEEDED", r
        assert r["positions"]["SYNTH:0"]["quantity"] == ("18" if kind == "SPLIT" else "9")
        assert r["account"]["cash_total"] == ("98.1" if kind == "SPLIT" else "107.1")
        assert r["account"]["receivable"] == "0"


def test_future_slices_cannot_change_committed_prefix(tmp_path):
    x = data()
    a = run(x, tmp_path / "a")
    for row in x["sidecar"]["rows"]:
        if row["session_id"] == x["sessions"][-1]["session_id"]:
            row["price"] = "103"
    b = run(x, tmp_path / "b")
    assert a["status"] == b["status"] == "SUCCEEDED"
    assert a["fills"] == b["fills"]
    assert a["valuations"][:-1] == b["valuations"][:-1]
    assert a["account"]["equity"] != b["account"]["equity"]


@pytest.mark.parametrize(
    "key,value",
    [
        ("schema_version", "future"),
        ("scope", "FORMAL"),
        ("financial_approval", "YES"),
        ("calendar_id", "NYSE"),
        ("request_id", "bad"),
        ("initial_cash", "0"),
        ("fee_budget", "-1"),
    ],
)
def test_strict_request_domains_fail_without_engine(key, value, tmp_path):
    x = data()
    x[key] = value
    r = run(x, tmp_path)
    assert r["status"] == "FAILED" and "fills" not in r


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown",
        "duplicate_asset",
        "duplicate_session",
        "session_order",
        "sidecar_hash",
        "row_uuid",
        "duplicate_slice",
        "slice_clock",
        "bad_price",
        "future_known",
        "duplicate_decision",
        "parent_uuid",
        "future_score",
        "factor_mutation",
    ],
)
def test_identity_and_pit_mutations_are_rejected(mutation):
    x = data()
    if mutation == "unknown":
        x["skip_approval"] = True
    elif mutation == "duplicate_asset":
        x["assets"].append(deepcopy(x["assets"][0]))
    elif mutation == "duplicate_session":
        x["sessions"].append(deepcopy(x["sessions"][0]))
    elif mutation == "session_order":
        x["sessions"][0]["close"] = x["sessions"][0]["open"]
    elif mutation == "row_uuid":
        x["sidecar"]["rows"][0]["slice_id"] = "bad"
    elif mutation == "duplicate_slice":
        x["sidecar"]["rows"].append(deepcopy(x["sidecar"]["rows"][0]))
    elif mutation == "slice_clock":
        x["sidecar"]["rows"][0]["event_time"] = x["sessions"][1]["open"]
    elif mutation == "bad_price":
        x["sidecar"]["rows"][0]["price"] = "0"
    elif mutation == "future_known":
        x["sidecar"]["rows"][0]["known_at"] = x["sessions"][1]["open"]
    elif mutation == "duplicate_decision":
        x["decisions"].append(deepcopy(x["decisions"][0]))
    elif mutation == "parent_uuid":
        x["sidecar"]["snapshot_id"] = str(uuid.uuid4())
    elif mutation == "future_score":
        p = reseal_portfolio(x)
        p["inputs"]["scores"][0]["data"]["rows"][0]["available_at"] = x["sessions"][1]["open"]
        put_portfolio(x, p)
    elif mutation == "factor_mutation":
        p = reseal_portfolio(x)
        p["inputs"]["scores"][0]["data"]["factor_ref"]["implementation_hash"] = "bad"
        put_portfolio(x, p)
    if mutation == "sidecar_hash":
        request = EngineeringBacktestRequest.create(x)
        raw = load(request.raw)
        raw["sidecar"]["content_sha256"] = "0" * 64
        request = EngineeringBacktestRequest.create(raw)
    else:
        request = seal_sidecar(x)
    with pytest.raises(ContractError):
        validate(request)


def test_formal_entry_is_only_rejection_and_cannot_release_signals(tmp_path, monkeypatch):
    monkeypatch.setattr(
        SignalProvider, "release", lambda *_: pytest.fail("formal gate ran a provider")
    )
    r = simulate_approved(fixture_request(), tmp_path, "a" * 40).read()
    assert r["reasons"] == ["APPROVAL_REQUIRED"] and r["scope"] == "FORMAL_APPROVAL_GATE"
    assert not (tmp_path / r["run_id"] / "transactions").exists()


def test_p4_return_tamper_and_published_output_mutation_fail_closed(tmp_path, monkeypatch):
    import aqrp.backtest.engine as engine
    from aqrp.portfolio.contracts import PortfolioResult

    original = engine.construct_engineering

    def tampered(*args):
        r = original(*args).read()
        r["target"]["quantities"]["SYNTH:0"] = "999"
        return PortfolioResult(canonical(r))

    monkeypatch.setattr(engine, "construct_engineering", tampered)
    r = run(data(), tmp_path)
    assert r["status"] == "FAILED" and r["reasons"] == ["P4_RETURN_TERMINAL_BINDING_MISMATCH"]


def test_simulation_persisted_cash_mutation_preserves_failure(tmp_path, monkeypatch):
    original = ExperimentLedger.artifact

    def corrupted(self, run_id, name, payload):
        if name == "result.json" and payload.get("schema_version") == "simulation-result/1.0.0":
            payload = deepcopy(payload)
            payload["account"]["cash_set"] = "99.1"
        return original(self, run_id, name, payload)

    monkeypatch.setattr(ExperimentLedger, "artifact", corrupted)
    with pytest.raises(ContractError, match="SIMULATION_PUBLISHED_BYTES_CHANGED"):
        run(data(), tmp_path)
    run_id = next(p.name for p in tmp_path.iterdir() if p.is_dir())
    assert ExperimentLedger(tmp_path).verify(run_id)["status"] == "FAILED"
    with pytest.raises(ContractError, match="PUBLICATION_FAILED_NOT_REPLAYABLE"):
        result_engineering(tmp_path, run_id)
    with pytest.raises(ContractError):
        audit_bytes(b"{}", {"expected": "not empty"})


def test_post_terminal_added_result_cannot_acquire_evidence_role(tmp_path):
    ledger = ExperimentLedger(tmp_path)
    run_id = ledger.start(
        {},
        {
            "code_commit": "a" * 40,
            "code_bundle": "x",
            "data_hash": "x",
            "environment": {},
            "protocol_hash": "x",
            "permission_domain": "ENGINEERING_TEST_ONLY",
            "seed": 0,
        },
    )
    ledger.finish(run_id, "SUCCEEDED")
    (ledger.path(run_id) / "result.json").write_bytes(canonical({"status": "SUCCEEDED"}))
    with pytest.raises(ContractError, match="SIMULATION_ARTIFACT_NOT_TERMINAL_MANIFESTED"):
        result_engineering(tmp_path, run_id)


def test_sdk_cli_same_services_and_required_arguments(tmp_path, capsys):
    path = tmp_path / "request.json"
    path.write_bytes(fixture_request().raw)
    root = tmp_path / "runs"
    assert cli(["simulate", "--root", str(root), "--request", str(path), "--commit", "a" * 40]) == 0
    r = json.loads(capsys.readouterr().out)
    assert cli(["status", "--root", str(root), "--run-id", r["run_id"]]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "SUCCEEDED"
    assert cli(["result", "--root", str(root), "--run-id", r["run_id"]]) == 0
    assert json.loads(capsys.readouterr().out)["state_sha256"] == r["state_sha256"]
    assert (
        cli(
            [
                "replay",
                "--root",
                str(root),
                "--run-id",
                r["run_id"],
                "--destination",
                str(tmp_path / "replay"),
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["status"] == "NUMERICAL_REPLAY_VERIFIED"
    for op in ("simulate", "replay", "result"):
        with pytest.raises(SystemExit):
            cli([op, "--root", str(root)])


@pytest.mark.parametrize("stage", ["BEFORE_COMMIT", "AFTER_COMMIT"])
def test_actual_process_crash_and_deterministic_prefix_recovery(tmp_path, stage):
    request = tmp_path / "request.json"
    request.write_bytes(fixture_request().raw)
    root = tmp_path / "engine"
    script = tmp_path / "crash.py"
    script.write_text(
        """import os,sys,json
from pathlib import Path
from aqrp.backtest.contracts import EngineeringBacktestRequest,validate
from aqrp.backtest.engine import Simulator
root=Path(sys.argv[1]);request=EngineeringBacktestRequest(Path(sys.argv[2]).read_bytes())
def fault(stage):
    if stage != sys.argv[3]: return
    paths=list((root/'transactions').glob('prepared-*.json')) if stage=='BEFORE_COMMIT' else list((root/'transactions').glob('commit-*.json'))
    if paths:
        item=json.loads(max(paths,key=lambda p:p.stat().st_mtime_ns).read_bytes())
        if any(v['kind']=='Fill' for v in item['children']): os._exit(63)
Simulator(validate(request),root,'a'*40,fault=fault).run()
""",
        encoding="utf-8",
    )
    p = subprocess.run(
        [sys.executable, str(script), str(root), str(request), stage], capture_output=True
    )
    assert p.returncode == 63, p.stderr.decode(errors="replace")
    recovered = TransactionStore(root / "transactions")
    assert len(recovered.state["fills"]) == (0 if stage == "BEFORE_COMMIT" else 1)
    resumed = Simulator(validate(fixture_request()), root, "a" * 40)
    state = resumed.run()
    assert len(state["fills"]) == 1 and state["fees"] == 1
    assert account(state)["cash_total"] == F("98.1")
    pristine = Simulator(validate(fixture_request()), tmp_path / "pristine", "a" * 40)
    assert pristine.run() == state
    assert all(v["commit_seq"] == i + 1 for i, v in enumerate(resumed.store.records))
