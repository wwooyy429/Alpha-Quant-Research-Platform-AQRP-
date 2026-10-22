from copy import deepcopy

import pytest

from aqrp.core.canonical import canonical
from aqrp.core.errors import ContractError
from aqrp.portfolio.contracts import (
    PortfolioRequest,
    boolean,
    checksum,
    identifier,
    integer,
    load,
    number,
    prepare,
)

from .helpers import change, fixture, reseal


@pytest.mark.parametrize(
    "path,value",
    [
        ("schema_version", "wrong"),
        ("context.session_index", True),
        ("context.currency", ""),
        ("context.snapshot_sha256", "x"),
        ("source.kind", "REAL_ACCOUNT"),
        ("source.scope", "APPROVED"),
        ("source.dataset_kind", "REAL"),
        ("source.financial_approval", "ResearchValidated"),
        ("profile.profile_id", "A_SHARE"),
        ("profile.max_age_sessions", 1),
        ("profile.allow_full_close_odd_lot", 1),
        ("profile.fee_reserve", "-1"),
        ("policy.mode", "SKIP_RISK"),
        ("policy.weighting", "optimizer"),
        ("policy.top_k", 0),
        ("policy.long_k", False),
        ("policy.short_k", -1),
        ("policy.gross", "-1"),
        ("policy.net", "2"),
        ("policy.factor_weights", {}),
        ("policy.factor_weights", {"F1": "0"}),
        ("inputs.prices.data.0.price", "0"),
        ("inputs.prices.data.0.lot", "0"),
        ("inputs.prices.data.0.price", "-1"),
        ("inputs.status.data.0.tradable", None),
        ("inputs.status.data.0.in_universe", 0),
        ("inputs.securities.data.0.symbol", ""),
        ("inputs.securities.data.0.market_id", "OTHER"),
        ("inputs.securities.data.0.currency", "USD"),
        ("inputs.exposures.data.0.industry", None),
        ("inputs.exposures.data.0.beta", None),
        ("inputs.permissions.data.0.short_permission", None),
        ("inputs.permissions.data.0.borrow_limit_total", "-1"),
        ("inputs.permissions.data.0.sellable_qty", "-1"),
        ("inputs.account.data.equity", "0"),
        ("inputs.account.data.total_cash", "999"),
        ("inputs.account.data.restricted_cash", "1001"),
        ("inputs.account.data.short_restriction", "1"),
        ("inputs.account.data.nonshort_restriction", "-1"),
        ("inputs.account.data.price_ref", "OTHER"),
        ("inputs.account.data.valuation_time", "2024-02-01T16:00:00.000001Z"),
        ("inputs.account.data.positions", {}),
        ("inputs.account.data.positions.0.security_id", "UNKNOWN"),
        ("constraints.per_asset", {}),
        ("constraints.per_asset.SYNTH:A", "-1"),
        ("constraints.gross_max", "-1"),
        ("constraints.leverage_max", "-1"),
        ("constraints.turnover_max", "-1"),
        ("constraints.net_min", "2"),
        ("constraints.beta_min", "3"),
        ("constraints.allow_cash_only", "yes"),
        ("constraints.industries", {}),
        ("constraints.industries.I.net_min", "3"),
        ("constraints.industries.I.gross_max", "-1"),
        ("inputs.scores", []),
        ("inputs.scores.0.data.stage", "lookahead"),
        ("inputs.scores.0.data.factor_ref.implementation_hash", "bad"),
        ("inputs.scores.0.data.factor_ref.factor_id", ""),
        ("inputs.scores.0.data.params_hash", "bad"),
        ("inputs.scores.0.data.rows.0.security_id", "UNKNOWN"),
        ("inputs.scores.0.data.rows.0.valid", 1),
        ("inputs.scores.0.data.rows.0.score", None),
        ("inputs.scores.0.data.rows.0.session_index", 1),
        ("inputs.scores.0.data.rows.0.session_index", -1),
        ("inputs.scores.0.data.rows.0.signal_time", "2024-02-01T16:00:00.000001Z"),
    ],
)
def test_strict_inputs_reject_even_with_new_valid_content_hash(path, value):
    x = change(fixture(), path, value)
    # Even a fixture author who can reseal hashes cannot bypass schema/PIT/risk semantics.
    with pytest.raises(ContractError):
        prepare(reseal(x))


@pytest.mark.parametrize(
    "name", ["securities", "prices", "status", "exposures", "permissions", "account", "scores"]
)
@pytest.mark.parametrize("clock", ["event_time", "available_at", "as_of"])
def test_every_input_clock_boundary(name, clock):
    x = fixture()
    e = x["inputs"][name]
    if name == "scores":
        e = e[0]
    e[clock] = "2024-02-01T16:00:00.000001Z"
    with pytest.raises(ContractError):
        prepare(reseal(x))


@pytest.mark.parametrize(
    "name", ["securities", "prices", "status", "exposures", "permissions", "account", "scores"]
)
def test_every_input_context_must_align(name):
    x = fixture()
    e = x["inputs"][name]
    if name == "scores":
        e = e[0]
    e["context"] = deepcopy(e["context"])
    e["context"]["snapshot_id"] = "other"
    with pytest.raises(ContractError, match="CONTEXT_MISMATCH"):
        prepare(reseal(x))


@pytest.mark.parametrize(
    "name", ["securities", "prices", "status", "exposures", "permissions", "scores"]
)
def test_row_future_not_hidden_by_header(name):
    x = fixture()
    rows = (
        x["inputs"][name]["data"] if name != "scores" else x["inputs"]["scores"][0]["data"]["rows"]
    )
    rows[0]["available_at"] = "2024-02-01T16:00:00.000001Z"
    with pytest.raises(ContractError):
        prepare(reseal(x))


@pytest.mark.parametrize(
    "path",
    [
        "schema_version",
        "context.currency",
        "profile.fee_reserve",
        "policy.gross",
        "constraints.beta_max",
        "inputs",
        "inputs.prices.data.0.price",
    ],
)
def test_unknown_or_missing_fields(path):
    x = fixture()
    parts = path.split(".")
    o = x
    for k in parts[:-1]:
        o = o[int(k)] if isinstance(o, list) else o[k]
    del o[parts[-1]]
    with pytest.raises(ContractError):
        prepare(PortfolioRequest.create(x))


def test_hash_duplicate_and_invalid_json():
    x = fixture()
    x["inputs"]["prices"]["data"][0]["price"] = "99"
    with pytest.raises(ContractError, match="INPUT_HASH_MISMATCH"):
        prepare(PortfolioRequest.create(x))
    for raw in [b'{"a":1,"a":2}', b'{"a":NaN}', b"not-json", b"\xff"]:
        with pytest.raises(ContractError):
            load(raw)
    x = fixture()
    x["inputs"]["prices"]["data"].append(deepcopy(x["inputs"]["prices"]["data"][0]))
    with pytest.raises(ContractError, match="DUPLICATE_SECURITY"):
        prepare(reseal(x))
    x = fixture()
    x["inputs"]["account"]["data"]["positions"] *= 2
    with pytest.raises(ContractError, match="INVALID_POSITION"):
        prepare(reseal(x))
    x = fixture()
    s = deepcopy(x["inputs"]["scores"][0])
    x["inputs"]["scores"].append(s)
    with pytest.raises(ContractError):
        prepare(reseal(x))
    x = fixture()
    x["inputs"]["exposures"]["data"] = []
    with pytest.raises(ContractError, match="MISSING_SECURITY_INPUT"):
        prepare(reseal(x))


@pytest.mark.parametrize(
    "value",
    [True, False, 1, 1.5, None, [], {}, "nan", "Infinity", "1e101", "1e-101", "x", "1" * 35],
)
def test_money_is_finite_decimal_string(value):
    with pytest.raises(ContractError):
        number(value)


def test_exact_float_score_projection_and_timezone_equivalence():
    assert number(0.5, score=True) == number("0.5")
    for value in [float("inf"), float("nan")]:
        with pytest.raises(ContractError):
            number(value, score=True)
    x = fixture()
    x["inputs"]["prices"]["context"]["decision_time"] = "2024-02-02T00:00:00+08:00"
    x["inputs"]["prices"]["as_of"] = "2024-02-02T00:00:00+08:00"
    prepare(reseal(x))


@pytest.mark.parametrize(
    "func,value",
    [
        (identifier, ""),
        (identifier, 5),
        (identifier, "x" * 257),
        (checksum, "a"),
        (checksum, None),
        (boolean, 1),
        (integer, True),
        (integer, -1),
    ],
)
def test_primitive_type_guards(func, value):
    with pytest.raises(ContractError):
        func(value)


def test_not_a_frozen_request_and_unknown_manifest():
    with pytest.raises(ContractError):
        prepare({})
    x = fixture()
    x["source"]["fixture_manifest"]["unknown"] = "0" * 64
    with pytest.raises(ContractError, match="MANIFEST_MEMBERSHIP_MISMATCH"):
        prepare(PortfolioRequest.create(x))
    x = fixture()
    x["inputs"]["prices"]["schema_version"] = "wrong"
    with pytest.raises(ContractError):
        prepare(reseal(x))
    x = fixture()
    x["inputs"]["status"]["data"] = {}
    with pytest.raises(ContractError):
        prepare(reseal(x))
    x = fixture()
    x["inputs"]["scores"][0]["data"]["rows"][0]["valid"] = False
    with pytest.raises(ContractError):
        prepare(reseal(x))


def test_raw_input_bytes_are_immutable_copy():
    x = fixture()
    r = PortfolioRequest.create(x)
    before = r.raw
    x["policy"]["mode"] = "OTHER"
    assert r.raw == before and r.content_hash
    y = load(r.raw)
    y["policy"]["mode"] = "OTHER"
    assert load(r.raw)["policy"]["mode"] == "LONG_ONLY"
    assert canonical(load(r.raw)) == r.raw


@pytest.mark.parametrize("bad", [True, "text", bytearray(b"{}")])
def test_raw_request_must_be_immutable_bytes(bad):
    with pytest.raises(ContractError):
        PortfolioRequest(bad)


@pytest.mark.parametrize("version", ["latest", "*", "1", ">=1.0.0"])
def test_exact_factor_version_not_alias(version):
    x = fixture()
    x["inputs"]["scores"][0]["data"]["factor_ref"]["factor_version"] = version
    with pytest.raises(ContractError):
        prepare(reseal(x))


def test_calendar_mapping_cannot_claim_yesterday_is_current_session():
    x = fixture()
    row = x["inputs"]["scores"][0]["data"]["rows"][0]
    row.update(signal_time="2024-01-31T16:00:00Z", event_time="2024-01-31T16:00:00Z")
    with pytest.raises(ContractError, match="SCORE_SESSION_MAPPING_MISMATCH"):
        prepare(reseal(x))
    x = fixture()
    x["context"]["calendar_id"] = "REAL_CALENDAR"
    with pytest.raises(ContractError, match="UNSUPPORTED_SYNTHETIC_CALENDAR"):
        prepare(reseal(x))


def test_oversized_integer_score_rejected_not_overflow():
    with pytest.raises(ContractError):
        number(10**1000, score=True)
