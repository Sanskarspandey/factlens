"""Facts querying, inspection, extraction, and candidate matching endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.fact import Fact, FactStatus, ValueStatus
from app.models.document import Document
from app.schemas.fact import FactRead
from app.schemas.comparison import CandidateMatchRead
from app.schemas.common import APIResponse
from app.services.extraction_service import ExtractionService
from app.services.comparison_service import CandidateMatchingService

router = APIRouter()


def _serialize_fact_obj(f: Fact, db: Session) -> FactRead:
    doc = db.query(Document.filename).filter(Document.id == f.document_id).first()
    is_demo = bool(
        (f.source_section and "DEMO" in f.source_section.upper())
        or (f.document_id and f.document_id.startswith("doc_demo_"))
        or (f.id and f.id.startswith("fact_demo_"))
    )
    return FactRead(
        id=f.id,
        document_id=f.document_id,
        page_id=f.page_id,
        page_number=f.page_number,
        document_filename=doc.filename if doc else None,
        statement=f.statement,
        entity=f.entity,
        attribute=f.attribute,
        raw_value=f.raw_value,
        normalized_value=f.normalized_value,
        normalized_value_str=f.normalized_value_str,
        unit=f.unit,
        currency=f.currency,
        time_period=f.time_period,
        fiscal_year=f.fiscal_year,
        quarter=f.quarter,
        geography=f.geography,
        scope=f.scope,
        definition=f.definition,
        source_section=f.source_section,
        value_status=f.value_status or ValueStatus.ACTUAL,
        evidence_quote=f.evidence_quote,
        bounding_box=f.bounding_box,
        confidence=f.confidence,
        status=f.status,
        uncertainty_notes=f.uncertainty_notes,
        indexing_status=f.indexing_status,
        source_type="SYNTHETIC_DEMO" if is_demo else "PDF",
        created_at=f.created_at,
        updated_at=f.updated_at
    )


@router.post("/extract/{document_id}", response_model=APIResponse[dict])
async def extract_facts_endpoint(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Triggers end-to-end fact extraction, grounding, and vector indexing for a document."""
    extractor = ExtractionService(db)
    facts = await extractor.process_and_extract_document(document_id)
    return APIResponse(
        success=True,
        message=f"Extracted and indexed {len(facts)} grounded facts.",
        data={"document_id": document_id, "facts_extracted": len(facts)}
    )


@router.get("", response_model=APIResponse[List[FactRead]])
@router.get("/", response_model=APIResponse[List[FactRead]], include_in_schema=False)
async def list_facts(
    document_id: Optional[str] = None,
    entity: Optional[str] = None,
    attribute: Optional[str] = None,
    time_period: Optional[str] = None,
    fiscal_year: Optional[str] = None,
    quarter: Optional[str] = None,
    fact_status: Optional[FactStatus] = Query(None, alias="status"),
    search: Optional[str] = None,
    min_confidence: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lists facts with comprehensive filtering and keyword search.
    Supports filtering by document_id, entity, attribute, time_period, fiscal_year, quarter, status, and search query.
    """
    query = db.query(Fact)

    if document_id:
        query = query.filter(Fact.document_id == document_id)
    if entity:
        query = query.filter(Fact.entity.ilike(f"%{entity}%"))
    if attribute:
        query = query.filter(Fact.attribute.ilike(f"%{attribute}%"))
    if time_period:
        query = query.filter(Fact.time_period.ilike(f"%{time_period}%"))
    if fiscal_year:
        query = query.filter(Fact.fiscal_year.ilike(f"%{fiscal_year}%"))
    if quarter:
        query = query.filter(Fact.quarter.ilike(f"%{quarter}%"))
    if fact_status:
        query = query.filter(Fact.status == fact_status)
    if min_confidence is not None:
        query = query.filter(Fact.confidence >= min_confidence)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Fact.statement.ilike(search_pattern),
                Fact.evidence_quote.ilike(search_pattern),
                Fact.entity.ilike(search_pattern),
                Fact.attribute.ilike(search_pattern),
            )
        )

    facts = query.order_by(Fact.created_at.desc()).offset(skip).limit(limit).all()
    result = [_serialize_fact_obj(f, db) for f in facts]

    return APIResponse(
        success=True,
        data=result
    )


@router.get("/{fact_id}", response_model=APIResponse[FactRead])
async def get_fact(
    fact_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves a single fact with exact evidence quote, page number, bounding box, and normalization data."""
    fact = db.query(Fact).filter(Fact.id == fact_id).first()
    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fact '{fact_id}' not found."
        )

    return APIResponse(
        success=True,
        data=_serialize_fact_obj(fact, db)
    )


@router.get("/{fact_id}/matches", response_model=APIResponse[List[CandidateMatchRead]])
async def get_fact_candidate_matches(
    fact_id: str,
    top_k: int = Query(10, ge=1, le=50),
    min_score: float = Query(0.30, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    """
    Retrieves top semantically and structurally scored candidate matches for a fact.
    Computes candidate matches on-the-fly via ChromaDB vector retrieval + structured multi-dimensional scoring.
    """
    fact = db.query(Fact).filter(Fact.id == fact_id).first()
    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fact '{fact_id}' not found."
        )

    matcher = CandidateMatchingService(db)
    matches = matcher.find_and_score_candidates_for_fact(fact, top_k=top_k, min_score_threshold=min_score)

    from app.api.v1.endpoints.matches import _serialize_match
    serialized = [_serialize_match(m, db) for m in matches]

    return APIResponse(
        success=True,
        message=f"Found {len(serialized)} candidate matches for fact {fact_id}.",
        data=serialized
    )
