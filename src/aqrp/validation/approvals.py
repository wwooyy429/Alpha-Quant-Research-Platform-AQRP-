"""Research qualification proposals and human evidence; strategy remains a P5 gate."""

import json
import math
import re

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.validation.evaluator import verify_seal


def propose(candidate, protocol, metrics, multiplicity, evaluation, evidence):
    failures = []
    required = {"min_mean_ic", "min_days", "max_adjusted_p", "min_positive_fraction"}
    standards = protocol.get("standards", {})

    def number(value, low, high):
        return type(value) in (int, float) and math.isfinite(value) and low <= value <= high

    valid_standards = (
        required <= set(standards)
        and number(standards["min_mean_ic"], -1, 1)
        and type(standards["min_days"]) is int
        and standards["min_days"] > 0
        and number(standards["max_adjusted_p"], 0, 1)
        and standards["max_adjusted_p"] > 0
        and number(standards["min_positive_fraction"], 0, 1)
    )
    valid_metrics = (
        (metrics.get("mean") is None or number(metrics["mean"], -1, 1))
        and type(metrics.get("n")) is int
        and metrics["n"] >= 0
        and (metrics.get("positive_fraction") is None or number(metrics["positive_fraction"], 0, 1))
    )
    if (
        (required <= set(standards) and not valid_standards)
        or not valid_metrics
        or any(not number(p, 0, 1) for p in multiplicity.get("adjusted", []))
    ):
        failures.append("INVALID_APPROVAL_NUMBERS")
    if (
        not required <= set(standards)
        or not protocol.get("human_approval_record")
        or not protocol.get("frozen_at")
        or protocol.get("candidate_hash") != digest(candidate)
    ):
        failures.append("UNAPPROVED_STANDARDS")
    if (
        protocol.get("frozen_at")
        and evidence.get("validation_first_access_at")
        and utc(protocol["frozen_at"]) > utc(evidence["validation_first_access_at"])
    ):
        failures.append("POSTHOC_APPROVAL_PROTOCOL")
    if not evaluation.get("independence_verified") or evaluation.get("purpose") != "FINAL_TEST":
        failures.append("INDEPENDENT_TEST_NOT_VERIFIED")
    if (
        not multiplicity.get("complete")
        or not evidence.get("all_candidates_recorded")
        or evidence.get("contaminated")
    ):
        failures.append("FAMILY_INCOMPLETE_OR_CONTAMINATED")
    if not all(
        evidence.get(k)
        for k in (
            "independent_golden_ref",
            "implementation_review_ref",
            "code_hash",
            "data_hash",
            "environment_hash",
            "frozen_protocol_hash",
            "validation_first_access_at",
        )
    ):
        failures.append("INCOMPLETE_APPROVAL_EVIDENCE")
    if (
        not all(
            isinstance(evidence.get(k), str) and re.fullmatch("[0-9a-f]{64}", evidence[k])
            for k in ("code_hash", "data_hash", "environment_hash", "frozen_protocol_hash")
        )
        and "INCOMPLETE_APPROVAL_EVIDENCE" not in failures
    ):
        failures.append("INCOMPLETE_APPROVAL_EVIDENCE")
    if valid_standards and valid_metrics:
        if (
            metrics["mean"] is None
            or metrics["mean"] < standards["min_mean_ic"]
            or metrics["n"] < standards["min_days"]
        ):
            failures.append("IC_OR_SAMPLE_CRITERIA_FAILED")
        if (
            metrics["positive_fraction"] is None
            or metrics["positive_fraction"] < standards["min_positive_fraction"]
        ):
            failures.append("STABILITY_CRITERIA_FAILED")
        if (
            not multiplicity.get("adjusted")
            or any(not number(p, 0, 1) for p in multiplicity["adjusted"])
            or max(multiplicity["adjusted"]) > standards["max_adjusted_p"]
        ):
            failures.append("MULTIPLICITY_CRITERIA_FAILED")
    return {
        "candidate": candidate,
        "protocol_hash": digest(protocol),
        "metrics": metrics,
        "multiplicity": multiplicity,
        "evaluation": evaluation,
        "evidence": evidence,
        "eligible": not failures,
        "failures": failures,
        "state": "RESEARCH_VALIDATION_PROPOSAL" if not failures else "REJECTED",
        "strategy_approval": False,
    }


def record_decision(ledger, run_id, proposal, envelope, operator_key):
    record = verify_seal(envelope, operator_key)
    if (
        record["proposal_hash"] != digest(proposal)
        or not record["human_actor"]
        or record["state"] != "ResearchValidated"
        or not proposal["eligible"]
    ):
        raise ContractError("INVALID_HUMAN_RESEARCH_DECISION")
    ledger.verify(run_id)
    path = ledger.path(run_id) / "approvals.json"
    if not path.exists() or not any(
        digest(p) == digest(proposal) for p in json.loads(path.read_bytes()).values()
    ):
        raise ContractError("PROPOSAL_NOT_IN_IMMUTABLE_RUN")
    ledger.decision(
        run_id,
        {
            "envelope": envelope,
            "record": record,
            "proposal": proposal,
            "proposal_hash": digest(proposal),
        },
    )
    return {
        "state": "ResearchValidated",
        "proposal_hash": digest(proposal),
        "human_actor": record["human_actor"],
        "strategy_approval": False,
    }
