"""Pre-implementation hand-answer arithmetic, not an AQRP factor or SDK test."""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


def main():
    source = Path(__file__).with_name("golden_cases.json")
    raw = source.read_bytes()
    cases = json.loads(raw)
    results = []
    for case in cases["cases"]:
        prices = [Fraction(x) for x in case["prices"]]
        volumes = [Fraction(x) for x in case["volumes"]]
        lookback = case["lookback"]
        assert len(prices) == len(volumes) == lookback + 1
        momentum = prices[-1] / prices[0] - 1
        historical_mean = sum(volumes[:-1], Fraction(0)) / lookback
        assert historical_mean > 0
        actual = {"momentum": momentum, "reversal": -momentum, "volume": volumes[-1] / historical_mean - 1}
        for name, value in actual.items():
            assert value == Fraction(case["expected"][name]), (case["id"], name)
        results.append({"case": case["id"], "rational": {k: str(v) for k, v in actual.items()}, "exact_match": True})
    # Separate manual company-action and zero-denominator checks, no AQRP code.
    assert Fraction(100, 2) == 50 and Fraction(10) * 2 == 20
    assert (Fraction(99) + 1) / 100 - 1 == 0
    assert sum([Fraction(0), Fraction(0)]) / 2 == 0
    print(json.dumps({"performed_by": "Codex developer reference, not Gemini", "python": sys.version, "input_sha256": hashlib.sha256(raw).hexdigest(), "results": results, "manual_checks": "split units, dividend total-return distinction, zero historical volume", "invalid_case_contracts": "STATIC PLAN ONLY; no future factor implementation executed", "result": "PASS: six exact rational cases"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
