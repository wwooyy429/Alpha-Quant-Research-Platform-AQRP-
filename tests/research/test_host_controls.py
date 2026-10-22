"""OS policy logic simulations. These fixtures do not deploy/verify real isolation."""

import json
import stat
import sys
from types import SimpleNamespace

import pytest

from aqrp.core.errors import ContractError
from aqrp.validation import evaluator as module


def host(tmp_path):
    root = tmp_path / "sealed"
    root.mkdir()
    key = root / "operator-key"
    key.write_bytes(b"unit-fixture-not-an-actual-key" * 2)
    return module.OperatorPolicy(
        root, key, evaluator="1", research="2", auditor="3", trusted_owner="0"
    )


def test_windows_acl_token_and_owner_logic(tmp_path, monkeypatch):
    policy = host(tmp_path)
    monkeypatch.setattr(module, "IS_WINDOWS", True)
    acl = {"owner": "0", "protected": True, "entries": [{"sid": "1", "type": "Allow"}]}
    output = {"groups": "standard-users", "priv": "ordinary-token"}

    def command(args, **kwargs):
        if args[0] == "powershell":
            return json.dumps(acl)
        if "/user" in args:
            return '"fixture","1"\n'
        return output["groups" if "/groups" in args else "priv"]

    monkeypatch.setattr(module.subprocess, "check_output", command)
    assert module.identity() == "1"
    assert policy.verify_host() == policy.key_file.read_bytes()
    acl["protected"] = False
    with pytest.raises(ContractError, match="UNVERIFIED_ISOLATION"):
        policy.verify_host()
    acl["protected"] = True
    acl["entries"] = [{"sid": "2", "type": "Allow"}]
    with pytest.raises(ContractError, match="UNVERIFIED_ISOLATION"):
        policy.verify_host()
    acl["entries"] = []
    acl["owner"] = "1"
    with pytest.raises(ContractError, match="UNTRUSTED_OPERATOR_KEY_OWNER"):
        policy.verify_host()
    acl["owner"] = "0"
    output["groups"] = "S-1-5-32-544"
    with pytest.raises(ContractError, match="ELEVATED_EVALUATOR_TOKEN"):
        policy.verify_host()

    acl.update(
        owner="0", protected=True, entries=[{"sid": "1", "type": "Allow", "writable": False}]
    )
    module.readonly_runtime(policy.key_file, "0", {"0", "1"}, "2")
    acl["entries"][0]["writable"] = True
    with pytest.raises(ContractError, match="WRITABLE_EVALUATOR_RUNTIME"):
        module.readonly_runtime(policy.key_file, "0", {"0", "1"}, "2")
    acl.update(owner="1", entries=[])
    with pytest.raises(ContractError, match="UNTRUSTED_RUNTIME_OWNER_OR_WRITE_MODE"):
        module.readonly_runtime(policy.key_file, "0", {"0", "1"}, "2")
    output["groups"] = "standard"
    output["priv"] = "SeDebugPrivilege"
    with pytest.raises(ContractError, match="ELEVATED_EVALUATOR_TOKEN"):
        policy.verify_host()


def test_posix_uid_group_and_mode_logic(tmp_path, monkeypatch):
    policy = host(tmp_path)
    monkeypatch.setattr(module, "IS_WINDOWS", False)
    monkeypatch.setattr(module.os, "geteuid", lambda: 1, raising=False)
    acl_state = {"values": []}
    monkeypatch.setattr(module.os, "listxattr", lambda p: acl_state["values"], raising=False)
    monkeypatch.setattr(module.os, "getgrouplist", lambda name, gid: [gid], raising=False)
    monkeypatch.setitem(
        sys.modules,
        "pwd",
        SimpleNamespace(
            getpwuid=lambda uid: SimpleNamespace(
                pw_name="research" if uid == 2 else "auditor", pw_gid=20 if uid == 2 else 30
            )
        ),
    )
    # File metadata is simulated; no ownership or mode changes are performed.
    from pathlib import Path

    actual_stat = Path.stat
    state = {"uid": 0, "gid": 10, "mode": 0o600, "links": 1}

    def metadata(path, *args, **kwargs):
        real = actual_stat(path, *args, **kwargs)
        return SimpleNamespace(
            st_uid=state["uid"],
            st_gid=state["gid"],
            st_mode=stat.S_IFMT(real.st_mode) | state["mode"],
            st_nlink=state["links"],
        )

    monkeypatch.setattr(Path, "stat", metadata)
    assert module.identity() == "1"
    assert policy.verify_host() == policy.key_file.read_bytes()
    module.readonly_runtime(policy.key_file, "0", set(), "2")
    acl_state["values"] = ["system.posix_acl_access"]
    with pytest.raises(ContractError, match="UNVERIFIED_EXTENDED_ACL"):
        policy.verify_host()
    acl_state["values"] = []
    state["mode"] = 0o620
    with pytest.raises(ContractError, match="UNTRUSTED_RUNTIME_OWNER_OR_WRITE_MODE"):
        module.readonly_runtime(policy.key_file, "0", set(), "2")
    state["mode"] = 0o600
    state["mode"] = 0o604
    with pytest.raises(ContractError, match="UNVERIFIED_ISOLATION"):
        policy.verify_host()
    state["mode"] = 0o640
    with pytest.raises(ContractError, match="UNVERIFIED_ISOLATION"):
        policy.verify_host()
    state["mode"] = 0o600
    state["uid"] = 1
    with pytest.raises(ContractError, match="UNTRUSTED_OPERATOR_KEY_OWNER"):
        policy.verify_host()
    state["uid"] = 0
    state["links"] = 2
    with pytest.raises(ContractError, match="SEALED_PATH_LINK"):
        policy.verify_host()
    state["links"] = 1
    policy.groups = {20}
    with pytest.raises(ContractError, match="SHARED_OR_ELEVATED_PRINCIPAL"):
        policy.verify_host()
    policy.groups = {30}
    state.update(gid=30, mode=0o640)
    with pytest.raises(ContractError, match="OPERATOR_KEY_SHARED_WITH_AUDITOR"):
        policy.verify_host()
    policy.owner = "4"
    policy.auditor = "0"
    with pytest.raises(ContractError, match="SHARED_OR_ELEVATED_PRINCIPAL"):
        policy.verify_host()


@pytest.mark.parametrize("role,value", [("research", "0"), ("auditor", "0"), ("research", "")])
def test_all_four_principals_are_distinct_before_any_private_read(
    tmp_path, monkeypatch, role, value
):
    policy = host(tmp_path)
    monkeypatch.setattr(module, "identity", lambda: "1")
    setattr(policy, role, value)
    with pytest.raises(ContractError, match="WRONG_EVALUATOR_PRINCIPAL"):
        policy.verify_host()


def test_windows_auditor_readonly_and_no_operator_key_access(tmp_path, monkeypatch):
    acl = {
        "owner": "0",
        "protected": True,
        "entries": [{"sid": "3", "type": "Allow", "writable": False}],
    }
    monkeypatch.setattr(module.subprocess, "check_output", lambda *a, **k: json.dumps(acl))
    assert module._windows_permissions(tmp_path, {"0", "1", "3"}, "2", auditor="3") == "0"
    with pytest.raises(ContractError, match="UNVERIFIED_ISOLATION"):
        module._windows_permissions(tmp_path, {"0", "1"}, "2", auditor="3")
    acl["entries"][0]["writable"] = True
    with pytest.raises(ContractError, match="WRITABLE_AUDITOR_DOMAIN"):
        module._windows_permissions(tmp_path, {"0", "1", "3"}, "2", auditor="3")


def test_constructor_link_rejection(tmp_path, monkeypatch):
    from pathlib import Path

    monkeypatch.setattr(Path, "is_symlink", lambda self: True)
    with pytest.raises(ContractError, match="SEALED_PATH_LINK"):
        module.OperatorPolicy(
            tmp_path, tmp_path / "key", evaluator="1", research="2", auditor="3", trusted_owner="0"
        )
