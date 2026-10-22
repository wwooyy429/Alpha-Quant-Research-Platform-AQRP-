"""Explicit fake ACL/token adapters over real engineering files, NOT isolation evidence."""

import hashlib
import os
import uuid
from types import SimpleNamespace

from test_windows_acl import row
from test_windows_probe_contract import module

from aqrp.core.canonical import canonical
from aqrp.validation import engineering_input, evaluator
from aqrp.validation import windows_acl as m


def model_tree(tmp_path, monkeypatch, tables, make_snapshot):
    root = tmp_path / "sealed"
    (root / "inputs").mkdir(parents=True)
    (root / "work").mkdir()
    key = root / "key"
    key.write_bytes(b"public-model-key-material-not-a-real-credential")
    p = m.WindowsTreePolicy(
        root,
        owner="operator",
        evaluator="eval",
        research="research",
        auditor="audit",
        inherited_roots=(root,),
        readonly_roots=(root / "inputs",),
        key_file=key,
    )
    monkeypatch.setattr(m, "os", SimpleNamespace(name="nt", walk=os.walk))

    def descriptors(paths):
        records = []
        for path in paths:
            external = not path.is_relative_to(root)
            protected = external or path in (root, root / "inputs", key)
            readonly = external or p.is_readonly(path) or path == key
            r = row(
                path,
                directory=path.is_dir(),
                inherited=not protected,
                readonly=readonly,
                key=path == key,
            )
            if readonly:
                r["owner"] = "operator"
            records.append(r)
        return records

    monkeypatch.setattr(m, "read_descriptors", descriptors)
    monkeypatch.setattr(evaluator, "identity", lambda: "operator")
    source = make_snapshot(tables)
    ref = engineering_input.publish_engineering_input(source, root / "inputs", tree_policy=p)
    (root / "work/result.json").write_bytes(b'{"engineering_only":true}')
    probe = module()

    def owner():
        return {"sid": "operator", "elevated": False, "source": "MODEL_ADAPTER"}

    raw = probe.freeze_inventory(p, ref, str(uuid.uuid4()), "before", get_token=owner)
    inv = probe.inventory_document(raw, hashlib.sha256(raw).hexdigest())
    cfg = {
        k: inv[k]
        for k in ("scope", "principals", "objects", "attempt_id", "phase", "root", "policy_binding")
    }
    cfg["operator_inventory_sha256"] = hashlib.sha256(raw).hexdigest()
    return probe, p, ref, raw, cfg, owner


def perform(probe, raw, cfg, role, **kw):
    def opened(path, mask):
        from pathlib import Path

        root = Path(cfg["root"])
        read = role != "research" and not (role == "auditor" and path == root / "key")
        writable = (
            role == "evaluator"
            and not path.is_relative_to(root / "inputs")
            and path != root / "key"
        )
        allowed = read if mask == 1 else writable and mask in (2, 4, 0x10000)
        return {"opened": allowed, "winerror": 0 if allowed else 5, "mask": mask}

    return probe.probe(
        cfg,
        role,
        inventory_raw=raw,
        inventory_sha256=cfg["operator_inventory_sha256"],
        get_token=lambda: {
            "sid": cfg["principals"][role],
            "elevated": False,
            "source": "MODEL_ADAPTER",
        },
        open_access=kw.get("open_access", opened),
    )


def reseal_inventory(inv):
    from aqrp.core.canonical import digest

    inv["tree_state_sha256"] = digest({k: v for k, v in inv.items() if k != "tree_state_sha256"})
    return canonical(inv)
