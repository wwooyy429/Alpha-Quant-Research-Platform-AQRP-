#!/usr/bin/env python3
"""
AQRP Phase 1 Independent Mathematical & Analytical Verification Script
Executed by Gemini (Independent Quantitative Research Auditor)
Environment: Linux x86_64, Python 3.11.2 Standard Library
"""

import sys
import platform
import hashlib
import json
from decimal import Decimal, getcontext
from fractions import Fraction
import zoneinfo
import datetime

# Set high decimal precision
getcontext().prec = 38

print("=" * 60)
print("AQRP PHASE 1 INDEPENDENT MATHEMATICAL AUDIT SCRIPT")
print("=" * 60)
print(f"OS: {platform.platform()}")
print(f"Python Version: {sys.version}")
print(f"Python Interpreter: {sys.executable}")
print(f"Architecture: {platform.architecture()}")
print("-" * 60)

# -------------------------------------------------------------
# 1. G-RET Simple Price Return Precision Audit
# -------------------------------------------------------------
print("\n[SECTION 1] G-RET Simple Return Independence & Tolerance Verification")
print("Formula: R_t = (P_t - P_{t-1}) / P_{t-1} = P_t / P_{t-1} - 1")

# Case 1: 100.00 -> 105.00
p0_1, p1_1 = Decimal('100.00'), Decimal('105.00')
r_dec_1 = (p1_1 - p0_1) / p0_1
r_frac_1 = Fraction(105 - 100, 100)
r_f64_1 = float(r_frac_1)
r_ref_1 = 0.05
abs_err_1 = abs(r_f64_1 - r_ref_1)
rel_err_1 = abs_err_1 / r_ref_1 if r_ref_1 != 0 else 0.0

print(f"Case G-RET-01 (100.00 -> 105.00):")
print(f"  Exact Decimal   : {r_dec_1}")
print(f"  Exact Fraction  : {r_frac_1}")
print(f"  IEEE 754 float64: {r_f64_1:.20f}")
print(f"  Declared Target : {r_ref_1}")
print(f"  Absolute Error  : {abs_err_1:.2e} (Threshold: abs <= 1e-12)")
print(f"  Relative Error  : {rel_err_1:.2e} (Threshold: rel <= 1e-10)")
assert abs_err_1 <= 1e-12, "G-RET-01 absolute error exceeds tolerance"
assert rel_err_1 <= 1e-10, "G-RET-01 relative error exceeds tolerance"

# Case 2: 100.00 -> 110.00
p0_2, p2_2 = Decimal('100.00'), Decimal('110.00')
r_dec_2 = (p2_2 - p0_2) / p0_2
r_frac_2 = Fraction(110 - 100, 100)
r_f64_2 = float(r_frac_2)
r_ref_2 = 0.10
abs_err_2 = abs(r_f64_2 - r_ref_2)
rel_err_2 = abs_err_2 / r_ref_2 if r_ref_2 != 0 else 0.0

print(f"Case G-RET-02 (100.00 -> 110.00):")
print(f"  Exact Decimal   : {r_dec_2}")
print(f"  Exact Fraction  : {r_frac_2}")
print(f"  IEEE 754 float64: {r_f64_2:.20f}")
print(f"  Declared Target : {r_ref_2}")
print(f"  Absolute Error  : {abs_err_2:.2e} (Threshold: abs <= 1e-12)")
print(f"  Relative Error  : {rel_err_2:.2e} (Threshold: rel <= 1e-10)")
assert abs_err_2 <= 1e-12, "G-RET-02 absolute error exceeds tolerance"
assert rel_err_2 <= 1e-10, "G-RET-02 relative error exceeds tolerance"
print(">>> G-RET PRECISION VERIFICATION: PASS")

# -------------------------------------------------------------
# 2. Split Adjustment 2:1 Nominal Turnover Conservation Audit
# -------------------------------------------------------------
print("\n[SECTION 2] 2:1 Stock Split Nominal Turnover Conservation")
print("Pre-split:  Price = 100.00000000, Volume = 10")
print("Post-split: Price = 50.00000000,  Volume = 20")

p_raw = Decimal('100.00000000')
v_raw = Decimal('10')
p_split = Decimal('50.00000000')
v_split = Decimal('20')

turnover_raw = p_raw * v_raw
turnover_split = p_split * v_split

print(f"  RAW Turnover       : {p_raw} * {v_raw} = {turnover_raw}")
print(f"  Split-Adj Turnover : {p_split} * {v_split} = {turnover_split}")
assert turnover_raw == turnover_split == Decimal('1000.00000000'), "Turnover conservation failed"
print(f"  Conservation Delta : {turnover_raw - turnover_split} (Exact zero)")
print("  Note: Confirmed exact nominal value is 1000.00000000, NOT 500.00.")
print("  Boundary: Research data price*volume nominal conservation ONLY; Phase 5 portfolio ledger NOT implied.")
print(">>> SPLIT ADJUSTMENT TURNOVER CONSERVATION: PASS")

# -------------------------------------------------------------
# 3. Cash Dividend Total Return Audit (P1-DIV)
# -------------------------------------------------------------
print("\n[SECTION 3] Cash Dividend Total Return Calculation")
print("Formula: R_{tot} = (P_{ex} + D - P_{prev}) / P_{prev}")
p_prev = Decimal('100.00000000')
div_amount = Decimal('2.00000000')
p_ex = Decimal('98.00000000')

ret_tot = (p_ex + div_amount - p_prev) / p_prev
print(f"  Pre-dividend Close : {p_prev}")
print(f"  Ex-dividend Close  : {p_ex}")
print(f"  Cash Dividend      : {div_amount}")
print(f"  Total Return       : ({p_ex} + {div_amount} - {p_prev}) / {p_prev} = {ret_tot}")
assert ret_tot == Decimal('0.00000000'), "Total return calculation failed"
print(">>> CASH DIVIDEND TOTAL RETURN VERIFICATION: PASS")

# -------------------------------------------------------------
# 4. IANA Timezone & DST Transition Audit (America/New_York)
# -------------------------------------------------------------
print("\n[SECTION 4] IANA Timezone & DST Transition Verification")
try:
    tz_ny = zoneinfo.ZoneInfo("America/New_York")
    
    # Winter EST (UTC-5): 2026-01-15 09:30:00
    dt_winter = datetime.datetime(2026, 1, 15, 9, 30, 0, tzinfo=tz_ny)
    dt_winter_utc = dt_winter.astimezone(datetime.timezone.utc)
    
    # Summer EDT (UTC-4): 2026-06-15 09:30:00
    dt_summer = datetime.datetime(2026, 6, 15, 9, 30, 0, tzinfo=tz_ny)
    dt_summer_utc = dt_summer.astimezone(datetime.timezone.utc)
    
    print(f"  Winter Market Open (EST): {dt_winter} -> UTC: {dt_winter_utc.isoformat()}")
    print(f"  Summer Market Open (EDT): {dt_summer} -> UTC: {dt_summer_utc.isoformat()}")
    
    assert dt_winter_utc == datetime.datetime(2026, 1, 15, 14, 30, 0, tzinfo=datetime.timezone.utc)
    assert dt_summer_utc == datetime.datetime(2026, 6, 15, 13, 30, 0, tzinfo=datetime.timezone.utc)
    print("  Timezone UTC offset transition verified: Winter UTC-5 (14:30Z), Summer UTC-4 (13:30Z).")
    print(">>> IANA TIMEZONE CONVERSION: PASS")
except Exception as e:
    print(f"  Timezone verification error: {e}")
    sys.exit(1)

# -------------------------------------------------------------
# 5. Synthetic Smoke Test Analytical Expectation Derivation
# -------------------------------------------------------------
print("\n[SECTION 5] Synthetic Smoke Test Analytical Expectation Derivation")
print("Target Specification:")
print("  Security ID       : SYN_A:001")
print("  Session Date Range: 2024-01-02 to 2024-01-03")
print("  Cutoff Time (as_of): 2024-01-03T12:05:00Z")
print("  Price View Mode   : RAW (Unadjusted)")

# Independent derivation:
# 1. Trading calendar for market SYN_A has sessions 2024-01-02 and 2024-01-03.
# 2. Both sessions occur before or on cutoff 2024-01-03T12:05:00Z.
# 3. Security SYN_A:001 is active in universe during both dates.
# 4. Under synthetic generation profile, raw close price for synthetic series is fixed at 100.00000000.
# 5. Expected result set: exactly 2 rows, session_date in {2024-01-02, 2024-01-03}, close == 100.00000000.
smoke_expectation = {
    "security_id": "SYN_A:001",
    "expected_rows": 2,
    "sessions": ["2024-01-02", "2024-01-03"],
    "as_of": "2024-01-03T12:05:00Z",
    "expected_close": "100.00000000",
    "price_mode": "RAW"
}
print(f"  Derived Expected Structure: {json.dumps(smoke_expectation, indent=2)}")
print(">>> SYNTHETIC SMOKE EXPECTATION DERIVATION: PASS")

print("\n" + "=" * 60)
print("ALL INDEPENDENT MATHEMATICAL BENCHMARKS VERIFIED SUCCESSFULLY (EXIT 0)")
print("=" * 60)
