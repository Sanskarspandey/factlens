"""Unit tests for value, currency, unit, and date normalization (Phase 1 & Phase 2)."""
import pytest
from app.services.normalization_service import NormalizationService


@pytest.fixture
def normalizer():
    return NormalizationService()


def test_normalize_inr_crores_and_lakhs(normalizer):
    # ₹8,142 Cr
    val1 = normalizer.normalize_value("₹8,142 Cr")
    assert val1.raw == "₹8,142 Cr"  # Raw value preserved
    assert val1.numeric_value == 81420000000.0
    assert val1.currency == "INR"
    assert val1.scale == "crore"
    assert "81.42 billion" in val1.formatted_value or "8,142" in val1.formatted_value

    # Variations: 8142 crore and ₹8,142 crore should resolve to same numerical representation
    val1_b = normalizer.normalize_value("8142 crore")
    assert val1_b.numeric_value == 81420000000.0
    assert val1_b.scale == "crore"

    val1_c = normalizer.normalize_value("₹8,142 crore")
    assert val1_c.numeric_value == 81420000000.0
    assert val1_c.currency == "INR"

    # ₹25 Lakh
    val2 = normalizer.normalize_value("₹25 Lakh")
    assert val2.raw == "₹25 Lakh"
    assert val2.numeric_value == 2500000.0
    assert val2.currency == "INR"
    assert val2.scale == "lakh"

    # Rs. 500 crs
    val3 = normalizer.normalize_value("Rs. 500 crs")
    assert val3.numeric_value == 5000000000.0
    assert val3.currency == "INR"


def test_normalize_usd_and_scales(normalizer):
    # $383.29 billion
    val1 = normalizer.normalize_value("$383.29 billion")
    assert val1.raw == "$383.29 billion"
    assert val1.numeric_value == 383290000000.0
    assert val1.currency == "USD"
    assert val1.scale == "billion"
    assert "$383.29 billion" in val1.formatted_value

    # $50 million
    val2 = normalizer.normalize_value("$50 million")
    assert val2.numeric_value == 50000000.0
    assert val2.currency == "USD"
    assert val2.scale == "million"

    # $120 thousand
    val3 = normalizer.normalize_value("$120 thousand")
    assert val3.numeric_value == 120000.0
    assert val3.currency == "USD"

    # 1.4 million and 1,400,000 resolve to consistent numerical value
    val4 = normalizer.normalize_value("1.4 million")
    val5 = normalizer.normalize_value("1,400,000")
    assert val4.numeric_value == 1400000.0
    assert val5.numeric_value == 1400000.0


def test_normalize_negative_parentheses_and_percentages(normalizer):
    # (₹8,142 Cr) -> negative
    neg1 = normalizer.normalize_value("(₹8,142 Cr)")
    assert neg1.is_negative is True
    assert neg1.numeric_value == -81420000000.0
    assert neg1.currency == "INR"

    # ($50M) -> negative
    neg2 = normalizer.normalize_value("($50M)")
    assert neg2.is_negative is True
    assert neg2.numeric_value == -50000000.0
    assert neg2.currency == "USD"

    # (500) -> negative
    neg3 = normalizer.normalize_value("(500)")
    assert neg3.is_negative is True
    assert neg3.numeric_value == -500.0

    # 15.4%
    val1 = normalizer.normalize_value("15.4%")
    assert val1.numeric_value == 15.4
    assert val1.unit == "%"
    assert val1.currency is None

    # -2.5%
    val2 = normalizer.normalize_value("-2.5%")
    assert val2.numeric_value == -2.5
    assert val2.is_negative is True
    assert val2.unit == "%"


def test_currency_distinction_no_implicit_conversion(normalizer):
    # ₹100 and $100 must NOT be treated as equal numeric currencies
    inr_val = normalizer.normalize_value("₹100")
    usd_val = normalizer.normalize_value("$100")
    assert inr_val.currency == "INR"
    assert usd_val.currency == "USD"
    assert inr_val.currency != usd_val.currency


def test_normalize_fiscal_years_and_quarters(normalizer):
    # FY2023
    p1 = normalizer.normalize_time_period("FY2023")
    assert p1.standard_period == "FY2023"
    assert p1.fiscal_year == "FY2023"
    assert p1.period_type == "FISCAL_YEAR"

    # FY24
    p2 = normalizer.normalize_time_period("FY24")
    assert p2.standard_period == "FY2024"
    assert p2.fiscal_year == "FY2024"
    assert p2.period_type == "FISCAL_YEAR"

    # FY2025 / FY25
    p3 = normalizer.normalize_time_period("FY2025")
    assert p3.standard_period == "FY2025"
    assert p3.fiscal_year == "FY2025"

    p4 = normalizer.normalize_time_period("FY25")
    assert p4.standard_period == "FY2025"
    assert p4.fiscal_year == "FY2025"

    # Q4 2023
    q1 = normalizer.normalize_time_period("Q4 2023")
    assert q1.standard_period == "2023-Q4"
    assert q1.quarter == "Q4"
    assert q1.period_type == "QUARTER"

    # Q1 FY23
    q2 = normalizer.normalize_time_period("Q1 FY23")
    assert q2.standard_period == "2023-Q1"
    assert q2.quarter == "Q1"
    assert q2.period_type == "QUARTER"

    # Exact date December 31, 2023
    d1 = normalizer.normalize_time_period("December 31, 2023")
    assert d1.standard_period == "2023-12-31"
    assert d1.period_type == "EXACT_DATE"
