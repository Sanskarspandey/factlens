"""Demo cases endpoint to provide pre-configured verifiable test scenarios for evaluators."""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.document import Document, DocumentStatus
from app.models.fact import Fact, FactStatus, ValueStatus
from app.models.comparison import FactRelationship
from app.schemas.common import APIResponse
from app.services.reconciliation_service import ReconciliationService
from app.api.v1.endpoints.reconciliation import _serialize_relationship

router = APIRouter()


@router.get("/cases", response_model=APIResponse[List[Dict[str, Any]]])
async def get_demo_cases(db: Session = Depends(get_db)):
    """
    Returns descriptions and live references for the 4 required demonstration scenarios:
    1. Corroboration
    2. Genuine Contradiction
    3. Contextual Difference (Scope, Temporal, Status)
    4. Uncertainty & Failure Preservation
    """
    cases = [
        {
            "id": "case_1_corroboration",
            "title": "Case 1: Grounded Corroboration",
            "description": "Two documents report equivalent revenue under different notations for the same period and scope (₹8,142 crore in Annual Report P.12 vs ₹81.42 billion in Investor Deck P.5, FY24 Consolidated).",
            "expected_relationship": "CORROBORATED",
            "fact_a_preview": "₹8,142 Cr | FY2024 | Consolidated (INR)",
            "fact_b_preview": "₹81.42 B | FY2024 | Consolidated (INR)",
            "source_type": "PDF"
        },
        {
            "id": "case_2_contradiction",
            "title": "Case 2: Required Contradiction Scenario (Evaluator Demo Fixture)",
            "description": "Two filings share identical reporting context (Delhivery, FY2024, Consolidated), but report mutually exclusive headcount figures with a 26.15% variance (32,500 vs 24,000 employees). Labeled as an evaluator demo fixture as real audited filings rarely contradict internally.",
            "expected_relationship": "CONTRADICTED",
            "fact_a_preview": "32,500 employees | FY2024 | Consolidated",
            "fact_b_preview": "24,000 employees | FY2024 | Consolidated",
            "source_type": "SYNTHETIC_DEMO"
        },
        {
            "id": "case_3_contextual_difference",
            "title": "Case 3: Contextual Difference (Reporting Scope Divergence)",
            "description": "Apparent numerical divergence explained by reporting scope: Consolidated EBITDA (₹127 Cr) vs Standalone EBITDA (₹95 Cr) for FY24. Contextual dimensional divergence strictly precludes a false contradiction.",
            "expected_relationship": "CONTEXTUALLY_DIFFERENT",
            "fact_a_preview": "₹127 Cr | FY2024 | Consolidated",
            "fact_b_preview": "₹95 Cr | FY2024 | Standalone",
            "source_type": "PDF"
        },
        {
            "id": "case_4_uncertainty",
            "title": "Case 4: Preserved Uncertainty & Grounding Failure",
            "description": "Unverified evidence quotes or conditional projections are transparently preserved as UNCERTAIN without fabricating synthetic reconciliations (Conditional forecast vs unquantified claim with missing quote).",
            "expected_relationship": "UNCERTAIN",
            "fact_a_preview": "800M units | Conditional Forecast",
            "fact_b_preview": "Unquantified | Missing Quote",
            "source_type": "SYNTHETIC_DEMO"
        }
    ]
    return APIResponse(success=True, data=cases)


@router.post("/seed", response_model=APIResponse[Dict[str, Any]])
async def seed_demo_data(db: Session = Depends(get_db)):
    """
    Seeds standard demo documents, facts, and relationships so evaluators
    can immediately test and inspect all 4 scenarios across the entire UI.
    """
    # 1. Ensure demo documents
    doc_a = db.query(Document).filter(Document.id == "doc_demo_annual_report").first()
    if not doc_a:
        doc_a = Document(
            id="doc_demo_annual_report",
            filename="Delhivery_Annual_Report_FY24.pdf",
            file_path="./data/uploads/demo_annual_report.pdf",
            file_hash="demo_hash_annual_report",
            file_size=125000,
            num_pages=45,
            status=DocumentStatus.PROCESSED,
            metadata_json={"title": "Delhivery FY24 Annual Report"}
        )
        db.add(doc_a)

    doc_b = db.query(Document).filter(Document.id == "doc_demo_investor_presentation").first()
    if not doc_b:
        doc_b = Document(
            id="doc_demo_investor_presentation",
            filename="Delhivery_Investor_Presentation_Q4FY24.pdf",
            file_path="./data/uploads/demo_investor_presentation.pdf",
            file_hash="demo_hash_investor_pres",
            file_size=85000,
            num_pages=28,
            status=DocumentStatus.PROCESSED,
            metadata_json={"title": "Delhivery Q4 FY24 Investor Presentation"}
        )
        db.add(doc_b)

    db.commit()

    # 2. Seed Facts
    demo_facts = [
        # Case 1: Corroboration
        Fact(
            id="fact_demo_corroborate_a",
            document_id="doc_demo_annual_report",
            page_number=12,
            statement="Revenue from services was ₹8,142 crore during fiscal year 2024.",
            entity="Delhivery",
            attribute="Revenue from services",
            raw_value="₹8,142 crore",
            normalized_value=81420000000.0,
            normalized_value_str="₹81.42 billion",
            unit="INR",
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            geography="India",
            definition="GAAP",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Revenue from services was ₹8,142 crore during fiscal year 2024, representing 13% YoY growth.",
            confidence=0.98,
            status=FactStatus.VERIFIED
        ),
        Fact(
            id="fact_demo_corroborate_b",
            document_id="doc_demo_investor_presentation",
            page_number=5,
            statement="Total services revenue reached ₹81.42 billion in FY24.",
            entity="Delhivery",
            attribute="Revenue from services",
            raw_value="₹81.42 billion",
            normalized_value=81420000000.0,
            normalized_value_str="₹81.42 billion",
            unit="INR",
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            geography="India",
            definition="GAAP",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Total services revenue reached ₹81.42 billion in FY24 across express parcel and PTL segments.",
            confidence=0.98,
            status=FactStatus.VERIFIED
        ),

        # Case 2: Genuine Contradiction
        Fact(
            id="fact_demo_contradict_a",
            document_id="doc_demo_annual_report",
            page_number=18,
            statement="Delhivery headcount was 32,500 active employees at year end.",
            entity="Delhivery",
            attribute="Headcount",
            raw_value="32,500",
            normalized_value=32500.0,
            normalized_value_str="32,500",
            unit="employees",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            geography="India",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Delhivery headcount was 32,500 active employees at year end March 31, 2024.",
            confidence=0.96,
            status=FactStatus.VERIFIED
        ),
        Fact(
            id="fact_demo_contradict_b",
            document_id="doc_demo_investor_presentation",
            page_number=22,
            statement="Delhivery total workforce was reported as 24,000 employees as of FY24.",
            entity="Delhivery",
            attribute="Headcount",
            raw_value="24,000",
            normalized_value=24000.0,
            normalized_value_str="24,000",
            unit="employees",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            geography="India",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Delhivery total workforce was reported as 24,000 employees as of FY24 close.",
            confidence=0.96,
            status=FactStatus.VERIFIED
        ),

        # Case 3: Scope Difference
        Fact(
            id="fact_demo_scope_a",
            document_id="doc_demo_annual_report",
            page_number=30,
            statement="Consolidated EBITDA stood at ₹127 crore for the full year FY2024.",
            entity="Delhivery",
            attribute="EBITDA",
            raw_value="₹127 crore",
            normalized_value=1270000000.0,
            normalized_value_str="₹1.27 billion",
            unit="INR",
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Consolidated",
            geography="India",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Consolidated EBITDA stood at ₹127 crore for the full year FY2024 compared to ₹(67) Cr in FY23.",
            confidence=0.95,
            status=FactStatus.VERIFIED
        ),
        Fact(
            id="fact_demo_scope_b",
            document_id="doc_demo_annual_report",
            page_number=31,
            statement="Standalone operating EBITDA was ₹95 crore in FY2024.",
            entity="Delhivery",
            attribute="EBITDA",
            raw_value="₹95 crore",
            normalized_value=950000000.0,
            normalized_value_str="₹950.00 million",
            unit="INR",
            currency="INR",
            time_period="FY2024",
            fiscal_year="FY2024",
            scope="Standalone",
            geography="India",
            value_status=ValueStatus.ACTUAL,
            evidence_quote="Standalone operating EBITDA was ₹95 crore in FY2024 reflecting domestic corporate performance.",
            confidence=0.95,
            status=FactStatus.VERIFIED
        ),

        # Case 4: Uncertainty
        Fact(
            id="fact_demo_uncertain_a",
            document_id="doc_demo_investor_presentation",
            page_number=14,
            statement="Projected express parcel volume might exceed 800 million units.",
            entity="Delhivery",
            attribute="Volume",
            raw_value="800 million units",
            normalized_value=800000000.0,
            normalized_value_str="800.00 million",
            unit="units",
            time_period="FY2025",
            value_status=ValueStatus.FORECAST,
            evidence_quote="Projected express parcel volume might exceed 800 million units subject to festive demand.",
            confidence=0.70,
            status=FactStatus.UNCERTAIN,
            uncertainty_notes="Forward-looking projection with conditional festive variance."
        ),
        Fact(
            id="fact_demo_uncertain_b",
            document_id="doc_demo_investor_presentation",
            page_number=15,
            statement="Substantial volume growth anticipated in upcoming periods.",
            entity="Delhivery",
            attribute=None,
            raw_value=None,
            normalized_value=None,
            evidence_quote="",  # Missing evidence quote
            confidence=0.40,
            status=FactStatus.FAILED,
            uncertainty_notes="Evidence grounding missing and metric unquantified."
        )
    ]

    for f in demo_facts:
        existing = db.query(Fact).filter(Fact.id == f.id).first()
        if not existing:
            db.add(f)
        else:
            existing.statement = f.statement
            existing.entity = f.entity
            existing.attribute = f.attribute
            existing.raw_value = f.raw_value
            existing.normalized_value = f.normalized_value
            existing.normalized_value_str = f.normalized_value_str
            existing.scope = f.scope
            existing.time_period = f.time_period
            existing.fiscal_year = f.fiscal_year
            existing.evidence_quote = f.evidence_quote
            existing.status = f.status
            existing.uncertainty_notes = f.uncertainty_notes

    db.commit()

    # 3. Compute Reconciliations for Demo Pairs
    reconciler = ReconciliationService(db)
    pairs = [
        ("fact_demo_corroborate_a", "fact_demo_corroborate_b"),
        ("fact_demo_contradict_a", "fact_demo_contradict_b"),
        ("fact_demo_scope_a", "fact_demo_scope_b"),
        ("fact_demo_uncertain_a", "fact_demo_uncertain_b"),
    ]

    reconciled_results = []
    for f_a_id, f_b_id in pairs:
        fa = db.query(Fact).filter(Fact.id == f_a_id).first()
        fb = db.query(Fact).filter(Fact.id == f_b_id).first()
        if fa and fb:
            rel = reconciler.reconcile_fact_pair(fa, fb)
            reconciled_results.append(_serialize_relationship(rel, db))

    return APIResponse(
        success=True,
        message="Demo dataset seeded successfully with 4 verified reference cases.",
        data={
            "seeded_documents": 2,
            "seeded_facts": len(demo_facts),
            "reconciled_cases": len(reconciled_results)
        }
    )
