"""Pinned scanner controls and an exact source-byte seal; no product imports."""

import argparse
import hashlib
import json
import os
import random
import re
import string
import subprocess
import tomllib
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARENT_SHA = "73dbfe9e8ddd221da5ffd18a3cfa467ea8435dfa57b1ce4f28159eb6c5bab928"
EXECUTABLES = {
    "nt": "17157e2ee8b76fc8b1d8bee607a250e34b8a8023c8bc81822d4b5ee4d78fcb7c",
    "posix": "88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509",
}
PREFIX = "docs/audits/phase-7/self-review/MIG-001/"
FILES = [
    [
        PREFIX + n + ".json"
        for n in ("ORIGINAL_SUCCEEDED_STATUS", "HEALTHY_MIGRATION_CONTROL", "RESULT")
    ],
    [
        PREFIX + "cancelled-prefix/" + n + ".json"
        for n in (
            "LIVE_REFUSAL_BEFORE_IMPORT",
            "HEALTHY_MIGRATION_CONTROL",
            "ORIGINAL_CANCELLED_STATUS",
            "RESULT",
        )
    ],
]
PROOF = ROOT / "docs/audits/phase-7/self-review/SEC-001"
REPAIR_PROOF = ROOT / "docs/audits/phase-7/repairs-g2-001-002/scan-policy"
REPAIR_PROOF_SHA = "a4a0fa2d65ada964b1ac5546e2e2b5f912c9a0c3215a777a556350f8d14e5eb3"
REPAIR_FILES = [
    ["docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json"],
    ["docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json"],
    ["docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json"],
    ["docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json"],
    ["docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json"],
    ["docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json"],
    ["docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json"],
]
REPAIR_CONTROL_EXPECTATIONS = [
    {
        "name": "g2-public-00-original-child",
        "expected_exit": 0,
        "required_rule": None,
        "classification": "BENIGN_EXACT_EXCEPTION",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 0, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-00-original-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 0, "content": "ORIGINAL", "policy": "PARENT"},
    },
    {
        "name": "g2-public-00-changed-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 0, "content": "CHANGED", "policy": "PARENT"},
    },
    {
        "name": "g2-public-00-changed-child",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 0, "content": "CHANGED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-00-wrong-path",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "unrelated/g2-public.json",
        "source_fixture": {"proof_record": 0, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-00-wrong-pair",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 0, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-00-github-same-path",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 0, "content": "PAT", "policy": "CHILD"},
    },
    {
        "name": "g2-public-00-mixed-public-github",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 0, "content": "MIXED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-01-original-child",
        "expected_exit": 0,
        "required_rule": None,
        "classification": "BENIGN_EXACT_EXCEPTION",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 1, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-01-original-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 1, "content": "ORIGINAL", "policy": "PARENT"},
    },
    {
        "name": "g2-public-01-changed-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 1, "content": "CHANGED", "policy": "PARENT"},
    },
    {
        "name": "g2-public-01-changed-child",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 1, "content": "CHANGED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-01-wrong-path",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "unrelated/g2-public.json",
        "source_fixture": {"proof_record": 1, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-01-wrong-pair",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 1, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-01-github-same-path",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 1, "content": "PAT", "policy": "CHILD"},
    },
    {
        "name": "g2-public-01-mixed-public-github",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 1, "content": "MIXED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-02-original-child",
        "expected_exit": 0,
        "required_rule": None,
        "classification": "BENIGN_EXACT_EXCEPTION",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 2, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-02-original-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 2, "content": "ORIGINAL", "policy": "PARENT"},
    },
    {
        "name": "g2-public-02-changed-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 2, "content": "CHANGED", "policy": "PARENT"},
    },
    {
        "name": "g2-public-02-changed-child",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 2, "content": "CHANGED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-02-wrong-path",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "unrelated/g2-public.json",
        "source_fixture": {"proof_record": 2, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-02-wrong-pair",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 2, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-02-github-same-path",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 2, "content": "PAT", "policy": "CHILD"},
    },
    {
        "name": "g2-public-02-mixed-public-github",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 2, "content": "MIXED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-03-original-child",
        "expected_exit": 0,
        "required_rule": None,
        "classification": "BENIGN_EXACT_EXCEPTION",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 3, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-03-original-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 3, "content": "ORIGINAL", "policy": "PARENT"},
    },
    {
        "name": "g2-public-03-changed-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 3, "content": "CHANGED", "policy": "PARENT"},
    },
    {
        "name": "g2-public-03-changed-child",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 3, "content": "CHANGED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-03-wrong-path",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "unrelated/g2-public.json",
        "source_fixture": {"proof_record": 3, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-03-wrong-pair",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 3, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-03-github-same-path",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 3, "content": "PAT", "policy": "CHILD"},
    },
    {
        "name": "g2-public-03-mixed-public-github",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 3, "content": "MIXED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-04-original-child",
        "expected_exit": 0,
        "required_rule": None,
        "classification": "BENIGN_EXACT_EXCEPTION",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 4, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-04-original-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 4, "content": "ORIGINAL", "policy": "PARENT"},
    },
    {
        "name": "g2-public-04-changed-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 4, "content": "CHANGED", "policy": "PARENT"},
    },
    {
        "name": "g2-public-04-changed-child",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 4, "content": "CHANGED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-04-wrong-path",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "unrelated/g2-public.json",
        "source_fixture": {"proof_record": 4, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-04-wrong-pair",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 4, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-04-github-same-path",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 4, "content": "PAT", "policy": "CHILD"},
    },
    {
        "name": "g2-public-04-mixed-public-github",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 4, "content": "MIXED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-05-original-child",
        "expected_exit": 0,
        "required_rule": None,
        "classification": "BENIGN_EXACT_EXCEPTION",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 5, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-05-original-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 5, "content": "ORIGINAL", "policy": "PARENT"},
    },
    {
        "name": "g2-public-05-changed-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 5, "content": "CHANGED", "policy": "PARENT"},
    },
    {
        "name": "g2-public-05-changed-child",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 5, "content": "CHANGED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-05-wrong-path",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "unrelated/g2-public.json",
        "source_fixture": {"proof_record": 5, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-05-wrong-pair",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 5, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-05-github-same-path",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 5, "content": "PAT", "policy": "CHILD"},
    },
    {
        "name": "g2-public-05-mixed-public-github",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 5, "content": "MIXED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-06-original-child",
        "expected_exit": 0,
        "required_rule": None,
        "classification": "BENIGN_EXACT_EXCEPTION",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 6, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-06-original-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 6, "content": "ORIGINAL", "policy": "PARENT"},
    },
    {
        "name": "g2-public-06-changed-parent",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 6, "content": "CHANGED", "policy": "PARENT"},
    },
    {
        "name": "g2-public-06-changed-child",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 6, "content": "CHANGED", "policy": "CHILD"},
    },
    {
        "name": "g2-public-06-wrong-path",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "unrelated/g2-public.json",
        "source_fixture": {"proof_record": 6, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-06-wrong-pair",
        "expected_exit": 1,
        "required_rule": "generic-api-key",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_POLLUTION_REPRODUCTION.json",
        "source_fixture": {"proof_record": 6, "content": "ORIGINAL", "policy": "CHILD"},
    },
    {
        "name": "g2-public-06-github-same-path",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 6, "content": "PAT", "policy": "CHILD"},
    },
    {
        "name": "g2-public-06-mixed-public-github",
        "expected_exit": 1,
        "required_rule": "github-pat",
        "classification": "DETECTION_POSITIVE",
        "relative_path": "docs/audits/phase-7/g2-ec6bfce/received/PRIMARY_FAILED_HISTORY_REPRODUCTION.json",
        "source_fixture": {"proof_record": 6, "content": "MIXED", "policy": "CHILD"},
    },
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf8")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
    with path.open("xb") as stream:
        stream.write(raw)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def public_identifiers():
    proof = json.loads((PROOF / "PROOF.json").read_bytes())
    require(len(proof["records"]) == 2, "PUBLIC_PROOF_COUNT")
    identifiers = []
    for number, record in enumerate(proof["records"]):
        raw = (PROOF / record["preimage"]["file"]).read_bytes()
        config = json.loads(raw)
        require(canonical(config) == raw and len(raw) == 1606, "PUBLIC_PREIMAGE_BYTES")
        require(
            config["schema"] == "research/1"
            and config["purpose"] == "ENGINEERING_DEMO"
            and config["market_id"] == "SYN_A"
            and config["currency"] == "SYNCCY",
            "PUBLIC_SYNTHETIC_SCOPE",
        )
        value = digest(raw)
        require(
            value == record["public_config_sha256"] == record["preimage"]["sha256"], "PUBLIC_SHA256"
        )
        require(record["exact_repository_projection_files"] == FILES[number], "PUBLIC_EXACT_FILES")
        identifiers.append(value)
    return identifiers


def repair_public_identifiers():
    raw = (REPAIR_PROOF / "PROOF.json").read_bytes()
    require(digest(raw) == REPAIR_PROOF_SHA, "REPAIR_PUBLIC_PROOF_BYTES")
    proof = json.loads(raw)
    require(
        proof["schema"] == "phase7-G2-public-digest-proof/1"
        and proof["original_failure_findings"] == 12
        and len(proof["records"]) == 7,
        "REPAIR_PUBLIC_PROOF_SCOPE",
    )
    values = []
    for index, record in enumerate(proof["records"]):
        require(
            record["preimage"]["file"] == f"preimages/public-digest-{index:02d}.json",
            "REPAIR_PREIMAGE_PATH",
        )
        data = (REPAIR_PROOF / record["preimage"]["file"]).read_bytes()
        item = json.loads(data)
        require(
            canonical(item) == data
            and len(data) == record["preimage"]["bytes"]
            and digest(data) == record["preimage"]["sha256"] == record["public_sha256"],
            "REPAIR_PREIMAGE_RECOMPUTATION",
        )
        if record["category"] == "PUBLIC_SYNTHETIC_RESEARCH_CONFIG":
            require(
                item["schema"] == "research/1"
                and item["purpose"] == "ENGINEERING_DEMO"
                and item["market_id"] == "SYN_A"
                and item["currency"] == "SYNCCY"
                and "family" not in item,
                "REPAIR_PUBLIC_SYNTHETIC_SCOPE",
            )
        else:
            require(
                record["category"] == "PUBLIC_LOCAL_RUN_OWNER_ID"
                and set(item) == {"ledger_root", "run_id"}
                and item["ledger_root"].replace("\\", "/").endswith("/research-runs")
                and re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", item["run_id"]),
                "REPAIR_PUBLIC_OWNER_SCOPE",
            )
        require(
            record["exact_repository_projection_files"] == REPAIR_FILES[index],
            "REPAIR_EXACT_REPORT_FILES",
        )
        values.append(record["public_sha256"])
    for relative, expected in proof["projection_files"].items():
        require(relative in sum(REPAIR_FILES, []), "REPAIR_NO_OTHER_REPORT")
        data = (ROOT / relative).read_bytes()
        require(
            len(data) == expected["bytes"] and digest(data) == expected["sha256"],
            "REPAIR_ORIGINAL_REPORT_BYTES",
        )
    require(len(proof["locations"]) == 12, "REPAIR_LOCATION_COUNT")
    for location in proof["locations"]:
        require(location["repository_path"] in sum(REPAIR_FILES, []), "REPAIR_LOCATION_PATH")
        value = json.loads((ROOT / location["repository_path"]).read_bytes())
        for token in location["json_pointer"].lstrip("/").split("/"):
            token = token.replace("~1", "/").replace("~0", "~")
            value = value[int(token)] if isinstance(value, list) else value[token]
        matching = [r for r in proof["records"] if r["id"] == location["public_digest_id"]]
        require(
            len(matching) == 1 and value == matching[0]["public_sha256"],
            "REPAIR_ORIGINAL_LOCATION_VALUE",
        )
    return values


def policy():
    parent, child = ROOT / ".gitleaks.toml", ROOT / ".gitleaks-phase7.toml"
    require(digest(parent.read_bytes()) == PARENT_SHA, "PROTECTED_PARENT_CHANGED")
    values = public_identifiers()
    repair_values = repair_public_identifiers()
    config = tomllib.loads(child.read_text(encoding="utf8"))
    require(
        set(config) == {"title", "extend", "allowlists"}
        and config["extend"] == {"path": ".gitleaks.toml"},
        "CHILD_EXTENSION_ONLY",
    )
    parent_policy = tomllib.loads(parent.read_text(encoding="utf8"))["allowlists"]
    require(
        len(config["allowlists"]) == 4 + len(repair_values)
        and config["allowlists"][:2] == parent_policy,
        "EXACT_PARENT_ALLOWLISTS_PRESERVED",
    )
    for index, entry in enumerate(config["allowlists"][2:4]):
        require(
            set(entry)
            == {"targetRules", "description", "condition", "regexTarget", "paths", "regexes"},
            "NO_OTHER_POLICY_FIELDS",
        )
        require(
            entry["targetRules"] == ["generic-api-key"]
            and entry["condition"] == "AND"
            and entry["regexTarget"] == "secret",
            "EXACT_RULE_AND_CONDITION",
        )
        require(entry["regexes"] == ["^" + values[index] + "$"], "FULL_PUBLIC_IDENTIFIER_ONLY")
        require(
            entry["paths"] == ["(^|/)" + re.escape(p) + "$" for p in FILES[index]],
            "EXACT_SEVEN_PATHS_ONLY",
        )
    for index, entry in enumerate(config["allowlists"][4:]):
        require(
            set(entry)
            == {"targetRules", "description", "condition", "regexTarget", "paths", "regexes"},
            "REPAIR_NO_OTHER_POLICY_FIELDS",
        )
        require(
            entry["targetRules"] == ["generic-api-key"]
            and entry["condition"] == "AND"
            and entry["regexTarget"] == "secret",
            "REPAIR_EXACT_RULE_AND_CONDITION",
        )
        require(
            entry["regexes"] == ["^" + repair_values[index] + "$"],
            "REPAIR_FULL_PUBLIC_IDENTIFIER_ONLY",
        )
        require(
            entry["paths"] == ["(^|/)" + re.escape(p) + "$" for p in REPAIR_FILES[index]],
            "REPAIR_EXACT_REPORT_PAIR_ONLY",
        )
    return {
        "parent_sha256": PARENT_SHA,
        "child_sha256": digest(child.read_bytes()),
        "public_proof_sha256": digest((PROOF / "PROOF.json").read_bytes()),
        "repair_public_proof_sha256": REPAIR_PROOF_SHA,
    }, values


def source_files():
    """Enumeration errors, links, junctions and concurrent changes fail closed."""
    rows = []

    def error(exc):
        raise exc

    for folder, directories, names in os.walk(ROOT, topdown=True, onerror=error, followlinks=False):
        for name in sorted(directories + names):
            path = Path(folder) / name
            require(not path.is_symlink() and not path.is_junction(), "SOURCE_LINK_BOUNDARY")
            require(path.resolve().is_relative_to(ROOT), "SOURCE_PATH_BOUNDARY")
        for name in sorted(names):
            path = Path(folder) / name
            before = path.stat()
            require(path.is_file(), "SOURCE_NOT_REGULAR_FILE")
            raw = path.read_bytes()
            after = path.stat()
            require(
                (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
                and len(raw) == after.st_size,
                "SOURCE_CHANGED_DURING_READ",
            )
            rows.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "bytes": len(raw),
                    "sha256": digest(raw),
                }
            )
    return sorted(rows, key=lambda row: row["path"])


def scanner(
    executable, target, output, name, config, expected, required_rule=None, classification=None
):
    report = output / (name + ".json")
    argv = [
        str(executable),
        "dir",
        str(target),
        "--config",
        str(config),
        "--redact=100",
        "--no-banner",
        "--report-format",
        "json",
        "--report-path",
        str(report),
    ]
    environment = dict(os.environ)
    environment.pop("GITLEAKS_CONFIG_TOML", None)
    started = datetime.now(UTC).isoformat()
    with (
        (output / (name + ".stdout.log")).open("xb") as stdout,
        (output / (name + ".stderr.log")).open("xb") as stderr,
    ):
        result = subprocess.run(
            argv, cwd=ROOT, env=environment, stdout=stdout, stderr=stderr, timeout=180
        )
    require(report.is_file(), "SCANNER_REPORT_MISSING_" + name)
    findings = json.loads(report.read_bytes())
    require(isinstance(findings, list), "SCANNER_REPORT_SCHEMA")
    metadata = [
        {
            k: finding[k]
            for k in ("RuleID", "File", "StartLine", "StartColumn", "EndLine", "EndColumn")
        }
        for finding in findings
    ]
    record = {
        "name": name,
        "argv": argv,
        "cwd": str(ROOT),
        "started_utc": started,
        "ended_utc": datetime.now(UTC).isoformat(),
        "actual_exit": result.returncode,
        "expected_exit": expected,
        "redact_percent": 100,
        "classification": classification
        or ("DETECTION_POSITIVE" if expected == 1 else "BENIGN_EXACT_EXCEPTION"),
        "findings_without_values": metadata,
        "raw_files": [
            {"path": p.name, "bytes": p.stat().st_size, "sha256": digest(p.read_bytes())}
            for p in (
                report,
                output / (name + ".stdout.log"),
                output / (name + ".stderr.log"),
            )
        ],
    }
    save(output / (name + ".command.json"), record)
    require(result.returncode == expected, "SCANNER_CONTROL_EXIT_" + name)
    require((not findings) if expected == 0 else bool(findings), "SCANNER_CONTROL_FINDINGS_" + name)
    if required_rule is not None:
        require(required_rule in {f["RuleID"] for f in findings}, "SCANNER_CONTROL_RULE_" + name)
    return record


def capture_repair_controls(executable, out, child, positive):
    identifiers = repair_public_identifiers()
    controls = []
    for expected in REPAIR_CONTROL_EXPECTATIONS:
        fixture = expected["source_fixture"]
        index = fixture["proof_record"]
        raw = (ROOT / REPAIR_FILES[index][0]).read_bytes()
        if fixture["content"] == "CHANGED":
            changed = identifiers[index][:-1] + ("0" if identifiers[index][-1] != "0" else "1")
            raw = raw.replace(identifiers[index].encode(), changed.encode())
        elif fixture["content"] == "PAT":
            raw = positive
        elif fixture["content"] == "MIXED":
            raw += b"\n" + positive
        else:
            require(fixture["content"] == "ORIGINAL", "REPAIR_CONTROL_CONTENT")
        root = out / "fixtures" / expected["name"]
        save(root / expected["relative_path"], raw)
        controls.append(
            scanner(
                executable,
                root,
                out,
                expected["name"],
                ROOT / ".gitleaks.toml" if fixture["policy"] == "PARENT" else child,
                expected["expected_exit"],
                expected["required_rule"],
                expected["classification"],
            )
        )
    return controls


def capture(run):
    out = run / "scan-policy"
    require(not out.exists(), "IMMUTABLE_CAPTURE_ALREADY_EXISTS")
    effective, identifiers = policy()
    configured = os.environ.get("GITLEAKS_CONFIG")
    require(
        configured is not None and Path(configured).resolve() == ROOT / ".gitleaks-phase7.toml",
        "EXPLICIT_EFFECTIVE_CHILD_REQUIRED",
    )
    executable = run / ("gitleaks.exe" if os.name == "nt" else "gitleaks")
    require(digest(executable.read_bytes()) == EXECUTABLES[os.name], "PINNED_SCANNER_BINARY")
    version = subprocess.run(
        [str(executable), "version"], cwd=ROOT, capture_output=True, check=True
    )
    require(b"8.30.1" in version.stdout, "PINNED_SCANNER_VERSION")
    out.mkdir()
    save(out / "version.stdout.log", version.stdout)
    save(out / "version.stderr.log", version.stderr)
    save(out / "parent-config.toml", (ROOT / ".gitleaks.toml").read_bytes())
    save(out / "child-config.toml", (ROOT / ".gitleaks-phase7.toml").read_bytes())
    controls, fixtures = [], out / "fixtures"
    child = ROOT / ".gitleaks-phase7.toml"

    def case(name, relative, raw, expected, rule=None, config=None, classification=None):
        root = fixtures / name
        save(root / relative, raw)
        controls.append(
            scanner(executable, root, out, name, config or child, expected, rule, classification)
        )
        return root

    original = (ROOT / FILES[0][0]).read_bytes()
    other = (ROOT / FILES[1][2]).read_bytes()
    case("public-one-exact-original", FILES[0][0], original, 0)
    case("public-two-exact-original", FILES[1][2], other, 0)
    changed = identifiers[0][:-1] + ("0" if identifiers[0][-1] != "0" else "1")
    case(
        "changed-digest-parent-positive",
        FILES[0][0],
        original.replace(identifiers[0].encode(), changed.encode()),
        1,
        "generic-api-key",
        ROOT / ".gitleaks.toml",
    )
    case(
        "changed-digest-same-path",
        FILES[0][0],
        original.replace(identifiers[0].encode(), changed.encode()),
        1,
        "generic-api-key",
    )
    case(
        "same-digest-other-path",
        "unrelated/ORIGINAL_SUCCEEDED_STATUS.json",
        original,
        1,
        "generic-api-key",
    )
    case(
        "wrong-pair-original-path",
        FILES[1][2],
        other.replace(identifiers[1].encode(), identifiers[0].encode()),
        1,
        "generic-api-key",
    )
    fake = (
        "gh"
        + "p_"
        + "".join(random.Random(718).choices(string.ascii_letters + string.digits, k=36))
    ).encode()
    positive = b"token = " + fake + b"\n"
    case("github-same-allowed-path", FILES[0][0], positive, 1, "github-pat")
    case("mixed-public-and-github", FILES[0][0], original + b"\n" + positive, 1, "github-pat")
    case("github-unrelated-path", "unrelated/control.txt", positive, 1, "github-pat")
    inherited = tomllib.loads((ROOT / ".gitleaks.toml").read_text(encoding="utf8"))["allowlists"]
    phase1 = "docs/audits/phase-1/implementation/local-history/aqrp-3261ca7b-86e1-4f60-b77f-966595712fa9/artifacts.json"
    phase3 = "docs/audits/phase-3/implementation/validation-07e7c88/sdk/research/runs/826873ac-7112-4114-8518-1ae98b5c11d9/events.jsonl"
    require(len(inherited) == 2, "PROTECTED_PARENT_ALLOWLIST_COUNT")
    require(
        digest((ROOT / phase1).read_bytes())
        == "1d7a4007f40b316b45e20618b5752329cb60329895abbcc7f0eef1b5061797e6",
        "PROTECTED_PHASE1_EXCEPTION_FILE_CHANGED",
    )
    case("inherited-parent-phase1", phase1, (ROOT / phase1).read_bytes(), 0)
    case("inherited-parent-phase3", phase3, (ROOT / phase3).read_bytes(), 0)
    case(
        "inherited-phase1-other-path",
        "unrelated/artifacts.json",
        (ROOT / phase1).read_bytes(),
        1,
        "generic-api-key",
    )
    # Actual pinned 8.30.1 parent behavior: this preexisting P1 exception also
    # suppresses the mixed constructed PAT. Require exact parent/child equality;
    # this is an inherited limitation, never a detection positive or a repair.
    for name, configured_policy in (
        ("mixed-phase1-parent-known-limitation", ROOT / ".gitleaks.toml"),
        ("mixed-phase1-child-known-limitation", child),
    ):
        case(
            name,
            phase1,
            (ROOT / phase1).read_bytes() + b"\n" + positive,
            0,
            config=configured_policy,
            classification="KNOWN_BASELINE_LIMITATION",
        )
    case(
        "mixed-parent-phase3-and-github",
        phase3,
        (ROOT / phase3).read_bytes() + b"\n" + positive,
        1,
        "github-pat",
    )
    case(
        "inherited-sha-other-path",
        "unrelated/cache-event.jsonl",
        (ROOT / phase3).read_bytes(),
        1,
        "generic-api-key",
    )
    # All seven original files / all nine original matches must be excepted,
    # while every other scanner rule remains active for those same paths.
    all_originals = fixtures / "all-seven-immutable-originals"
    for relative in sum(FILES, []):
        save(all_originals / relative, (ROOT / relative).read_bytes())
    controls.append(
        scanner(executable, all_originals, out, "all-seven-immutable-originals", child, 0)
    )
    repair_controls = capture_repair_controls(executable, out, child, positive)
    before = source_files()
    source_scan = scanner(executable, ROOT, out, "actual-source-after-build", child, 0)
    after = source_files()
    require(before == after, "SOURCE_CHANGED_DURING_SCAN")
    manifest = {
        "schema": "all-actual-scanned-source-files/1",
        "source": str(ROOT),
        "files": after,
        "file_count": len(after),
        "includes_generated_build_and_metadata_files": True,
        "exclusions": [],
        "effective_policy": effective,
        "scanner_sha256": EXECUTABLES[os.name],
        "scope": "Exact actual SOURCE bytes after build and scanner controls, not only Git-tracked files.",
    }
    save(out / "scanned-source-manifest.json", manifest)
    save(
        out / "capture.json",
        {
            "schema": "phase7-scan-policy-capture/1",
            "result": "PASS",
            "created_utc": datetime.now(UTC).isoformat(),
            "source": str(ROOT),
            "effective_policy": effective,
            "scanner_sha256": EXECUTABLES[os.name],
            "controls": controls,
            "control_counts": {
                "total": len(controls),
                "detection_positives": sum(
                    row["classification"] == "DETECTION_POSITIVE" for row in controls
                ),
                "benign_exact_exceptions": sum(
                    row["classification"] == "BENIGN_EXACT_EXCEPTION" for row in controls
                ),
                "known_baseline_limitations": sum(
                    row["classification"] == "KNOWN_BASELINE_LIMITATION" for row in controls
                ),
            },
            "repair_controls": repair_controls,
            "repair_control_expectations": REPAIR_CONTROL_EXPECTATIONS,
            "repair_control_counts": {
                "total": len(repair_controls),
                "detection_positives": sum(
                    row["classification"] == "DETECTION_POSITIVE" for row in repair_controls
                ),
                "benign_exact_exceptions": sum(
                    row["classification"] == "BENIGN_EXACT_EXCEPTION" for row in repair_controls
                ),
                "known_baseline_limitations": 0,
            },
            "repair_original_failed_scan": {
                "findings": 12,
                "distinct_public_identifiers": 7,
                "original_failed_status_rewritten": False,
            },
            "known_baseline_limitation": {
                "parent_exit": 0,
                "child_exit": 0,
                "classification": "KNOWN_BASELINE_LIMITATION",
                "protected_phase1_file_sha256": "1d7a4007f40b316b45e20618b5752329cb60329895abbcc7f0eef1b5061797e6",
                "scope": "Existing parent runtime behavior is inherited unchanged. The original 5016-file gate and this byte pin protect the historical P1 file. This is neither a detection positive nor a newly closed security finding.",
            },
            "actual_source_scan": source_scan,
            "scanned_source_manifest_sha256": digest(
                (out / "scanned-source-manifest.json").read_bytes()
            ),
            "actual_source_files": len(after),
            "formal_Test": "NOT RUN",
            "financial_approval": "NONE",
            "Windows_R2": "DEFERRED / NOT VERIFIED",
        },
    )
    print("Pinned scanner policy controls and exact source capture PASS")


def verify(run):
    out = run / "scan-policy"
    effective, _ = policy()
    receipt = json.loads((out / "capture.json").read_bytes())
    raw = (out / "scanned-source-manifest.json").read_bytes()
    require(
        receipt["result"] == "PASS"
        and receipt["effective_policy"] == effective
        and digest(raw) == receipt["scanned_source_manifest_sha256"],
        "CAPTURE_IDENTITY_CHANGED",
    )
    require(
        receipt["repair_control_expectations"] == REPAIR_CONTROL_EXPECTATIONS
        and len(receipt["repair_controls"]) == len(REPAIR_CONTROL_EXPECTATIONS)
        and all(
            actual["name"] == expected["name"]
            and actual["actual_exit"] == actual["expected_exit"] == expected["expected_exit"]
            and actual["classification"] == expected["classification"]
            for actual, expected in zip(
                receipt["repair_controls"], REPAIR_CONTROL_EXPECTATIONS, strict=True
            )
        ),
        "REPAIR_CONTROL_TABLE_CHANGED",
    )
    manifest = json.loads(raw)
    require(
        manifest["source"] == str(ROOT) and manifest["effective_policy"] == effective,
        "SOURCE_IDENTITY_CHANGED",
    )
    current = source_files()
    require(current == manifest["files"], "SCANNED_SOURCE_FILE_SET_OR_BYTES_CHANGED")
    save(
        out / "verify.json",
        {
            "schema": "phase7-scanned-source-verification/1",
            "result": "PASS",
            "verified_utc": datetime.now(UTC).isoformat(),
            "source": str(ROOT),
            "scanned_source_manifest_sha256": digest(raw),
            "exact_all_files_and_sizes_and_hashes_unchanged": True,
            "actual_source_files": len(current),
            "scope": "Pure source-byte verification after tests/smokes; no product calls or scanner rerun.",
            "security_limit": "Endpoint source-file equality under the trusted SDK; no claim of continuous OS-enforced immutability. Windows R2 remains DEFERRED / NOT VERIFIED.",
        },
    )
    print("Exact scanned source remains unchanged after all checks PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root_run_dir", type=Path)
    parser.add_argument("--operation", choices=("capture", "verify"), required=True)
    args = parser.parse_args()
    run = args.root_run_dir.resolve()
    require(run.is_dir() and not run.is_relative_to(ROOT), "OUTPUT_MUST_BE_OUTSIDE_SOURCE")
    try:
        (capture if args.operation == "capture" else verify)(run)
    except BaseException as exc:
        failure = run / "scan-policy" / (args.operation + "-failure.json")
        if not failure.exists():
            save(
                failure,
                {
                    "result": "FAIL",
                    "operation": args.operation,
                    "error_type": type(exc).__name__,
                    "reason": str(exc),
                    "source": str(ROOT),
                    "captured_utc": datetime.now(UTC).isoformat(),
                    "original_failures_preserved": True,
                },
            )
        raise


if __name__ == "__main__":
    main()
