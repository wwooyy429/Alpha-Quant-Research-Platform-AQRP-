import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger, append_chain, mutex, read_chain


def lineage():
    return {
        "code_commit": "a" * 40,
        "code_bundle": "b" * 64,
        "data_hash": "c" * 64,
        "environment": {"lock": "d" * 64},
        "protocol_hash": "e" * 64,
        "permission_domain": "PUBLIC",
        "seed": 17,
    }


def test_terminal_integrity_decisions_compare_cache_and_catalogue(tmp_path):
    ledger = ExperimentLedger(tmp_path)
    assert ledger.catalogue() == []
    a = ledger.start({"x": 1}, lineage())
    assert ledger.register_trial(a, "f", "a", budget=3)["repeat_of"] == []
    ledger.artifact(a, "output.json", {"a": 1})
    ledger.artifact(a, "report.html", "<html>hello</html>")
    ledger.event(a, "COMPUTED", {"n": 1})
    m = ledger.finish(a, "SUCCEEDED")
    assert m["status"] == "SUCCEEDED"
    ledger.decision(a, {"human_record": "approved-research-only"})
    assert ledger.verify(a) == m
    b = ledger.start({"x": 1}, lineage())
    assert ledger.register_trial(b, "f", "a", budget=3)["repeat_of"] == [a]
    ledger.finish(b, "CANCELLED")
    assert not ledger.compare(a, b)["status_equal"]
    assert len(ledger.catalogue()) == 2
    for action in (
        lambda: ledger.event(a, "X", {}),
        lambda: ledger.artifact(a, "new.json", {}),
        lambda: ledger.finish(a, "FAILED"),
    ):
        with pytest.raises(ContractError, match="IMMUTABLE_TERMINAL_RUN"):
            action()
    assert ledger.cache_get({"profile": 1}) is None
    ledger.cache_put({"profile": 1}, {"value": [1, None]})
    ledger.cache_put({"profile": 1}, {"value": [1, None]})
    assert ledger.cache_get({"profile": 1}) == {"value": [1, None]}
    assert ledger.cache_get({"profile": 2}) is None
    with pytest.raises(ContractError, match="NONDETERMINISTIC_CACHE_RESULT"):
        ledger.cache_put({"profile": 1}, {})
    cache = next(tmp_path.glob("cache-*.json"))
    content = json.loads(cache.read_bytes())
    content["payload"] = {"value": "tampered"}
    cache.write_bytes(canonical(content))
    with pytest.raises(ContractError, match="CACHE_CORRUPTION"):
        ledger.cache_get({"profile": 1})


def test_family_preregistration_complete_failures_and_repeat_contamination(tmp_path):
    ledger = ExperimentLedger(tmp_path)
    assert not ledger.family("f", ["a", "b"], definitions={"a": "1", "b": "2"})["results"]
    f = ledger.family(
        "f", ["a", "b"], {"a": {"p": None, "reason": "FAILED"}}, definitions={"a": "1", "b": "2"}
    )
    assert f["results"]["a"]["p"] is None
    f = ledger.family("f", ["a", "b"], {"a": {"p": 0.01}}, definitions={"a": "1", "b": "2"})
    assert f["duplicate_hypotheses"] == ["a"]
    for declarations in ([], ["a", "a"]):
        with pytest.raises(ContractError, match="INVALID_FAMILY_DECLARATIONS"):
            ledger.family("f", declarations)
    with pytest.raises(ContractError, match="FAMILY_REDEFINED"):
        ledger.family("f", ["a", "b"], definitions={"a": "3", "b": "2"})
    with pytest.raises(ContractError, match="UNREGISTERED_HYPOTHESIS"):
        ledger.family("other", ["a"], {"x": {"p": 1}})


def test_failures_budget_and_tamper(tmp_path):
    ledger = ExperimentLedger(tmp_path)
    with pytest.raises(ContractError):
        ledger.start({}, {})
    for key in ("bad", None):
        with pytest.raises(ContractError):
            ledger.path(key)
    a = ledger.start({}, lineage())
    with pytest.raises(ContractError, match="NONTERMINAL_RUN"):
        ledger.verify(a)
    for name in ("../x.json", "manifest.json", "config.json", "lineage.json"):
        with pytest.raises(ContractError):
            ledger.artifact(a, name, {})
    with pytest.raises(ContractError):
        ledger.finish(a, "RELEASED")
    with pytest.raises(ContractError):
        ledger.register_trial(a, "", "x", budget=1)
    ledger.register_trial(a, "f", "x", budget=1)
    with pytest.raises(ContractError, match="EXPERIMENT_BUDGET_EXCEEDED"):
        ledger.register_trial(a, "f", "x", budget=1)
    assert len(read_chain(tmp_path / "trials.jsonl")) == 2
    ledger.finish(a, "FAILED")
    root = ledger.path(a)
    (root / "lineage.json").write_bytes(b"{}")
    with pytest.raises(ContractError, match="RUN_ARTIFACT_HASH_MISMATCH"):
        ledger.verify(a)
    (root / "manifest.json").write_bytes(b"{}")
    with pytest.raises(ContractError, match="RUN_MANIFEST_MISMATCH"):
        ledger.verify(a)


def test_hash_chain_and_concurrent_serialization(tmp_path):
    path = tmp_path / "chain.jsonl"
    assert read_chain(path) == []

    def append(i):
        with mutex(tmp_path / ".lock"):
            append_chain(path, "ITEM", {"i": i})

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(append, range(20)))
    assert len(read_chain(path)) == 20
    with mutex(tmp_path / ".lock"):
        with pytest.raises(ContractError, match="LEDGER_LOCK_TIMEOUT"):
            with mutex(tmp_path / ".lock", timeout=0.01):
                pytest.fail("must not obtain competing lock")
    data = path.read_bytes().replace(b'"i":0', b'"i":999')
    path.write_bytes(data)
    with pytest.raises(ContractError, match="LEDGER_CHAIN_CORRUPTED"):
        read_chain(path)
