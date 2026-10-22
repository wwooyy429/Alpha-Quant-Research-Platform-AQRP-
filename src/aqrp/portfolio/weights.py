"""Exact pre-registered factor aggregation and deterministic long/short legs."""

from .contracts import F, fail, number


def allocate(x, maps, scores):
    policy = x["policy"]
    factors = policy["factor_weights"]
    denominator = sum(abs(number(v)) for v in factors.values())
    combined, exclusions = {}, []
    for sid in sorted(maps["securities"]):
        state = maps["status"][sid]
        if not state["in_universe"] or not state["tradable"]:
            exclusions.append({"security_id": sid, "reason": "NOT_SELECTABLE"})
        elif any(sid not in rows or not rows[sid]["valid"] for rows in scores.values()):
            exclusions.append({"security_id": sid, "reason": "OUTSIDE_VALID_INTERSECTION"})
        else:
            combined[sid] = (
                sum(
                    number(factors[k]) * number(rows[sid]["score"], score=True)
                    for k, rows in scores.items()
                )
                / denominator
            )
    ranked = sorted(combined, key=lambda sid: (-combined[sid], sid))
    ties = [sid for sid in ranked if sum(combined[sid] == v for v in combined.values()) > 1]
    weights = {s: F(0) for s in maps["securities"]}
    if not ranked:
        if policy["mode"] == "LONG_SHORT" and number(policy["gross"]):
            fail("INFEASIBLE_EMPTY_LEG")
        return weights, {
            "scores": combined,
            "ranked": ranked,
            "ties": ties,
            "exclusions": exclusions,
            "reason": "EMPTY_INTERSECTION",
        }
    if policy["mode"] == "LONG_ONLY":
        selected = ranked[: policy["top_k"]]
        parts = {
            s: F(1) if policy["weighting"] == "equal" else max(combined[s], 0) for s in selected
        }
        total = sum(parts.values())
        if total:
            weights.update({s: v / total for s, v in parts.items()})
        reason = "NONE" if total else "NO_POSITIVE_SCORE"
    else:
        g, n = number(policy["gross"]), number(policy["net"])
        long_budget, short_budget = (g + n) / 2, (g - n) / 2
        if policy["weighting"] == "equal":
            longs = ranked[: policy["long_k"]] if long_budget else []
            shorts = list(reversed(ranked))[: policy["short_k"]] if short_budget else []
            if set(longs) & set(shorts) or (
                long_budget and short_budget and policy["long_k"] + policy["short_k"] > len(ranked)
            ):
                fail("INFEASIBLE_OVERLAPPING_LEGS")
            values = {s: F(1) for s in ranked}
        else:
            center = sum(combined.values()) / len(combined)
            centered = {s: v - center for s, v in combined.items()}
            longs = (
                [s for s in ranked if centered[s] > 0][: policy["long_k"]] if long_budget else []
            )
            shorts = (
                [s for s in reversed(ranked) if centered[s] < 0][: policy["short_k"]]
                if short_budget
                else []
            )
            values = {s: abs(v) for s, v in centered.items()}
        for leg, budget in [(longs, long_budget), (shorts, -short_budget)]:
            if budget and not leg:
                fail("INFEASIBLE_EMPTY_LEG")
            total = sum(values[s] for s in leg)
            if total:
                weights.update({s: budget * values[s] / total for s in leg})
        reason = "NONE"
    return weights, {
        "scores": combined,
        "ranked": ranked,
        "ties": ties,
        "exclusions": exclusions,
        "reason": reason,
    }
