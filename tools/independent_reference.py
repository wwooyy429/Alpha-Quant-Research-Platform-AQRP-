"""Development reference using standard-library arithmetic only, never the AQRP SDK.

This is developer-executed reference evidence, not an additional Gemini audit.
The answers were stated in the pre-reviewed GOLDEN_REFERENCE before implementation.
"""

import json
from decimal import Decimal as D
from fractions import Fraction


def main():
    answers = {
        "return_100_110": str(Fraction(110, 100) - 1),
        "return_100_105": str(Fraction(105, 100) - 1),
        "dividend_return": str((D(98) + D(2)) / D(100) - 1),
        "split_price": str(D(100) / D(2)),
        "split_volume": str(D(10) * D(2)),
        "split_notional": str((D(100) / D(2)) * (D(10) * D(2))),
        "decimal_sum": str(D(".10") + D(".20")),
    }
    assert answers == {
        "return_100_110": "1/10",
        "return_100_105": "1/20",
        "dividend_return": "0",
        "split_price": "50",
        "split_volume": "20",
        "split_notional": "1000",
        "decimal_sum": "0.30",
    }
    print(json.dumps(answers, sort_keys=True))


if __name__ == "__main__":
    main()
