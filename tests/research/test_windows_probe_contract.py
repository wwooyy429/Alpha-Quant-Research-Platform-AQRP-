"""Probe bookkeeping tests, distinct from actual three-token execution."""

import hashlib
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
def test_actual_member_hash_and_each_access_bit(tmp_path, role):
    probe = module()
    objects = []
    for i in range(11):
        p = tmp_path / str(i)
        p.write_bytes(str(i).encode())
        objects.append(
            {
                "path": str(p),
                "bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "kind": "snapshot_input"
                if i < 9
                else ("publication_sidecar" if i == 9 else "dynamic_product"),
            }
        )
    cfg = {
        "scope": "ENGINEERING_DEMO_ONLY",
        "principals": {"research": "r", "evaluator": "e", "auditor": "a", "operator": "o"},
        "objects": objects,
        "operator_inventory_sha256": "f" * 64,
        "attempt_id": "test-only",
        "phase": "after",
    }

    def access(path, mask):
        opened = (role != "research" and mask == 1) or (
            role == "evaluator" and path.name == "10" and mask in (2, 4, 0x10000)
        )
        return {"opened": opened, "winerror": 0 if opened else 5}

    def get_token():
        return {"sid": cfg["principals"][role], "elevated": False}

    result = probe.probe(cfg, role, get_token=get_token, open_access=access)
    assert result["all_pass"] and len(result["checks"]) == (66 if role == "research" else 77)
    # A missing object / sharing violation MUST NOT be counted as access denied.
    result = probe.probe(
        cfg, role, get_token=get_token, open_access=lambda p, m: {"opened": False, "winerror": 2}
    )
    assert not result["all_pass"]
    with pytest.raises(ValueError):
        probe.probe(cfg, role, get_token=lambda: {"sid": "wrong", "elevated": False})
    cfg["objects"] = objects[:8]
    with pytest.raises(ValueError, match="ACTUAL_INPUT"):
        probe.probe(cfg, role, get_token=get_token)


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
