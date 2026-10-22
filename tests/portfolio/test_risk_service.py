from copy import deepcopy
from decimal import localcontext

import pytest

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.portfolio.construct import build_candidate, compute
from aqrp.portfolio.contracts import F, load, project
from aqrp.portfolio.service import construct_approved, construct_engineering, replay_engineering
from aqrp.risk.checks import assess, check_target

from .helpers import change, fixture, reseal

COMMIT = "a" * 40


@pytest.mark.parametrize(
    "path,value,reason",
    [
        ("constraints.gross_max", "0.9", "GROSS"),
        ("constraints.net_max", "0.9", "NET"),
        ("constraints.net_min", "1.1", "NET"),
        ("constraints.leverage_max", "0.9", "LEVERAGE"),
        ("constraints.turnover_max", "0.9", "TURNOVER"),
        ("constraints.beta_max", "0.9", "BETA"),
        ("constraints.beta_min", "1.1", "BETA"),
        ("constraints.industries.I.net_max", "0.9", "INDUSTRY_NET"),
        ("constraints.industries.I.net_min", "1.1", "INDUSTRY_NET"),
        ("constraints.industries.I.gross_max", "0.9", "INDUSTRY_GROSS"),
        ("profile.fee_reserve", "1", "FREE_CASH"),
    ],
)
def test_public_service_enforces_each_limit(path, value, reason, tmp_path):
    x = change(fixture(), path, value)
    if path == "constraints.net_min":
        x["constraints"]["net_max"] = "2"
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert reason in r["reasons"] and "target" not in r
    assert r["manifest"]["status"] == "FAILED"


@pytest.mark.parametrize("weighting", ["equal", "score"])
@pytest.mark.parametrize("kind", ["SHORT_PERMISSION", "BORROW_TOTAL"])
def test_short_permissions_not_implicit_zero_or_extra_borrow(weighting, kind, tmp_path):
    x = fixture()
    x["policy"].update(mode="LONG_SHORT", weighting=weighting, net="0")
    row = x["inputs"]["permissions"]["data"][1]
    if kind == "SHORT_PERMISSION":
        row["short_permission"] = False
    else:
        row["borrow_limit_total"] = "49.999999999999"
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert kind in r["reasons"] and "target" not in r


def test_nonselected_holding_is_sold_only_if_sellable(tmp_path):
    x = fixture()
    x["inputs"]["account"]["data"]["total_cash"] = "900"
    x["inputs"]["account"]["data"]["positions"][0]["quantity"] = "10"
    x["inputs"]["scores"][0]["data"]["rows"][0]["score"] = "0"
    x["inputs"]["permissions"]["data"][0]["sellable_qty"] = "9"
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert "SELLABLE" in r["reasons"]


@pytest.mark.parametrize("flag", [True, False])
def test_short_full_close_never_bypasses_halt(flag, tmp_path):
    x = fixture("short_close")
    x["profile"]["allow_full_close_odd_lot"] = flag
    x["inputs"]["status"]["data"][0]["tradable"] = False
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert "NOT_TRADABLE" in r["reasons"] and "target" not in r


def test_signed_industry_does_not_replace_industry_gross(tmp_path):
    x = fixture()
    x["policy"].update(mode="LONG_SHORT", weighting="equal", gross="1", net="0")
    x["constraints"]["industries"]["I"]["gross_max"] = "0.9"
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert "INDUSTRY_GROSS" in r["reasons"]
    assert r["risk"]["post"]["metrics"]["industries"]["I"] == {"net": "0", "gross": "1"}


def test_approved_net_budget_can_fail_funding(tmp_path):
    x = fixture()
    x["policy"].update(mode="LONG_SHORT", weighting="equal", gross="1.2", net="0.2")
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert r["risk"]["post"]["metrics"]["weights"] == {"SYNTH:A": "0.7", "SYNTH:B": "-0.5"}
    assert r["risk"]["post"]["metrics"]["free_cash"] == "-200" and "FREE_CASH" in r["reasons"]


@pytest.mark.parametrize(
    "offset,passed", [(F(0), True), (F(1, 2 * 10**12), True), (F(2, 10**12), False)]
)
def test_explicit_ratio_tolerance_boundary(offset, passed):
    x, m, p, _, _, _, _ = compute(reseal(fixture()))
    x["constraints"]["per_asset"]["SYNTH:A"] = "0.75"
    d = assess(x, m, p, {"SYNTH:A": (F(3, 4) + offset) * 100, "SYNTH:B": F(0)}, post=False)
    row = next(
        c for c in d["checks"] if c["code"] == "ASSET_WEIGHT" and c["security_id"] == "SYNTH:A"
    )
    assert row["passed"] == passed


@pytest.mark.parametrize("mode", ["LONG_ONLY", "LONG_SHORT"])
def test_empty_universe_and_cash_forbidden(mode, tmp_path):
    x = fixture()
    x["policy"]["mode"] = mode
    if mode == "LONG_SHORT":
        x["policy"]["net"] = "0"
    x["inputs"]["scores"][0]["data"]["rows"] = []
    x["constraints"]["allow_cash_only"] = False
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert r["status"] in ("REJECTED", "INFEASIBLE") and "target" not in r


def test_overlapping_long_short_legs_and_zero_budget(tmp_path):
    x = fixture()
    x["policy"].update(mode="LONG_SHORT", weighting="equal", net="0", long_k=2, short_k=1)
    r = construct_engineering(reseal(x), tmp_path / "bad", COMMIT).read()
    assert r["reasons"] == ["INFEASIBLE_OVERLAPPING_LEGS"]
    x["policy"].update(gross="0", net="0")
    r = construct_engineering(reseal(x), tmp_path / "zero", COMMIT).read()
    assert r["status"] == "SUCCEEDED" and r["target"]["gross"] == "0"


def test_deterministic_result_projection_uuid_unique_and_terminal_immutable(tmp_path):
    req = reseal(fixture())
    a = construct_engineering(req, tmp_path, COMMIT).read()
    b = construct_engineering(req, tmp_path, COMMIT).read()
    assert a["run_id"] != b["run_id"] and a["target"] == b["target"] and a["risk"] == b["risk"]
    ledger = ExperimentLedger(tmp_path)
    with pytest.raises(ContractError, match="IMMUTABLE_TERMINAL_RUN"):
        ledger.artifact(a["run_id"], "new.json", {})
    with pytest.raises(ContractError, match="IMMUTABLE_TERMINAL_RUN"):
        ledger.finish(a["run_id"], "SUCCEEDED")
    stored = load((tmp_path / a["run_id"] / "config.json").read_bytes())
    assert bytes.fromhex(stored["raw_request_hex"]) == req.raw
    assert digest(a["target"]) != digest(a["risk"])


def test_candidate_and_output_copies_cannot_mutate_service(tmp_path):
    req = reseal(fixture())
    obj = construct_engineering(req, tmp_path, COMMIT)
    a = obj.read()
    a["target"]["quantities"]["SYNTH:A"] = "999999"
    assert obj.read()["target"]["quantities"]["SYNTH:A"] == "75"
    assert check_target(build_candidate(req), req)["passed"]
    with pytest.raises(ContractError):
        construct_engineering({}, tmp_path, COMMIT)


def test_projection_does_not_depend_on_decimal_precision():
    with localcontext() as c:
        c.prec = 3
        assert project({"x": F(1, 3)})["x"] == "0." + "3" * 34


def test_unexpected_failure_recorded_not_masked(monkeypatch, tmp_path):
    import aqrp.portfolio.service as service

    def broken(_):
        raise RuntimeError("deliberate storage/compute failure")

    monkeypatch.setattr(service, "build_candidate", broken)
    with pytest.raises(RuntimeError):
        service.construct_engineering(reseal(fixture()), tmp_path, COMMIT)
    runs = [p for p in tmp_path.iterdir() if p.is_dir()]
    assert len(runs) == 1
    assert ExperimentLedger(tmp_path).verify(runs[0].name)["status"] == "FAILED"


def test_formal_corrupted_policy_fail_closed(monkeypatch, tmp_path):
    import aqrp.portfolio.service as service

    monkeypatch.setattr(service, "reviewed_policy", lambda: {"financial_approval": "forged"})
    with pytest.raises(ContractError, match="UNAPPROVED_EXECUTION_ENVIRONMENT"):
        construct_approved(reseal(fixture()), tmp_path, COMMIT)


def test_replay_missing_result_and_post_manifest_modification(tmp_path):
    ledger = ExperimentLedger(tmp_path)
    lineage = {
        "code_commit": COMMIT,
        "code_bundle": "x",
        "data_hash": "x",
        "environment": {},
        "protocol_hash": "x",
        "permission_domain": "TEST",
        "seed": 0,
    }
    run = ledger.start({}, lineage)
    ledger.finish(run, "FAILED")
    with pytest.raises(ContractError, match="RESULT_NOT_IN_TERMINAL_MANIFEST"):
        replay_engineering(tmp_path, run)
    (ledger.path(run) / "result.json").write_bytes(b"{}")
    with pytest.raises(ContractError, match="RESULT_NOT_IN_TERMINAL_MANIFEST"):
        replay_engineering(tmp_path, run)


def test_real_beta_dot_product_and_distinct_sectors(tmp_path):
    x = fixture()
    x["inputs"]["exposures"]["data"][0]["beta"] = "1.2"
    x["inputs"]["exposures"]["data"][1].update(beta="0.8", industry="J")
    x["constraints"]["industries"]["J"] = dict(x["constraints"]["industries"]["I"])
    x["constraints"]["beta_max"] = "1"
    r = construct_engineering(reseal(x), tmp_path, COMMIT).read()
    assert r["risk"]["post"]["metrics"]["beta"] == "1.1"
    assert r["risk"]["post"]["metrics"]["industries"] == {
        "I": {"net": "0.75", "gross": "0.75"},
        "J": {"net": "0.25", "gross": "0.25"},
    }
    assert "BETA" in r["reasons"]


def test_three_asset_centered_long_short_and_input_permutation(tmp_path):
    x = fixture()
    for name, e in x["inputs"].items():
        if name == "scores":
            continue
        if name == "account":
            e["data"]["positions"].append({"security_id": "SYNTH:C", "quantity": "0"})
        else:
            row = deepcopy(e["data"][0])
            row["security_id"] = "SYNTH:C"
            e["data"].append(row)
    score = x["inputs"]["scores"][0]["data"]["rows"]
    row = deepcopy(score[0])
    row.update(security_id="SYNTH:C", score="-2")
    score.append(row)
    x["policy"].update(mode="LONG_SHORT", weighting="score", gross="1", net="0", top_k=3, long_k=2)
    x["constraints"]["per_asset"]["SYNTH:C"] = "1"
    a = construct_engineering(reseal(x), tmp_path / "a", COMMIT).read()
    assert a["status"] == "SUCCEEDED"
    assert a["target"]["quantities"] == {"SYNTH:A": "43", "SYNTH:B": "6", "SYNTH:C": "-50"}
    assert a["target"]["gross"] == "0.99" and a["target"]["free_cash"] == "10"
    for name, e in x["inputs"].items():
        if name not in ("scores", "account"):
            e["data"].reverse()
    x["inputs"]["scores"][0]["data"]["rows"].reverse()
    b = construct_engineering(reseal(x), tmp_path / "b", COMMIT).read()
    assert a["target"]["quantities"] == b["target"]["quantities"]
