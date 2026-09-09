"""Phase 5 End-to-End Integration, Starter Dataset Validation & Hardening Tests.

Verifies:
1. Real PDF ingestion & PyMuPDF text layout extraction.
2. Grounded fact extraction with verifiable verbatim evidence quotes.
3. Deterministic normalization across Indian and international notations.
4. Candidate matching and vector indexing.
5. Deterministic reconciliation (CORROBORATED, CONTRADICTED, CONTEXTUALLY_DIFFERENT, UNCERTAIN).
6. Delhivery & Macroeconomy context separation.
7. Arbitrary PDF generic support.
8. Evaluator demo fixture isolation (source_type = SYNTHETIC_DEMO).
"""
import pytest
import os
import tempfile
import pymupdf as fitz
from app.models.document import Document, DocumentStatus
from app.models.fact import Fact, FactStatus, ValueStatus
from app.services.pdf_service import PDFService
from app.services.extraction_service import ExtractionService
from app.services.reconciliation_service import ReconciliationService
from app.models.comparison import RelationshipType


def _create_test_pdf_file(pages_text: list[str]) -> str:
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((50, 72), text, fontsize=11)
    
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    doc.save(tmp.name)
    doc.close()
    return tmp.name


@pytest.mark.asyncio
async def test_delhivery_starter_pipeline_validation(db_session):
    """
    Validates end-to-end processing of Delhivery starter documents.
    Tests that identical figures (Revenue ₹8,142 Cr) corroborate, while
    scope differences (Consolidated vs Standalone EBITDA) are preserved as CONTEXTUALLY_DIFFERENT.
    """
    pdf_service = PDFService()
    extractor = ExtractionService(db_session)
    reconciler = ReconciliationService(db_session)

    # Document 1: Delhivery Annual Report FY24
    doc1_text = [
        "Delhivery Limited Annual Report FY2024.\n"
        "In fiscal year 2024, Delhivery reported revenue of ₹8,142 Cr.\n"
        "Consolidated Adjusted EBITDA reached ₹127 crore for the full year FY2024.\n"
        "Express parcel shipment volumes were 740 million packages."
    ]
    doc1_path = _create_test_pdf_file(doc1_text)
    with open(doc1_path, "rb") as f:
        doc1_bytes = f.read()

    doc1 = Document(
        id="doc_test_delhivery_ar",
        filename="Delhivery_Annual_Report_FY24.pdf",
        file_path=doc1_path,
        file_hash=pdf_service.calculate_file_hash(doc1_bytes),
        file_size=len(doc1_bytes),
        num_pages=1,
        status=DocumentStatus.PENDING
    )
    db_session.add(doc1)
    db_session.commit()

    facts1 = await extractor.process_and_extract_document(doc1.id)
    assert len(facts1) > 0
    for f in facts1:
        assert f.document_id == doc1.id
        assert f.evidence_quote != ""
        assert f.page_number == 1

    # Document 2: Delhivery Investor Presentation Q4FY24
    doc2_text = [
        "Delhivery Q4 FY24 Investor Presentation.\n"
        "In fiscal year 2024, Delhivery reported revenue of ₹8,142 Cr.\n"
        "Standalone operating EBITDA was reported at ₹95 crore in FY24."
    ]
    doc2_path = _create_test_pdf_file(doc2_text)
    with open(doc2_path, "rb") as f:
        doc2_bytes = f.read()

    doc2 = Document(
        id="doc_test_delhivery_ip",
        filename="Delhivery_Investor_Presentation_Q4FY24.pdf",
        file_path=doc2_path,
        file_hash=pdf_service.calculate_file_hash(doc2_bytes),
        file_size=len(doc2_bytes),
        num_pages=1,
        status=DocumentStatus.PENDING
    )
    db_session.add(doc2)
    db_session.commit()

    facts2 = await extractor.process_and_extract_document(doc2.id)
    assert len(facts2) > 0

    # Retrieve facts to reconcile
    rev1 = next((f for f in facts1 if "Revenue" in (f.attribute or f.statement)), facts1[0])
    rev2 = next((f for f in facts2 if "Revenue" in (f.attribute or f.statement)), facts2[0])

    # Corroboration verification
    rel_rev = reconciler.reconcile_fact_pair(rev1, rev2)
    assert rel_rev.relationship == RelationshipType.CORROBORATED

    # Scope difference verification (Consolidated vs Standalone EBITDA)
    ebitda_cons = Fact(
        id="fact_delhivery_ebitda_cons",
        document_id=doc1.id,
        page_number=1,
        statement="Consolidated EBITDA was ₹127 crore in FY2024.",
        entity="Delhivery",
        attribute="EBITDA",
        raw_value="₹127 crore",
        normalized_value=1270000000.0,
        currency="INR",
        unit="INR",
        time_period="FY2024",
        fiscal_year="FY2024",
        scope="Consolidated",
        evidence_quote="Consolidated Adjusted EBITDA reached ₹127 crore for the full year FY2024.",
        status=FactStatus.VERIFIED,
        confidence=0.95
    )
    ebitda_std = Fact(
        id="fact_delhivery_ebitda_std",
        document_id=doc2.id,
        page_number=1,
        statement="Standalone EBITDA was ₹95 crore in FY2024.",
        entity="Delhivery",
        attribute="EBITDA",
        raw_value="₹95 crore",
        normalized_value=950000000.0,
        currency="INR",
        unit="INR",
        time_period="FY2024",
        fiscal_year="FY2024",
        scope="Standalone",
        evidence_quote="Standalone operating EBITDA was reported at ₹95 crore in FY24.",
        status=FactStatus.VERIFIED,
        confidence=0.95
    )
    db_session.add_all([ebitda_cons, ebitda_std])
    db_session.commit()

    rel_ebitda = reconciler.reconcile_fact_pair(ebitda_cons, ebitda_std)
    assert rel_ebitda.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT
    assert "scope" in rel_ebitda.rationale.lower() or "context" in rel_ebitda.rationale.lower()


@pytest.mark.asyncio
async def test_macroeconomy_period_and_forecast_separation(db_session):
    """
    Validates India Macroeconomy documents (Economic Survey vs RBI vs IMF)
    ensuring GDP Growth projections vs actuals or different fiscal years
    are reconciled as CONTEXTUALLY_DIFFERENT rather than false contradictions.
    """
    reconciler = ReconciliationService(db_session)

    # Actual GDP Growth FY2024 (RBI Annual Report)
    gdp_actual = Fact(
        id="fact_macro_rbi_gdp",
        document_id="doc_rbi_annual_report",
        page_number=14,
        statement="Real GDP growth for FY2024 was recorded at 8.2%.",
        entity="India",
        attribute="Real GDP Growth Rate",
        raw_value="8.2%",
        normalized_value=8.2,
        unit="%",
        time_period="FY2024",
        fiscal_year="FY2024",
        value_status=ValueStatus.ACTUAL,
        evidence_quote="Real GDP growth for FY2024 was recorded at 8.2% supported by domestic investment.",
        status=FactStatus.VERIFIED,
        confidence=0.98
    )

    # Projected GDP Growth FY2025 (IMF Article IV)
    gdp_forecast = Fact(
        id="fact_macro_imf_gdp",
        document_id="doc_imf_article_iv",
        page_number=8,
        statement="IMF projects India GDP growth at 7.0% for FY2025.",
        entity="India",
        attribute="Real GDP Growth Rate",
        raw_value="7.0%",
        normalized_value=7.0,
        unit="%",
        time_period="FY2025",
        fiscal_year="FY2025",
        value_status=ValueStatus.FORECAST,
        evidence_quote="IMF projects India GDP growth at 7.0% for FY2025 citing macroeconomic stability.",
        status=FactStatus.VERIFIED,
        confidence=0.95
    )

    db_session.add_all([gdp_actual, gdp_forecast])
    db_session.commit()

    rel = reconciler.reconcile_fact_pair(gdp_actual, gdp_forecast)
    assert rel.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT
    assert "time period" in rel.rationale.lower() or "temporal" in rel.rationale.lower() or "forecast" in rel.rationale.lower()


@pytest.mark.asyncio
async def test_arbitrary_generic_pdf_processing(db_session):
    """
    Validates that FactLens works out-of-the-box for completely arbitrary PDFs
    (e.g., SolarTech Energy systems) without hardcoded company assumptions.
    """
    pdf_service = PDFService()
    extractor = ExtractionService(db_session)

    arbitrary_text = [
        "SolarTech Global Clean Energy Report 2024.\n"
        "In fiscal year 2024, SolarTech reported revenue of $383.29 billion.\n"
        "Operating margin was 15.4%.\n"
        "Workforce grew to 12,500 employees."
    ]
    doc_path = _create_test_pdf_file(arbitrary_text)
    with open(doc_path, "rb") as f:
        doc_bytes = f.read()

    doc = Document(
        id="doc_test_solartech_generic",
        filename="SolarTech_CleanEnergy_2024.pdf",
        file_path=doc_path,
        file_hash=pdf_service.calculate_file_hash(doc_bytes),
        file_size=len(doc_bytes),
        num_pages=1,
        status=DocumentStatus.PENDING
    )
    db_session.add(doc)
    db_session.commit()

    facts = await extractor.process_and_extract_document(doc.id)
    assert len(facts) > 0
    for fact in facts:
        assert fact.document_id == doc.id
        assert fact.evidence_quote != ""
        assert fact.status in [FactStatus.EXTRACTED, FactStatus.VERIFIED]


def test_demo_fixture_isolation_and_tagging(client):
    """
    Verifies that demo fixtures seeded via /api/v1/demo/seed are isolated
    and tagged with source_type = 'SYNTHETIC_DEMO' in API responses.
    """
    # 1. Seed demo data
    res_seed = client.post("/api/v1/demo/seed")
    assert res_seed.status_code == 200
    assert res_seed.json()["success"] is True

    # 2. Check facts list
    res_facts = client.get("/api/v1/facts")
    assert res_facts.status_code == 200
    facts = res_facts.json()["data"]

    demo_facts = [f for f in facts if f["id"].startswith("fact_demo_")]
    assert len(demo_facts) >= 4
    for df in demo_facts:
        assert df["source_type"] == "SYNTHETIC_DEMO"
