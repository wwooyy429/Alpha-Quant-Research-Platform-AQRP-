"""Probe bookkeeping tests, distinct from actual three-token execution."""

import importlib.util
import os
from pathlib import Path

import pytest


def module():
    path = Path(__file__).parents[2] / "tools/windows_access_probe.py"
    spec = importlib.util.spec_from_file_location("probe_candidate", path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.mark.parametrize("role", ["research", "auditor", "evaluator"])
def test_actual_member_hash_and_each_access_bit(tmp_path, role, monkeypatch, tables, make_snapshot):
    from windows_model import model_tree, perform

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    result = perform(probe, raw, cfg, role)
    assert (
        result["listed_checks_pass"] and not result["coverage_verified"] and not result["all_pass"]
    )
    assert result["execution_mode"] == "MODEL_ADAPTER"
    result = perform(
        probe, raw, cfg, role, open_access=lambda p, m: {"opened": False, "winerror": 2, "mask": m}
    )
    assert not result["listed_checks_pass"]
    with pytest.raises(ValueError, match="WRONG_REAL_SUBJECT"):
        probe.probe(
            cfg,
            role,
            inventory_raw=raw,
            inventory_sha256=cfg["operator_inventory_sha256"],
            get_token=lambda: {"sid": "wrong", "elevated": False},
        )
    cfg["objects"] = cfg["objects"][:-1]
    with pytest.raises(ValueError, match="SET_OR_BINDING"):
        perform(probe, raw, cfg, role)


def test_native_readonly_metadata_capture_on_available_os(tmp_path):
    # No account/ACL changes. A current token read is NOT the required three tokens.
    if os.name == "nt":
        from aqrp.validation.windows_acl import read_descriptors

        p = tmp_path / "实际输入.json"
        p.write_bytes(b"public-engineering")
        rows = read_descriptors([p])
        assert len(rows) == 1 and rows[0]["owner"]
        probe = module()
        actual = probe.token()
        assert actual["sid"].startswith("S-1-")
        assert probe.access(p, 1)["opened"]
    else:
        assert module().__doc__.startswith("Read-only three-token engineering probe")
