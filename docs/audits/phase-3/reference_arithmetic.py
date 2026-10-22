"""Developer reference of hand-fixed proposals only; no AQRP import or business implementation."""

import hashlib
import json
import platform
import sys
import uuid
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path


def dec(value):
    value = F(value)
    return Decimal(value.numerator) / Decimal(value.denominator)


def ranks(values):
    ordered = sorted(range(len(values)), key=lambda i: values[i])
    result = [None] * len(values)
    begin = 0
    while begin < len(values):
        end = begin + 1
        while end < len(values) and values[ordered[end]] == values[ordered[begin]]:
            end += 1
        rank = F(begin + 1 + end, 2)
        for i in ordered[begin:end]:
            result[i] = rank
        begin = end
    return result


def correlation(x, y):
    x, y = list(map(F, x)), list(map(F, y))
    mx, my = sum(x) / len(x), sum(y) / len(y)
    cross = sum((a - mx) * (b - my) for a, b in zip(x, y))
    xx = sum((a - mx) ** 2 for a in x)
    yy = sum((b - my) ** 2 for b in y)
    return dec(cross) / dec(xx * yy).sqrt()


def linear_quantile(values, p):
    values = sorted(map(F, values))
    position = F(p) * (len(values) - 1)
    low = position.numerator // position.denominator
    return values[low] + (position - low) * (values[min(low + 1, len(values) - 1)] - values[low])


def solve_ols(x, y):
    x, y = [list(map(F, row)) for row in x], list(map(F, y))
    n = len(x[0])
    matrix = [
        [sum(row[i] * row[j] for row in x) for j in range(n)]
        + [sum(row[i] * value for row, value in zip(x, y))]
        for i in range(n)
    ]
    for i in range(n):
        pivot = next(j for j in range(i, n) if matrix[j][i])
        matrix[i], matrix[pivot] = matrix[pivot], matrix[i]
        scale = matrix[i][i]
        matrix[i] = [v / scale for v in matrix[i]]
        for j in range(n):
            if j != i:
                scale = matrix[j][i]
                matrix[j] = [a - scale * b for a, b in zip(matrix[j], matrix[i])]
    beta = [row[-1] for row in matrix]
    return beta, [v - sum(a * b for a, b in zip(row, beta)) for row, v in zip(x, y)]


def corrected(pvalues, method):
    ordered = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    m = len(pvalues)
    result = [F(0)] * m
    if method == "holm":
        running = F(0)
        for k, i in enumerate(ordered):
            running = min(F(1), max(running, (m - k) * pvalues[i]))
            result[i] = running
    else:
        c = sum((F(1, j) for j in range(1, m + 1)), F(0)) if method == "by" else F(1)
        running = F(1)
        for k in range(m - 1, -1, -1):
            i = ordered[k]
            running = min(running, F(m, k + 1) * c * pvalues[i])
            result[i] = running
    return result


def main():
    path = Path(__file__).with_name("golden_cases.json")
    payload = path.read_bytes()
    cases = json.loads(payload)["cases"]
    checked = []
    for case in cases:
        ident, data = case["id"], case["input"]
        if ident.startswith("P3-PV"):
            p, v = list(map(F, data["close"])), list(map(F, data["volume"]))
            result = (p[-1] / p[-2] - 1) * (v[-1] / (sum(v[:-1]) / data["L"]) - 1)
            assert result == F(case["expected"])
        elif ident == "P3-IC":
            result = correlation(data["x"], data["y"])
            assert abs(result - Decimal("0.19") / Decimal("0.0452").sqrt()) < Decimal("1e-50")
            rank_ic = correlation(ranks(data["x"]), ranks(list(map(F, data["y"]))))
            assert abs(rank_ic - dec(case["expected_spearman"])) < Decimal("1e-50")
        elif ident == "P3-TIE":
            assert ranks(data["x"]) == list(map(F, case["expected_ranks"]))
            assert abs(
                correlation(ranks(data["x"]), ranks(data["y"])) - Decimal(3).sqrt() / 2
            ) < Decimal("1e-50")
        elif ident == "P3-Z-ICIR":
            values = list(map(F, data["IC"]))
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
            assert mean == F(case["expected_ic_mean"])
            assert dec(variance).sqrt() == dec(case["expected_ic_sample_std"])
            assert dec(mean) / dec(variance).sqrt() == dec(case["expected_icir"])
            x = list(map(F, data["x"]))
            z = [dec(v) / Decimal("2.5").sqrt() for v in x]
            assert abs(sum(z)) < Decimal("1e-50")
            assert abs(sum(v * v for v in z) / 4 - 1) < Decimal("1e-50")
        elif ident == "P3-ROLL":
            x = list(map(F, data["x"]))
            e = case["expected"]
            assert sum(x) == F(e["sum"]) and sum(x) / len(x) == F(e["mean"])
            assert dec(sum((v - 2) ** 2 for v in x) / 2).sqrt() == dec(e["std_ddof1"])
            assert min(x) == F(e["min"]) and max(x) == F(e["max"])
            assert x[-2] == F(e["delay1"]) and x[-1] - x[-2] == F(e["delta1"])
            assert correlation(x, data["y"]) == dec(e["correlation"])
            assert ranks(data["ts_rank_input"])[-1] / data["L"] == F(e["ts_rank"])
        elif ident == "P3-WINSOR":
            lo, hi = [linear_quantile(data["x"], p) for p in data["quantiles"]]
            assert [min(max(F(v), lo), hi) for v in data["x"]] == list(map(F, case["expected"]))
        elif ident == "P3-MAD":
            median = sorted(map(F, data["x"]))[2]
            mad = sorted(abs(F(v) - median) for v in data["x"])[2]
            assert median == F(case["median"]) and mad == F(case["MAD"])
            assert [
                min(max(F(v), median - data["k"] * mad), median + data["k"] * mad)
                for v in data["x"]
            ] == list(map(F, case["expected"]))
        elif ident == "P3-OLS":
            beta, residual = solve_ols(data["X"], data["y"])
            assert beta == list(map(F, case["expected_beta"])) and residual == list(
                map(F, case["expected_residual"])
            )
            assert all(
                sum(F(row[j]) * e for row, e in zip(data["X"], residual)) == 0 for j in range(3)
            )
        elif ident == "P3-GROUP":
            labels = list(map(F, data["labels"]))
            means = [sum(labels[i : i + 2]) / 2 for i in (0, 2, 4)]
            assert means == list(map(F, case["expected_group_mean"]))
            assert means[-1] - means[0] == F(case["expected_tmb"])
            assert correlation([1, 2, 3], ranks(means)) == dec(case["expected_monotonicity"])
        elif ident == "P3-HAC":
            values = list(map(F, data["IC"]))
            n, q = len(values), data["q"]
            mean = sum(values) / n
            u = [v - mean for v in values]
            gamma = [sum(u[t] * u[t - k] for t in range(k, n)) / n for k in range(q + 1)]
            s = gamma[0] + 2 * sum((1 - F(k, q + 1)) * gamma[k] for k in range(1, q + 1))
            e = case["expected"]
            assert mean == F(e["mean"]) and gamma == [F(e["gamma0"]), F(e["gamma1"])]
            assert s == F(e["S"]) and s / n == F(e["var_mean"])
            assert dec(s / n).sqrt() == dec(e["se"])
        elif ident == "P3-MULTI":
            for method in ("holm", "by", "bh"):
                assert corrected(list(map(F, data["p"])), method) == list(
                    map(F, case["expected_" + method])
                )
        elif ident == "P3-LABEL":
            entry, exit = data["signal_session"] + 1, data["signal_session"] + 1 + data["h"]
            assert entry == case["expected_entry_session"] and exit == case["expected_exit_session"]
            assert F(data["opens"][exit], data["opens"][entry]) - 1 == F(case["expected_return"])
        elif ident == "P3-LABEL-ACTION":
            assert F(
                data["split"] * (data["exit_price"] + data["cash_per_postsplit_share"]),
                data["entry_price"],
            ) - 1 == F(case["expected_return"])
        elif ident == "P3-PURGE":
            a, b, safe = (
                data["train_label_closed"],
                data["heldout_protected_closed"],
                data["safe_train_label_closed"],
            )
            assert (max(a[0], b[0]) <= min(a[1], b[1])) == case["expected_purge"]
            assert (max(safe[0], b[0]) <= min(safe[1], b[1])) == case["expected_safe_overlap"]
            assert (
                list(range(b[1] + 1, b[1] + 1 + data["embargo_sessions"]))
                == case["expected_post_holdout_blocked_sessions"]
            )
        else:
            raise AssertionError("Unverified case: " + ident)
        checked.append(ident)
    print(
        json.dumps(
            {
                "run_id": str(uuid.uuid4()),
                "scope": "Developer stdlib reference arithmetic only; not AQRP implementation or Gemini QA-004 approval",
                "python": sys.version,
                "os": platform.platform(),
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "reference_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "cases_passed": checked,
                "count": len(checked),
                "business_tests": "NOT RUN / P3 Planned",
                "gemini_golden_review": "REVIEW REQUIRED",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    with localcontext() as context:
        context.prec = 64
        main()
