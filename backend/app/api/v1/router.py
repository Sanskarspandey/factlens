"""FastAPI API v1 root router aggregating all endpoints."""
from fastapi import APIRouter
from app.api.v1.endpoints import documents, facts, matches, index, comparison, reconciliation, health, stats, audit, demo, evaluation

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(facts.router, prefix="/facts", tags=["Facts"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches"])
api_router.include_router(index.router, prefix="/index", tags=["Index"])
api_router.include_router(comparison.router, prefix="/comparison", tags=["Comparison"])
api_router.include_router(reconciliation.router, prefix="/reconciliation", tags=["Reconciliation"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
api_router.include_router(demo.router, prefix="/demo", tags=["Demo"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["Evaluation"])
