"""Trusted workspace catalogue and shared frozen request builder for CLI/SDK/UI."""

import re
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path

from aqrp.backtest.transactions import guard_path
from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import SnapshotRef
from aqrp.core.environment import runtime_manifest, verify_runtime
from aqrp.core.errors import ContractError
from aqrp.data.exposures import ExposureRef, exposures_as_of
from aqrp.data.snapshot import verify_snapshot
from aqrp.experiments.ledger import immutable_write, mutex
from aqrp.factors.admission import BUILTINS, LOCK_HASH, builtin_spec, bundle_hash
from aqrp.portfolio.contracts import load
from aqrp.research.synthetic import synthetic_research
from aqrp.services.research import ResearchRequest, hypotheses, hypothesis_definition
from aqrp.ui.environment import ui_environment
from aqrp.ui.numbers import decimal_parts, percent
from aqrp.validation.labels import CoverageRef


@dataclass(frozen=True)
class EffectiveRequest:
    raw: bytes

    @property
    def config_hash(self):
        return digest(load(self.raw))


def initialize(root, code_commit):
    root = guard_path(root)
    root.mkdir(parents=True, exist_ok=True)
    if not re.fullmatch("[0-9a-f]{40}", code_commit):
        raise ContractError("FULL_CODE_SHA_REQUIRED")
    with mutex(root / ".catalog-lock"):
        path = root / "catalog.json"
        if path.exists():
            current = catalogue(root)
            if current["code_commit"] != code_commit:
                raise ContractError("CATALOG_CODE_COMMIT_CHANGED")
            return current
        c, s, e, v = synthetic_research(root / "inputs", sessions=24, assets=6, factor_ids=BUILTINS)
        body = {
            "schema": "task-catalog/1",
            "code_commit": code_commit,
            "code_bundle": bundle_hash(),
            "config": load(canonical(c)),
            "snapshot": {**asdict(s), "root": str(s.root)},
            "exposures": {**asdict(e), "root": str(e.root)},
            "coverage": {"payload": v.payload.decode(), "checksum": v.checksum},
            "scope": "ENGINEERING_TEST_ONLY",
            "financial_approval": "NONE",
            "core_environment": runtime_manifest(),
            "ui_environment": ui_environment(),
            "factor_specs": [asdict(builtin_spec(n)) for n in BUILTINS],
        }
        body["revision"] = digest(body)
        immutable_write(path, canonical(body))
    return catalogue(root)


def references(root, cat):
    s = cat["snapshot"]
    e = cat["exposures"]
    v = cat["coverage"]
    for item in [s, e]:
        if not guard_path(item["root"]).is_relative_to(guard_path(root)):
            raise ContractError("CATALOG_INPUT_OUTSIDE_WORKSPACE")
    return (
        SnapshotRef(Path(s["root"]), s["snapshot_id"], s["manifest_hash"]),
        ExposureRef(Path(e["root"]), e["manifest_hash"], e["parent_hash"]),
        CoverageRef(v["payload"].encode(), v["checksum"]),
    )


def catalogue(root):
    raw = guard_path(Path(root) / "catalog.json").read_bytes()
    cat = load(raw)
    if (
        canonical(cat) != raw
        or digest({k: v for k, v in cat.items() if k != "revision"}) != cat["revision"]
    ):
        raise ContractError("CATALOG_IDENTITY_CHANGED")
    if (
        cat.get("schema") != "task-catalog/1"
        or type(cat.get("code_commit")) is not str
        or not re.fullmatch("[0-9a-f]{40}", cat["code_commit"])
        or cat["factor_specs"] != load(canonical([asdict(builtin_spec(n)) for n in BUILTINS]))
        or cat["code_bundle"] != bundle_hash()
        or cat["scope"] != "ENGINEERING_TEST_ONLY"
        or cat["financial_approval"] != "NONE"
    ):
        raise ContractError("CATALOG_EXECUTION_IDENTITY_CHANGED")
    verify_runtime(runtime_manifest())
    if cat["core_environment"] != runtime_manifest() or cat["ui_environment"] != ui_environment():
        raise ContractError("CATALOG_ENVIRONMENT_CHANGED")
    s, e, v = references(root, cat)
    verify_snapshot(s)
    exposures_as_of(
        e,
        cat["config"]["evaluation_cutoff"],
        cat["config"]["market_id"],
        cat["config"]["currency"],
        [],
    )
    v.read(s.manifest_hash)
    return cat


FIELDS = {
    "kind",
    "factor_ids",
    "factor_refs",
    "lookback",
    "direction",
    "weights_percent",
    "start",
    "end",
    "horizons",
    "neutralize",
    "initial_cash",
    "fee_budget",
    "policy",
    "constraints",
    "source_task",
    "profile",
}


def validate_draft(draft):
    if not isinstance(draft, dict) or set(draft) - FIELDS:
        raise ContractError("UNKNOWN_TASK_DRAFT_FIELD")
    if draft.get("kind", "research") not in ("research", "engineering_pipeline", "replay"):
        raise ContractError("APPROVAL_REQUIRED")
    if draft.get("kind", "research") != "replay" and set(draft) & {"source_task", "profile"}:
        raise ContractError("INVALID_TASK_KIND_FIELD")
    if "factor_ids" in draft and (
        not isinstance(draft["factor_ids"], list)
        or any(type(n) is not str for n in draft["factor_ids"])
    ):
        raise ContractError("INVALID_FACTOR_SELECTION")
    if "horizons" in draft and not isinstance(draft["horizons"], list):
        raise ContractError("INVALID_RESEARCH_HORIZON_GRID")
    if "weights_percent" in draft and not isinstance(draft["weights_percent"], dict):
        raise ContractError("FACTOR_WEIGHTS_REQUIRED")
    if "policy" in draft:
        policy = draft["policy"]
        if not isinstance(policy, dict) or set(policy) - {
            "mode",
            "weighting",
            "top_k",
            "long_k",
            "short_k",
            "gross",
            "net",
        }:
            raise ContractError("INVALID_PORTFOLIO_POLICY_OVERRIDE")
        if policy.get("mode", "LONG_ONLY") not in ("LONG_ONLY", "LONG_SHORT") or policy.get(
            "weighting", "equal"
        ) not in ("equal", "score"):
            raise ContractError("INVALID_PORTFOLIO_POLICY_OVERRIDE")
    if "constraints" in draft and (
        not isinstance(draft["constraints"], dict)
        or set(draft["constraints"])
        - {
            "per_asset",
            "gross_max",
            "net_min",
            "net_max",
            "leverage_max",
            "turnover_max",
            "beta_min",
            "beta_max",
            "industries",
            "allow_cash_only",
        }
    ):
        raise ContractError("INVALID_RISK_OVERRIDE")
    for name in ["initial_cash", "fee_budget"]:
        if name in draft:
            coef, _ = decimal_parts(draft[name])
            if coef < 0:
                raise ContractError("INVALID_ENGINEERING_BUDGET", name)
    if "weights_percent" in draft:
        for value in draft["weights_percent"].values():
            percent(value)
    if "lookback" in draft and (
        type(draft["lookback"]) is not int or not 1 <= draft["lookback"] <= 20
    ):
        raise ContractError("INVALID_LOOKBACK")
    if "direction" in draft and (
        type(draft["direction"]) is not int or draft["direction"] not in [-1, 1]
    ):
        raise ContractError("INVALID_DIRECTION")
    if "neutralize" in draft and type(draft["neutralize"]) is not bool:
        raise ContractError("INVALID_NEUTRALIZATION")
    return draft


def freeze_request(root, draft, defaults_revision=0, defaults=None):
    validate_draft(draft)
    base = deepcopy(defaults or {}) if draft.get("kind") != "replay" else {}
    base.update(draft)
    validate_draft(base)
    cat = catalogue(root)
    kind = base.get("kind", "research")
    if kind == "replay":
        if set(base) - {"kind", "source_task", "profile"} or base.get(
            "profile", "P5_NUMERICAL"
        ) not in ("P5_NUMERICAL", "PUBLISHED_REF_PROJECTION"):
            raise ContractError("REPLAY_PROFILE_NOT_REGISTERED")
        if base.get("profile") == "PUBLISHED_REF_PROJECTION":
            from aqrp.services.task_history import history_catalogue

            history = history_catalogue(root)
            if base["source_task"] != history["id"]:
                raise ContractError("HISTORICAL_CATALOG_CHANGED")
            payload = {
                "source_task": history["id"],
                "profile": "PUBLISHED_REF_PROJECTION",
                "history_sha256": digest(history),
            }
        else:
            source = str(__import__("uuid").UUID(base["source_task"]))
            payload = {"source_task": source, "profile": "P5_NUMERICAL"}
    else:
        config = deepcopy(cat["config"])
        names = base.get("factor_ids", ["momentum"])
        if not names or len(names) != len(set(names)) or not set(names) <= set(BUILTINS):
            raise ContractError("UNKNOWN_OR_DUPLICATE_CATALOG_FACTOR")
        expected_refs = [asdict(builtin_spec(n).ref) for n in names]
        if "factor_refs" in base and base["factor_refs"] != expected_refs:
            raise ContractError("EXACT_RESEARCH_REF_MISMATCH")
        config["candidates"] = [
            {
                "ref": r,
                "parameters": {"lookback": base.get("lookback", 2)},
                "direction": base.get("direction", 1),
                "hypothesis": n,
            }
            for n, r in zip(names, expected_refs, strict=True)
        ]
        if "horizons" in base:
            config["horizons"] = base["horizons"]
        if (
            not config["horizons"]
            or any(type(h) is not int or h < 1 or h > 10 for h in config["horizons"])
            or len(set(config["horizons"])) != len(config["horizons"])
        ):
            raise ContractError("INVALID_RESEARCH_HORIZON_GRID")
        config["pipeline"]["neutralize"] = base.get("neutralize", True)
        for field in ["start", "end"]:
            if field in base:
                from datetime import date

                if date.fromisoformat(base[field]).isoformat() != base[field]:
                    raise ContractError("INVALID_SESSION_DATE")
        config["decisions"] = [
            d
            for d in config["decisions"]
            if base.get("start", d["session"]) <= d["session"] <= base.get("end", d["session"])
        ]
        if not config["decisions"]:
            raise ContractError("NO_REQUIRED_DECISIONS")
        config["family"].update(
            id="ui-engineering-" + digest({k: v for k, v in config.items() if k != "family"}),
            budget=12,
        )
        config["family"]["hypotheses"] = [h["hypothesis"] for h in hypotheses(config)]
        s, e, v = references(root, cat)
        config["family"]["definitions"] = {
            h["hypothesis"]: hypothesis_definition(
                h, config, s.manifest_hash, e.manifest_hash, v.checksum
            )
            for h in hypotheses(config)
        }
        weights = base.get("weights_percent", {n: "100" for n in names})
        if set(weights) != set(names):
            raise ContractError("FACTOR_WEIGHT_SELECTION_MISMATCH")
        payload = {
            "research": config,
            "execution": {
                "initial_cash": base.get("initial_cash", "1000"),
                "fee_budget": base.get("fee_budget", "10"),
                "factor_weights": {n: percent(weights[n]) for n in names},
                "policy": base.get("policy", {}),
                "constraints": base.get("constraints", {}),
            },
            "raw_draft": base,
        }
    return EffectiveRequest(
        canonical(
            {
                "schema": "task-request/1",
                "kind": kind,
                "catalogue_revision": cat["revision"],
                "defaults_revision": defaults_revision,
                "code_commit": cat["code_commit"],
                "code_bundle": cat["code_bundle"],
                "core_lock_hash": LOCK_HASH,
                "ui_lock_hash": cat["ui_environment"]["lock_sha256"],
                "environment_hash": digest(
                    {"core": cat["core_environment"], "ui": cat["ui_environment"]}
                ),
                "payload": payload,
            }
        )
    )


def research_request(root, request):
    cat = catalogue(root)
    s, e, v = references(root, cat)
    return ResearchRequest.create(request["payload"]["research"], s, e, v, request["code_commit"])
