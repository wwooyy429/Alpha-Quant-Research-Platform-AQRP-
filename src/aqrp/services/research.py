"""PIT research orchestration, immutable experiments and JSON/HTML reporting."""

import hashlib
import html
import json
import math
from dataclasses import asdict, dataclass
from datetime import date

import pandas as pd

from aqrp.core.canonical import canonical, digest
from aqrp.core.contracts import QuerySpec
from aqrp.core.environment import runtime_manifest, verify_runtime
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.query import universe_at
from aqrp.data.snapshot import verify_snapshot
from aqrp.data.store import read_snapshot
from aqrp.experiments.ledger import ExperimentLedger
from aqrp.factors.admission import LOCK_HASH, builtin_spec, bundle_manifest
from aqrp.factors.contracts import FactorRef
from aqrp.factors.engine import FactorEngine
from aqrp.factors.registry import FactorRegistry
from aqrp.research.numerics import correlation, group_metrics, ic_summary
from aqrp.research.pipeline import compose, pipeline
from aqrp.validation.approvals import propose
from aqrp.validation.inference import adjust_pvalues, bandwidth, hac
from aqrp.validation.labels import make_labels
from aqrp.validation.splits import partition, purged_train, validate_splits, walk_forward


def serial(value):
    """Explicit numeric nulls; raw nonfinite values never enter canonical JSON."""
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


@dataclass(frozen=True)
class ResearchRequest:
    config: bytes
    snapshot: object
    exposures: object
    coverage: object
    code_commit: str

    @classmethod
    def create(cls, config, snapshot, exposures, coverage, code_commit):
        return cls(canonical(config), snapshot, exposures, coverage, code_commit)


def _specs(candidates):
    registry = FactorRegistry()
    result = []
    for candidate in candidates:
        if set(candidate) != {"ref", "parameters", "direction", "hypothesis"}:
            raise ContractError("INVALID_RESEARCH_CANDIDATE_SCHEMA")
        ref = FactorRef(**candidate["ref"])
        spec = builtin_spec(ref.factor_id, ref.factor_version)
        if ref != spec.ref:
            raise ContractError("EXACT_RESEARCH_REF_MISMATCH")
        registry.register(
            spec.implementation_version,
            spec,
            actor="research-service",
            reason="fixed-preregistered-candidate",
            evidence="engineering-receipt",
        )
        result.append((candidate, spec))
    return registry, result


def hypotheses(config):
    """Every evaluated candidate × horizon, including composites, is a family slot."""
    bases = [{**c, "stage": "final"} for c in config["candidates"]]
    if config.get("composite"):
        composite = config["composite"]
        bases.append(
            {
                "hypothesis": composite["hypothesis"],
                "ref": {"research_composite_sha256": digest(composite)},
                "parameters": {},
                "direction": 1,
                "stage": "composite",
            }
        )
    return [
        {
            **c,
            "score_key": c["hypothesis"],
            "hypothesis": c["hypothesis"] + "::h=" + str(h),
            "horizon": h,
        }
        for c in bases
        for h in config["horizons"]
    ]


def measurements(stages, labels, config):
    """Pair only matching session/security/horizon; keep all invalid-day reasons."""
    rows = []
    by_key = {(r["session"], r["security_id"], r["horizon"]): r for r in labels}
    for stage, item in stages.items():
        frame = item["rows"]
        for (factor, session), section in frame.groupby(["factor_key", "session"], sort=True):
            for horizon in config["horizons"]:
                paired = [
                    (r.score, by_key.get((str(session), r.security_id, horizon), {}).get("label"))
                    for r in section.itertuples()
                ]
                scores, returns = zip(*paired)
                ic = correlation(scores, returns, min_n=config["min_ic_n"])
                rank = correlation(scores, returns, rank=True, min_n=config["min_ic_n"])
                grouping = group_metrics(scores, returns, config["groups"], config["min_group_n"])
                rows.append(
                    {
                        "factor_key": factor,
                        "stage": stage,
                        "session": str(session),
                        "horizon": horizon,
                        "split": partition(str(session), config["splits"]),
                        "ic": ic,
                        "rank_ic": rank,
                        "groups": grouping,
                    }
                )
    summaries = []
    keys = sorted({(r["factor_key"], r["stage"], r["horizon"], r["split"]) for r in rows})
    for factor, stage, horizon, split in keys:
        series = [
            r
            for r in rows
            if (r["factor_key"], r["stage"], r["horizon"], r["split"])
            == (factor, stage, horizon, split)
        ]
        annual = {}
        for year in sorted({r["session"][:4] for r in series}):
            annual[year] = ic_summary(
                [r["ic"]["value"] for r in series if r["session"].startswith(year)]
            )
        summaries.append(
            {
                "factor_key": factor,
                "stage": stage,
                "horizon": horizon,
                "split": split,
                "ic": ic_summary([r["ic"]["value"] for r in series]),
                "rank_ic": ic_summary([r["rank_ic"]["value"] for r in series]),
                "annual": annual,
                "tmb": ic_summary([r["groups"]["tmb"] for r in series]),
            }
        )
    return {
        "daily": rows,
        "summaries": summaries,
        "decay": [
            {
                "factor_key": r["factor_key"],
                "split": r["split"],
                "horizon": r["horizon"],
                "mean_ic": r["ic"]["mean"],
            }
            for r in summaries
            if r["stage"] in ("final", "composite")
        ],
    }


def hypothesis_definition(candidate, config, snapshot_hash, exposure_hash, coverage_hash):
    return digest(
        {
            "candidate": candidate,
            "protocol": {k: v for k, v in config.items() if k not in ("family", "candidates")},
            "family_profile": {k: v for k, v in config["family"].items() if k != "definitions"},
            "snapshot": snapshot_hash,
            "exposures": exposure_hash,
            "coverage": coverage_hash,
        }
    )


def research(request, output_root, *, task_context=None):
    """One shared service for CLI and SDK. Formal Test is a separate sealed entry."""
    return _research(request, output_root, task_context=task_context)


def _research(request, output_root, *, operator_claims=None, task_context=None):
    config = json.loads(request.config)
    ledger = ExperimentLedger(output_root)
    bundle = digest(bundle_manifest())
    lineage = {
        "code_commit": request.code_commit,
        "code_bundle": bundle,
        "data_hash": request.snapshot.manifest_hash,
        "exposure_hash": request.exposures.manifest_hash if request.exposures else None,
        "coverage_hash": request.coverage.checksum,
        "environment": {**runtime_manifest(), "lock": LOCK_HASH},
        "protocol_hash": digest(config),
        "permission_domain": config.get("purpose"),
        "seed": config.get("seed"),
        "cost_rules": "NOT_APPLICABLE_P3_RESEARCH_NO_EXECUTION_ORDERS",
    }
    run_id = ledger.start(config, lineage, task_context=task_context)
    try:
        if task_context is not None:
            task_context.checkpoint()
        verify_runtime(lineage["environment"])
        validate_splits(config["splits"])
        if config["purpose"] not in ("DEVELOPMENT", "ENGINEERING_DEMO") and not (
            config["purpose"] == "FINAL_TEST" and operator_claims
        ):
            raise ContractError("USE_SEALED_OPERATOR_ENTRY_FOR_FINAL_TEST")
        coverage = request.coverage.read(request.snapshot.manifest_hash)
        if config["purpose"] == "ENGINEERING_DEMO" and coverage["scope"] != "PUBLIC_ENGINEERING":
            raise ContractError("ENGINEERING_INPUT_MUST_BE_PUBLIC")
        if config["purpose"] == "DEVELOPMENT" and not utc(config["evaluation_cutoff"]) <= utc(
            config["development_cutoff"]
        ) < utc(config["splits"]["test"][0] + "T00:00:00Z"):
            raise ContractError("DEVELOPMENT_CUTOFF_ENTERS_TEST")
        if any(w["fit"][1] > config["splits"]["test"][0] for w in config["walk_forward"]):
            raise ContractError("TEST_CANNOT_ENTER_WALK_FORWARD_FIT")
        if config["purpose"] == "FINAL_TEST" and coverage["scope"] != "OPERATOR_SEALED":
            raise ContractError("FORMAL_COVERAGE_MUST_BE_SEALED")
        verify_snapshot(request.snapshot)
        if (
            request.exposures is not None
            and request.exposures.parent_hash != request.snapshot.manifest_hash
        ):
            raise ContractError("EXPOSURE_RESEARCH_PARENT_MISMATCH")
        if (
            type(config["seed"]) is not int
            or type(config["min_ic_n"]) is not int
            or config["min_ic_n"] < 3
        ):
            raise ContractError("INVALID_RESEARCH_NUMERIC_PROFILE")
        if (
            not config["horizons"]
            or len(set(config["horizons"])) != len(config["horizons"])
            or any(type(h) is not int or h < 1 for h in config["horizons"])
        ):
            raise ContractError("INVALID_RESEARCH_HORIZON_GRID")
        declarations = config["family"]["hypotheses"]
        definitions = config["family"]["definitions"]
        if set(definitions) != set(declarations):
            raise ContractError("INCOMPLETE_PREREGISTERED_HYPOTHESES")
        ledger.family(config["family"]["id"], declarations, definitions=definitions)
        registry, candidates = _specs(config["candidates"])
        if not candidates:
            raise ContractError("NO_RESEARCH_CANDIDATES")
        analysis_candidates = hypotheses(config)
        if len({c["hypothesis"] for c in analysis_candidates}) != len(analysis_candidates):
            raise ContractError("DUPLICATE_RESEARCH_HYPOTHESIS")
        trials = []
        for candidate in analysis_candidates:
            if candidate["hypothesis"] not in declarations:
                raise ContractError("UNREGISTERED_HYPOTHESIS")
            if definitions[candidate["hypothesis"]] != hypothesis_definition(
                candidate,
                config,
                request.snapshot.manifest_hash,
                lineage["exposure_hash"],
                request.coverage.checksum,
            ):
                raise ContractError("HYPOTHESIS_CHANGED_AFTER_PREREGISTRATION")
            trials.append(
                ledger.register_trial(
                    run_id,
                    config["family"]["id"],
                    candidate["hypothesis"],
                    budget=config["family"]["budget"],
                    hypothesis_spec=candidate,
                )
            )
            if candidate["direction"] not in (-1, 1) or type(candidate["direction"]) is not int:
                raise ContractError("INVALID_FACTOR_DIRECTION")
        _, tables = read_snapshot(request.snapshot)
        markets = {r["security_id"]: r["market_id"] for r in tables["security_master"].to_pylist()}
        calendar = sorted(
            [
                r
                for r in tables["calendar"].to_pylist()
                if r["calendar_id"] == config["calendar_id"]
                and r["market_id"] == config["market_id"]
            ],
            key=lambda r: r["session_date"],
        )
        if len({r["session_date"] for r in calendar}) != len(calendar):
            raise ContractError("RESEARCH_CALENDAR_REVISION_MUST_BE_FROZEN")
        decisions = [
            {"session": date.fromisoformat(r["session"]), "decision_time": utc(r["decision_time"])}
            for r in config["decisions"]
        ]
        if not decisions:
            raise ContractError("EMPTY_RESEARCH_DECISIONS")
        if [r["session"] for r in decisions] != sorted({r["session"] for r in decisions}):
            raise ContractError("INVALID_DECISION_GRID")
        if config["purpose"] == "DEVELOPMENT" and any(
            partition(str(r["session"]), config["splits"]) not in ("train", "validation")
            for r in decisions
        ):
            raise ContractError("TEST_ACCESS_FORBIDDEN_IN_DEVELOPMENT")
        if any(partition(str(r["session"]), config["splits"]) == "outside" for r in decisions):
            raise ContractError("DECISION_OUTSIDE_REGISTERED_SPLITS")
        engine = FactorEngine(registry)
        rows, all_ids, engine_evidence = [], set(), []
        cache_key = {"config": config, "lineage": lineage}
        cached = ledger.cache_get(cache_key)
        if cached is None:
            for decision in decisions:
                if task_context is not None:
                    task_context.checkpoint()
                members = universe_at(
                    config["universe_id"], decision["decision_time"], request.snapshot
                )
                ids = tuple(
                    sorted(
                        {
                            r["security_id"]
                            for r in members
                            if markets[r["security_id"]] == config["market_id"]
                        }
                    )
                )
                if not ids:
                    raise ContractError("EMPTY_HISTORICAL_UNIVERSE")
                all_ids.update(ids)
                for candidate, spec in candidates:
                    query = QuerySpec(
                        ids,
                        config["market_id"],
                        config["calendar_id"],
                        (calendar[0]["session_date"], decision["session"]),
                        fields=spec.required_fields,
                        price_basis=spec.price_basis,
                    )
                    batch = engine.run(
                        spec.ref,
                        query,
                        decision["decision_time"],
                        request.snapshot,
                        parameters=candidate["parameters"],
                        run_id=run_id,
                        seed=config["seed"],
                    )
                    engine_evidence.append(
                        {
                            "factor": asdict(spec.ref),
                            "session": str(decision["session"]),
                            "content_hash": batch.content_hash,
                            "logical_hash": batch.logical_hash,
                            "config": json.loads(batch.config_snapshot),
                            "config_snapshot_utf8": batch.config_snapshot.decode("utf-8"),
                            "config_snapshot_sha256": hashlib.sha256(
                                batch.config_snapshot
                            ).hexdigest(),
                            "signals": [asdict(r) for r in batch.rows],
                            "origin_run_id": run_id,
                        }
                    )
                    for row in batch.rows:
                        rows.append(
                            {
                                "factor_key": candidate["hypothesis"],
                                "factor_ref": asdict(spec.ref),
                                "params_hash": json.loads(batch.config_snapshot)["params_hash"],
                                "signal_time": row.signal_time,
                                "session": str(decision["session"]),
                                "security_id": row.security_id,
                                "score": row.factor_value,
                                "decision_time": decision["decision_time"],
                                "available_at": row.available_at,
                                "validity": row.validity,
                                "reason": row.reason,
                            }
                        )
            cached = serial(
                {"rows": rows, "security_ids": sorted(all_ids), "engine_evidence": engine_evidence}
            )
            ledger.cache_put(cache_key, cached)
        else:
            ledger.event(run_id, "CACHE_HIT", {"key_hash": digest(cache_key)})
        if task_context is not None:
            task_context.checkpoint()
        ledger.artifact(run_id, "engine.json", cached["engine_evidence"])
        stages = pipeline(
            pd.DataFrame(cached["rows"]),
            config["pipeline"],
            request.exposures,
            market=config["market_id"],
            currency=config["currency"],
            calendar_grid=[
                str(r["session_date"])
                for r in calendar
                if decisions[0]["session"] <= r["session_date"] <= decisions[-1]["session"]
            ],
        )
        for stage, item in stages.items():
            ledger.artifact(
                run_id,
                stage + ".json",
                serial({k: v.to_dict("records") if k == "rows" else v for k, v in item.items()}),
            )
        synthesis = None
        if config.get("composite"):
            synthesis = compose(stages["final"]["rows"], config["composite"])
            ledger.artifact(run_id, "composite.json", serial(synthesis))
            if synthesis["scores"]:
                composite_frame = pd.DataFrame(synthesis["scores"])
                stages["composite"] = {"rows": composite_frame}
        labels = make_labels(
            request.snapshot,
            decisions,
            cached["security_ids"],
            config["horizons"],
            config["evaluation_cutoff"],
            request.coverage,
        )
        if config["purpose"] == "DEVELOPMENT" and any(
            r["label"] is not None and utc(r["available_at"]) > utc(config["development_cutoff"])
            for r in labels
        ):
            raise ContractError("DEVELOPMENT_LABEL_AFTER_ALLOWED_CUTOFF")
        directions = {c["hypothesis"]: c["direction"] for c, _ in candidates}
        # Direction is selected in preregistered development, applied exactly once.
        measured = {}
        for stage, item in stages.items():
            frame = item["rows"].copy(deep=True)
            frame["score"] = [
                r.score * directions.get(r.factor_key, 1) if pd.notna(r.score) else None
                for r in frame.itertuples()
            ]
            measured[stage] = {"rows": frame}
        metrics = measurements(measured, labels, config)
        calendar_dates = [str(r["session_date"]) for r in calendar]
        oos = {
            "train_for_validation": purged_train(
                labels,
                config["splits"]["train"],
                config["splits"]["validation"],
                config["fit_cutoff"],
                calendar_dates,
                config["splits"]["embargo_sessions"],
            ),
            "walk_forward": walk_forward(
                labels, config["walk_forward"], calendar_dates, config["splits"]["embargo_sessions"]
            ),
        }
        marginal = {}
        infer = config["inference"]
        for candidate in analysis_candidates:
            values = [
                r["ic"]["value"]
                for r in metrics["daily"]
                if r["factor_key"] == candidate["score_key"]
                and r["stage"] == candidate["stage"]
                and r["split"] == ("test" if operator_claims else "validation")
                and r["horizon"] == candidate["horizon"]
            ]
            valid = [v for v in values if v is not None]
            if len(valid) < 2:
                result = {"p": None, "reason": "INSUFFICIENT_VALID_HAC_SAMPLE"}
            else:
                lag = min(len(valid) - 1, bandwidth(len(valid), candidate["horizon"], infer["m0"]))
                if operator_claims:
                    qualification = {
                        **infer.get("qualifications", {}).get(
                            candidate["hypothesis"], infer.get("qualification", {})
                        ),
                        "complete_session_grid": len(valid) == len(values),
                        "actual_session_grid": [
                            r["session"]
                            for r in metrics["daily"]
                            if r["factor_key"] == candidate["score_key"]
                            and r["stage"] == candidate["stage"]
                            and r["split"] == "test"
                            and r["horizon"] == candidate["horizon"]
                        ],
                    }
                    if (
                        qualification.get("horizon") != candidate["horizon"]
                        or qualification.get("m0") != infer["m0"]
                        or digest(qualification)
                        != operator_claims.get("qualification_hashes", {}).get(
                            candidate["hypothesis"], operator_claims.get("qualification_hash")
                        )
                    ):
                        raise ContractError("FORMAL_QUALIFICATION_NOT_AUTHORIZED")
                    lag = bandwidth(qualification["planned_n"], candidate["horizon"], infer["m0"])
                    result = hac(valid, lag, mode="FORMAL_ASYMPTOTIC", qualification=qualification)
                else:
                    result = hac(valid, lag, mode="ENGINEERING_DEMO")
                result["complete_session_grid"] = len(valid) == len(values)
            marginal[candidate["hypothesis"]] = result
        family = ledger.family(
            config["family"]["id"], declarations, marginal, definitions=definitions
        )
        raw = [family["results"].get(k, {}).get("p") for k in declarations]
        multiplicity = adjust_pvalues(
            raw, config["family"]["method"], bh_evidence=config["family"].get("bh_evidence")
        )
        multiplicity.update(
            hypotheses=declarations,
            contaminated=bool(family["duplicate_hypotheses"])
            or any(t["repeat_of"] for t in trials),
        )
        for name, payload in (
            ("labels", labels),
            ("metrics", metrics),
            ("oos", oos),
            ("inference", marginal),
            ("multiplicity", multiplicity),
        ):
            ledger.artifact(run_id, name + ".json", serial(payload))
        proposals = {}
        for candidate in analysis_candidates:
            summary = next(
                (
                    r["ic"]
                    for r in metrics["summaries"]
                    if r["stage"] == candidate["stage"]
                    and r["factor_key"] == candidate["score_key"]
                    and r["horizon"] == candidate["horizon"]
                    and r["split"] == ("test" if operator_claims else "validation")
                ),
                ic_summary([]),
            )
            evidence = {
                "all_candidates_recorded": set(family["results"]) == set(declarations),
                "contaminated": multiplicity["contaminated"],
                "code_hash": bundle,
                "data_hash": request.snapshot.manifest_hash,
                "environment_hash": digest(lineage["environment"]),
                "frozen_protocol_hash": digest(config),
                "validation_first_access_at": min(t["first_validation_access_at"] for t in trials),
                "independent_golden_ref": (operator_claims or {}).get("independent_golden_ref"),
                "implementation_review_ref": (operator_claims or {}).get(
                    "implementation_review_ref"
                ),
            }
            proposals[candidate["hypothesis"]] = propose(
                candidate,
                config.get("approval_protocols", {}).get(
                    candidate["hypothesis"], config.get("approval_protocol", {})
                ),
                summary,
                multiplicity,
                {"purpose": config["purpose"], "independence_verified": bool(operator_claims)},
                evidence,
            )
        ledger.artifact(run_id, "approvals.json", serial(proposals))
        report = {
            "schema": "research-report/1",
            "run_id": run_id,
            "purpose": config["purpose"],
            "financial_approval": "NONE",
            "independence_verified": bool(operator_claims),
            "formal_test_status": "PRIVATE_OPERATOR_EXECUTION"
            if operator_claims
            else "NOT_DEPLOYED_NOT_EXECUTED",
            "lineage": lineage,
            "metrics": metrics,
            "multiplicity": multiplicity,
            "approval": proposals,
        }
        document = (
            "<!doctype html><meta charset='utf-8'><title>AQRP research</title><h1>AQRP research</h1><pre>"
            + html.escape(json.dumps(serial(report), ensure_ascii=False, indent=2))
            + "</pre>"
        )
        ledger.artifact(run_id, "report.json", serial(report))
        ledger.artifact(run_id, "report.html", document)
        ledger.artifact(
            run_id,
            "report-html.json",
            {
                "media_type": "text/html",
                "content": document,
                "sha256": hashlib.sha256(document.encode()).hexdigest(),
            },
        )
        if task_context is not None:
            task_context.checkpoint()
        ledger.finish(run_id, "SUCCEEDED")
        return {"run_id": run_id, "manifest": ledger.verify(run_id), "report": serial(report)}
    except BaseException as exc:
        ledger.artifact(
            run_id,
            "failure.json",
            {"error_type": type(exc).__name__, "code": getattr(exc, "code", "EXECUTION_ERROR")},
        )
        ledger.finish(run_id, "CANCELLED" if isinstance(exc, KeyboardInterrupt) else "FAILED")
        raise


def evaluate_sealed(request, evaluator):
    """Operator-only application entry; no policy or filesystem path from user JSON.

    OS host/authorization checks precede private data loading. All raw outputs
    stay under the sealed control root; only opaque completion leaves it.
    """
    config = json.loads(request.config)
    if config.get("purpose") != "FINAL_TEST" or evaluator.policy is None:
        raise ContractError("SEALED_FINAL_TEST_REQUIRED")
    bindings = {
        "config_hash": digest(config),
        "code_commit": request.code_commit,
        "code_bundle": digest(bundle_manifest()),
        "snapshot": request.snapshot.manifest_hash,
        "exposures": request.exposures.manifest_hash if request.exposures else None,
        "coverage": request.coverage.checksum,
    }
    claims = evaluator.policy.authorize(bindings)
    # Input paths and deployment roots are selected by the trusted launcher.
    for path in (
        request.snapshot.root,
        request.exposures.root if request.exposures else request.snapshot.root,
    ):
        if not path.resolve().is_relative_to(evaluator.policy.root):
            raise ContractError("FINAL_INPUT_OUTSIDE_SEALED_ROOT")
    return evaluator.process(
        bindings,
        lambda: _research(request, evaluator.root / "research-runs", operator_claims=claims),
        purpose="FINAL_TEST",
    )
