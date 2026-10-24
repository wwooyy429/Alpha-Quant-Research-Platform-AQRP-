"""Managed ledger schema gates reject incomplete whole-request declarations."""

from copy import deepcopy

import pytest

from aqrp.core.errors import ContractError
from aqrp.experiments.ledger import ExperimentLedger

BASE = {
    "candidates": [{"hypothesis": "literal", "ref": {}, "parameters": {}, "direction": 1}],
    "horizons": [1],
    "family": {
        "id": "literal-family",
        "hypotheses": ["literal::h=1"],
        "definitions": {"literal::h=1": "a" * 64},
        "budget": 3,
    },
}


@pytest.mark.parametrize(
    "fault",
    [
        "no-candidates",
        "duplicate",
        "no-definitions",
        "undeclared",
        "boolean-budget",
        "bad-hash",
        "numeric-hash",
        "no-horizons",
        "bad-aliases",
    ],
)
def test_complete_units_gate_rejects_each_incomplete_schema(fault):
    cfg = deepcopy(BASE)
    if fault == "no-candidates":
        cfg["candidates"] = []
    elif fault == "duplicate":
        cfg["candidates"] *= 2
    elif fault == "no-definitions":
        del cfg["family"]["definitions"]
    elif fault == "undeclared":
        cfg["family"]["hypotheses"] = []
    elif fault == "boolean-budget":
        cfg["family"]["budget"] = True
    elif fault == "bad-hash":
        cfg["family"]["definitions"]["literal::h=1"] = "not-sha256"
    elif fault == "numeric-hash":
        cfg["family"]["definitions"]["literal::h=1"] = 1
    elif fault == "no-horizons":
        cfg["horizons"] = []
    else:
        cfg["family"]["hypothesis_aliases"] = {"unknown": "one"}
    with pytest.raises(
        ContractError, match="ADMISSION_SCHEMA_ERROR|INVALID_CAMPAIGN_HYPOTHESIS_ALIASES"
    ):
        ExperimentLedger._research_units(cfg)


def test_original_standalone_prepare_is_not_assigned_a_managed_budget(tmp_path):
    ledger = ExperimentLedger(tmp_path)
    assert ledger.prepare_research({}, {}) is None
    assert ExperimentLedger._research_units(BASE) == [
        {"hypothesis_alias": "literal::h=1", "definition_hash": "a" * 64}
    ]
