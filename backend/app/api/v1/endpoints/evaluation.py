"""Evaluation Lab endpoint exposing live deterministic evaluation execution."""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import APIResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter()


@router.post("/run", response_model=APIResponse[Dict[str, Any]])
async def run_evaluation_suite(db: Session = Depends(get_db)):
    """
    Executes the deterministic evaluation test suite across:
    1. Corroboration
    2. Contradiction
    3. Contextual Difference
    4. Uncertainty Preservation
    5. Evidence Grounding
    6. Normalization
    Returns actual observed verification results.
    """
    eval_service = EvaluationService(db)
    results = eval_service.run_evaluation()
    return APIResponse(
        success=True,
        message=f"Evaluation completed: {results['summary']['passed_scenarios']}/{results['summary']['total_scenarios']} passed in {results['summary']['execution_time_ms']}ms.",
        data=results
    )


@router.get("/latest", response_model=APIResponse[Dict[str, Any]])
async def get_latest_evaluation(db: Session = Depends(get_db)):
    """Fetches the latest evaluation suite results."""
    eval_service = EvaluationService(db)
    results = eval_service.run_evaluation()
    return APIResponse(
        success=True,
        data=results
    )
