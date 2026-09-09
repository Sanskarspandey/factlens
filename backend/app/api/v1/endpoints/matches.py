"""Candidate match querying and inspection endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.comparison import FactCandidateMatch, MatchType
from app.models.fact import Fact
from app.models.document import Document
from app.schemas.comparison import CandidateMatchRead
from app.schemas.fact import FactRead
from app.schemas.common import APIResponse

router = APIRouter()


def _serialize_fact(fact: Optional[Fact], db: Session) -> Optional[FactRead]:
    if not fact:
        return None
    doc = db.query(Document.filename).filter(Document.id == fact.document_id).first()
    is_demo = bool(
        (fact.source_section and "DEMO" in fact.source_section.upper())
        or (fact.document_id and fact.document_id.startswith("doc_demo_"))
        or (fact.id and fact.id.startswith("fact_demo_"))
    )
    return FactRead(
        id=fact.id,
        document_id=fact.document_id,
        page_id=fact.page_id,
        page_number=fact.page_number,
        document_filename=doc.filename if doc else None,
        statement=fact.statement,
        entity=fact.entity,
        attribute=fact.attribute,
        raw_value=fact.raw_value,
        normalized_value=fact.normalized_value,
        normalized_value_str=fact.normalized_value_str,
        unit=fact.unit,
        currency=fact.currency,
        time_period=fact.time_period,
        fiscal_year=fact.fiscal_year,
        quarter=fact.quarter,
        geography=fact.geography,
        scope=fact.scope,
        definition=fact.definition,
        source_section=fact.source_section,
        value_status=fact.value_status,
        evidence_quote=fact.evidence_quote,
        bounding_box=fact.bounding_box,
        confidence=fact.confidence,
        status=fact.status,
        uncertainty_notes=fact.uncertainty_notes,
        indexing_status=fact.indexing_status,
        source_type="SYNTHETIC_DEMO" if is_demo else "PDF",
        created_at=fact.created_at,
        updated_at=fact.updated_at
    )


def _serialize_match(match: FactCandidateMatch, db: Session) -> CandidateMatchRead:
    src_fact = db.query(Fact).filter(Fact.id == match.source_fact_id).first()
    cand_fact = db.query(Fact).filter(Fact.id == match.candidate_fact_id).first()

    return CandidateMatchRead(
        id=match.id,
        source_fact_id=match.source_fact_id,
        candidate_fact_id=match.candidate_fact_id,
        semantic_similarity=match.semantic_similarity,
        entity_score=match.entity_score,
        attribute_score=match.attribute_score,
        time_score=match.time_score,
        scope_score=match.scope_score,
        geography_score=match.geography_score,
        definition_score=match.definition_score,
        currency_score=match.currency_score,
        overall_score=match.overall_score,
        match_type=match.match_type,
        reason=match.reason,
        structured_diff=match.structured_diff,
        created_at=match.created_at,
        source_fact=_serialize_fact(src_fact, db),
        candidate_fact=_serialize_fact(cand_fact, db)
    )


@router.get("", response_model=APIResponse[List[CandidateMatchRead]])
@router.get("/", response_model=APIResponse[List[CandidateMatchRead]], include_in_schema=False)
async def list_matches(
    document_id: Optional[str] = None,
    entity: Optional[str] = None,
    attribute: Optional[str] = None,
    match_type: Optional[MatchType] = None,
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Lists candidate matches with filtering options:
    - document_id
    - entity
    - attribute
    - match_type (LIKELY_SAME_FACT, RELATED_FACT, TEMPORAL_VARIANT, INCOMPATIBLE_CONTEXT, LOW_CONFIDENCE)
    - min_score (e.g. 0.6)
    """
    query = db.query(FactCandidateMatch)

    if document_id:
        # Matches where source or candidate fact belongs to document
        query = query.join(Fact, FactCandidateMatch.source_fact_id == Fact.id).filter(Fact.document_id == document_id)
    if match_type:
        query = query.filter(FactCandidateMatch.match_type == match_type)
    if min_score is not None:
        query = query.filter(FactCandidateMatch.overall_score >= min_score)

    matches = query.order_by(FactCandidateMatch.overall_score.desc()).offset(skip).limit(limit).all()

    # In-memory entity/attribute filter if specified
    serialized = []
    for m in matches:
        res = _serialize_match(m, db)
        if entity:
            src_ent = (res.source_fact.entity or "").lower() if res.source_fact else ""
            cand_ent = (res.candidate_fact.entity or "").lower() if res.candidate_fact else ""
            if entity.lower() not in src_ent and entity.lower() not in cand_ent:
                continue
        if attribute:
            src_attr = (res.source_fact.attribute or "").lower() if res.source_fact else ""
            cand_attr = (res.candidate_fact.attribute or "").lower() if res.candidate_fact else ""
            if attribute.lower() not in src_attr and attribute.lower() not in cand_attr:
                continue
        serialized.append(res)

    return APIResponse(
        success=True,
        data=serialized
    )


@router.get("/{match_id}", response_model=APIResponse[CandidateMatchRead])
async def get_match(
    match_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves a single candidate match with source fact, candidate fact, similarity scores, and diff analysis."""
    match = db.query(FactCandidateMatch).filter(FactCandidateMatch.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate match '{match_id}' not found."
        )

    return APIResponse(
        success=True,
        data=_serialize_match(match, db)
    )
