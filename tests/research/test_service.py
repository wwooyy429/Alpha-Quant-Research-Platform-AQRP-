import json
from copy import deepcopy
from dataclasses import asdict

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.experiments.reproduction import reproduce_current
from aqrp.research.synthetic import synthetic_research
from aqrp.services.cli import main
from aqrp.services.research import ResearchRequest, hypotheses, hypothesis_definition, research

SHA = "3861ef1637bc2b4c28725d7afc5f2e1f02242e80"


@pytest.fixture(scope="module")
def inputs(tmp_path_factory):
    root = tmp_path_factory.mktemp("research-input")
    return synthetic_research(root, sessions=24, assets=6)


def request(inputs, config=None):
    c, s, e, v = inputs
    if config is not None:
        if config["candidates"]:
            config["family"]["hypotheses"] = [r["hypothesis"] for r in hypotheses(config)]
        config["family"]["definitions"] = {
            r["hypothesis"]: hypothesis_definition(
                r, config, s.manifest_hash, e.manifest_hash, v.checksum
            )
            for r in hypotheses(config)
        }
        if not config["candidates"]:
            config["family"]["definitions"] = c["family"]["definitions"]
    return ResearchRequest.create(c if config is None else config, s, e, v, SHA)


def test_full_chain_cache_reproduce_and_cli(inputs, tmp_path, capsys):
    req = request(inputs)
    result = research(req, tmp_path / "runs")
    run_id = result["run_id"]
    ledger = ExperimentLedger(tmp_path / "runs")
    root = ledger.path(run_id)
    assert result["manifest"]["status"] == "SUCCEEDED"
    assert result["report"]["financial_approval"] == "NONE"
    assert not result["report"]["independence_verified"]
    for stage in ("raw", "clean", "standardized", "neutralized", "final"):
        artifact = json.loads((root / (stage + ".json")).read_bytes())
        assert artifact["status"] == "EXECUTED"
        assert artifact["rows"]
    labels = json.loads((root / "labels.json").read_bytes())
    assert all(r["label"] is not None for r in labels)
    assert result["report"]["metrics"]["decay"]
    assert json.loads((root / "oos.json").read_bytes())["train_for_validation"]["train"]
    assert (
        reproduce_current(req, tmp_path / "runs", run_id)["status"] == "DECLARED_PROJECTION_MATCH"
    )
    assert len(ledger.catalogue()) == 2
    c, s, e, v = inputs
    source = tmp_path / "request.json"
    source.write_bytes(
        canonical(
            {
                "config": c,
                "snapshot": {**asdict(s), "root": str(s.root)},
                "exposures": {**asdict(e), "root": str(e.root)},
                "coverage": v.read(s.manifest_hash),
                "code_commit": SHA,
            }
        )
    )
    assert main([str(source), "--output", str(tmp_path / "cli")]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "SUCCEEDED"


def test_full_factor_replacement(inputs, tmp_path):
    from aqrp.factors.admission import builtin_spec

    c = deepcopy(inputs[0])
    c["candidates"][0].update(ref=asdict(builtin_spec("reversal").ref), hypothesis="reversal")
    c["family"].update(id="public-reversal", hypotheses=["reversal"])
    momentum = research(request(inputs), tmp_path / "momentum")
    result = research(request(inputs, c), tmp_path / "reversal")
    assert result["manifest"]["status"] == "SUCCEEDED"
    assert all(r["factor_key"] == "reversal" for r in result["report"]["metrics"]["daily"])
    # Relational sign property supplements the independent fixed answers.
    for stage in ("raw", "final"):
        left = json.loads(
            (tmp_path / "momentum" / momentum["run_id"] / (stage + ".json")).read_bytes()
        )["rows"]
        right = json.loads(
            (tmp_path / "reversal" / result["run_id"] / (stage + ".json")).read_bytes()
        )["rows"]
        assert [(r["session"], r["security_id"]) for r in left] == [
            (r["session"], r["security_id"]) for r in right
        ]
        for a, b in zip(left, right):
            assert (
                b["score"] is None
                if a["score"] is None
                else b["score"] == pytest.approx(-a["score"], abs=1e-12)
            )
    for a, b in zip(momentum["report"]["metrics"]["daily"], result["report"]["metrics"]["daily"]):
        assert (
            b["ic"]["value"] is None
            if a["ic"]["value"] is None
            else b["ic"]["value"] == pytest.approx(-a["ic"]["value"], abs=1e-10)
        )


def test_parameter_grid_and_composite_are_all_counted_in_family(inputs, tmp_path):
    c = deepcopy(inputs[0])
    second = deepcopy(c["candidates"][0])
    second.update(hypothesis="momentum-L3", parameters={"lookback": 3})
    c["candidates"].append(second)
    c["family"].update(id="parameter-grid-and-composite", budget=20)
    c["composite"] = {
        "hypothesis": "fixed-composite",
        "factor_keys": ["momentum", "momentum-L3"],
        "weights": [1, 2],
        "directions": [1, 1],
        "direction_applied": False,
        "input_stage": "final",
        "normalization": "cross_sectional_sample_z",
        "min_n": 3,
        "redundancy": None,
    }
    result = research(request(inputs, c), tmp_path)
    assert result["report"]["multiplicity"]["m"] == 6
    assert len(result["report"]["approval"]) == 6
    assert any(r["stage"] == "composite" for r in result["report"]["metrics"]["daily"])
    root = tmp_path / result["run_id"]
    assert json.loads((root / "composite.json").read_bytes())["scores"]
    evidence = json.loads((root / "engine.json").read_bytes())
    from aqrp.core.canonical import digest

    for e in evidence:
        assert (
            digest({"rows": e["signals"], "config": e["config_snapshot_utf8"]}) == e["content_hash"]
        )


def test_cli_module_entry_is_thin(inputs, tmp_path, monkeypatch, capsys):
    import runpy
    import sys

    from aqrp.services import research as module

    c, s, e, v = inputs
    raw = {
        "config": c,
        "snapshot": {**asdict(s), "root": str(s.root)},
        "exposures": None,
        "coverage": v.read(s.manifest_hash),
        "code_commit": SHA,
    }
    source = tmp_path / "request.json"
    source.write_bytes(canonical(raw))
    monkeypatch.setattr(
        module,
        "research",
        lambda request, output: {"run_id": "unit-mock", "manifest": {"status": "SUCCEEDED"}},
    )
    monkeypatch.setattr(
        sys, "argv", ["aqrp-research", str(source), "--output", str(tmp_path / "out")]
    )
    monkeypatch.delitem(sys.modules, "aqrp.services.cli", raising=False)
    with pytest.raises(SystemExit) as exit:
        runpy.run_module("aqrp.services.cli", run_name="__main__")
    assert exit.value.code == 0
    assert json.loads(capsys.readouterr().out)["run_id"] == "unit-mock"


@pytest.mark.parametrize(
    "field,value,code",
    [
        ("purpose", "FINAL_TEST", "USE_SEALED_OPERATOR_ENTRY"),
        ("candidates", [], "NO_RESEARCH_CANDIDATES"),
        ("decisions", [], "EMPTY_RESEARCH_DECISIONS"),
    ],
)
def test_failures_are_durably_recorded(inputs, tmp_path, field, value, code):
    c = deepcopy(inputs[0])
    c[field] = value
    with pytest.raises(ContractError, match=code):
        research(request(inputs, c), tmp_path)
    ledger = ExperimentLedger(tmp_path)
    assert ledger.catalogue()[0]["status"] == "FAILED"
    assert list(tmp_path.glob("*/failure.json"))
