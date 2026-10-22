"""R3 adversarial regressions using model ACLs/tokens, never real role execution."""

import copy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_windows_acl import policy, row
from test_windows_probe_contract import module

from aqrp.core.errors import ContractError
from aqrp.validation import windows_acl as m


def test_r3_001_real_walk_cannot_certify_incomplete_subset(tmp_path, monkeypatch):
    root = tmp_path / "sealed"
    (root / "work").mkdir(parents=True)
    (root / "work/unseen.json").write_bytes(b"engineering data, must not be skipped")
    monkeypatch.setattr(m, "os", SimpleNamespace(name="nt", walk=os.walk))
    monkeypatch.setattr(
        m,
        "read_descriptors",
        lambda paths: [
            row(
                p,
                directory=p.is_dir(),
                inherited=p != root and p.is_relative_to(root),
                readonly=not p.is_relative_to(root),
            )
            for p in paths
        ],
    )
    proof = policy(root)
    assert proof.verify()["objects"] == 3
    original = os.scandir

    def denied(path):
        if Path(path) == root / "work":
            raise PermissionError(13, "model injected error", str(path))
        return original(path)

    monkeypatch.setattr(os, "scandir", denied)
    with pytest.raises(ContractError, match="ACL_ENUMERATION_FAILED"):
        proof.verify()


def test_r3_002_hash_string_without_authoritative_inventory_must_reject(tmp_path):
    objects = []
    for i in range(11):
        p = tmp_path / str(i)
        p.write_bytes(str(i).encode())
        objects.append(
            {
                "path": str(p),
                "kind": "snapshot_input"
                if i < 9
                else ("publication_sidecar" if i == 9 else "dynamic_product"),
                "bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
        )
    cfg = {
        "scope": "ENGINEERING_DEMO_ONLY",
        "principals": {"research": "r", "evaluator": "e", "auditor": "a", "operator": "o"},
        "objects": objects[:10],
        "operator_inventory_sha256": "f" * 64,
        "attempt_id": "model-only",
        "phase": "after",
    }
    with pytest.raises(ValueError):
        module().probe(
            cfg,
            "research",
            get_token=lambda: {"sid": "r", "elevated": False},
            open_access=lambda p, m: {"opened": False, "winerror": 5},
        )


@pytest.mark.parametrize("failure", ["is_dir", "stat"])
def test_directory_entry_errors_cannot_hide_a_real_subtree(tmp_path, monkeypatch, failure):
    root = tmp_path / "sealed"
    (root / "work").mkdir(parents=True)
    (root / "work/unseen").write_bytes(b"must be covered")
    monkeypatch.setattr(m, "os", SimpleNamespace(name="nt", walk=os.walk))
    monkeypatch.setattr(
        m,
        "read_descriptors",
        lambda paths: [
            row(
                p,
                directory=p.is_dir(),
                inherited=p != root and p.is_relative_to(root),
                readonly=not p.is_relative_to(root),
            )
            for p in paths
        ],
    )
    original = os.scandir

    class Entry:
        def __init__(self, e):
            self.e = e

        def __getattr__(self, k):
            return getattr(self.e, k)

        def is_dir(self, *a, **kw):
            if self.e.name == "work":
                raise PermissionError(13, "injected entry classification failure", self.e.path)
            return self.e.is_dir(*a, **kw)

        def stat(self, *a, **kw):
            if self.e.name == "work" and failure == "stat":
                raise PermissionError(13, "injected entry stat failure", self.e.path)
            return self.e.stat(*a, **kw)

    class Scan:
        def __init__(self, path):
            self.native = original(path)

        def __iter__(self):
            return self

        def __next__(self):
            return Entry(next(self.native))

        def __enter__(self):
            self.native.__enter__()
            return self

        def __exit__(self, *a):
            return self.native.__exit__(*a)

    monkeypatch.setattr(os, "scandir", Scan)
    if failure == "is_dir":
        # A strict collector may avoid the error-prone is_dir API entirely.
        assert policy(root).verify()["objects"] == 3
    else:
        with pytest.raises(ContractError, match="ACL_ENUMERATION_FAILED"):
            policy(root).verify()


@pytest.mark.parametrize("phase", ["before", "after"])
@pytest.mark.parametrize("error", [PermissionError, FileNotFoundError, OSError])
def test_each_traversal_stage_preserves_native_error(tmp_path, monkeypatch, phase, error):
    root = tmp_path / "sealed"
    (root / "work").mkdir(parents=True)
    (root / "work/a").write_bytes(b"x")
    p = policy(root)

    def descriptors(paths):
        return [
            row(
                q,
                directory=q.is_dir(),
                inherited=q != root and q.is_relative_to(root),
                readonly=not q.is_relative_to(root),
            )
            for q in paths
        ]

    monkeypatch.setattr(m, "read_descriptors", descriptors)
    calls = 0

    original_scan = os.scandir

    def scan(path):
        nonlocal calls
        if Path(path) == root / "work":
            calls += 1
        if Path(path) == root / "work" and calls == (1 if phase == "before" else 2):
            errno = {PermissionError: 13, FileNotFoundError: 2, OSError: 5}[error]
            raise error(errno, "injected native collection failure", str(root / "work"))
        return original_scan(path)

    monkeypatch.setattr(m, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(os, "scandir", scan)
    with pytest.raises(ContractError, match="ACL_ENUMERATION_FAILED") as caught:
        p.verify()
    detail = json.loads(caught.value.field)
    assert detail["phase"] == phase and detail["path"] == str(root / "work")
    assert detail["errno"] == {PermissionError: 13, FileNotFoundError: 2, OSError: 5}[error]
    assert detail["error_type"] == error.__name__
    assert caught.value.__cause__ is not None


@pytest.mark.parametrize("phase", ["before", "after"])
def test_missing_object_metadata_is_structured(tmp_path, phase):
    with pytest.raises(ContractError, match="ACL_TREE_METADATA_FAILED") as e:
        m.tree_stat(tmp_path / "missing", phase)
    assert json.loads(e.value.field)["phase"] == phase


def test_walk_itself_raising_io_error_fails_closed(tmp_path, monkeypatch):
    def walk(*a, **kw):
        raise OSError(5, "injected IO", str(tmp_path))

    monkeypatch.setattr(os, "scandir", walk)
    with pytest.raises(ContractError, match="ACL_ENUMERATION_FAILED"):
        m.enumerate_tree(tmp_path, "after")


def test_complete_directory_file_and_private_key_coverage_requires_reconciliation(
    tmp_path, monkeypatch, tables, make_snapshot
):
    from windows_model import model_tree, perform

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    results = [perform(probe, raw, cfg, role) for role in ("research", "evaluator", "auditor")]
    for result in results:
        assert (
            result["listed_checks_pass"]
            and not result["coverage_verified"]
            and not result["all_pass"]
        )
        for item in cfg["objects"]:
            if item["object_type"] == "directory":
                checks = [c for c in result["checks"] if c["path"] == item["path"]]
                assert any(
                    c["operation"] == "delete_child"
                    and c["observed"]["mask"] == 0x40
                    and not c["expected_open"]
                    for c in checks
                )
                assert not any(c["operation"] == "actual_bytes" for c in checks)
        keychecks = [c for c in result["checks"] if c["path"] == str(p.key_file)]
        assert next(c for c in keychecks if c["operation"] == "read")["expected_open"] == (
            result["role"] == "evaluator"
        )
    reconciled = probe.reconcile(
        cfg, raw, cfg["operator_inventory_sha256"], results, get_token=owner
    )
    assert reconciled["coverage_verified"] and reconciled["all_pass"]
    assert (
        not reconciled["real_token_claims"]
        and reconciled["overall_windows_isolation"] == "NOT_VERIFIED"
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "omit_dynamic",
        "omit_directory",
        "extra",
        "hash",
        "attempt",
        "phase",
        "root",
        "policy",
        "principals",
    ],
)
def test_config_tamper_cannot_keep_authoritative_full_hash(
    tmp_path, monkeypatch, tables, make_snapshot, mutation
):
    from windows_model import model_tree, perform

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    if mutation == "omit_dynamic":
        cfg["objects"] = [r for r in cfg["objects"] if r["kind"] != "dynamic_product"]
    if mutation == "omit_directory":
        cfg["objects"] = [r for r in cfg["objects"] if r["path"] != str(p.root / "work")]
    if mutation == "extra":
        cfg["objects"].append(copy.deepcopy(cfg["objects"][0]))
    if mutation == "hash":
        cfg["operator_inventory_sha256"] = "0" * 64
    if mutation == "attempt":
        cfg["attempt_id"] = "00000000-0000-4000-8000-000000000001"
    if mutation == "phase":
        cfg["phase"] = "after"
    if mutation == "root":
        cfg["root"] = str(tmp_path)
    if mutation == "policy":
        cfg["policy_binding"] = "0" * 64
    if mutation == "principals":
        cfg["principals"]["auditor"] = "different"
    for role in ("research", "evaluator", "auditor"):
        with pytest.raises(ValueError):
            perform(probe, raw, cfg, role)


@pytest.mark.parametrize(
    "mutation",
    [
        "type",
        "members",
        "gate_subset",
        "duplicate",
        "relative",
        "outside",
        "gate_error",
        "gate_hash",
        "state_hash",
    ],
)
def test_inventory_internal_proof_or_boundary_error_rejected(
    tmp_path, monkeypatch, tables, make_snapshot, mutation
):
    from windows_model import model_tree, reseal_inventory

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    inv = json.loads(raw)
    if mutation == "type":
        inv["objects"][0]["object_type"] = "file"
    if mutation == "members":
        inv["objects"][0]["members"] = []
    if mutation == "gate_subset":
        inv["gate"]["tree_objects"] = inv["gate"]["tree_objects"][:-1]
    if mutation == "duplicate":
        inv["objects"].append(inv["objects"][-1])
    if mutation == "relative":
        inv["objects"][-1]["path"] = "relative"
    if mutation == "outside":
        inv["objects"][-1]["path"] = str(tmp_path / "outside")
    if mutation == "gate_error":
        inv["enumeration_complete"] = False
    if mutation == "gate_hash":
        inv["gate_after_sha256"] = "0" * 64
    if mutation == "state_hash":
        inv["tree_state_sha256"] = "0" * 64
    new = (
        raw
        if mutation == "none"
        else (json.dumps(inv).encode() if mutation == "state_hash" else reseal_inventory(inv))
    )
    with pytest.raises(ValueError):
        probe.inventory_document(new, hashlib.sha256(new).hexdigest())


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_role",
        "missing_check",
        "wrong_sid",
        "wrong_phase",
        "bad_access",
        "bad_content",
        "drift",
        "untrusted_operator",
    ],
)
def test_reconciliation_rechecks_full_coverage_and_fresh_real_tree(
    tmp_path, monkeypatch, tables, make_snapshot, mutation
):
    from windows_model import model_tree, perform

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    results = [perform(probe, raw, cfg, role) for role in ("research", "evaluator", "auditor")]
    if mutation == "missing_role":
        results = results[:2]
    if mutation == "missing_check":
        results[0]["checks"] = results[0]["checks"][:-1]
    if mutation == "wrong_sid":
        results[0]["token"]["sid"] = "wrong"
    if mutation == "wrong_phase":
        results[0]["phase"] = "after"
    if mutation == "bad_access":
        results[0]["checks"][0]["observed"]["winerror"] = 2
    if mutation == "bad_content":
        next(c for c in results[1]["checks"] if c["operation"] == "actual_bytes")["sha256"] = (
            "0" * 64
        )
    if mutation == "drift":
        (p.root / "work/unlisted.json").write_bytes(b"exists but absent from inventory")
    if mutation == "untrusted_operator":

        def owner():
            return {"sid": "research", "elevated": False}

    with pytest.raises(ValueError):
        probe.reconcile(cfg, raw, cfg["operator_inventory_sha256"], results, get_token=owner)


def test_before_after_chain_all_dynamic_files_and_directories(
    tmp_path, monkeypatch, tables, make_snapshot
):
    from windows_model import model_tree, perform

    probe, p, ref, before, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    oldhash = hashlib.sha256(before).hexdigest()
    extra = p.root / "work/new-directory"
    extra.mkdir()
    (extra / "actual-product.json").write_bytes(b"new engineering output")
    after = probe.freeze_inventory(
        p,
        ref,
        cfg["attempt_id"],
        "after",
        get_token=owner,
        before_raw=before,
        before_sha256=oldhash,
    )
    inv = json.loads(after)
    assert inv["added_paths"] == sorted([str(extra), str(extra / "actual-product.json")])
    assert inv["predecessor_sha256"] == oldhash
    config = {
        k: inv[k]
        for k in ("scope", "principals", "objects", "attempt_id", "phase", "root", "policy_binding")
    }
    config["operator_inventory_sha256"] = hashlib.sha256(after).hexdigest()
    results = [perform(probe, after, config, r) for r in ("research", "evaluator", "auditor")]
    assert probe.reconcile(
        config,
        after,
        config["operator_inventory_sha256"],
        results,
        get_token=owner,
        before_raw=before,
        before_sha256=oldhash,
    )["coverage_verified"]
    with pytest.raises(ValueError):
        probe.freeze_inventory(
            p,
            ref,
            cfg["attempt_id"],
            "after",
            get_token=owner,
            before_raw=before,
            before_sha256="0" * 64,
        )
    with pytest.raises(ValueError, match="BINDING"):
        probe.freeze_inventory(
            p,
            ref,
            "00000000-0000-4000-8000-000000000001",
            "after",
            get_token=owner,
            before_raw=before,
            before_sha256=oldhash,
        )


@pytest.mark.parametrize(
    "mutation", ["key_changed", "elevated_operator", "wrong_phase", "missing_predecessor"]
)
def test_operator_capture_rejects_unsafe_lifecycle(
    tmp_path, monkeypatch, tables, make_snapshot, mutation
):
    from windows_model import model_tree

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    phase = "after"
    before = raw
    if mutation == "key_changed":
        p.key_file.write_bytes(b"changed model-only key")
    if mutation == "elevated_operator":

        def owner():
            return {"sid": "operator", "elevated": True}

    if mutation == "wrong_phase":
        phase = "invalid"
    if mutation == "missing_predecessor":
        before = None
    with pytest.raises(ValueError):
        probe.freeze_inventory(
            p,
            ref,
            cfg["attempt_id"],
            phase,
            get_token=owner,
            before_raw=before,
            before_sha256=cfg["operator_inventory_sha256"],
        )


@pytest.mark.parametrize("failure", ["permission", "wrong_type"])
def test_real_directory_listing_failure_never_counts_as_bytes_success(
    tmp_path, monkeypatch, tables, make_snapshot, failure
):
    from windows_model import model_tree, perform

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    target = p.root / "work"
    if failure == "permission":
        original = Path.iterdir

        def denied(path):
            if path == target:
                raise PermissionError(13, "model native enumeration denied", str(path))
            return original(path)

        monkeypatch.setattr(Path, "iterdir", denied)
    else:
        (target / "result.json").unlink()
        target.rmdir()
        target.write_bytes(b"not a directory")
    result = perform(probe, raw, cfg, "auditor")
    assert not result["listed_checks_pass"] and not result["all_pass"]
    check = next(
        c
        for c in result["checks"]
        if c["path"] == str(target) and c["operation"] == "actual_members"
    )
    assert not check["pass"]


def test_operator_config_export_is_exact_and_pin_checked(
    tmp_path, monkeypatch, tables, make_snapshot
):
    from windows_model import model_tree

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    assert probe.probe_config(raw, cfg["operator_inventory_sha256"]) == cfg
    with pytest.raises(ValueError):
        probe.probe_config(raw, "0" * 64)


def test_freeze_cli_publishes_immutable_inventory_and_derived_probe_config(
    tmp_path, monkeypatch, tables, make_snapshot, capsys
):
    import sys

    from windows_model import model_tree

    from aqrp.core.canonical import canonical

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    inv = json.loads(raw)
    config = tmp_path / "operator.json"
    config.write_bytes(
        canonical(
            {
                "policy": inv["policy"],
                "snapshot": inv["snapshot"],
                "attempt_id": inv["attempt_id"],
                "phase": "before",
            }
        )
    )
    out = tmp_path / "inventory.json"
    pc = tmp_path / "probe.json"
    original = probe.freeze_inventory

    def modeled(*args, **kw):
        return original(*args, get_token=owner, **kw)

    monkeypatch.setattr(probe, "freeze_inventory", modeled)
    monkeypatch.setattr(probe, "os", SimpleNamespace(name="nt", fstat=os.fstat))
    argv = [
        "probe",
        str(config),
        "--sha256",
        hashlib.sha256(config.read_bytes()).hexdigest(),
        "--mode",
        "freeze",
        "--output",
        str(out),
        "--probe-config-output",
        str(pc),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    probe.main()
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["sha256"] == hashlib.sha256(out.read_bytes()).hexdigest()
    assert receipt["probe_config_sha256"] == hashlib.sha256(pc.read_bytes()).hexdigest()
    assert json.loads(pc.read_bytes()) == probe.probe_config(out.read_bytes(), receipt["sha256"])
    assert receipt["overall_windows_isolation"] == "NOT_VERIFIED"
    with pytest.raises(FileExistsError):
        probe.main()


@pytest.mark.parametrize("failure", ["hash", "inside_root", "missing_inventory"])
def test_cli_cannot_bypass_hash_or_boundary(tmp_path, monkeypatch, tables, make_snapshot, failure):
    import sys

    from windows_model import model_tree

    from aqrp.core.canonical import canonical

    probe, p, ref, raw, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    inv = json.loads(raw)
    config = tmp_path / "operator.json"
    config.write_bytes(
        canonical(
            {
                "policy": inv["policy"],
                "snapshot": inv["snapshot"],
                "attempt_id": inv["attempt_id"],
                "phase": "before",
            }
        )
    )
    monkeypatch.setattr(probe, "os", SimpleNamespace(name="nt"))
    argv = ["probe", str(config), "--sha256", hashlib.sha256(config.read_bytes()).hexdigest()]
    if failure == "hash":
        argv[-1] = "0" * 64
    if failure == "inside_root":
        argv += [
            "--mode",
            "freeze",
            "--output",
            str(p.root / "inventory.json"),
            "--probe-config-output",
            str(tmp_path / "probe.json"),
        ]
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit):
        probe.main()


def test_model_full_phase_evidence_export(tmp_path, monkeypatch, tables, make_snapshot):
    """Export original model receipts for review; never substitutes for native subjects."""
    from windows_model import model_tree, perform

    from aqrp.core.canonical import canonical

    probe, p, ref, before, cfg, owner = model_tree(tmp_path, monkeypatch, tables, make_snapshot)
    output = Path(os.environ.get("AQRP_ARTIFACT_DIR", str(tmp_path))) / "windows-probe-model"
    output.mkdir()

    def store(name, value):
        (output / name).write_bytes(value if isinstance(value, bytes) else canonical(value))

    phases = []
    for phase in ("before", "after"):
        if phase == "after":
            folder = p.root / "work/new"
            folder.mkdir()
            (folder / "actual-product.json").write_bytes(b'{"model":true}')
        raw = (
            before
            if phase == "before"
            else probe.freeze_inventory(
                p,
                ref,
                cfg["attempt_id"],
                "after",
                get_token=owner,
                before_raw=before,
                before_sha256=hashlib.sha256(before).hexdigest(),
            )
        )
        sha = hashlib.sha256(raw).hexdigest()
        config = probe.probe_config(raw, sha)
        store(phase + "-inventory.json", raw)
        store(phase + "-config.json", config)
        results = [perform(probe, raw, config, r) for r in ("research", "evaluator", "auditor")]
        for r in results:
            store(phase + "-" + r["role"] + ".json", r)
        receipt = probe.reconcile(
            config,
            raw,
            sha,
            results,
            get_token=owner,
            before_raw=before if phase == "after" else None,
            before_sha256=hashlib.sha256(before).hexdigest() if phase == "after" else None,
        )
        assert receipt["coverage_verified"] and not receipt["real_token_claims"]
        store(phase + "-reconciled.json", receipt)
        phases.append(receipt)
    truncated = copy.deepcopy(config)
    truncated["objects"] = [r for r in config["objects"] if r["kind"] != "dynamic_product"]
    negatives = []
    for role in ("research", "evaluator", "auditor"):
        with pytest.raises(ValueError) as caught:
            perform(probe, raw, truncated, role)
        negatives.append(
            {
                "role": role,
                "rejected": str(caught.value),
                "original_hash_retained": truncated["operator_inventory_sha256"] == sha,
            }
        )
    store("truncated-negative.json", negatives)
    store(
        "RESULT.json",
        {
            "kind": "MODEL_ADAPTER_ONLY",
            "real_ACL_or_account_changes": False,
            "phases": phases,
            "nine_real_engineering_files_verified": 9,
            "native_three_subject_execution": "NOT_EXECUTED",
            "overall_windows_isolation": "NOT_VERIFIED",
            "formal_Test": False,
            "financial_approval": "NONE",
        },
    )
