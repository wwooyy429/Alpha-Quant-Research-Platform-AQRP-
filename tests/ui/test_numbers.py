"""Literal audited answers and independent rational oracle for actual UI converters."""

import json
from decimal import Inexact, InvalidOperation, Rounded, localcontext
from fractions import Fraction
from pathlib import Path

import pytest

from aqrp.ui.numbers import ReferenceNumberError, decimal_parts, exact_text, fixed_view, percent

D = Path(__file__).resolve().parents[2] / "docs/audits/phase-6"
ORIGINAL = json.loads((D / "GOLDEN_CANDIDATES.json").read_bytes())["cases"]
SUPPLEMENTAL = json.loads((D / "SUPPLEMENTAL_CANDIDATES.json").read_bytes())["cases"]
NUMERIC = {
    "weight",
    "money",
    "quantity",
    "small",
    "ic_display",
    "percent_display",
    "numeric_rejection",
}


def invoke(kind, x):
    if kind == "weight":
        return percent(x["percent"])
    if kind == "money":
        return fixed_view(x["value"], 2, grouping=True)
    if kind == "ic_display":
        return fixed_view(x["value"], 4)
    if kind == "percent_display":
        return fixed_view(x["value"], 4, multiply=100) + "%"
    coefficient, scale = decimal_parts(x["value"])
    if kind == "quantity" and scale:
        raise ReferenceNumberError("REFERENCE_INTEGER_REQUIRED")
    return exact_text(coefficient, scale)


@pytest.mark.parametrize(
    "case", [c for c in ORIGINAL + SUPPLEMENTAL if c["kind"] in NUMERIC], ids=lambda c: c["id"]
)
def test_audited_literal_numeric_answers(case):
    if case["kind"] == "numeric_rejection":
        with pytest.raises(ReferenceNumberError) as error:
            invoke(case["inputs"]["numeric_kind"], case["inputs"]["fields"])
        assert error.value.code == case["expected"]["error"]
    else:
        assert invoke(case["kind"], case["inputs"]) == case["expected"]


@pytest.mark.parametrize("precision", [1, 2, 7, 28, 80, 160])
@pytest.mark.parametrize(
    "text",
    [
        "0",
        "-0",
        ".5",
        "+.005",
        "-.005",
        "1.005",
        "1.015",
        "-1.025",
        "999.995",
        "-999.995",
        "0.123456789012345678901234567890123456789",
        "999999999999999999999999999999.995",
    ],
)
def test_rational_half_even_and_context_invariance(text, precision):
    # Fraction/round is a separate algorithm; never calculate expected via the converter.
    n = round(Fraction(text) * 100)
    sign = "-" if n < 0 else ""
    digits = str(abs(n)).zfill(3)
    expected = sign + f"{int(digits[:-2]):,}." + digits[-2:]
    with localcontext() as context:
        context.prec = precision
        for trap in [Inexact, Rounded, InvalidOperation]:
            context.traps[trap] = True
        assert fixed_view(text, 2, grouping=True) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "1.",
        "1..2",
        "--1",
        "+",
        ".",
        "NaN",
        "Infinity",
        "1e3",
        "０.５",
        "1_000",
        None,
        False,
        1,
        {},
        "9" * 4097,
        "+" + "9" * 4097,
    ],
)
def test_explicit_rejection_and_original_value_is_not_mutated(text):
    before = text
    with pytest.raises(ReferenceNumberError):
        decimal_parts(text)
    assert text == before


def test_exact_percentage_and_boundary_no_global_limit_change():
    import sys

    before = sys.get_int_max_str_digits()
    assert percent("-12.50") == "-0.125"
    assert percent("9" * 4096) == "9" * 4094 + ".99"
    assert exact_text(-1250, 2, trim=False) == "-12.50"
    assert sys.get_int_max_str_digits() == before
