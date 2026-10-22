"""Independent ACL counterexamples. Model tests are NOT three-principal OS evidence."""

import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from aqrp.core.errors import ContractError
from aqrp.validation import windows_acl as m
from aqrp.validation.evaluator import OperatorPolicy


def policy(root):
    return m.WindowsTreePolicy(
        root,
        owner="operator",
        evaluator="eval",
        research="research",
        auditor="audit",
        inherited_roots=(root,),
    )


def row(p, *, directory=True, inherited=False, readonly=False, key=False):
    flags = 3 if directory else 0
    aces = [
        (m.OWNER_RIGHTS, "Deny", 0xC0000),
        ("operator", "Allow", 0x1F01FF),
        (m.SYSTEM, "Allow", 0x1F01FF),
        (m.ADMINS, "Allow", 0x1F01FF),
        ("eval", "Allow", 0x1200A9 if readonly else 0x1301BF),
    ]
    if not key:
        aces.append(("audit", "Allow", 0x1200A9))
    return {
        "path": str(p),
        "owner": "eval" if inherited else "operator",
        "protected": not inherited,
        "entries": [
            {
                "sid": s,
                "type": t,
                "mask": v,
                "inheritance": flags,
                "propagation": 0,
                "inherited": inherited,
            }
            for s, t, v in aces
        ],
    }


def tree(tmp_path):
    root = tmp_path / "sealed"
    dirs = {root: True, root / "work": True, root / "work/access.jsonl": False}
    rows = [row(p, directory=d, inherited=p != root) for p, d in dirs.items()]
    return policy(root), rows, dirs


def test_valid_dynamic_chain_and_previous_owner_rights_gap(tmp_path):
    p, rows, dirs = tree(tmp_path)
    assert p.verify_rows(rows, dirs)
    # The actual R2 shape had no OW deny: it must remain rejected, not retro-pass.
    for r in rows:
        r["entries"] = [e for e in r["entries"] if e["sid"] != m.OWNER_RIGHTS]
    with pytest.raises(ContractError, match="UNPROVEN_WINDOWS_EFFECTIVE_ACL"):
        p.verify_rows(rows, dirs)


@pytest.mark.parametrize(
    "mutation",
    [
        "broad",
        "auditor_write",
        "eval_dacl",
        "ow_allow",
        "missing_ow",
        "duplicate",
        "generic",
        "propagation",
        "no_inherit",
        "inherit_only",
        "bool_mask",
        "extra_deny",
    ],
)
def test_effective_permission_counterexamples(tmp_path, mutation):
    p, rows, dirs = tree(tmp_path)
    es = rows[-1]["entries"]
    if mutation == "broad":
        es[-1]["sid"] = "S-1-1-0"
    if mutation == "auditor_write":
        es[-1]["mask"] |= 2
    if mutation == "eval_dacl":
        es[-2]["mask"] |= 0x40000
    if mutation == "ow_allow":
        es[0]["type"] = "Allow"
    if mutation == "missing_ow":
        es.pop(0)
    if mutation == "duplicate":
        es.append(copy.deepcopy(es[-1]))
    if mutation == "generic":
        es[-1]["mask"] = 0x80000000
    if mutation == "propagation":
        es[-1]["propagation"] = 1
    if mutation == "no_inherit":
        es[-1]["inheritance"] = 1
    if mutation == "inherit_only":
        es[-1]["propagation"] = 2
    if mutation == "bool_mask":
        es[-1]["mask"] = True
    if mutation == "extra_deny":
        es.append({**es[0], "sid": "audit"})
    with pytest.raises(ContractError):
        p.verify_rows(rows, dirs)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "duplicate",
        "owner",
        "outside",
        "no_anchor",
        "protected_eval",
        "protected_inherited",
        "explicit_child",
        "flag_type",
        "inherited_type",
        "not_directory",
        "key_inherited",
        "missing_anchor",
        "parent_projection",
    ],
)
def test_trust_and_complete_chain_counterexamples(tmp_path, mutation):
    p, rows, dirs = tree(tmp_path)
    key = None
    if mutation == "missing":
        rows.pop()
    if mutation == "duplicate":
        rows.append(rows[-1])
    if mutation == "owner":
        rows[-1]["owner"] = "attacker"
    if mutation == "outside":
        r = rows.pop()
        dirs.pop(Path(r["path"]))
        r["path"] = str(tmp_path / "outside")
        rows.append(r)
        dirs[Path(r["path"])] = False
    if mutation == "no_anchor":
        p.inherited_roots = frozenset()
    if mutation == "protected_eval":
        rows[-1]["protected"] = True
    if mutation == "protected_inherited":
        rows[0]["entries"][0]["inherited"] = True
    if mutation == "explicit_child":
        rows[-1]["entries"][0]["inherited"] = False
    if mutation == "flag_type":
        rows[-1]["protected"] = 0
    if mutation == "inherited_type":
        rows[-1]["entries"][0]["inherited"] = 1
    if mutation == "not_directory":
        dirs[p.root / "work"] = False
    if mutation == "key_inherited":
        key = Path(rows[-1]["path"])
    if mutation == "missing_anchor":
        p.inherited_roots |= {p.root / "absent"}
    if mutation == "parent_projection":
        # Independently valid RO protected parent cannot justify RW inherited child.
        rows[1] = row(p.root / "work", readonly=True)
        p.readonly_roots = frozenset({p.root / "work"})
        rows[-1] = row(p.root / "work/access.jsonl", directory=False, inherited=True, readonly=True)
        # Root and work are RO-valid, but alter the parent only after its self-check
        # via a direct mismatched key-child role projection.
        key = p.root / "work/access.jsonl"
    with pytest.raises(ContractError):
        p.verify_rows(rows, dirs, key_file=key)


def test_protected_readonly_input_and_key(tmp_path):
    p, rows, dirs = tree(tmp_path)
    root = p.root
    inp = root / "inputs"
    data = inp / "snapshot"
    key = root / "key"
    p.readonly_roots = frozenset({inp})
    rows += [
        row(inp, readonly=True),
        {**row(data, inherited=True, readonly=True), "owner": "operator"},
        row(key, directory=False, readonly=True, key=True),
    ]
    dirs.update({inp: True, data: True, key: False})
    assert p.verify_rows(rows, dirs, key_file=key)
    wrong = copy.deepcopy(rows)
    wrong[-1]["owner"] = "eval"
    with pytest.raises(ContractError):
        p.verify_rows(wrong, dirs, key_file=key)
    wrong = copy.deepcopy(rows)
    wrong[-2]["owner"] = "eval"
    with pytest.raises(ContractError, match="OPERATOR_PREBUILT_INPUT_REQUIRED"):
        p.verify_rows(wrong, dirs, key_file=key)
    assert p.binding != policy(root).binding


def test_policy_and_ancestor_bindings(tmp_path):
    p, rows, dirs = tree(tmp_path)
    with pytest.raises(ContractError):
        m.WindowsTreePolicy(p.root, owner="eval", evaluator="eval", research="r", auditor="a")
    with pytest.raises(ContractError):
        m.WindowsTreePolicy(
            p.root, owner="o", evaluator="e", research="r", auditor="a", inherited_roots=(tmp_path,)
        )
    ancestors = [row(a, readonly=True) for a in p.root.parents]
    p.verify_ancestors(ancestors)
    with pytest.raises(ContractError):
        p.verify_ancestors(ancestors[:-1])
    bad = copy.deepcopy(ancestors)
    bad[0]["owner"] = "eval"
    with pytest.raises(ContractError):
        p.verify_ancestors(bad)
    bad = copy.deepcopy(ancestors)
    bad[0]["entries"].append({"sid": "Users", "type": "Allow", "mask": 0x40, "propagation": 0})
    with pytest.raises(ContractError):
        p.verify_ancestors(bad)
    bad[0]["entries"][-1]["propagation"] = 2
    p.verify_ancestors(bad)
    root = p.root
    root.mkdir()
    (root / "key").write_bytes(b"test-only")
    p.key_file = root / "key"
    OperatorPolicy(
        root,
        root / "key",
        trusted_owner="operator",
        evaluator="eval",
        research="research",
        auditor="audit",
        windows_tree_policy=p,
    )
    with pytest.raises(ContractError, match="BINDING_MISMATCH"):
        OperatorPolicy(
            root,
            root / "key",
            trusted_owner="other",
            evaluator="eval",
            research="research",
            auditor="audit",
            windows_tree_policy=p,
        )


def test_capture_and_live_tree_lifecycle(tmp_path, monkeypatch):
    root = tmp_path / "sealed"
    root.mkdir()
    (root / "work").mkdir()
    (root / "work/a").write_bytes(b"actual-file")
    p = policy(root)
    paths = [root, root / "work", root / "work/a"]
    rows = [row(x, directory=x.is_dir(), inherited=x != root) for x in paths]
    actual = json.dumps(rows).encode()
    monkeypatch.setattr(m.subprocess, "check_output", lambda argv, **kw: actual)
    assert m.read_descriptors(paths) == rows
    # Fake OS adapter ONLY tests proof orchestration; this is not a token test.
    monkeypatch.setattr(m, "os", SimpleNamespace(name="nt", walk=os.walk))
    monkeypatch.setattr(
        m,
        "read_descriptors",
        lambda ps: rows if ps and ps[0] == root else [row(a, readonly=True) for a in root.parents],
    )
    assert p.verify()["objects"] == 3
    calls = 0

    def changing(ps):
        nonlocal calls
        if ps[0] != root:
            return [row(a, readonly=True) for a in root.parents]
        calls += 1
        return rows if calls == 1 else rows[:-1]

    monkeypatch.setattr(m, "read_descriptors", changing)
    with pytest.raises(ContractError, match="ACL_TREE_CHANGED"):
        p.verify()
    monkeypatch.setattr(m, "os", SimpleNamespace(name="posix"))
    with pytest.raises(ContractError, match="WINDOWS_NTFS_REQUIRED"):
        p.verify()


def test_incomplete_and_replaced_objects_fail_closed(tmp_path, monkeypatch):
    root = tmp_path / "sealed"
    root.mkdir()
    child = root / "a"
    child.write_bytes(b"a")
    p = policy(root)
    monkeypatch.setattr(m, "os", SimpleNamespace(name="nt", walk=os.walk))

    def descriptors(paths):
        if paths[0] != root:
            return [row(a, readonly=True) for a in root.parents]
        return [row(root), row(child, directory=False, inherited=True)]

    monkeypatch.setattr(m, "read_descriptors", descriptors)
    assert p.verify()["objects"] == 2
    os.link(child, root / "hardlink")
    with pytest.raises(ContractError, match="SEALED_PATH_LINK"):
        p.verify()
    (root / "hardlink").unlink()
    original = m.read_descriptors

    def new_member(paths):
        result = original(paths)
        if paths[0] == root:
            (root / "new").write_bytes(b"x")
        return result

    monkeypatch.setattr(m, "read_descriptors", new_member)
    with pytest.raises(ContractError, match="ACL_TREE_CHANGED"):
        p.verify()
    (root / "new").unlink()

    def replace_member(paths):
        result = original(paths)
        if paths[0] == root:
            child.rename(tmp_path / "old-a")
            child.write_bytes(b"new")
        return result

    monkeypatch.setattr(m, "read_descriptors", replace_member)
    with pytest.raises(ContractError, match="ACL_TREE_CHANGED"):
        p.verify()


def test_new_acl_policy_requires_new_signed_authorization(tmp_path, monkeypatch):
    from aqrp.core.canonical import canonical
    from aqrp.validation import evaluator

    root = tmp_path / "sealed"
    root.mkdir()
    key = root / "key"
    key.write_bytes(b"test-only-generated-key-material-0000")
    p = policy(root)
    p.key_file = key
    op = OperatorPolicy(
        root,
        key,
        evaluator="eval",
        research="research",
        auditor="audit",
        trusted_owner="operator",
        windows_tree_policy=p,
    )
    monkeypatch.setattr(op, "verify_host", lambda: key.read_bytes())
    (root / "authorization.json").write_bytes(canonical(evaluator.seal({}, key.read_bytes())))
    with pytest.raises(ContractError, match="WINDOWS_ACL_PROFILE_NOT_AUTHORIZED"):
        op.authorize({})
    # Windows branch really calls the bound verifier; mocked token is not OS proof.
    called = []
    monkeypatch.setattr(evaluator, "IS_WINDOWS", True)
    monkeypatch.setattr(evaluator, "identity", lambda: "eval")
    monkeypatch.setattr(
        evaluator.subprocess, "check_output", lambda *a, **k: "no privileged groups"
    )
    monkeypatch.setattr(p, "verify", lambda **kw: called.append(kw))
    del op.verify_host
    assert op.verify_host() == key.read_bytes() and called == [{"key_file": key}]


def test_private_key_bound_to_full_publication_gate(tmp_path, monkeypatch):
    root = tmp_path / "sealed"
    root.mkdir()
    key = root / "key"
    key.write_bytes(b"fixture-only")
    p = policy(root)
    p.key_file = key
    rows = [row(root), row(key, directory=False, readonly=True, key=True)]
    monkeypatch.setattr(m, "os", SimpleNamespace(name="nt", walk=os.walk))
    monkeypatch.setattr(
        m,
        "read_descriptors",
        lambda paths: rows if paths[0] == root else [row(a, readonly=True) for a in root.parents],
    )
    assert p.verify()["objects"] == 2
    missing = {root: True}
    with pytest.raises(ContractError, match="MISSING_OR_INVALID_OPERATOR_KEY"):
        p.verify_rows(rows[:1], missing)
    with pytest.raises(ContractError, match="MISSING_OR_INVALID_OPERATOR_KEY"):
        p.verify_rows(rows, {root: True, key: True})
    with pytest.raises(ContractError, match="ACL_KEY_OUTSIDE_ROOT"):
        m.WindowsTreePolicy(
            root, owner="o", evaluator="e", research="r", auditor="a", key_file=tmp_path / "outside"
        )
