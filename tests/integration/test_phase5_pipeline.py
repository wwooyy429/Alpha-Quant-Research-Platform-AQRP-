"""BT-010 / INT-002: real P1 nine files, P3 terminal originals, P4 and full simulation."""

from copy import deepcopy

import pytest

from aqrp.backtest.contracts import validate
from aqrp.backtest.synthetic import research_backtests, seal_sidecar
from aqrp.core.canonical import canonical, digest
from aqrp.core.errors import ContractError
from aqrp.factors.admission import bundle_manifest
from aqrp.portfolio.contracts import load
from aqrp.services.backtest import replay_engineering, simulate_engineering


@pytest.fixture(scope="module")
def research_inputs(tmp_path_factory):
    root = tmp_path_factory.mktemp("P5-real-P1-P3-inputs")
    inputs = research_backtests(root, "a" * 40)
    return root, inputs


def test_real_factor_replacement_complete_simulations_and_replay(research_inputs):
    root, inputs = research_inputs
    core_before = bundle_manifest()
    results = {}
    for name, request in inputs.items():
        validate(request)
        (root / (name + "-request.json")).write_bytes(request.raw)
        r = simulate_engineering(request, root / (name + "-runs"), "a" * 40).read()
        assert r["status"] == "SUCCEEDED", r
        assert r["fills"] and r["orders"] and r["journal"] and r["performance"]
        assert r["scope"] == "ENGINEERING_TEST_ONLY" and r["financial_approval"] == "NONE"
        assert (
            replay_engineering(root / (name + "-runs"), r["run_id"], root / (name + "-replay"))[
                "status"
            ]
            == "NUMERICAL_REPLAY_VERIFIED"
        )
        results[name] = r
    assert bundle_manifest() == core_before
    a, b = results["momentum"], results["reversal"]
    assert {f["security_id"] for f in a["fills"]} != {f["security_id"] for f in b["fills"]}
    xa, xb = load(inputs["momentum"].raw), load(inputs["reversal"].raw)
    assert {k: v for k, v in xa.items() if k != "decisions"} == {
        k: v for k, v in xb.items() if k != "decisions"
    }
    for req in xa["decisions"]:
        assert load(req["portfolio_request_utf8"])["source"]["kind"] == "RESEARCH_ARTIFACT"
    snapshot = next((root / "inputs/dataset").iterdir())
    assert len(list(snapshot.glob("*.parquet"))) == 8 and (snapshot / "manifest.json").is_file()


@pytest.mark.parametrize(
    "kind",
    ["parent_id", "score", "unmanifested", "source_hash", "p1_manifest", "historical_volume"],
)
def test_actual_p3_lineage_mutations_rejected_even_if_rehashed(research_inputs, kind):
    _, requests = research_inputs
    x = deepcopy(load(requests["momentum"].raw))
    p = load(x["decisions"][0]["portfolio_request_utf8"])
    binding = p["source"]["research_bindings"][0]
    if kind == "parent_id":
        p["context"]["snapshot_id"] = "other-legal-snapshot-id"
        binding["snapshot"]["snapshot_id"] = "other-legal-snapshot-id"
        x["sidecar"]["snapshot_id"] = "other-legal-snapshot-id"
        for name, envelope in p["inputs"].items():
            for e in envelope if name == "scores" else [envelope]:
                e["context"]["snapshot_id"] = "other-legal-snapshot-id"
    elif kind == "score":
        p["inputs"]["scores"][0]["data"]["rows"][0]["score"] = 999
    elif kind == "unmanifested":
        binding["stage"] = "raw"
    elif kind == "source_hash":
        binding["snapshot"]["manifest_hash"] = "0" * 64
    elif kind == "historical_volume":
        x["sidecar"]["volume_history"][0]["shares"] = "999999"
    else:
        binding["snapshot_manifest_sha256"] = "0" * 64
    entries = [e for name, e in p["inputs"].items() if name != "scores"] + p["inputs"]["scores"]
    for e in entries:
        e["content_sha256"] = digest({k: v for k, v in e.items() if k != "content_sha256"})
    p["source"]["fixture_manifest"] = {e["ref"]: e["content_sha256"] for e in entries}
    x["decisions"][0]["portfolio_request_utf8"] = canonical(p).decode()
    with pytest.raises(ContractError):
        validate(seal_sidecar(x))
