"""Vector indexing and candidate generation management endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.fact import Fact
from app.services.comparison_service import CandidateMatchingService
from app.schemas.comparison import RebuildIndexResponse
from app.schemas.common import APIResponse
from app.services.vector.chroma_store import vector_store

router = APIRouter()


@router.post("/rebuild", response_model=APIResponse[RebuildIndexResponse])
async def rebuild_index(db: Session = Depends(get_db)):
    """
    Rebuilds/re-indexes all facts from SQLite into ChromaDB vector store
    and generates candidate matches across the knowledge layer.
    Safe to run repeatedly.
    """
    matcher = CandidateMatchingService(db)
    indexed_count = matcher.index_all_facts()

    # Generate candidate matches across all indexed facts
    facts = db.query(Fact).all()
    total_matches = 0
    for f in facts:
        matches = matcher.find_and_score_candidates_for_fact(f, top_k=10)
        total_matches += len(matches)

    vector_count = vector_store.count()

    return APIResponse(
        success=True,
        message=f"Vector index rebuilt successfully. Indexed {indexed_count} facts, found {total_matches} candidate pairings.",
        data=RebuildIndexResponse(
            facts_indexed=indexed_count,
            total_vectors=vector_count,
            status="SUCCESS",
            message=f"Indexed {indexed_count} facts into ChromaDB. Total vectors in store: {vector_count}."
        )
    )
