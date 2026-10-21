"""
AQRP Phase 2 Plan Pre-Review Mathematical Verification Script
Original Reference: docs/audits/phase-2/gemini/aqrp_phase2_plan_pre_review_report.md Section 7
Reviewer: Gemini (Independent Quantitative Research Auditor)
Environment: Linux x86_64 Sandbox, Python 3.11 Standard Library
"""

import sys
from decimal import Decimal
from fractions import Fraction

def log(msg):
    print(f"[MATH_VERIFY] {msg}")

def main():
    log("=== AQRP Phase 2 Independent Mathematical Verification ===")
    
    # 1. Momentum Benchmark: p_prev = 100, p_curr = 121 -> ret = 21/100 = 0.21
    p_prev = Fraction(100, 1)
    p_curr = Fraction(121, 1)
    ret_mom_exact = (p_curr - p_prev) / p_prev
    ret_mom_float = float(ret_mom_exact)
    expected_mom = 0.21
    diff_mom = abs(ret_mom_float - expected_mom)
    log(f"1. Momentum Benchmark: exact={ret_mom_exact}, float={ret_mom_float:.18f}, expected={expected_mom}")
    log(f"   abs_diff={diff_mom:.2e}, rel_diff=0.00e+00 -> PASS (bit aligned)")
    assert diff_mom < 1e-12

    # 2. Reversal Benchmark: Single negative sign of Momentum -> -21/100 = -0.21
    ret_rev_exact = -ret_mom_exact
    ret_rev_float = float(ret_rev_exact)
    expected_rev = -0.21
    diff_rev = abs(ret_rev_float - expected_rev)
    log(f"2. Reversal Benchmark: exact={ret_rev_exact}, float={ret_rev_float:.18f}, expected={expected_rev}")
    log(f"   abs_diff={diff_rev:.2e}, rel_diff=0.00e+00 -> PASS (bit aligned)")
    assert diff_rev < 1e-12

    # 3. Cross-sectional Quantile / Volume Ratio Benchmark: 3/5 = 0.60
    # In Phase 2: Historical volume average excludes current bar; ratio = 1800 / 3000 = 3/5 = 0.60
    hist_volumes = [1000, 2000, 3000, 4000, 5000]
    curr_volume = 1800
    hist_avg = Fraction(sum(hist_volumes), len(hist_volumes))
    vol_ratio_exact = Fraction(curr_volume, 1) / hist_avg
    vol_ratio_float = float(vol_ratio_exact)
    expected_ratio = 0.60
    diff_ratio = abs(vol_ratio_float - expected_ratio)
    log(f"3. Volume Ratio Benchmark: hist_avg={hist_avg}, curr={curr_volume}, ratio_exact={vol_ratio_exact}")
    log(f"   float={vol_ratio_float:.18f}, expected={expected_ratio}, abs_diff={diff_ratio:.2e} -> PASS (3/5 volume ratio, not portfolio weight)")
    assert diff_ratio < 1e-12
    assert vol_ratio_exact == Fraction(3, 5)

    # 4. Security B Multi-period Return Series: (-1/5, 1/5, 0)
    rets_exact = [Fraction(-1, 5), Fraction(1, 5), Fraction(0, 1)]
    rets_float = [float(r) for r in rets_exact]
    expected_rets = [-0.20, 0.20, 0.00]
    for r_f, exp_r in zip(rets_float, expected_rets):
        assert abs(r_f - exp_r) < 1e-12
    log(f"4. Security B Multi-period Returns: float={rets_float}, expected={expected_rets} -> PASS")

    # 5. Split-adjusted Return (2:1 split, price 100 -> 50)
    p_pre_split = Decimal('100.00')
    p_post_split = Decimal('50.00')
    split_ratio = Decimal('2.0')
    p_adj_prev = p_pre_split / split_ratio
    ret_split = float((p_post_split - p_adj_prev) / p_adj_prev)
    log(f"5. Split-adjusted Return: p_adj_prev={p_adj_prev}, p_curr={p_post_split}, ret={ret_split:.6f} -> PASS (exact 0.0)")
    assert abs(ret_split) < 1e-12

    # 6. Dividend Adjustment Return
    # Close 100, Cash div 1.00, Ex-dividend price 99
    p_close = Decimal('100.00')
    p_ex = Decimal('99.00')
    cash_div = Decimal('1.00')
    pure_price_ret = float((p_ex - p_close) / p_close)
    total_ret = float((p_ex + cash_div - p_close) / p_close)
    log(f"6. Dividend Pure Price Return: {pure_price_ret:.6f} (expected -0.01), Total Return: {total_ret:.6f} (expected 0.0) -> PASS")
    assert abs(pure_price_ret - (-0.01)) < 1e-12
    assert abs(total_ret - 0.0) < 1e-12

    log("=== ALL 6 GOLDEN BENCHMARKS VERIFIED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()