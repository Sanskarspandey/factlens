"""Schemas for fact candidate matching, structured comparison, and reconciliation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.comparison import RelationshipType, MatchType
from app.schemas.fact import FactRead


class CandidateMatchRead(BaseModel):
    """Phase 2 candidate match between two facts with structured score breakdowns."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_fact_id: str
    candidate_fact_id: str
    semantic_similarity: float
    entity_score: float
    attribute_score: float
    time_score: float
    scope_score: float
    geography_score: float
    definition_score: float
    currency_score: float
    overall_score: float
    match_type: MatchType
    reason: str
    structured_diff: Optional[Dict[str, Any]] = None
    created_at: datetime
    source_fact: Optional[FactRead] = None
    candidate_fact: Optional[FactRead] = None


class CandidateMatchFilter(BaseModel):
    document_id: Optional[str] = None
    entity: Optional[str] = None
    attribute: Optional[str] = None
    match_type: Optional[MatchType] = None
    min_score: Optional[float] = None


class RebuildIndexResponse(BaseModel):
    facts_indexed: int
    total_vectors: int
    status: str
    message: str


class ValueComparisonResult(BaseModel):
    """Deterministic numeric comparison breakdown."""
    source_raw: Optional[str] = None
    source_normalized: Optional[float] = None
    source_formatted: Optional[str] = None
    candidate_raw: Optional[str] = None
    candidate_normalized: Optional[float] = None
    candidate_formatted: Optional[str] = None
    absolute_difference: Optional[float] = None
    relative_difference: Optional[float] = None
    percentage_difference: Optional[float] = None
    direction: Optional[str] = "INCOMPARABLE"  # EQUAL, INCREASE, DECREASE, INCOMPARABLE
    within_tolerance: bool = False
    match_tolerance: float = 0.01


class ContextComparisonResult(BaseModel):
    """Structured dimension differences across two facts."""
    entity_match: bool = True
    attribute_match: bool = True
    time_match: bool = True
    fiscal_year_match: bool = True
    quarter_match: bool = True
    scope_match: bool = True
    geography_match: bool = True
    definition_match: bool = True
    value_status_match: bool = True
    currency_match: bool = True
    unit_match: bool = True
    dimension_differences: Dict[str, str] = {}
    is_contextually_compatible: bool = True


class SupportingEvidenceItem(BaseModel):
    """Verbatim grounding provenance for a fact."""
    fact_id: str
    document_id: str
    document_filename: Optional[str] = None
    page_number: int
    evidence_quote: str
    statement: str


class SupportingEvidence(BaseModel):
    """Grounding evidence from both source and candidate documents."""
    source_evidence: SupportingEvidenceItem
    candidate_evidence: SupportingEvidenceItem


class CompareFactsRequest(BaseModel):
    fact_a_id: str
    fact_b_id: str
    use_llm_for_ambiguous: Optional[bool] = False


class VerdictChecklistItem(BaseModel):
    """Structured checklist item explaining why a reconciliation verdict was reached."""
    label: str
    status: str = "PASS"  # PASS, WARN, INFO, FAIL
    detail: Optional[str] = None


class FactRelationshipRead(BaseModel):
    """Phase 3 final reconciliation result with complete diagnostic provenance."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_fact_id: str
    candidate_fact_id: str
    relationship: RelationshipType
    confidence: float = 1.0
    similarity_score: Optional[float] = None
    rationale: str
    value_comparison: Optional[ValueComparisonResult] = None
    context_comparison: Optional[ContextComparisonResult] = None
    supporting_evidence: Optional[SupportingEvidence] = None
    uncertainty_notes: Optional[str] = None
    reasoning_method: str = "DETERMINISTIC"  # DETERMINISTIC, LLM_ASSISTED
    difference_analysis: Optional[Dict[str, Any]] = None  # Backwards compatibility alias
    verdict_checklist: Optional[List[VerdictChecklistItem]] = None
    created_at: datetime
    source_fact: Optional[FactRead] = None
    candidate_fact: Optional[FactRead] = None

    # Aliases for backwards compatibility
    @property
    def fact_a_id(self) -> str:
        return self.source_fact_id

    @property
    def fact_b_id(self) -> str:
        return self.candidate_fact_id


class ReconciliationFilter(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    document_id: Optional[str] = None
    entity: Optional[str] = None
    attribute: Optional[str] = None
    min_confidence: Optional[float] = None


class ReconciliationRunRequest(BaseModel):
    document_ids: Optional[List[str]] = Field(default=None, description="Optional document IDs to restrict reconciliation to")
    min_candidate_score: Optional[float] = Field(default=0.30, ge=0.0, le=1.0)
    use_llm_for_ambiguous: Optional[bool] = False


class ReconciliationRunResponse(BaseModel):
    total_evaluated: int
    corroborated_count: int
    contradicted_count: int
    contextually_different_count: int
    uncertain_count: int
    reconciled_pairs: List[FactRelationshipRead] = []


class ReconciliationLLMResult(BaseModel):
    """Pydantic schema to strictly constrain and validate LLM output for ambiguous cases."""
    relationship: RelationshipType = Field(description="Must be EXACTLY ONE of: CORROBORATED, CONTRADICTED, CONTEXTUALLY_DIFFERENT, UNCERTAIN")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    rationale: str = Field(description="Auditable explanation citing specific factual dimensions and numbers")
    context_difference: Optional[Dict[str, str]] = Field(default=None, description="Dimension differences identified (e.g. {'scope': 'consolidated vs standalone'})")
    uncertainty_notes: Optional[str] = Field(default=None, description="Detailed reasons for any ambiguity or missing information")


class ReconciliationRequest(BaseModel):
    document_ids: List[str] = Field(description="IDs of documents to compare facts across", min_length=2)
    session_title: Optional[str] = None
    similarity_threshold: Optional[float] = 0.70
    entities_filter: Optional[List[str]] = None


class ReconciliationSummaryStats(BaseModel):
    total_comparisons: int = 0
    corroborated_count: int = 0
    contradicted_count: int = 0
    contextually_different_count: int = 0
    uncertain_count: int = 0


class ReconciliationSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    document_ids: List[str]
    summary_stats: Optional[ReconciliationSummaryStats] = None
    created_at: datetime
    relationships: List[FactRelationshipRead] = []
