"""Audit, extraction failure, and uncertainty tracking endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.audit import ExtractionFailure
from app.models.fact import Fact, FactStatus
from app.models.comparison import FactRelationship, RelationshipType
from app.models.document import Document
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/failures", response_model=APIResponse[List[dict]])
async def list_extraction_failures(
    document_id: Optional[str] = None,
    stage: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Lists preserved extraction, grounding, and parsing failures."""
    query = db.query(ExtractionFailure)
    if document_id:
        query = query.filter(ExtractionFailure.document_id == document_id)
    if stage:
        query = query.filter(ExtractionFailure.stage == stage)

    failures = query.order_by(ExtractionFailure.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for f in failures:
        doc = db.query(Document.filename).filter(Document.id == f.document_id).first()
        result.append({
            "id": f.id,
            "document_id": f.document_id,
            "document_filename": doc.filename if doc else None,
            "page_number": f.page_number,
            "stage": f.stage,
            "raw_content": f.raw_content,
            "error_type": f.error_type,
            "error_message": f.error_message,
            "context_data": f.context_data,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })

    return APIResponse(success=True, data=result)


@router.get("/uncertainties", response_model=APIResponse[dict])
async def list_uncertainties(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Lists facts with uncertain status or ambiguous extractions, plus uncertain reconciliations."""
    uncertain_facts = db.query(Fact).filter(
        (Fact.status == FactStatus.UNCERTAIN) | (Fact.uncertainty_notes.isnot(None))
    ).order_by(Fact.created_at.desc()).offset(skip).limit(limit).all()

    uncertain_rels = db.query(FactRelationship).filter(
        FactRelationship.relationship == RelationshipType.UNCERTAIN
    ).order_by(FactRelationship.created_at.desc()).offset(skip).limit(limit).all()

    facts_data = [
        {
            "id": f.id,
            "type": "FACT_UNCERTAINTY",
            "document_id": f.document_id,
            "statement": f.statement,
            "entity": f.entity,
            "attribute": f.attribute,
            "evidence_quote": f.evidence_quote,
            "uncertainty_notes": f.uncertainty_notes,
            "confidence": f.confidence,
            "created_at": f.created_at.isoformat() if f.created_at else None
        }
        for f in uncertain_facts
    ]

    rels_data = [
        {
            "id": r.id,
            "type": "RECONCILIATION_UNCERTAINTY",
            "source_fact_id": r.fact_a_id,
            "candidate_fact_id": r.fact_b_id,
            "relationship": r.relationship.value,
            "rationale": r.rationale,
            "uncertainty_notes": r.uncertainty_notes,
            "confidence": r.confidence,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in uncertain_rels
    ]

    return APIResponse(
        success=True,
        data={
            "uncertain_facts": facts_data,
            "uncertain_reconciliations": rels_data
        }
    )
