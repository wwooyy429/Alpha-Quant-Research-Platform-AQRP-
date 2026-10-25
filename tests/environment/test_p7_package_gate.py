"""Independent structural negative controls for the stage package admission."""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "p7_package_gate", Path(__file__).resolve().parents[2] / "tools/check_phase7_package.py"
)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


def inventories():
    return (
        {
            "old": {"bytes": 1, "sha256": "old"},
            "changed": {"bytes": 2, "sha256": "new"},
            "added": {"bytes": 3, "sha256": "added"},
        },
        [
            {"path": "old", "bytes": 1, "sha256": "old"},
            {"path": "changed", "bytes": 1, "sha256": "original"},
        ],
        [
            {"path": "changed", "bytes": 2, "sha256": "new"},
            {"path": "added", "bytes": 3, "sha256": "added"},
        ],
        {"changed": ["changed"], "added": ["added"]},
    )


def test_exact_inventory_keeps_unchanged_and_each_new_byte():
    assert GATE.verify_inventory(*inventories()) == (1, 1, 1)


@pytest.mark.parametrize(
    "mutation",
    [
        "deletion",
        "unlisted",
        "financial",
        "current_bytes",
        "missing_identity",
        "duplicate_identity",
    ],
)
def test_gate_fails_closed_for_each_inventory_discrepancy(mutation):
    actual, baseline, identity, allowed = inventories()
    if mutation == "deletion":
        del actual["old"]
    elif mutation == "unlisted":
        actual["src/aqrp/broker/undeclared.py"] = {"bytes": 1, "sha256": "new"}
    elif mutation == "financial":
        actual["old"]["sha256"] = "changed-financial-answer"
    elif mutation == "current_bytes":
        actual["added"]["sha256"] = "post-lock-change"
    elif mutation == "missing_identity":
        identity.pop()
    elif mutation == "duplicate_identity":
        identity.append(identity[-1])
    with pytest.raises(AssertionError):
        GATE.verify_inventory(actual, baseline, identity, allowed)


def test_only_one_exact_self_identity_exclusion():
    actual, baseline, identity, allowed = inventories()
    own = GATE.D + "IMPLEMENTATION_IDENTITY.json"
    actual[own] = {"bytes": 10, "sha256": "self"}
    allowed["added"].append(own)
    assert GATE.verify_inventory(actual, baseline, identity, allowed) == (1, 1, 2)
    actual[GATE.D + "injected.json"] = {"bytes": 2, "sha256": "extra"}
    with pytest.raises(AssertionError):
        GATE.verify_inventory(actual, baseline, identity, allowed)


def test_reject_links_and_rogue_files_without_ignoring_whole_source(tmp_path):
    (tmp_path / "src/aqrp").mkdir(parents=True)
    (tmp_path / "src/aqrp/x.py").write_bytes(b"x")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__/ignored.pyc").write_bytes(b"cache")
    actual = GATE.files(tmp_path)
    assert set(actual) == {"src/aqrp/x.py"}
    assert actual["src/aqrp/x.py"] == {
        "bytes": 1,
        "sha256": "2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881",
    }
