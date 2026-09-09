"""Schemas for normalized values, currencies, units, and temporal periods."""
from typing import Optional
from pydantic import BaseModel, Field


class NormalizedValue(BaseModel):
    raw: str = Field(description="Raw original value extracted from text, e.g. '$383.29B', '(₹8,142 Cr)'")
    numeric_value: Optional[float] = Field(default=None, description="Parsed canonical floating point number, e.g. 383290000000.0, -81420000000.0")
    formatted_value: Optional[str] = Field(default=None, description="Human friendly canonical string, e.g. '₹81.42 billion'")
    unit: Optional[str] = Field(default=None, description="Standardized unit, e.g., USD, %, metric_ton, kWh")
    currency: Optional[str] = Field(default=None, description="ISO currency code if applicable, e.g. USD, EUR, INR")
    scale: Optional[str] = Field(default=None, description="Scale multiplier name: crore, lakh, billion, million, thousand, percent, absolute")
    is_estimated: bool = Field(default=False, description="True if value contains approximately/est.")
    is_negative: bool = Field(default=False, description="True if value is negative (e.g. from parentheses or minus sign)")


class NormalizedTimePeriod(BaseModel):
    raw: str = Field(description="Raw temporal string, e.g. 'the fourth quarter ended Dec 2023', 'FY2024'")
    standard_period: str = Field(description="Canonical representation, e.g., '2023-Q4', 'FY2023', '2023-12-31'")
    fiscal_year: Optional[str] = Field(default=None, description="Standardized fiscal year, e.g., 'FY2023', 'FY2024'")
    quarter: Optional[str] = Field(default=None, description="Quarter, e.g., 'Q1', 'Q2', 'Q3', 'Q4'")
    start_date: Optional[str] = Field(default=None, description="ISO-8601 YYYY-MM-DD")
    end_date: Optional[str] = Field(default=None, description="ISO-8601 YYYY-MM-DD")
    period_type: Optional[str] = Field(default=None, description="QUARTER, FISCAL_YEAR, YEAR, MONTH, EXACT_DATE, MULTI_YEAR, UNKNOWN")
