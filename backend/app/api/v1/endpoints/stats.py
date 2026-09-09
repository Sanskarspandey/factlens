"""System statistics endpoint for the dashboard."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document, DocumentPage
from app.models.fact import Fact
from app.models.comparison import FactRelationship, RelationshipType
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[dict])
@router.get("/", response_model=APIResponse[dict], include_in_schema=False)
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Returns real, dynamic system statistics:
    - documents, pages, facts, reconciliations
    - corroborated, contradicted, contextually_different, uncertain
    """
    doc_count = db.query(Document).count()
    page_count = db.query(DocumentPage).count()
    fact_count = db.query(Fact).count()
    rel_count = db.query(FactRelationship).count()

    corroborated = db.query(FactRelationship).filter(FactRelationship.relationship == RelationshipType.CORROBORATED).count()
    contradicted = db.query(FactRelationship).filter(FactRelationship.relationship == RelationshipType.CONTRADICTED).count()
    contextually_diff = db.query(FactRelationship).filter(FactRelationship.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT).count()
    uncertain = db.query(FactRelationship).filter(FactRelationship.relationship == RelationshipType.UNCERTAIN).count()

    return APIResponse(
        success=True,
        data={
            "documents": doc_count,
            "pages": page_count,
            "facts": fact_count,
            "reconciliations": rel_count,
            "corroborated": corroborated,
            "contradicted": contradicted,
            "contextually_different": contextually_diff,
            "uncertain": uncertain
        }
    )
