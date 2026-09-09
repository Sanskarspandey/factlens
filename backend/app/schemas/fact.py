"""Fact extraction, grounding, and serialization schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.fact import FactStatus, ValueStatus
from app.schemas.normalization import NormalizedValue, NormalizedTimePeriod


class ExtractedFactItem(BaseModel):
    """Raw structured output item produced by the LLM extraction pipeline."""
    statement: str = Field(description="Clear natural language claim or fact statement")
    entity: Optional[str] = Field(default=None, description="Primary subject or entity the fact is about (e.g. 'Delhivery', 'Acme Corp')")
    attribute: Optional[str] = Field(default=None, description="Metric or property being stated (e.g. 'Revenue from operations')")
    raw_value: Optional[str] = Field(default=None, description="Exact value text as stated in the PDF")
    evidence_quote: str = Field(description="Verbatim exact quote from the page text supporting this fact")
    time_period_raw: Optional[str] = Field(default=None, description="Time period as mentioned in text (e.g. 'FY2024')")
    fiscal_year: Optional[str] = Field(default=None, description="Fiscal year e.g. 'FY2024'")
    quarter: Optional[str] = Field(default=None, description="Quarter e.g. 'Q1', 'Q4'")
    geography: Optional[str] = Field(default=None, description="Geographic scope e.g. 'India', 'Global'")
    scope: Optional[str] = Field(default=None, description="Reporting scope e.g. 'Consolidated', 'Standalone'")
    definition: Optional[str] = Field(default=None, description="Definition or accounting baseline e.g. 'GAAP', 'Adjusted'")
    source_section: Optional[str] = Field(default=None, description="Section of PDF where fact was extracted")
    value_status: ValueStatus = Field(default=ValueStatus.ACTUAL, description="ACTUAL, ESTIMATE, FORECAST, GUIDANCE, TARGET, UNKNOWN")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in the extraction accuracy")
    is_uncertain: bool = Field(default=False, description="Whether the fact has ambiguous wording or uncertain figures")
    uncertainty_notes: Optional[str] = Field(default=None, description="Notes on what makes this extraction uncertain or ambiguous")
    bounding_box: Optional[List[float]] = Field(default=None, description="Coordinates [x0, y0, x1, y1] on the page")


class PageExtractionResult(BaseModel):
    """Container for all facts extracted from a single page."""
    page_number: int
    facts: List[ExtractedFactItem] = []
    parsing_issues: List[str] = []


class FactBase(BaseModel):
    document_id: str
    page_number: int
    statement: str
    entity: Optional[str] = None
    attribute: Optional[str] = None
    raw_value: Optional[str] = None
    normalized_value: Optional[float] = None
    normalized_value_str: Optional[str] = None
    unit: Optional[str] = None
    currency: Optional[str] = None
    time_period: Optional[str] = None
    fiscal_year: Optional[str] = None
    quarter: Optional[str] = None
    geography: Optional[str] = None
    scope: Optional[str] = None
    definition: Optional[str] = None
    source_section: Optional[str] = None
    value_status: ValueStatus = ValueStatus.ACTUAL
    evidence_quote: str
    bounding_box: Optional[List[float]] = None
    confidence: float = 1.0
    status: FactStatus = FactStatus.EXTRACTED
    uncertainty_notes: Optional[str] = None
    indexing_status: Optional[str] = "PENDING"
    source_type: Optional[str] = "PDF"


class FactCreate(FactBase):
    page_id: Optional[str] = None
    embedding_id: Optional[str] = None


class FactRead(FactBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_id: Optional[str] = None
    document_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FactFilter(BaseModel):
    document_id: Optional[str] = None
    entity: Optional[str] = None
    attribute: Optional[str] = None
    time_period: Optional[str] = None
    fiscal_year: Optional[str] = None
    quarter: Optional[str] = None
    geography: Optional[str] = None
    scope: Optional[str] = None
    status: Optional[FactStatus] = None
    min_confidence: Optional[float] = None
    search_query: Optional[str] = None
