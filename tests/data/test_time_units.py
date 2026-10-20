from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal
from fractions import Fraction

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from aqrp.core.canonical import canonical, default
from aqrp.core.errors import ContractError, TimestampResolutionError, UnsupportedCurrency
from aqrp.core.math import simple_price_return
from aqrp.core.time import iana, localize, utc
from aqrp.core.units import MarketProfile, convert, decimal


@pytest.mark.parametrize(
    "bad", ["2024-01-02", "badTtime", datetime(2024, 1, 2), date(2024, 1, 2), None, 3]
)
def test_data_002_time_rejection(bad):
    with pytest.raises(ContractError):
        utc(bad)


@pytest.mark.parametrize(
    "bad", ["2024-01-02T16:00:00.000000001Z", pd.Timestamp("2024-01-02T16:00:00.123456789Z")]
)
def test_data_002_nanoseconds(bad):
    with pytest.raises(TimestampResolutionError):
        utc(bad)


def test_data_003_dst_and_local_date():
    assert utc("2024-03-08T09:30:00-05:00", "America/New_York") == datetime(
        2024, 3, 8, 14, 30, tzinfo=UTC
    )
    assert utc("2024-03-11T09:30:00-04:00", "America/New_York") == datetime(
        2024, 3, 11, 13, 30, tzinfo=UTC
    )
    assert utc("2024-04-02T00:30:00+08:00", "Asia/Shanghai") == datetime(
        2024, 4, 1, 16, 30, tzinfo=UTC
    )
    assert utc("2024-01-02T16:00:00.123456000Z").microsecond == 123456
    assert localize(datetime(2024, 3, 11, 9, 30), "America/New_York") == datetime(
        2024, 3, 11, 13, 30, tzinfo=UTC
    )
    with pytest.raises(ContractError, match="AMBIGUOUS"):
        localize(datetime(2024, 11, 3, 1, 30), "America/New_York")
    assert localize(datetime(2024, 11, 3, 1, 30), "America/New_York", fold=0).hour == 5
    assert localize(datetime(2024, 11, 3, 1, 30), "America/New_York", fold=1).hour == 6
    with pytest.raises(ContractError, match="NONEXISTENT"):
        localize(datetime(2024, 3, 10, 2, 30), "America/New_York")
    for bad in (None, "../UTC", "Bad/Zone", "", 123):
        with pytest.raises(ContractError):
            iana(bad)
    with pytest.raises(ContractError, match="OFFSET"):
        utc("2024-07-01T09:30:00-05:00", "America/New_York")
    with pytest.raises(ContractError):
        localize(datetime(2024, 1, 1, tzinfo=UTC), "UTC")
    with pytest.raises(ContractError):
        localize("date", "UTC")
    with pytest.raises(ContractError):
        localize(datetime(2024, 1, 1), "UTC", fold=2)


def test_data_011_known_answers():
    assert decimal("0.10") + decimal("0.20") == Decimal("0.30")
    assert convert("3", "lot", lot_size="100") == Decimal("300")
    assert convert("1.25", "thousand_currency") == Decimal("1250")
    assert convert("0", "share") == Decimal(0)
    assert convert("1", "currency") == Decimal(1)
    with pytest.raises(UnsupportedCurrency):
        convert("1", "currency", currency="USD")
    with pytest.raises(ContractError):
        convert("1", "share", profile=MarketProfile(profile_id="UNKNOWN"))
    for unit, value, lot in [
        ("lot", "1", "0"),
        ("lot", "1", "1.5"),
        ("unknown", "1", None),
        ("share", "-1", None),
        ("share", "0.5", None),
    ]:
        with pytest.raises(ContractError):
            convert(value, unit, lot_size=lot)


@pytest.mark.parametrize(
    "bad", [0.1, True, None, [], "abc", "NaN", "Infinity", "1e20", "0.000000001"]
)
def test_data_011_decimal_boundaries(bad):
    with pytest.raises(ContractError):
        decimal(bad)


@given(st.integers(0, 10**12))
def test_data_011_units_property(shares):
    assert convert(str(shares), "lot", lot_size=100) == Decimal(shares * 100)


@given(st.integers(1, 10**9), st.integers(1, 10**9))
def test_qa_002_rational_reference(previous, current):
    expected = float(Fraction(current, previous) - 1)
    assert simple_price_return(str(previous), str(current)).value == pytest.approx(
        expected, abs=1e-12, rel=1e-10
    )


def test_qa_002_golden_return_and_serialization():
    assert simple_price_return("100", "110").value == pytest.approx(0.10, abs=1e-12, rel=1e-10)
    assert simple_price_return("100", "105").value == pytest.approx(0.05, abs=1e-12, rel=1e-10)
    assert simple_price_return(None, "100").validity == "MISSING"
    assert simple_price_return("100", None).value is None
    for previous, current in [("0", "100"), ("-1", "100"), ("100", "0")]:
        with pytest.raises(ContractError):
            simple_price_return(previous, current)
    assert (
        canonical({"b": Decimal(".30"), "a": date(2024, 1, 2)}) == b'{"a":"2024-01-02","b":"0.30"}'
    )
    assert b"+00:00" in canonical(datetime(2024, 1, 2, tzinfo=UTC))
    with pytest.raises(TypeError):
        default(object())
    with pytest.raises(ValueError):
        canonical(float("nan"))


@given(st.integers(-1000000, 1000000))
def test_data_002_exact_microsecond_order(delta):
    base = datetime(2024, 1, 2, 16, 5, tzinfo=UTC)
    t = base + timedelta(microseconds=delta)
    assert (utc(t) <= base) == (delta <= 0)
    assert utc(t.astimezone(timezone(timedelta(hours=8)))) == t
