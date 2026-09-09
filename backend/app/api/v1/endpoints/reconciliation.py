"""Cross-document reconciliation, corroboration, contradiction, and context querying endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.comparison import FactRelationship, RelationshipType, ReconciliationSession
from app.models.fact import Fact
from app.models.document import Document
from app.schemas.comparison import (
    FactRelationshipRead,
    CompareFactsRequest,
    ReconciliationRunRequest,
    ReconciliationRunResponse,
    ReconciliationRequest,
    ReconciliationSessionRead,
    ReconciliationSummaryStats
)
from app.schemas.fact import FactRead
from app.schemas.common import APIResponse
from app.services.reconciliation_service import ReconciliationService

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


def _serialize_relationship(rel: FactRelationship, db: Session) -> FactRelationshipRead:
    src_fact = db.query(Fact).filter(Fact.id == rel.fact_a_id).first()
    cand_fact = db.query(Fact).filter(Fact.id == rel.fact_b_id).first()
    from app.services.reconciliation_service import build_verdict_checklist
    checklist = build_verdict_checklist(
        relationship=rel.relationship,
        fact_a=src_fact,
        fact_b=cand_fact,
        val_comp=rel.value_comparison,
        ctx_comp=rel.context_comparison,
        uncertainty_notes=rel.uncertainty_notes
    )

    return FactRelationshipRead(
        id=rel.id,
        source_fact_id=rel.fact_a_id,
        candidate_fact_id=rel.fact_b_id,
        relationship=rel.relationship,
        confidence=rel.confidence,
        similarity_score=rel.similarity_score,
        rationale=rel.rationale,
        value_comparison=rel.value_comparison,
        context_comparison=rel.context_comparison,
        supporting_evidence=rel.supporting_evidence,
        uncertainty_notes=rel.uncertainty_notes,
        reasoning_method=rel.reasoning_method or "DETERMINISTIC",
        difference_analysis=rel.difference_analysis,
        verdict_checklist=checklist,
        created_at=rel.created_at,
        source_fact=_serialize_fact(src_fact, db),
        candidate_fact=_serialize_fact(cand_fact, db)
    )


@router.get("", response_model=APIResponse[List[FactRelationshipRead]])
@router.get("/", response_model=APIResponse[List[FactRelationshipRead]], include_in_schema=False)
async def list_reconciliations(
    relationship_type: Optional[RelationshipType] = Query(None, alias="relationship"),
    document_id: Optional[str] = None,
    entity: Optional[str] = None,
    attribute: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Lists cross-document reconciliation results with filtering options:
    - relationship (CORROBORATED, CONTRADICTED, CONTEXTUALLY_DIFFERENT, UNCERTAIN)
    - document_id
    - entity
    - attribute
    - min_confidence
    """
    query = db.query(FactRelationship)

    if relationship_type:
        query = query.filter(FactRelationship.relationship == relationship_type)
    if min_confidence is not None:
        query = query.filter(FactRelationship.confidence >= min_confidence)
    if document_id:
        query = query.join(Fact, FactRelationship.fact_a_id == Fact.id).filter(Fact.document_id == document_id)

    relationships = query.order_by(FactRelationship.created_at.desc()).offset(skip).limit(limit).all()

    serialized = []
    for rel in relationships:
        r_read = _serialize_relationship(rel, db)
        if entity:
            src_ent = (r_read.source_fact.entity or "").lower() if r_read.source_fact else ""
            cand_ent = (r_read.candidate_fact.entity or "").lower() if r_read.candidate_fact else ""
            if entity.lower() not in src_ent and entity.lower() not in cand_ent:
                continue
        if attribute:
            src_attr = (r_read.source_fact.attribute or "").lower() if r_read.source_fact else ""
            cand_attr = (r_read.candidate_fact.attribute or "").lower() if r_read.candidate_fact else ""
            if attribute.lower() not in src_attr and attribute.lower() not in cand_attr:
                continue
        serialized.append(r_read)

    return APIResponse(
        success=True,
        data=serialized
    )


@router.post("/run", response_model=APIResponse[ReconciliationRunResponse])
async def run_reconciliation(
    request: ReconciliationRunRequest = ReconciliationRunRequest(),
    db: Session = Depends(get_db)
):
    """
    Runs idempotent cross-document reconciliation across candidate pairs.
    Applies the deterministic 7-step decision hierarchy and persists FactRelationship records.
    """
    reconciler = ReconciliationService(db)
    reconciled = reconciler.reconcile_candidate_matches(
        min_candidate_score=request.min_candidate_score or 0.30,
        document_ids=request.document_ids,
        use_llm_for_ambiguous=request.use_llm_for_ambiguous or False
    )

    counts = {
        "corroborated": sum(1 for r in reconciled if r.relationship == RelationshipType.CORROBORATED),
        "contradicted": sum(1 for r in reconciled if r.relationship == RelationshipType.CONTRADICTED),
        "contextually_different": sum(1 for r in reconciled if r.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT),
        "uncertain": sum(1 for r in reconciled if r.relationship == RelationshipType.UNCERTAIN),
    }

    serialized_pairs = [_serialize_relationship(r, db) for r in reconciled]

    return APIResponse(
        success=True,
        message=f"Reconciled {len(reconciled)} fact candidate pairs.",
        data=ReconciliationRunResponse(
            total_evaluated=len(reconciled),
            corroborated_count=counts["corroborated"],
            contradicted_count=counts["contradicted"],
            contextually_different_count=counts["contextually_different"],
            uncertain_count=counts["uncertain"],
            reconciled_pairs=serialized_pairs
        )
    )


@router.post("/pair", response_model=APIResponse[FactRelationshipRead])
async def reconcile_pair_endpoint(
    request: CompareFactsRequest,
    db: Session = Depends(get_db)
):
    """Compares and reconciles a specific pair of facts by their IDs."""
    fact_a = db.query(Fact).filter(Fact.id == request.fact_a_id).first()
    fact_b = db.query(Fact).filter(Fact.id == request.fact_b_id).first()

    if not fact_a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fact '{request.fact_a_id}' not found.")
    if not fact_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fact '{request.fact_b_id}' not found.")

    reconciler = ReconciliationService(db)
    rel = reconciler.reconcile_fact_pair(
        fact_a=fact_a,
        fact_b=fact_b,
        use_llm_for_ambiguous=request.use_llm_for_ambiguous or False
    )

    return APIResponse(
        success=True,
        message=f"Reconciled pair {fact_a.id} and {fact_b.id} as {rel.relationship.value}.",
        data=_serialize_relationship(rel, db)
    )


@router.post("/reconcile", response_model=APIResponse[ReconciliationSessionRead], status_code=status.HTTP_201_CREATED)
async def create_reconciliation_session(
    request: ReconciliationRequest,
    db: Session = Depends(get_db)
):
    """Executes full cross-document reconciliation across documents and returns a session report."""
    reconciler = ReconciliationService(db)
    session = await reconciler.reconcile_documents(
        document_ids=request.document_ids,
        title=request.session_title,
        similarity_threshold=request.similarity_threshold or 0.30
    )

    rel_reads = [_serialize_relationship(r, db) for r in session.relationships]

    stats = None
    if session.summary_stats:
        stats = ReconciliationSummaryStats(**session.summary_stats)

    return APIResponse(
        success=True,
        message="Cross-document reconciliation session completed.",
        data=ReconciliationSessionRead(
            id=session.id,
            title=session.title,
            description=session.description,
            document_ids=session.document_ids,
            summary_stats=stats,
            created_at=session.created_at,
            relationships=rel_reads
        )
    )


@router.get("/sessions", response_model=APIResponse[List[ReconciliationSessionRead]])
async def list_reconciliation_sessions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lists past reconciliation sessions and cross-document comparison reports."""
    sessions = db.query(ReconciliationSession).order_by(ReconciliationSession.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for s in sessions:
        rel_reads = [_serialize_relationship(r, db) for r in s.relationships]
        stats = ReconciliationSummaryStats(**s.summary_stats) if s.summary_stats else None
        result.append(
            ReconciliationSessionRead(
                id=s.id,
                title=s.title,
                description=s.description,
                document_ids=s.document_ids,
                summary_stats=stats,
                created_at=s.created_at,
                relationships=rel_reads
            )
        )

    return APIResponse(
        success=True,
        data=result
    )


@router.get("/sessions/{session_id}", response_model=APIResponse[ReconciliationSessionRead])
async def get_reconciliation_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves full details and matrix relationships for a reconciliation session."""
    session = db.query(ReconciliationSession).filter(ReconciliationSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reconciliation session '{session_id}' not found."
        )

    rel_reads = [_serialize_relationship(r, db) for r in session.relationships]
    stats = ReconciliationSummaryStats(**session.summary_stats) if session.summary_stats else None

    return APIResponse(
        success=True,
        data=ReconciliationSessionRead(
            id=session.id,
            title=session.title,
            description=session.description,
            document_ids=session.document_ids,
            summary_stats=stats,
            created_at=session.created_at,
            relationships=rel_reads
        )
    )


@router.post("/{fact_id}", response_model=APIResponse[List[FactRelationshipRead]])
async def reconcile_fact_endpoint(
    fact_id: str,
    top_k: int = Query(10, ge=1, le=50),
    min_score: float = Query(0.30, ge=0.0, le=1.0),
    use_llm: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Runs candidate matching and reconciliation for a single target fact."""
    fact = db.query(Fact).filter(Fact.id == fact_id).first()
    if not fact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fact '{fact_id}' not found.")

    reconciler = ReconciliationService(db)
    rels = reconciler.reconcile_fact(fact_id, top_k=top_k, min_score=min_score, use_llm_for_ambiguous=use_llm)
    serialized = [_serialize_relationship(r, db) for r in rels]

    return APIResponse(
        success=True,
        message=f"Reconciled fact '{fact_id}' against {len(serialized)} candidates.",
        data=serialized
    )


@router.get("/{reconciliation_id}", response_model=APIResponse[FactRelationshipRead])
async def get_reconciliation(
    reconciliation_id: str,
    db: Session = Depends(get_db)
):
    """Retrieves single reconciliation diagnosis with full source/candidate facts, diffs, and evidence."""
    rel = db.query(FactRelationship).filter(FactRelationship.id == reconciliation_id).first()
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reconciliation record '{reconciliation_id}' not found."
        )

    return APIResponse(
        success=True,
        data=_serialize_relationship(rel, db)
    )
