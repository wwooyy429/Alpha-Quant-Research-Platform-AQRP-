"""Five explicit stages, PIT neutralization and preregistered research synthesis."""

import math
from itertools import combinations

import numpy as np
import pandas as pd

from aqrp.core.canonical import digest
from aqrp.core.errors import ContractError
from aqrp.core.time import utc
from aqrp.data.exposures import exposures_as_of
from aqrp.research.numerics import clean, conditional, correlation, ols, rolling, standardize


def operators(frame, specs, calendar_grid=None):
    """Closed structured operators, aligned to the complete supplied decision grid."""
    result = frame.copy(deep=True)
    result["score"] = pd.to_numeric(result["score"], errors="raise").astype(float)
    for spec in specs:
        op = spec["op"]
        if op == "rank":
            for _, section in result.groupby(["factor_key", "session"]):
                result.loc[section.index, "score"] = np.array(
                    standardize(section["score"], "rank"), dtype=float
                )
        elif op == "conditional":
            result["score"] = conditional(
                result["score"].tolist(),
                spec["comparison"],
                [spec["threshold"]] * len(result),
                result["score"].tolist(),
                [spec["otherwise"]] * len(result),
            )
        else:
            grid = sorted(result["session"].unique()) if calendar_grid is None else calendar_grid
            frozen_input = result.copy(deep=True)
            for (key, sid), section in frozen_input.groupby(["factor_key", "security_id"]):
                section = section.set_index("session").reindex(grid)
                other = None
                if op == "correlation":
                    other = (
                        frozen_input[
                            (frozen_input["factor_key"] == spec["other_factor"])
                            & (frozen_input["security_id"] == sid)
                        ]
                        .set_index("session")["score"]
                        .reindex(grid)
                        .tolist()
                    )
                values = rolling(section["score"].tolist(), spec["length"], op, other)
                lookup = dict(zip(grid, values))
                selected = (result["factor_key"] == key) & (result["security_id"] == sid)
                result.loc[selected, "score"] = (
                    result.loc[selected, "session"].map(lookup).to_numpy(dtype=float)
                )
    return result


def pipeline(frame, spec, exposure_ref=None, *, market=None, currency=None, calendar_grid=None):
    current = frame.copy(deep=True)
    current["score"] = pd.to_numeric(current["score"], errors="raise").astype(float)
    if current.duplicated(["factor_key", "session", "security_id"]).any():
        raise ContractError("DUPLICATE_STAGE_SCORE")
    for _, section in current.groupby(["factor_key", "session"]):
        if section["decision_time"].nunique() != 1:
            raise ContractError("MIXED_DECISION_TIMES")
    if "available_at" in current and any(
        utc(r.available_at) > utc(r.decision_time) for r in current.itertuples()
    ):
        raise ContractError("STAGE_INPUT_NOT_AVAILABLE_AT_DECISION")
    current["stage"] = "raw"
    current["validity"] = ["VALID" if math.isfinite(x) else "INVALID" for x in current["score"]]
    if "reason" not in current:
        current["reason"] = "NONE"
    current.loc[current["validity"] == "INVALID", "reason"] = "RAW_NONFINITE_INPUT"
    current.loc[current["validity"] == "INVALID", "score"] = np.nan
    stages = {
        "raw": {
            "status": "EXECUTED",
            "input_ref": None,
            "rows": current.copy(deep=True),
            "diagnostics": [],
            "counts": {"input": len(current), "valid": int((current["validity"] == "VALID").sum())},
        }
    }
    current = operators(current, spec.get("operators", []), calendar_grid)
    for stage in ("clean", "standardized", "neutralized", "final"):
        previous = list(stages)[-1]
        diagnostics = []
        enabled = stage == "final" or (
            spec["neutralize"] if stage == "neutralized" else spec[stage]["method"] != "none"
        )
        if enabled and stage != "final":
            for (factor, session), group in current.groupby(["factor_key", "session"], sort=True):
                values = group["score"].tolist()
                if stage == "clean":
                    result = clean(values, spec[stage]["method"], spec[stage])
                elif stage == "standardized":
                    result = standardize(values, spec[stage]["method"])
                else:
                    if exposure_ref is None:
                        raise ContractError("EXPOSURES_REQUIRED")
                    cutoff = group["decision_time"].iloc[0]
                    exposure = exposures_as_of(
                        exposure_ref, cutoff, market, currency, set(group["security_id"])
                    )
                    valid = []
                    for index, (sid, value) in enumerate(zip(group["security_id"], values)):
                        e = exposure.get(sid)
                        if (
                            e
                            and e["industry"] is not None
                            and e["market_cap"] is not None
                            and pd.notna(value)
                        ):
                            valid.append((index, float(value), e))
                    result = [None] * len(values)
                    if valid:
                        industries = sorted({e["industry"] for _, _, e in valid})
                        design = [
                            [1]
                            + [float(e["industry"] == i) for i in industries[1:]]
                            + [math.log(float(e["market_cap"]))]
                            for _, _, e in valid
                        ]
                        fit = ols([value for _, value, _ in valid], design)
                        for (index, _, _), residual in zip(valid, fit["residual"]):
                            result[index] = residual
                        diagnostics.append(
                            {
                                "factor": factor,
                                "session": session,
                                "fit_scope": "CURRENT_PIT_SECTION",
                                "fit_cutoff": cutoff,
                                "industry_base": industries[0],
                                "n_excluded": len(values) - len(valid),
                                "exposure_hash": exposure_ref.manifest_hash,
                                **{k: v for k, v in fit.items() if k != "residual"},
                            }
                        )
                    else:
                        diagnostics.append(
                            {
                                "factor": factor,
                                "session": session,
                                "reason": "NO_VALID_EXPOSURES",
                                "n_excluded": len(values),
                            }
                        )
                current.loc[group.index, "score"] = np.array(result, dtype=float)
        current["stage"] = stage
        current["validity"] = [
            "VALID" if pd.notna(x) and math.isfinite(x) else "INVALID" for x in current["score"]
        ]
        missing = (current["validity"] == "INVALID") & (current["reason"] == "NONE")
        current.loc[missing, "reason"] = stage.upper() + "_NONFINITE_OR_INSUFFICIENT_INPUT"
        stages[stage] = {
            "status": "EXECUTED"
            if enabled or (stage == "clean" and spec.get("operators"))
            else "SKIPPED",
            "input_ref": previous,
            "rows": current.copy(deep=True),
            "diagnostics": diagnostics,
            "pipeline_hash": digest(spec),
            "fit_scope": "PIT_CROSS_SECTION_NO_LABELS",
            "counts": {
                "input": len(current),
                "valid": int((current["validity"] == "VALID").sum()),
                "invalid": int((current["validity"] == "INVALID").sum()),
            },
        }
    return stages


def compose(frame, spec):
    keys = spec["factor_keys"]
    weights = spec["weights"]
    directions = spec["directions"]
    if type(spec["min_n"]) is not int or spec["min_n"] < 2:
        raise ContractError("INVALID_COMPOSITE_MIN_N")
    rule = spec["redundancy"]
    if rule is not None and (
        type(rule["min_pair_n"]) is not int
        or rule["min_pair_n"] < 2
        or type(rule["min_days"]) is not int
        or rule["min_days"] < 1
        or not 0 <= rule["tau"] <= 1
        or not 0 <= rule["min_fraction"] <= 1
    ):
        raise ContractError("INVALID_REDUNDANCY_PROFILE")
    if len(set(keys)) != len(keys) or len(keys) != len(weights) or len(keys) != len(directions):
        raise ContractError("INVALID_COMPOSITE_KEYS")
    if any(
        type(w) not in (int, float) or not math.isfinite(w) or w < 0 for w in weights
    ) or not sum(weights):
        raise ContractError("INVALID_WEIGHTS")
    if (
        any(type(d) is not int or d not in (-1, 1) for d in directions)
        or spec["direction_applied"] is not False
    ):
        raise ContractError("DIRECTION_ALREADY_APPLIED_OR_INVALID")
    selected = [(k, w, d) for k, w, d in zip(keys, weights, directions) if w > 0]
    if len(selected) < 2 or spec["normalization"] != "cross_sectional_sample_z":
        raise ContractError("INSUFFICIENT_COMPONENTS_OR_NORMALIZATION")
    if frame["stage"].nunique() != 1 or frame["stage"].iloc[0] != spec["input_stage"]:
        raise ContractError("COMPOSITE_STAGE_MISMATCH")
    scores = []
    pairs = []
    for session, group in frame.groupby("session", sort=True):
        table = group.pivot(index="security_id", columns="factor_key", values="score").reindex(
            columns=[k for k, _, _ in selected]
        )
        table = table.replace([np.inf, -np.inf], np.nan).dropna()
        if len(table) < spec["min_n"]:
            pairs.append(
                {"session": session, "reason": "INSUFFICIENT_INTERSECTION", "n": len(table)}
            )
            continue
        z = table.apply(lambda col: standardize(col.tolist(), "zscore"), axis=0)
        if z.isna().any().any():
            pairs.append({"session": session, "reason": "ZERO_VARIANCE", "n": len(table)})
            continue
        value = sum(z[k] * w * d for k, w, d in selected) / sum(w for _, w, _ in selected)
        for sid, v in value.items():
            scores.append(
                {
                    "session": session,
                    "security_id": sid,
                    "score": float(v),
                    "factor_key": spec.get("hypothesis", digest(spec)),
                    "stage": group["stage"].iloc[0],
                    "mask_hash": digest(list(table.index)),
                    "composite_hash": digest(spec),
                }
            )
        for a, b in combinations(range(len(selected)), 2):
            ka, _, da = selected[a]
            kb, _, db = selected[b]
            pearson = correlation(table[ka], table[kb], min_n=2)
            rank = correlation(table[ka], table[kb], rank=True, min_n=2)
            rule = spec["redundancy"]
            flag = (
                None
                if rule is None or len(table) < rule["min_pair_n"]
                else abs(rank["value"]) >= rule["tau"]
            )
            pairs.append(
                {
                    "session": session,
                    "a": ka,
                    "b": kb,
                    "pearson": pearson,
                    "spearman": rank,
                    "signed_spearman": rank["value"] * da * db,
                    "flag": flag,
                    "reason": "NONE",
                    "classification": "UNCLASSIFIED" if flag is None else "DIAGNOSTIC_ONLY",
                }
            )
    aggregates = []
    for a, b in combinations([k for k, _, _ in selected], 2):
        eligible = [
            p for p in pairs if p.get("a") == a and p.get("b") == b and p["flag"] is not None
        ]
        rule = spec["redundancy"]
        flag = (
            None
            if rule is None or len(eligible) < rule["min_days"]
            else sum(p["flag"] for p in eligible) / len(eligible) >= rule["min_fraction"]
        )
        aggregates.append(
            {
                "a": a,
                "b": b,
                "eligible_days": len(eligible),
                "flag": flag,
                "auto_weight_change": False,
            }
        )
    return {"scores": scores, "pairs": pairs, "redundancy": aggregates, "spec_hash": digest(spec)}
