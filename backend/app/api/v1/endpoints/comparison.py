"""Pairwise Fact comparison endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.comparison import CompareFactsRequest, FactRelationshipRead
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("/compare-pair", response_model=APIResponse[FactRelationshipRead])
async def compare_fact_pair(
    request: CompareFactsRequest,
    db: Session = Depends(get_db)
):
    """
    Compares two facts and returns their relationship:
    - CORROBORATED
    - CONTRADICTED
    - CONTEXTUALLY_DIFFERENT
    - UNCERTAIN
    Along with a detailed rationale and difference breakdown.
    """
    from app.models.fact import Fact
    from app.services.reconciliation_service import ReconciliationService
    from app.api.v1.endpoints.reconciliation import _serialize_relationship

    fact_a = db.query(Fact).filter(Fact.id == request.fact_a_id).first()
    fact_b = db.query(Fact).filter(Fact.id == request.fact_b_id).first()

    if not fact_a:
        raise HTTPException(status_code=404, detail=f"Fact '{request.fact_a_id}' not found.")
    if not fact_b:
        raise HTTPException(status_code=404, detail=f"Fact '{request.fact_b_id}' not found.")

    reconciler = ReconciliationService(db)
    rel = reconciler.reconcile_fact_pair(
        fact_a=fact_a,
        fact_b=fact_b,
        use_llm_for_ambiguous=request.use_llm_for_ambiguous or False
    )

    return APIResponse(
        success=True,
        message=f"Reconciled {fact_a.id} and {fact_b.id} as {rel.relationship.value}.",
        data=_serialize_relationship(rel, db)
    )
