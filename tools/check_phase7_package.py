"""P7 implementation admission; prior source/answers and exact changes are frozen.

This is a developer package check, never independent G2 or financial approval.
The old P6 checker is preserved and executed in its own released environment.
"""

import base64
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path

from aqrp.factors.admission import LOCK_HASH, PACKAGE, bundle_manifest, reviewed_policy

ROOT = Path(__file__).resolve().parents[1]
D = "docs/audits/phase-7/"
BASELINE_SHA256 = "4bac5d9c98e2e3f74065d1c95b5ce94f482420c022a8e146f59375a37081b646"
ALLOWLIST_SHA256 = "ab029c8b6d9f5dd5b927e2d13efbc1ccd1936a7eb57b6877a66cb4bfdb233415"
G1 = "645049ae9b08710ed93189b80547d14c87d80584"
P6 = "d563347ad11e1f26e131dc06e343250282c05c33"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(root, name, expected=None):
    raw = (root / name).read_bytes()
    assert expected is None or sha(raw) == expected, name
    return json.loads(raw)


def files(root):
    ignored = {".git", "__pycache__", ".ruff_cache", ".pytest_cache", ".hypothesis", "build"}
    result = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(p in ignored or p.endswith(".egg-info") for p in relative.parts):
            continue
        assert not path.is_symlink() and not path.is_junction(), relative
        if path.is_file():
            raw = path.read_bytes()
            result[relative.as_posix()] = {"bytes": len(raw), "sha256": sha(raw)}
    return result


def verify_inventory(actual, baseline, identity, allowed):
    """No deletion, unexplained file, or unlisted mutation is accepted."""
    baseline = {x["path"]: {k: x[k] for k in ("bytes", "sha256")} for x in baseline}
    assert set(baseline) <= set(actual), "Baseline deletion"
    changed = {p for p in baseline if actual[p] != baseline[p]}
    added = set(actual) - set(baseline)
    assert changed == set(allowed["changed"]), ("Unexplained changes", changed)
    assert added == set(allowed["added"]), ("Unexplained additions", added)
    rows = {x["path"]: {k: x[k] for k in ("bytes", "sha256")} for x in identity}
    assert len(rows) == len(identity), "Duplicate current identity"
    # This file is the only self-hash exclusion, not a directory exemption.
    expected = changed | added
    expected.discard(D + "IMPLEMENTATION_IDENTITY.json")
    assert set(rows) == expected, "Incomplete current identity"
    assert all(actual[p] == row for p, row in rows.items()), "Current bytes changed"
    return len(baseline) - len(changed), len(changed), len(added)


def verify_installed(root, manifest):
    source = root / "src/aqrp"
    data_files = {
        "factors/reviewed_code.json",
        "ui/requirements-windows.lock",
        "ui/requirements-linux.lock",
    }
    installed = {p.relative_to(PACKAGE).as_posix(): p for p in PACKAGE.rglob("*.py")}
    expected = {row["path"]: row["sha256"] for row in manifest["files"]}
    assert set(installed) == set(expected), "Installed module set"
    assert {p.relative_to(source).as_posix() for p in source.rglob("*.py")} == set(expected)
    for folder in (source, PACKAGE):
        members = {
            p.relative_to(folder).as_posix()
            for p in folder.rglob("*")
            if p.is_file() and "__pycache__" not in p.relative_to(folder).parts
        }
        assert members == set(expected) | data_files, "Unlisted package member"
    distribution = importlib.metadata.distribution("aqrp")
    record = {str(f).replace("\\", "/"): f for f in distribution.files}
    for name, checksum in expected.items():
        assert sha(installed[name].read_bytes()) == checksum == sha((source / name).read_bytes())
        item = record["aqrp/" + name]
        encoded = base64.urlsafe_b64encode(bytes.fromhex(checksum)).rstrip(b"=").decode()
        assert item.hash.mode == "sha256" and item.hash.value == encoded, name
    for name in data_files:
        assert (PACKAGE / name).read_bytes() == (source / name).read_bytes(), name
    assert distribution.version == "0.7.0.dev1"
    assert (
        not json.loads(distribution.read_text("direct_url.json"))
        .get("dir_info", {})
        .get("editable")
    )


def main():
    authorization = load(ROOT, D + "IMPLEMENTATION_AUTHORIZATION.json")
    assert authorization["implementation_authorized"] and authorization["G1_reviewed_sha"] == G1
    assert all(v == "EXPLICITLY_ACCEPTED" for v in authorization["conditions"].values())
    assert not any(
        authorization[k]
        for k in (
            "G2_or_user_stage_acceptance",
            "merge_tag_release_authorized",
            "deployment_live_accounts_ACL_services_scheduler_authorized",
            "formal_Test_authorized",
        )
    )
    assert authorization["financial_approval"] == "NONE"
    baseline = load(ROOT, D + "IMPLEMENTATION_BASELINE_FILES.json", BASELINE_SHA256)
    assert baseline["source_commit"] == "8106bbe6fbb73b5b4336d42e4c27b3adb1cf6ff8"
    allowed = load(ROOT, D + "IMPLEMENTATION_ALLOWED_PATHS.json", ALLOWLIST_SHA256)
    identity = load(ROOT, D + "IMPLEMENTATION_IDENTITY.json")
    counts = verify_inventory(files(ROOT), baseline["files"], identity["current_files"], allowed)
    old_identity = load(ROOT, "docs/audits/phase-6/IMPLEMENTATION_IDENTITY.json")
    assert len(old_identity["preserved_files"]) == 5016
    for row in old_identity["preserved_files"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] and sha(raw) == row["sha256"], row["path"]
    design = load(ROOT, D + "DESIGN_IDENTITY.json")
    assert design["reviewed_sha"] == G1
    for row in design["files"]:
        raw = (ROOT / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] and sha(raw) == row["sha256"], row["path"]
    manifest, policy = bundle_manifest(), reviewed_policy()
    assert (
        identity["bundle_manifest"] == manifest
        and identity["bundle_sha256"] == policy["bundle_sha256"]
    )
    assert policy["financial_approval"] == "NONE" and policy["environment"] == "TEST_ONLY"
    assert policy["review_ref"] == D + "ENGINEERING_CODE_REVIEW.md"
    verify_installed(ROOT, manifest)
    assert sha((ROOT / "requirements.lock").read_bytes()) == LOCK_HASH
    for os_name in ("windows", "linux"):
        raw = (ROOT / f"requirements-ui-{os_name}.lock").read_bytes()
        assert raw == (ROOT / f"src/aqrp/ui/requirements-{os_name}.lock").read_bytes()
        assert (
            raw == (ROOT / f"docs/audits/phase-6/UI_EXTENSION_{os_name.upper()}.lock").read_bytes()
        )
    rows = list(
        csv.DictReader((ROOT / "docs/requirements.csv").read_text(encoding="utf-8").splitlines())
    )
    selected = [r for r in rows if r["phase"] == "7"]
    assert len(rows) == 106 and len(selected) == 5
    assert sum(r["tier"] == "MVP" for r in selected) == 3
    snapshot = load(ROOT, D + "REQUIREMENTS_SNAPSHOT.json")
    assert selected == snapshot["requirements"]
    assert not (ROOT / "src/aqrp/broker").exists()
    for row in manifest["files"]:
        if (
            row["path"].startswith(("backtest/", "execution/"))
            and row["path"] != "backtest/synthetic.py"
        ):
            text = (ROOT / "src/aqrp" / row["path"]).read_text(encoding="utf-8")
            assert not any(
                s in text for s in ("FactorRegistry", "import streamlit", "factors.builtins")
            )
    print(
        json.dumps(
            {
                "scope": "P7 developer IMPLEMENTATION package gate; G2 PENDING",
                "G1": G1,
                "phase6_baseline": P6,
                "requirements": 5,
                "MVP": 3,
                "Competition Ready": 2,
                "modules": len(manifest["files"]),
                "bundle_sha256": policy["bundle_sha256"],
                "preserved_changed_added": counts,
                "checker_sha256": sha(Path(__file__).read_bytes()),
                "result": "PASS",
            }
        )
    )


if __name__ == "__main__":
    main()
