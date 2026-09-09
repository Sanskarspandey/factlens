"""Schemas package initialization."""
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.document import DocumentBase, DocumentCreate, DocumentRead, DocumentDetailRead, DocumentPageRead
from app.schemas.normalization import NormalizedValue, NormalizedTimePeriod
from app.schemas.fact import (
    FactBase,
    FactCreate,
    FactRead,
    FactFilter,
    ExtractedFactItem,
    PageExtractionResult
)
from app.schemas.comparison import (
    CandidateMatchRead,
    CandidateMatchFilter,
    RebuildIndexResponse,
    CompareFactsRequest,
    FactRelationshipRead,
    ReconciliationRequest,
    ReconciliationSummaryStats,
    ReconciliationSessionRead
)

__all__ = [
    "APIResponse",
    "PaginatedResponse",
    "DocumentBase",
    "DocumentCreate",
    "DocumentRead",
    "DocumentDetailRead",
    "DocumentPageRead",
    "NormalizedValue",
    "NormalizedTimePeriod",
    "FactBase",
    "FactCreate",
    "FactRead",
    "FactFilter",
    "ExtractedFactItem",
    "PageExtractionResult",
    "CandidateMatchRead",
    "CandidateMatchFilter",
    "RebuildIndexResponse",
    "CompareFactsRequest",
    "FactRelationshipRead",
    "ReconciliationRequest",
    "ReconciliationSummaryStats",
    "ReconciliationSessionRead",
]
