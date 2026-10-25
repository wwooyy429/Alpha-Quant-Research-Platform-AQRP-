"""Frozen P7 engineering protocol: ten non-browser actors, then actual UI cases.

The default SDK command deliberately reports BROWSER_PENDING. Only separately
captured real-browser evidence can complete the full protocol; AppTest is never
counted as browser evidence. No network provider, account or formal Test entry.
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from e2e_reference import canonical, compare_checked, file_manifest, known_answer, sha, verify_run
from streamlit.testing.v1 import AppTest

import aqrp
from aqrp.competition import adapt_engineering, adapter_spec, execute_engineering, input_reference
from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.experiments.admission import (
    BudgetAuthority,
    advance_actor,
    capture_activation,
    complete_actor,
    install_execution_plan,
    open_protocol_driver,
)
from aqrp.services.task_requests import EffectiveRequest, catalogue, initialize
from aqrp.services.tasks import TaskService

ORACLES = Path(__file__).resolve().parents[1] / "docs/audits/phase-7"
NAMES = ("momentum", "reversal")
SOURCE_SLOT = "sdk-main-momentum"


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
    if path.exists():
        assert path.read_bytes() == raw, "Immutable evidence changed: " + str(path)
    else:
        with path.open("xb") as handle:
            handle.write(raw)
    return path


def read(path):
    return json.loads(Path(path).read_bytes())


def counts(root):
    authority = BudgetAuthority(root)
    with authority.transaction() as connection:
        authority.verify(connection, require_projections=True)
        attempts = list(connection.execute("SELECT payload,decision FROM admissions"))
        claims = list(connection.execute("SELECT ledger_root,run_id FROM trial_claims"))
        executed = 0
        for claim in claims:
            directory = Path(claim["ledger_root"]) / claim["run_id"]
            if (directory / "manifest.json").is_file() and read(directory / "manifest.json")[
                "status"
            ] == "SUCCEEDED":
                verify_run(directory)
                executed += 1
        return {
            "requested_units": sum(len(json.loads(row["payload"])["units"]) for row in attempts),
            "rejected_attempts": sum(row["decision"] != "ADMITTED" for row in attempts),
            "registered_units": len(claims),
            "executed_units": executed,
            "executed_units_scope": "Original byte-verified SUCCEEDED P3 units; no inferred successful execution for failed or partial runs",
            "admitted_units": connection.execute(
                "SELECT coalesce(sum(debit),0) FROM admissions WHERE decision='ADMITTED'"
            ).fetchone()[0],
            "attempts": connection.execute("SELECT count(*) FROM admissions").fetchone()[0],
            "trials": connection.execute("SELECT count(*) FROM trial_claims").fetchone()[0],
        }


def identity(cat):
    runner = Path(__file__).resolve()
    return {
        "runner_path": str(runner),
        "runner_sha256": sha(runner.read_bytes()),
        "code_bundle": cat["code_bundle"],
        "code_commit": cat["code_commit"],
    }


def driver(root, metadata):
    return open_protocol_driver(root, metadata["plan_hash"], metadata["identity"])


def current_slot(root):
    activation = capture_activation(root)
    assert activation is not None, "No trusted actor activated"
    with BudgetAuthority(root).transaction() as connection:
        row = connection.execute(
            "SELECT payload,binding FROM execution_plan_slots WHERE slot=?",
            (activation["slot_id"],),
        ).fetchone()
        return activation, json.loads(row[0]), None if row[1] is None else json.loads(row[1])


def advance(root, metadata):
    existing = capture_activation(root)
    return advance_actor(
        driver(root, metadata), -1 if existing is None else existing["activation_seq"]
    )


def receipt_evidence(root, owner, legacy=False):
    if legacy:
        path = root / "research-runs" / owner / "manifest.json"
    else:
        path = root / "tasks" / owner / "request.json"
    return [{"path": str(path), "sha256": sha(path.read_bytes())}]


def finish(root, metadata, owner, status, legacy=False):
    return complete_actor(
        driver(root, metadata),
        {"owner_id": owner, "status": status, "evidence": receipt_evidence(root, owner, legacy)},
    )


def legacy_request(root, frozen):
    cat = catalogue(root)
    return {
        "config": json.loads(frozen.raw)["payload"]["research"],
        "snapshot": cat["snapshot"],
        "exposures": cat["exposures"],
        "coverage": json.loads(cat["coverage"]["payload"]),
        "code_commit": cat["code_commit"],
    }


def charged_slot(name, kind, request_hash, root):
    return {
        "slot_id": name,
        "service_kind": kind,
        "request_hash": request_hash,
        "output_root": str(root / "research-runs"),
        "requested_units": 1,
        "grant_capacity": 1,
        "max_admitted_owners": 1,
        "expected_status": "SUCCEEDED",
    }


def prepare(run, developer_fixture=False):
    output = Path(run).resolve() / "e2e"
    if (output / "PROTOCOL.json").exists():
        metadata = read(output / "PROTOCOL.json")
        assert metadata["developer_fixture"] is developer_fixture
        assert metadata["main"]["identity"]["runner_sha256"] == sha(Path(__file__).read_bytes())
        for item in metadata["oracles"]:
            assert sha((output / "oracles" / item["name"]).read_bytes()) == item["sha256"]
        return output, metadata
    output.mkdir()
    env = read(Path(run) / "environment.json")
    if not developer_fixture:
        assert env.get("dirty") is False, "Fixed clean SDK identity required"
    root = output / "workspace"
    negative = output / "original-risk-workspace"
    cat = initialize(root, env["code_commit"])
    negcat = initialize(negative, env["code_commit"])
    service = TaskService(root)
    # UI normally omits default direction1; freezing it as a trusted defaults
    # field makes all original actors submit identical effective bytes.
    service.save_defaults(0, {"direction": 1})
    candidate = read(ORACLES / "E2E_PROTOCOL_CANDIDATES.json")
    variants = {(v["protocol"], v["factor"]): v["draft"] for v in candidate["variants"]}
    service.register_campaign("p7-main-12", list(variants.values()))
    frozen = {}
    for key, draft in variants.items():
        draft = {**draft, "campaign_id": "p7-main-12"}
        value = service.freeze(draft)
        name = "-".join(key)
        frozen[key] = value
        save(output / "requests" / (name + "-draft.json"), draft)
        save(output / "requests" / (name + "-effective.json"), value.raw)
    actors = []
    # G1 allocation is unchanged; this execution order is frozen before any
    # result so CI can run ten actors without pretending browser completion.
    for entry in ("sdk", "task-cli", "apptest", "legacy-cli"):
        for factor in NAMES:
            name = entry + "-main-" + factor
            value = frozen[("main", factor)]
            old = entry == "legacy-cli"
            actors.append({"name": name, "entry": entry, "protocol": "main", "factor": factor})
            if old:
                save(output / "requests" / (name + ".json"), legacy_request(root, value))
    for factor in NAMES:
        actors.append(
            {
                "name": "sdk-transparent-" + factor,
                "entry": "sdk",
                "protocol": "transparent",
                "factor": factor,
            }
        )
    for factor in NAMES:
        actors.append(
            {
                "name": "browser-main-" + factor,
                "entry": "REAL_BROWSER",
                "protocol": "main",
                "factor": factor,
            }
        )
    slots = []
    for actor in actors:
        value = frozen[(actor["protocol"], actor["factor"])]
        h = (
            digest(json.loads(value.raw)["payload"]["research"])
            if actor["entry"] == "legacy-cli"
            else value.config_hash
        )
        slots.append(
            charged_slot(
                actor["name"], "LEGACY" if actor["entry"] == "legacy-cli" else "TASK", h, root
            )
        )
    template = json.loads(frozen[("main", "momentum")].raw)
    template.update(
        kind="replay", payload={"source_task": "$SOURCE_TASK", "profile": "P5_NUMERICAL"}
    )
    for name, expected in (
        ("browser-cancel-replay", "CANCELLED"),
        ("browser-normal-replay", "SUCCEEDED"),
    ):
        slots.append(
            {
                "slot_id": name,
                "service_kind": "TASK_REPLAY",
                "request_hash": None,
                "output_root": str(root / "replay-runs"),
                "requested_units": 0,
                "grant_capacity": 0,
                "max_admitted_owners": 1,
                "expected_status": expected,
                "source_slot": SOURCE_SLOT,
                "originalsource_request_hash": frozen[("main", "momentum")].config_hash,
                "profile": "P5_NUMERICAL",
                "request_template": template,
            }
        )
    main_plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "MAIN_SUCCESS",
        **identity(cat),
        "catalogue_hash": digest(cat),
        "data_hash": cat["snapshot"]["manifest_hash"],
        "slots": slots,
    }
    negative_draft = {
        "kind": "engineering_pipeline",
        "factor_ids": ["momentum"],
        "universe_id": "SYN_U",
        "campaign_id": "p7-original-risk-1",
        "start": "2024-01-06",
        "end": "2024-01-06",
        "lookback": 2,
        "horizons": [1],
        "neutralize": True,
        "weights_percent": {"momentum": "100"},
        "initial_cash": "1000",
        "fee_budget": "10",
        "policy": {"top_k": 1},
        "constraints": {"gross_max": "0"},
    }
    ns = TaskService(negative)
    ns.register_campaign(
        "p7-original-risk-1", [{k: v for k, v in negative_draft.items() if k != "campaign_id"}]
    )
    negative_request = ns.freeze(negative_draft)
    save(output / "requests/negative-risk-draft.json", negative_draft)
    save(output / "requests/negative-risk-effective.json", negative_request.raw)
    risk_slot = charged_slot(
        "browser-original-risk", "TASK", negative_request.config_hash, negative
    )
    risk_slot.update(expected_status="FAILED", expected_code="REQUIRED_STAGE_REJECTED")
    negative_plan = {
        "schema": "p7-execution-plan/1",
        "purpose": "ORIGINAL_P6_RISK_1",
        **identity(negcat),
        "catalogue_hash": digest(negcat),
        "data_hash": negcat["snapshot"]["manifest_hash"],
        "slots": [risk_slot],
    }
    # BOTH actual roots/data identities are frozen before actor1 is activated.
    metadata = {
        "schema": "p7-engineering-protocol/1",
        "created_at": datetime.now(UTC).isoformat(),
        "main": {
            "workspace": str(root),
            "identity": identity(cat),
            "plan_hash": install_execution_plan(root, main_plan, identity(cat)),
        },
        "risk": {
            "workspace": str(negative),
            "identity": identity(negcat),
            "plan_hash": install_execution_plan(negative, negative_plan, identity(negcat)),
        },
        "actors": actors,
        "allocation": {"MAIN": 12, "ORIGINAL_P6_RISK": 1, "REPLAY_RESEARCH": 0},
        "runtime_order": "ten nonbrowser, two realbrowser, queuedcancel andnormalreplay; no allocation changes",
        "sdk_environment": env,
        "developer_fixture": developer_fixture,
        "oracles": [],
        "scope": "ENGINEERING_TEST_ONLY",
        "formal_Test": "NOT RUN",
        "financial_approval": "NONE",
        "Windows_R2": "DEFERRED / NOT VERIFIED",
        "independent_G2": "PENDING",
    }
    for name in (
        "E2E_PROTOCOL_CANDIDATES.json",
        "MAIN_PIPELINE_CANDIDATES.json",
        "FINANCIAL_FEASIBILITY_CANDIDATES.json",
        "GOLDEN_CANDIDATES.json",
        "BROWSER_NEGATIVE_PROTOCOL.md",
    ):
        raw = (ORACLES / name).read_bytes()
        save(output / "oracles" / name, raw)
        metadata["oracles"].append({"name": name, "sha256": sha(raw), "bytes": len(raw)})
    save(
        output / "PREREGISTERED_INPUTS.json",
        {
            "main": input_reference(root),
            "risk": input_reference(negative),
            "same_recipe_not_claimed_independent_samples": True,
            "source_member_equality": {
                n: input_reference(root)["tables"][n]["sha256"]
                == input_reference(negative)["tables"][n]["sha256"]
                for n in input_reference(root)["tables"]
            },
        },
    )
    save(output / "PROTOCOL.json", metadata)
    return output, metadata


def command(output, name, arguments, cwd):
    started = datetime.now(UTC).isoformat()
    proc = subprocess.run([sys.executable, *arguments], cwd=cwd, capture_output=True)
    save(output / "commands" / (name + ".stdout.log"), proc.stdout)
    save(output / "commands" / (name + ".stderr.log"), proc.stderr)
    save(
        output / "commands" / (name + ".json"),
        {
            "argv": [sys.executable, *arguments],
            "cwd": str(cwd),
            "started_at": started,
            "ended_at": datetime.now(UTC).isoformat(),
            "exit_code": proc.returncode,
            "python": sys.executable,
        },
    )
    assert proc.returncode == 0, (name, proc.stdout[-1000:], proc.stderr[-1000:])
    return json.loads(proc.stdout)


def component(root, draft):
    os.environ["AQRP_WORKSPACE"] = str(root)
    app = AppTest.from_file(
        str(Path(aqrp.__file__).parent / "ui/app.py"), default_timeout=120
    ).run()
    app.sidebar.radio[0].set_value("Strategy Backtest").run()
    app.multiselect[0].set_value(draft["factor_ids"])
    fields = {v.label: v for v in app.text_input}
    for label, key in (
        ("First decision session (YYYY-MM-DD)", "start"),
        ("Last decision session (YYYY-MM-DD)", "end"),
        ("Initial cash (exact decimal)", "initial_cash"),
        ("Fee budget (exact decimal)", "fee_budget"),
    ):
        fields[label].set_value(draft[key])
    fields["Prediction horizons (session counts)"].set_value(",".join(map(str, draft["horizons"])))
    fields["Execution sessions (optional comma-separated YYYY-MM-DD)"].set_value(
        ",".join(draft.get("execution_sessions", []))
    )
    for label, value in (
        ("Stock universe", draft["universe_id"]),
        ("Preregistered research campaign", draft["campaign_id"]),
    ):
        next(v for v in app.selectbox if v.label == label).set_value(value)
    next(v for v in app.checkbox if v.label == "Industry / size neutralization").set_value(
        draft["neutralize"]
    )
    for prefix, key in (
        ("Factor weights", "weights_percent"),
        ("Portfolio policy", "policy"),
        ("Risk overrides", "constraints"),
    ):
        next(v for v in app.text_area if v.label.startswith(prefix)).set_value(
            json.dumps(draft[key])
        )
    next(v for v in app.button if v.label == "Submit engineering pipeline").click().run()
    assert not app.exception and not app.error, (
        [x.value for x in app.exception],
        [x.value for x in app.error],
    )
    task = app.session_state["engineering_pipelinetask"]
    service = TaskService(root)
    deadline = time.monotonic() + 600
    while service.state.get(task)["status"] not in {"SUCCEEDED", "FAILED", "CANCELLED"}:
        assert time.monotonic() < deadline, task
        time.sleep(0.2)
    app.run()
    assert not app.exception
    return service.status(task)


def record_task(output, metadata, actor, row):
    root = Path(metadata["main"]["workspace"])
    service = TaskService(root)
    assert row["status"] == "SUCCEEDED", row
    request = service.request(row["task_id"])
    expected = read(
        output / "requests" / (actor["protocol"] + "-" + actor["factor"] + "-effective.json")
    )
    assert request == expected
    result = row["result"]
    checked = known_answer(
        root / "research-runs",
        result["research_run_id"],
        root / "backtest-runs",
        result["backtest_run_id"],
        actor["factor"],
        actor["protocol"],
        output / "oracles",
    )
    expected_p = 10 if actor["protocol"] == "main" else 1
    assert set(row["slots"]) == {"R", "B", *["P:" + str(i) for i in range(expected_p)]}
    assert all(s["state"] == "VERIFIED_SUCCESS" for s in row["slots"].values())
    record = {
        "actor": actor,
        "task": row,
        "known_answer_checks": checked["checks"],
        "counts": counts(root),
    }
    save(output / "actors" / (actor["name"] + ".json"), record)
    save(output / "projections" / (actor["name"] + ".json"), checked["projection"])
    if actor["protocol"] == "main" and actor["name"] != "sdk-main-" + actor["factor"]:
        baseline = read(output / "projections" / ("sdk-main-" + actor["factor"] + ".json"))
        save(
            output / "comparisons" / (actor["name"] + ".json"),
            compare_checked(baseline, checked["projection"]),
        )
    finish(root, metadata["main"], row["task_id"], row["status"])
    return record


def run_nonbrowser(output, metadata, next_only=False):
    root = Path(metadata["main"]["workspace"])
    existing = [
        a for a in metadata["actors"][:10] if (output / "actors" / (a["name"] + ".json")).exists()
    ]
    assert existing == metadata["actors"][: len(existing)], "Only a verified prefix may resume"
    remaining = metadata["actors"][len(existing) : 10]
    for actor in remaining[:1] if next_only else remaining:
        name = actor["name"]
        assert not (output / "actors" / (name + ".json")).exists(), "Do not retry completed actors"
        activation = advance(root, metadata["main"])
        assert activation["slot_id"] == name
        before = counts(root)
        service = TaskService(root)
        frozen = EffectiveRequest(
            (
                output
                / "requests"
                / (actor["protocol"] + "-" + actor["factor"] + "-effective.json")
            ).read_bytes()
        )
        draft = read(
            output / "requests" / (actor["protocol"] + "-" + actor["factor"] + "-draft.json")
        )
        if actor["entry"] == "sdk":
            spec = adapter_spec(root)
            mapped = adapt_engineering(
                root, spec, input_reference(root), draft, json.loads(spec.raw)["rules"]
            )
            assert json.loads(mapped.raw)["task_request_utf8"].encode() == frozen.raw
            save(output / "adapter-receipts" / (name + ".json"), mapped.raw)
            row = execute_engineering(root, mapped, name)
        elif actor["entry"] == "task-cli":
            row = command(
                output,
                name,
                [
                    "-m",
                    "aqrp.services.task_cli",
                    "submit",
                    "--workspace",
                    str(root),
                    "--request",
                    str(
                        output
                        / "requests"
                        / (actor["protocol"] + "-" + actor["factor"] + "-effective.json")
                    ),
                    "--key",
                    name,
                    "--wait",
                ],
                root,
            )
        elif actor["entry"] == "apptest":
            row = component(root, draft)
        else:
            old_r = command(
                output,
                name + "-research",
                [
                    "-m",
                    "aqrp.services.cli",
                    str(output / "requests" / (name + ".json")),
                    "--output",
                    str(root / "research-runs"),
                ],
                root,
            )
            assert old_r["status"] == "SUCCEEDED"
            request = service._pipeline_request(json.loads(frozen.raw), {"run_id": old_r["run_id"]})
            path = save(output / "requests" / (name + "-P5.json"), request.raw)
            b_root = root / "legacy-backtest-runs" / name
            old_b = command(
                output,
                name + "-backtest",
                [
                    "-c",
                    "from aqrp.services.backtest_cli import main; raise SystemExit(main())",
                    "simulate",
                    "--root",
                    str(b_root),
                    "--request",
                    str(path),
                    "--commit",
                    metadata["main"]["identity"]["code_commit"],
                ],
                root,
            )
            assert old_b["status"] == "SUCCEEDED"
            checked = known_answer(
                root / "research-runs",
                old_r["run_id"],
                b_root,
                old_b["run_id"],
                actor["factor"],
                "main",
                output / "oracles",
            )
            baseline = read(output / "projections" / ("sdk-main-" + actor["factor"] + ".json"))
            save(
                output / "comparisons" / (name + ".json"),
                compare_checked(baseline, checked["projection"]),
            )
            save(output / "projections" / (name + ".json"), checked["projection"])
            save(
                output / "actors" / (name + ".json"),
                {
                    "actor": actor,
                    "research": old_r,
                    "backtest": {
                        "run_id": old_b["run_id"],
                        "status": old_b["status"],
                        "root": str(b_root),
                    },
                    "known_answer_checks": checked["checks"],
                    "counts": counts(root),
                },
            )
            finish(root, metadata["main"], old_r["run_id"], "SUCCEEDED", True)
            assert counts(root)["admitted_units"] == before["admitted_units"] + 1
            continue
        record_task(output, metadata, actor, row)
        assert counts(root)["admitted_units"] == before["admitted_units"] + 1
    if next_only and len(existing) < 9:
        return {
            "status": "ACTOR_COMPLETE_PROTOCOL_INCOMPLETE",
            "main": counts(root),
            "developer_fixture": metadata["developer_fixture"],
        }
    assert counts(root)["admitted_units"] == counts(root)["trials"] == 10
    summary = {
        "status": "NONBROWSER_COMPLETE_BROWSER_PENDING",
        "actual_nonbrowser_research_actors": 10,
        "actual_browser_actors": 0,
        "main": counts(root),
        "risk": counts(Path(metadata["risk"]["workspace"])),
        "P7_integration": "INCOMPLETE",
        "independent_G2": "PENDING",
        "scope": "ENGINEERING_TEST_ONLY",
        "formal_Test": "NOT RUN",
        "financial_approval": "NONE",
        "Windows_R2": "DEFERRED / NOT VERIFIED",
    }
    save(output / "NONBROWSER_RESULT.json", summary)
    return summary


def browser_evidence(path, slot, task, root):
    body = read(path)
    assert body["type"] == "REAL_BROWSER" and body["slot_id"] == slot and body["task_id"] == task
    assert body["url"].startswith(("http://127.0.0.1:", "http://localhost:"))
    kinds = set()
    for item in body["files"]:
        p = Path(item["path"]).resolve()
        raw = p.read_bytes()
        assert len(raw) == item["bytes"] and sha(raw) == item["sha256"]
        kinds.add(item["kind"])
        if item["kind"] == "SCREENSHOT":
            assert raw.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff"))
        if item["kind"] == "DOWNLOAD":
            assert TaskService(root).artifact(task, item["slot"], item["name"]) == raw
    assert {"AX", "SCREENSHOT", "OPERATIONS"} <= kinds
    if slot != "browser-cancel-replay":
        assert "DOWNLOAD" in kinds
    if slot == "browser-original-risk":
        assert {("P:0", "risk.json"), ("P:0", "result.json"), ("B", "result.json")} <= {
            (i.get("slot"), i.get("name")) for i in body["files"] if i["kind"] == "DOWNLOAD"
        }
    return body


def source_files(output, metadata):
    record = read(output / "actors" / (SOURCE_SLOT + ".json"))["task"]
    root = Path(metadata["main"]["workspace"])
    result = {}
    for kind, folder in (("research", "research-runs"), ("backtest", "backtest-runs")):
        run = record["result"][kind + "_run_id"]
        result[kind] = file_manifest(root / folder / run)
    return result


def enqueue_cancel(output, metadata):
    root = Path(metadata["main"]["workspace"])
    act = advance(root, metadata["main"])
    assert act["slot_id"] == "browser-cancel-replay"
    before = {"counts": counts(root), "source_files": source_files(output, metadata)}
    source = read(output / "actors" / (SOURCE_SLOT + ".json"))["task"]["task_id"]
    service = TaskService(root)
    receipt = service.submit(
        service.freeze({"kind": "replay", "source_task": source}), "p7-browser-cancel-replay-01"
    )
    assert receipt["status"] == "QUEUED" and receipt["slots"] == {}
    assert counts(root) == {**before["counts"], "attempts": before["counts"]["attempts"] + 1}
    save(output / "browser-cancel-before.json", before)
    save(output / "browser-cancel-queued.json", receipt)
    return receipt


def complete_browser(output, metadata, which, evidence_path):
    root = Path(metadata[which]["workspace"])
    activation, slot, binding = current_slot(root)
    assert binding is not None
    task = binding["owner_id"]
    evidence = browser_evidence(evidence_path, slot["slot_id"], task, root)
    row = TaskService(root).status(task)
    assert row["status"] == slot["expected_status"], row
    save(output / "browser-evidence" / (slot["slot_id"] + ".json"), evidence)
    if slot["slot_id"].startswith("browser-main-"):
        actor = next(a for a in metadata["actors"] if a["name"] == slot["slot_id"])
        return record_task(output, metadata, actor, row)
    if slot["slot_id"] == "browser-original-risk":
        assert row["error"] == "REQUIRED_STAGE_REJECTED"
        assert row["slots"]["R"]["state"] == row["slots"]["B"]["state"] == "VERIFIED_SUCCESS"
        assert row["slots"]["P:0"]["state"] == "VERIFIED_FAILURE"
        service = TaskService(root)
        b = json.loads(service.artifact(task, "B", "result.json"))
        p = json.loads(service.artifact(task, "P:0", "result.json"))
        assert b["fills"] == [] and b["account"]["cash_total"] == b["account"]["equity"] == "1000"
        assert all(x["quantity"] == "0" for x in b["positions"].values())
        assert p["status"] == "REJECTED" and p["risk"]["passed"] is False
        assert counts(root)["admitted_units"] == counts(root)["trials"] == 1
    elif slot["slot_id"] == "browser-cancel-replay":
        assert row["cancel_requested"] and row["slots"] == {}
        before = read(output / "browser-cancel-before.json")
        service = TaskService(root)
        assert service.work(task)["status"] == "CANCELLED"
        from aqrp.services.task_worker import start_worker

        assert start_worker(service, task)["status"] == "ALREADY_SUBMITTED"
        source = read(output / "actors" / (SOURCE_SLOT + ".json"))["task"]["task_id"]
        repeated = service.submit(
            service.freeze({"kind": "replay", "source_task": source}), "p7-browser-cancel-replay-01"
        )
        assert repeated["task_id"] == task and repeated["slots"] == {}
        alternate = read(output / "actors/sdk-main-reversal.json")["task"]["task_id"]
        changed = service.freeze({"kind": "replay", "source_task": alternate})
        unchanged_counts = counts(root)
        try:
            service.submit(changed, "p7-browser-cancel-replay-01")
        except ContractError as exc:
            assert exc.code == "ADMISSION_IDEMPOTENCY_CONFLICT"
            save(
                output / "controls/cancel-replay-different-request.json",
                {
                    "rejected": exc.code,
                    "different_request_sha256": changed.config_hash,
                    "before": unchanged_counts,
                    "after": counts(root),
                },
            )
        else:
            raise AssertionError("Cancelled replay key accepted another request")
        assert counts(root) == unchanged_counts
        assert counts(root)["admitted_units"] == before["counts"]["admitted_units"] == 12
        assert counts(root)["trials"] == before["counts"]["trials"] == 12
        assert source_files(output, metadata) == before["source_files"]
    elif slot["slot_id"] == "browser-normal-replay":
        assert row["result"]["replay"]["status"] == "NUMERICAL_REPLAY_VERIFIED"
        assert set(row["slots"]) == {"E", *["P:" + str(i) for i in range(10)]}
        before = read(output / "browser-cancel-before.json")
        assert source_files(output, metadata) == before["source_files"]
        assert counts(root)["admitted_units"] == counts(root)["trials"] == 12
    else:
        raise AssertionError("Unregistered browser case")
    finish(root, metadata[which], task, row["status"])
    save(
        output / "actors" / (slot["slot_id"] + ".json"),
        {"task": row, "counts": counts(root), "activation": activation},
    )
    return row


def finalize(output, metadata):
    assert metadata["developer_fixture"] is False and metadata["sdk_environment"]["dirty"] is False
    root = Path(metadata["main"]["workspace"])
    negative = Path(metadata["risk"]["workspace"])
    checked = []
    for actor in metadata["actors"]:
        record = read(output / "actors" / (actor["name"] + ".json"))
        if actor["entry"] == "legacy-cli":
            research_id = record["research"]["run_id"]
            backtest_id = record["backtest"]["run_id"]
            b_root = root / "legacy-backtest-runs" / actor["name"]
            assert Path(record["backtest"]["root"]) == b_root
        else:
            row = TaskService(root).status(record["task"]["task_id"])
            assert row["status"] == "SUCCEEDED"
            expected = (
                output
                / "requests"
                / (actor["protocol"] + "-" + actor["factor"] + "-effective.json")
            ).read_bytes()
            assert TaskService(root).state.get(row["task_id"])["raw"].encode() == expected
            research_id, backtest_id = (
                row["result"]["research_run_id"],
                row["result"]["backtest_run_id"],
            )
            b_root = root / "backtest-runs"
        fresh = known_answer(
            root / "research-runs",
            research_id,
            b_root,
            backtest_id,
            actor["factor"],
            actor["protocol"],
            output / "oracles",
        )
        assert canonical(fresh["projection"]) == canonical(
            read(output / "projections" / (actor["name"] + ".json"))
        )
        checked.append({"actor": actor["name"], "checks": fresh["checks"]})
    for name in ("browser-cancel-replay", "browser-normal-replay", "browser-original-risk"):
        assert (output / "actors" / (name + ".json")).is_file()
    for name in (
        "browser-main-momentum",
        "browser-main-reversal",
        "browser-cancel-replay",
        "browser-normal-replay",
        "browser-original-risk",
    ):
        which_root = negative if name == "browser-original-risk" else root
        task = read(output / "actors" / (name + ".json"))["task"]["task_id"]
        browser_evidence(output / "browser-evidence" / (name + ".json"), name, task, which_root)
        actual = TaskService(which_root).status(task)
        expected_status = (
            "FAILED"
            if name == "browser-original-risk"
            else "CANCELLED"
            if name == "browser-cancel-replay"
            else "SUCCEEDED"
        )
        assert actual["status"] == expected_status
    assert (
        source_files(output, metadata)
        == read(output / "browser-cancel-before.json")["source_files"]
    )
    with BudgetAuthority(root).transaction() as c:
        assert (
            c.execute(
                "SELECT count(*) FROM execution_plan_activations WHERE completion IS NOT NULL"
            ).fetchone()[0]
            == 14
        )
    with BudgetAuthority(negative).transaction() as c:
        assert (
            c.execute(
                "SELECT count(*) FROM execution_plan_activations WHERE completion IS NOT NULL"
            ).fetchone()[0]
            == 1
        )
    assert counts(root)["admitted_units"] == counts(root)["trials"] == 12
    assert counts(negative)["admitted_units"] == counts(negative)["trials"] == 1
    for which, workspace in (("main", root), ("risk", negative)):
        with closing(sqlite3.connect(workspace / "task-control/tasks.sqlite")) as source:
            destination = output / (which + "-final.sqlite")
            assert not destination.exists()
            with closing(sqlite3.connect(destination)) as target:
                source.backup(target)
    result = {
        "status": "DEVELOPER_ENGINEERING_PROTOCOL_COMPLETE",
        "main": counts(root),
        "risk": counts(negative),
        "browser_research_actors": 2,
        "browser_negative_cases": ["risk", "queued_cancel", "normal_replay"],
        "independent_G2": "PENDING",
        "financial_approval": "NONE",
        "formal_Test": "NOT RUN",
        "Windows_R2": "DEFERRED / NOT VERIFIED",
        "deployed": False,
        "real_market_support": False,
        "final_original_artifact_rechecks": checked,
    }
    save(output / "FINAL_RESULT.json", result)
    save(
        output / "FINAL_FILE_MANIFEST.json", {"self_excluded": True, "files": file_manifest(output)}
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument(
        "--operation",
        choices=(
            "run",
            "run-next",
            "prepare",
            "advance-browser",
            "complete-browser",
            "enqueue-cancel",
            "finalize",
        ),
        default="run",
    )
    parser.add_argument("--workspace", choices=("main", "risk"), default="main")
    parser.add_argument("--browser-evidence", type=Path)
    parser.add_argument(
        "--developer-fixture",
        action="store_true",
        help="Explicit dirty-source selftest fixture; cannot finalize or serve as fixed G2 evidence",
    )
    args = parser.parse_args(argv)
    output, metadata = prepare(args.run, args.developer_fixture)
    if args.operation == "prepare":
        result = metadata
    elif args.operation in {"run", "run-next"}:
        result = run_nonbrowser(output, metadata, args.operation == "run-next")
    elif args.operation == "advance-browser":
        root = Path(metadata[args.workspace]["workspace"])
        result = advance(root, metadata[args.workspace])
        assert result["slot_id"].startswith("browser-")
    elif args.operation == "complete-browser":
        assert args.browser_evidence is not None
        result = complete_browser(output, metadata, args.workspace, args.browser_evidence)
    elif args.operation == "enqueue-cancel":
        result = enqueue_cancel(output, metadata)
    else:
        result = finalize(output, metadata)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
