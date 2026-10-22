"""Unvalidated targets only; no account mutation, broker or order creation."""

from aqrp.core.canonical import canonical

from .contracts import TargetCandidate, number, prepare, project
from .weights import allocate


def compute(request):
    x, maps, positions, scores = prepare(request)
    weights, diagnostic = allocate(x, maps, scores)
    equity = number(x["inputs"]["account"]["data"]["equity"])
    ideal, rounded, holding = {}, {}, []
    for sid, weight in weights.items():
        price, lot = (number(maps["prices"][sid][k]) for k in ("price", "lot"))
        q = weight * equity / price
        ideal[sid] = q
        if q == positions[sid]:
            rounded[sid] = q
            holding.append(sid)
        else:
            rounded[sid] = (1 if q >= 0 else -1) * (abs(q) // lot) * lot
    return x, maps, positions, ideal, rounded, diagnostic, holding


def build_candidate(request):
    _, _, _, ideal, rounded, diagnostic, holding = compute(request)
    return TargetCandidate(
        canonical(
            project(
                {
                    "schema_version": "unvalidated-target/1.0.0",
                    "ideal": ideal,
                    "rounded": rounded,
                    "rounding_residual": {sid: ideal[sid] - rounded[sid] for sid in ideal},
                    "selection": diagnostic,
                    "unchanged_holdings": holding,
                    "validated": False,
                }
            )
        ),
        request.content_hash,
    )
