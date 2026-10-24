"""Stdlib-only P7 oracle/byte reader; never imports the implementation under test."""

import json
import math
from fractions import Fraction
from pathlib import Path
from statistics import mean, stdev

from ui_reference import actor, canonical, compare, sha, verify_run


def known_answer(research_root, research_id, backtest_root, backtest_id, factor, protocol, oracles):
    """Check frozen G1 answers first; parity alone cannot validate wrong actors."""
    projection = actor(research_root, research_id, backtest_root, backtest_id)
    r = Path(research_root) / research_id
    b = Path(backtest_root) / backtest_id
    result = json.loads((b / "result.json").read_bytes())
    checks = 0

    def equal(actual, expected):
        nonlocal checks
        assert actual == expected, (actual, expected)
        checks += 1

    def close(actual, expected):
        nonlocal checks
        assert math.isclose(float(actual), float(expected), abs_tol=1e-12, rel_tol=1e-10), (
            actual,
            expected,
        )
        checks += 1

    equal(result["financial_approval"], "NONE")
    equal(result["scope"], "ENGINEERING_TEST_ONLY")
    equal(result["executable"], False)
    if protocol == "main":
        oracle = json.loads((Path(oracles) / "MAIN_PIPELINE_CANDIDATES.json").read_bytes())
        financial = json.loads(
            (Path(oracles) / "FINANCIAL_FEASIBILITY_CANDIDATES.json").read_bytes()
        )
        summary = next(s for s in financial["summaries"] if s["name"] == factor)
        equal(len(projection["mapping_proofs"]), 10)
        previous = None
        for portfolio, selected in zip(
            projection["financial"]["portfolios"], summary["selected_sequence"], strict=True
        ):
            equal(portfolio["status"], "SUCCEEDED")
            equal(portfolio["risk"]["passed"], True)
            equal(portfolio["selection"]["ranked"][0], selected)
            expected_quantities = {
                f"SYN_A:{i:03d}": "4" if f"SYN_A:{i:03d}" == selected else "0" for i in range(1, 7)
            }
            equal(portfolio["target"]["quantities"], expected_quantities)
            expected_deltas = {
                sid: str((4 if sid == selected else 0) - (4 if sid == previous else 0))
                for sid in expected_quantities
            }
            equal(portfolio["target"]["deltas"], expected_deltas)
            previous = selected
        for key, expected in summary["final"].items():
            equal(Fraction(result["account"][key]), Fraction(expected))
        equal(len(result["fills"]), 15)
        equal(sum((Fraction(f["fee"]) for f in result["fills"]), Fraction()), Fraction(15))
        equal(sum((Fraction(f["slippage_cost"]) for f in result["fills"]), Fraction()), Fraction(6))
        equal(
            {s: p["quantity"] for s, p in result["positions"].items()}, summary["final_positions"]
        )
        for fill in result["fills"]:
            equal(abs(Fraction(fill["signed_qty"])), Fraction(4))
            equal(fill["direction"], "LONG")
        daily = projection["research_metrics"]["daily"]
        labels = json.loads((r / "labels.json").read_bytes())
        equal(len(labels), 114)
        for section in oracle["sections"]:
            rows = sorted(
                [x for x in labels if x["session"] == section["session"] and x["horizon"] == 1],
                key=lambda x: x["security_id"],
            )
            equal([x["security_id"] for x in rows], oracle["inputs"]["assets"])
            for row, expected in zip(rows, section["raw_next_open_label"], strict=True):
                equal(row["reason"], "NONE")
                close(row["label"], Fraction(expected))
        for stage in ("raw", "clean", "standardized", "neutralized", "final"):
            rows = json.loads((r / (stage + ".json")).read_bytes())["rows"]
            equal(sorted({x["session"] for x in rows}), [s["session"] for s in oracle["sections"]])
            for section in oracle["sections"]:
                values = sorted(
                    [
                        x
                        for x in rows
                        if x["session"] == section["session"] and x["factor_key"] == factor
                    ],
                    key=lambda x: x["security_id"],
                )
                equal(len(values), 6)
                if stage == "raw":
                    expected = [
                        Fraction(x) * (1 if factor == "momentum" else -1)
                        for x in section["raw_momentum"]
                    ]
                elif stage in ("clean", "standardized"):
                    expected = [
                        float(x) * (1 if factor == "momentum" else -1)
                        for x in section["momentum_" + stage]
                    ]
                else:
                    expected = section[factor + "_final"]
                for actual, answer in zip(values, expected, strict=True):
                    equal(actual["validity"], "VALID")
                    close(actual["score"], answer)
                if stage == "final":
                    stats = next(
                        x
                        for x in daily
                        if x["factor_key"] == factor
                        and x["stage"] == "final"
                        and x["session"] == section["session"]
                        and x["horizon"] == 1
                    )
                    answer = section["statistics"][factor]
                    close(stats["ic"]["value"], answer["pearson_ic"])
                    close(stats["rank_ic"]["value"], answer["spearman_rank_ic"])
                    equal(stats["groups"]["counts"], answer["group_counts"])
                    for actual, expected in zip(
                        stats["groups"]["means"], answer["group_mean_returns"], strict=True
                    ):
                        close(actual, expected)
                    close(stats["groups"]["tmb"], answer["top_minus_bottom"])
        all_final = sorted(
            [
                x
                for x in daily
                if x["factor_key"] == factor and x["stage"] == "final" and x["horizon"] == 1
            ],
            key=lambda x: x["session"],
        )
        for source_key, oracle_key in (("ic", "pearson"), ("rank_ic", "spearman")):
            # The product has per-split summaries. The frozen G1 whole19 summary
            # is checked through an independent stdlib reduction of its actual
            # daily observations, never represented as a missing product field.
            values = [x[source_key]["value"] for x in all_final]
            summary = oracle["IC_summaries"][factor][oracle_key]
            equal(len(values), summary["n"])
            close(mean(values), summary["mean"])
            close(stdev(values), summary["sample_std_ddof1"])
            close(mean(values) / stdev(values), summary["unannualized_icir"])
            close(sum(x > 0 for x in values) / len(values), summary["positive_fraction"])
            for split in ("train", "validation", "test"):

                def partition(session):
                    return (
                        "train"
                        if session < "2024-01-10"
                        else "validation"
                        if session < "2024-01-18"
                        else "test"
                    )

                expected = [
                    float(
                        s["statistics"][factor][
                            "pearson_ic" if oracle_key == "pearson" else "spearman_rank_ic"
                        ]
                    )
                    for s in oracle["sections"]
                    if partition(s["session"]) == split
                ]
                actual = next(
                    s[source_key]
                    for s in projection["research_metrics"]["summaries"]
                    if s["factor_key"] == factor
                    and s["stage"] == "final"
                    and s["horizon"] == 1
                    and s["split"] == split
                )
                equal(actual["n"], len(expected))
                equal(actual["annualized"], False)
                close(actual["mean"], mean(expected))
                close(actual["std_ddof1"], stdev(expected))
                close(actual["icir"], mean(expected) / stdev(expected))
                close(actual["positive_fraction"], sum(x > 0 for x in expected) / len(expected))
                equal(
                    [x["session"] for x in all_final if x["split"] == split],
                    [s["session"] for s in oracle["sections"] if partition(s["session"]) == split],
                )
    else:
        equal(protocol, "transparent")
        equal(result["account"]["cash_total"], "98.1")
        equal(result["account"]["equity"], "998.1")
        # No sale, short, dividend or open order in this independently declared
        # one-buy case: all cash is settled, with zero unsettled/restricted buckets.
        equal(result["account"]["cash_set"], "98.1")
        for key in ("U_free", "U_short", "S_set", "O_N", "O_F", "P_res", "Z"):
            equal(result["account"][key], "0")
        equal(len(result["fills"]), 1)
        fill = result["fills"][0]
        equal(fill["signed_qty"], "9")
        equal(fill["fee"], "1")
        equal(fill["price"], "100.1")
        equal(fill["security_id"], "SYN_A:002" if factor == "momentum" else "SYN_A:001")
        golden = json.loads((Path(oracles) / "GOLDEN_CANDIDATES.json").read_bytes())
        answer = next(
            c["expected"]
            for c in golden["cases"]
            if c["id"] == ("P7-G02" if factor == "momentum" else "P7-G03")
        )
        rows = sorted(
            json.loads((r / "raw.json").read_bytes())["rows"], key=lambda x: x["security_id"]
        )
        equal(len(rows), 6)
        for row, value in zip(rows, answer, strict=True):
            close(row["score"], Fraction(value))
    return {
        "checks": checks,
        "projection": projection,
        "scope": "Developer actual execution against unchanged G1 independent-formula answers; not independent G2",
    }


def compare_checked(a, b):
    result = compare(a, b)
    assert result["research_equal"] and result["financial_exact_equal"], result
    return result


def file_manifest(root):
    root = Path(root).resolve()
    result = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction()):
            raise AssertionError("Linked evidence member: " + str(p))
        if p.is_file():
            raw = p.read_bytes()
            result.append(
                {"path": p.relative_to(root).as_posix(), "bytes": len(raw), "sha256": sha(raw)}
            )
    return result


__all__ = ["known_answer", "compare_checked", "file_manifest", "verify_run", "canonical", "sha"]
