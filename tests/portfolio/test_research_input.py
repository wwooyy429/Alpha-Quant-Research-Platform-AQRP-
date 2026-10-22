import json
from pathlib import Path

import pytest

from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.portfolio.contracts import load, prepare
from aqrp.portfolio.research_input import _read, bind_research
from aqrp.portfolio.service import construct_engineering

from .helpers import fixture, reseal

PUBLISHED = Path(__file__).parents[2] / "docs/audits/phase-3/publication/sdk/research"
ORIGINAL = "0c902a7a-6e21-4003-9e18-365bf8bc3b68"


def projected_payload():
    x = fixture()
    p = json.loads((PUBLISHED / "request.json").read_bytes())
    stages = json.loads((PUBLISHED / "runs" / ORIGINAL / "final.json").read_bytes())
    decision = stages["rows"][0]["decision_time"]
    ids = ["SYN_A:001", "SYN_A:002"]
    context = {
        **x["context"],
        "decision_time": decision,
        "currency": p["config"]["currency"],
        "market_id": p["config"]["market_id"],
        "snapshot_id": p["snapshot"]["snapshot_id"],
        "snapshot_sha256": p["snapshot"]["manifest_hash"],
    }
    x["context"] = context
    x["policy"]["factor_weights"] = {"momentum": "1"}
    x["constraints"]["per_asset"] = {s: "1" for s in ids}
    for name, e in x["inputs"].items():
        if name == "scores":
            continue
        e["context"] = context
        for k in ("event_time", "available_at", "as_of"):
            e[k] = decision
        if name == "account":
            for row, sid in zip(e["data"]["positions"], ids):
                row["security_id"] = sid
            e["data"]["valuation_time"] = decision
        else:
            for row, sid in zip(e["data"], ids):
                row["security_id"] = sid
                for k in ("event_time", "available_at", "as_of"):
                    row[k] = decision
                if name == "securities":
                    row.update(market_id=context["market_id"], currency=context["currency"])
    return x


def bound():
    x = projected_payload()
    r = bind_research(x, PUBLISHED / "runs", ORIGINAL)
    # Rehash the non-score declared account/market inputs after explicit projection.
    return reseal(load(r.raw))


def test_actual_published_p3_stage_to_p4_engineering_not_reexecuted_factor(tmp_path):
    r = bound()
    prepare(r)
    result = construct_engineering(r, tmp_path, "a" * 40).read()
    assert result["status"] == "SUCCEEDED"
    assert result["target"]["quantities"] == {"SYN_A:001": "100", "SYN_A:002": "0"}
    assert result["financial_approval"] == "NONE"


@pytest.mark.parametrize(
    "key,value",
    [
        ("manifest_sha256", "0" * 64),
        ("artifact_sha256", "0" * 64),
        ("source_calendar_id", "wrong"),
        ("factor_key", "absent"),
        ("stage", "labels"),
    ],
)
def test_binding_tamper_even_resealed_input(key, value):
    x = load(bound().raw)
    x["source"]["research_bindings"][0][key] = value
    with pytest.raises(ContractError):
        prepare(reseal(x))


def test_mutated_score_not_cured_by_new_envelope_hash():
    x = load(bound().raw)
    x["inputs"]["scores"][0]["data"]["rows"][0]["score"] = 999
    with pytest.raises(ContractError, match="RESEARCH_SCORE_PROJECTION_CHANGED"):
        prepare(reseal(x))


@pytest.mark.parametrize("value", [[], None, {}])
def test_missing_source_bindings(value):
    x = load(bound().raw)
    x["source"]["research_bindings"] = value
    with pytest.raises(ContractError):
        prepare(reseal(x))


def test_invalid_stage_and_missing_root(tmp_path):
    with pytest.raises(ContractError):
        bind_research(projected_payload(), PUBLISHED / "runs", ORIGINAL, stage="labels")
    with pytest.raises(ContractError):
        bind_research(projected_payload(), tmp_path / "absent", ORIGINAL)
    assert not (tmp_path / "absent").exists()


def test_binding_parent_snapshot_rejected():
    x = load(bound().raw)
    x["context"]["snapshot_sha256"] = "0" * 64
    for name, e in x["inputs"].items():
        for item in e if name == "scores" else [e]:
            item["context"] = x["context"]
    with pytest.raises(ContractError, match="RESEARCH_SOURCE_BINDING_MISMATCH"):
        prepare(reseal(x))


def test_unmanifested_and_changed_bytes_are_rejected(tmp_path):
    ledger = ExperimentLedger(tmp_path)
    run = ledger.start(
        {},
        {
            "code_commit": "a" * 40,
            "code_bundle": "x",
            "data_hash": "x",
            "environment": {},
            "protocol_hash": "x",
            "permission_domain": "TEST",
            "seed": 0,
        },
    )
    ledger.artifact(run, "final.json", {"rows": []})
    m = ledger.finish(run, "SUCCEEDED")
    with pytest.raises(ContractError, match="RESEARCH_ARTIFACT_NOT_MANIFESTED"):
        _read(ledger, run, "report.json", m)
    (ledger.path(run) / "final.json").write_bytes(b"{}")
    with pytest.raises(ContractError, match="RESEARCH_ARTIFACT_BYTES_CHANGED"):
        _read(ledger, run, "final.json", m)
