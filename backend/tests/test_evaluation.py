"""Tests for FactLens Evaluation Service, Evaluation Lab Endpoints, and Verdict Checklist."""
import pytest
from app.services.evaluation_service import EvaluationService
from app.services.reconciliation_service import build_verdict_checklist
from app.models.comparison import RelationshipType
from app.models.fact import Fact, FactStatus, ValueStatus


def test_evaluation_service_run_deterministic(db_session):
    """Verifies that EvaluationService runs all deterministic test fixtures and returns passing results."""
    eval_service = EvaluationService(db_session)
    results = eval_service.run_evaluation()

    assert "summary" in results
    assert "categories" in results
    assert "scenarios" in results

    summary = results["summary"]
    assert summary["total_scenarios"] >= 6
    assert summary["passed_scenarios"] == summary["total_scenarios"]
    assert summary["failed_scenarios"] == 0

    # Ensure categories cover all core dimensions
    cat_names = [c["name"] for c in results["categories"]]
    assert "Corroboration" in cat_names
    assert "Contradiction" in cat_names
    assert "Contextual Difference" in cat_names
    assert "Uncertainty" in cat_names
    assert "Evidence Grounding" in cat_names
    assert "Normalization" in cat_names


def test_evaluation_api_endpoints(client):
    """Verifies POST /api/v1/evaluation/run and GET /api/v1/evaluation/latest endpoints."""
    # Test POST /run
    res_run = client.post("/api/v1/evaluation/run")
    assert res_run.status_code == 200
    json_run = res_run.json()
    assert json_run["success"] is True
    assert json_run["data"]["summary"]["total_scenarios"] >= 6

    # Test GET /latest
    res_latest = client.get("/api/v1/evaluation/latest")
    assert res_latest.status_code == 200
    json_latest = res_latest.json()
    assert json_latest["success"] is True
    assert json_latest["data"]["summary"]["passed_scenarios"] >= 6


def test_build_verdict_checklist_structure():
    """Verifies that build_verdict_checklist constructs structured deterministic items."""
    fact_a = Fact(
        id="f_test_a",
        entity="Acme",
        attribute="Revenue",
        fiscal_year="FY2024",
        scope="Consolidated",
        currency="USD",
        raw_value="$100M",
        normalized_value=100000000.0,
        status=FactStatus.VERIFIED
    )
    fact_b = Fact(
        id="f_test_b",
        entity="Acme",
        attribute="Revenue",
        fiscal_year="FY2024",
        scope="Consolidated",
        currency="USD",
        raw_value="$100M",
        normalized_value=100000000.0,
        status=FactStatus.VERIFIED
    )

    # 1. Corroborated checklist
    val_comp = {
        "percentage_difference": 0.0,
        "match_tolerance": 0.01,
        "source_formatted": "$100.00M",
        "candidate_formatted": "$100.00M"
    }
    checklist_corr = build_verdict_checklist(
        relationship=RelationshipType.CORROBORATED,
        fact_a=fact_a,
        fact_b=fact_b,
        val_comp=val_comp,
        ctx_comp={}
    )
    assert len(checklist_corr) >= 6
    assert any("Same entity" in item["label"] for item in checklist_corr)
    assert any("Difference: 0.00%" in item["label"] for item in checklist_corr)

    # 2. Contradicted checklist
    checklist_contra = build_verdict_checklist(
        relationship=RelationshipType.CONTRADICTED,
        fact_a=fact_a,
        fact_b=fact_b,
        val_comp={"percentage_difference": 25.0, "match_tolerance": 0.01},
        ctx_comp={}
    )
    assert any(item["status"] == "WARN" for item in checklist_contra)
    assert any("disagreement" in item["label"].lower() for item in checklist_contra)
