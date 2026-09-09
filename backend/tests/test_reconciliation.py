"""Unit and integration tests for Phase 3 reconciliation, corroboration, contradiction, and context differences."""
import pytest
from pydantic import ValidationError
from app.models.fact import Fact, FactStatus, ValueStatus
from app.models.document import Document, DocumentStatus
from app.models.comparison import RelationshipType, FactRelationship
from app.schemas.comparison import ReconciliationLLMResult
from app.services.reconciliation_service import (
    ReconciliationService,
    ValueComparisonEngine,
    ContextComparisonEngine
)


def create_mock_fact(
    fact_id: str,
    doc_id: str,
    statement: str,
    entity: str = "Company X",
    attribute: str = "Revenue",
    raw_value: str = "₹100 crore",
    normalized_value: float = 1000000000.0,
    normalized_value_str: str = "₹100.00 Cr",
    unit: str = "INR",
    currency: str = "INR",
    time_period: str = "FY2024",
    fiscal_year: str = "FY2024",
    quarter: str = None,
    scope: str = "Consolidated",
    geography: str = "India",
    definition: str = "GAAP",
    value_status: ValueStatus = ValueStatus.ACTUAL,
    evidence_quote: str = "Company X generated revenue of ₹100 crore in FY2024.",
    page_number: int = 1,
    status: FactStatus = FactStatus.EXTRACTED
) -> Fact:
    return Fact(
        id=fact_id,
        document_id=doc_id,
        statement=statement,
        entity=entity,
        attribute=attribute,
        raw_value=raw_value,
        normalized_value=normalized_value,
        normalized_value_str=normalized_value_str,
        unit=unit,
        currency=currency,
        time_period=time_period,
        fiscal_year=fiscal_year,
        quarter=quarter,
        scope=scope,
        geography=geography,
        definition=definition,
        value_status=value_status,
        evidence_quote=evidence_quote,
        page_number=page_number,
        status=status,
        confidence=0.95
    )


def test_demo_case_1_corroboration(db_session):
    """
    CASE 1 — CORROBORATION:
    ₹100 crore vs ₹1 billion in FY2024, Consolidated.
    Both normalize to 1,000,000,000 INR.
    """
    doc_a = Document(id="doc_demo_a", filename="annual_report_a.pdf", file_path="fake_a.pdf", file_hash="hash_a", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    doc_b = Document(id="doc_demo_b", filename="investor_presentation_b.pdf", file_path="fake_b.pdf", file_hash="hash_b", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    db_session.add_all([doc_a, doc_b])
    db_session.commit()

    fact_a = create_mock_fact(
        fact_id="fact_demo_1a",
        doc_id="doc_demo_a",
        statement="Company X recorded revenue of ₹100 crore in FY2024.",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        normalized_value_str="₹100.00 Cr",
        evidence_quote="Company X recorded revenue of ₹100 crore in FY2024."
    )
    fact_b = create_mock_fact(
        fact_id="fact_demo_1b",
        doc_id="doc_demo_b",
        statement="Total revenue amounted to ₹1 billion during FY2024.",
        raw_value="₹1 billion",
        normalized_value=1000000000.0,
        normalized_value_str="₹1.00 billion",
        evidence_quote="Total revenue amounted to ₹1 billion during FY2024."
    )
    db_session.add_all([fact_a, fact_b])
    db_session.commit()

    reconciler = ReconciliationService(db_session)
    rel = reconciler.reconcile_fact_pair(fact_a, fact_b)

    assert rel.relationship == RelationshipType.CORROBORATED
    assert rel.confidence >= 0.95
    assert "Corroborated" in rel.rationale
    assert rel.value_comparison["within_tolerance"] is True
    assert rel.value_comparison["relative_difference"] == 0.0
    assert rel.supporting_evidence["source_evidence"]["fact_id"] == "fact_demo_1a"
    assert rel.supporting_evidence["candidate_evidence"]["fact_id"] == "fact_demo_1b"


def test_demo_case_2_genuine_contradiction(db_session):
    """
    CASE 2 — GENUINE CONTRADICTION:
    Company X revenue FY2024 = ₹100 crore vs ₹150 crore (Consolidated).
    Identical context, materially different values (50% difference).
    """
    doc_a = Document(id="doc_demo_2a", filename="report_2a.pdf", file_path="fake_2a.pdf", file_hash="hash_2a", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    doc_b = Document(id="doc_demo_2b", filename="report_2b.pdf", file_path="fake_2b.pdf", file_hash="hash_2b", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    db_session.add_all([doc_a, doc_b])
    db_session.commit()

    fact_a = create_mock_fact(
        fact_id="fact_demo_2a",
        doc_id="doc_demo_2a",
        statement="Company X revenue in FY2024 was ₹100 crore.",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        normalized_value_str="₹100.00 Cr"
    )
    fact_b = create_mock_fact(
        fact_id="fact_demo_2b",
        doc_id="doc_demo_2b",
        statement="Company X revenue in FY2024 reached ₹150 crore.",
        raw_value="₹150 crore",
        normalized_value=1500000000.0,
        normalized_value_str="₹150.00 Cr"
    )
    db_session.add_all([fact_a, fact_b])
    db_session.commit()

    reconciler = ReconciliationService(db_session)
    rel = reconciler.reconcile_fact_pair(fact_a, fact_b)

    assert rel.relationship == RelationshipType.CONTRADICTED
    assert "Contradicted" in rel.rationale
    assert rel.value_comparison["within_tolerance"] is False
    assert rel.value_comparison["absolute_difference"] == 500000000.0
    assert abs(rel.value_comparison["percentage_difference"] - 33.3333) < 0.1 or rel.value_comparison["percentage_difference"] == 50.0 or rel.value_comparison["relative_difference"] > 0.05
    assert "500,000,000" in rel.rationale or "Absolute difference" in rel.rationale


def test_demo_case_3_contextual_difference_scope_and_temporal(db_session):
    """
    CASE 3 — APPARENT CONTRADICTION EXPLAINED BY CONTEXT:
    1. Consolidated (₹100 Cr) vs Standalone (₹90 Cr) -> CONTEXTUALLY_DIFFERENT
    2. FY2023 (₹100 Cr) vs FY2024 (₹150 Cr) -> CONTEXTUALLY_DIFFERENT
    3. ACTUAL vs FORECAST -> CONTEXTUALLY_DIFFERENT
    """
    doc_a = Document(id="doc_demo_3a", filename="report_3a.pdf", file_path="fake_3a.pdf", file_hash="hash_3a", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    doc_b = Document(id="doc_demo_3b", filename="report_3b.pdf", file_path="fake_3b.pdf", file_hash="hash_3b", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    db_session.add_all([doc_a, doc_b])
    db_session.commit()

    # 1. Scope Difference
    fact_cons = create_mock_fact(
        fact_id="fact_cons",
        doc_id="doc_demo_3a",
        statement="Consolidated revenue was ₹100 crore in FY2024.",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        scope="Consolidated"
    )
    fact_stand = create_mock_fact(
        fact_id="fact_stand",
        doc_id="doc_demo_3b",
        statement="Standalone revenue stood at ₹90 crore in FY2024.",
        raw_value="₹90 crore",
        normalized_value=900000000.0,
        scope="Standalone"
    )
    db_session.add_all([fact_cons, fact_stand])
    db_session.commit()

    reconciler = ReconciliationService(db_session)
    rel_scope = reconciler.reconcile_fact_pair(fact_cons, fact_stand)
    assert rel_scope.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT
    assert "scope" in rel_scope.rationale.lower()
    assert rel_scope.context_comparison["dimension_differences"]["scope"] == "Consolidated vs Standalone"

    # 2. Temporal Difference (FY2023 vs FY2024)
    fact_fy23 = create_mock_fact(
        fact_id="fact_fy23",
        doc_id="doc_demo_3a",
        statement="Revenue was ₹100 crore in FY2023.",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        time_period="FY2023",
        fiscal_year="FY2023"
    )
    fact_fy24 = create_mock_fact(
        fact_id="fact_fy24",
        doc_id="doc_demo_3b",
        statement="Revenue was ₹150 crore in FY2024.",
        raw_value="₹150 crore",
        normalized_value=1500000000.0,
        time_period="FY2024",
        fiscal_year="FY2024"
    )
    db_session.add_all([fact_fy23, fact_fy24])
    db_session.commit()

    rel_time = reconciler.reconcile_fact_pair(fact_fy23, fact_fy24)
    assert rel_time.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT
    assert "fiscal" in rel_time.rationale.lower() or "period" in rel_time.rationale.lower()

    # 3. Value Status Difference (ACTUAL vs FORECAST)
    fact_actual = create_mock_fact(
        fact_id="fact_act",
        doc_id="doc_demo_3a",
        statement="Actual revenue was ₹100 crore.",
        raw_value="₹100 crore",
        normalized_value=1000000000.0,
        value_status=ValueStatus.ACTUAL
    )
    fact_forecast = create_mock_fact(
        fact_id="fact_fore",
        doc_id="doc_demo_3b",
        statement="Forecasted revenue is ₹120 crore.",
        raw_value="₹120 crore",
        normalized_value=1200000000.0,
        value_status=ValueStatus.FORECAST
    )
    db_session.add_all([fact_actual, fact_forecast])
    db_session.commit()

    rel_status = reconciler.reconcile_fact_pair(fact_actual, fact_forecast)
    assert rel_status.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT
    assert "basis" in rel_status.rationale.lower() or "status" in rel_status.rationale.lower() or "reporting" in rel_status.rationale.lower()


def test_demo_case_4_uncertainty_and_failure_preservation(db_session):
    """
    CASE 4 — EXTRACTION / REASONING FAILURE:
    1. Missing evidence quote -> UNCERTAIN
    2. Missing normalized value -> UNCERTAIN
    3. Ambiguous metric -> UNCERTAIN
    """
    doc = Document(id="doc_demo_4", filename="report_4.pdf", file_path="fake_4.pdf", file_hash="hash_4", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    db_session.add(doc)
    db_session.commit()

    # 1. Missing evidence quote
    fact_good = create_mock_fact("f_good", "doc_demo_4", "Revenue is 100", evidence_quote="Revenue is 100")
    fact_no_quote = create_mock_fact("f_no_quote", "doc_demo_4", "Revenue is 100", evidence_quote="")
    db_session.add_all([fact_good, fact_no_quote])
    db_session.commit()

    reconciler = ReconciliationService(db_session)
    rel_quote = reconciler.reconcile_fact_pair(fact_good, fact_no_quote)
    assert rel_quote.relationship == RelationshipType.UNCERTAIN
    assert "evidence" in rel_quote.rationale.lower()
    assert rel_quote.uncertainty_notes is not None

    # 2. Missing normalized value
    fact_no_norm = create_mock_fact("f_no_norm", "doc_demo_4", "Revenue is substantial", raw_value="substantial", normalized_value=None)
    db_session.add(fact_no_norm)
    db_session.commit()

    rel_norm = reconciler.reconcile_fact_pair(fact_good, fact_no_norm)
    assert rel_norm.relationship == RelationshipType.UNCERTAIN
    assert "normalized" in rel_norm.rationale.lower() or "unavailable" in rel_norm.rationale.lower()

    # 3. Ambiguous entity/metric
    fact_ambig = create_mock_fact("f_ambig", "doc_demo_4", "Amount is 100", entity=None, attribute=None)
    db_session.add(fact_ambig)
    db_session.commit()

    rel_ambig = reconciler.reconcile_fact_pair(fact_good, fact_ambig)
    assert rel_ambig.relationship == RelationshipType.UNCERTAIN
    assert "ambiguous" in rel_ambig.rationale.lower() or "metric" in rel_ambig.rationale.lower()


def test_numeric_tolerance_boundaries(db_session):
    """
    Tests numeric comparison tolerance boundaries:
    - 0.5% difference <= 1% tolerance -> CORROBORATED
    - 2.0% difference > 1% tolerance -> CONTRADICTED
    """
    doc = Document(id="doc_tol", filename="tol.pdf", file_path="fake_tol.pdf", file_hash="hash_tol", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    db_session.add(doc)
    db_session.commit()

    fact_base = create_mock_fact("f_base", "doc_tol", "Revenue is 100M", normalized_value=100000000.0)
    fact_close = create_mock_fact("f_close", "doc_tol", "Revenue is 100.5M", normalized_value=100500000.0)  # 0.5% diff
    fact_divergent = create_mock_fact("f_div", "doc_tol", "Revenue is 103M", normalized_value=103000000.0)  # 3.0% diff

    db_session.add_all([fact_base, fact_close, fact_divergent])
    db_session.commit()

    reconciler = ReconciliationService(db_session)

    # 0.5% difference within 1% tolerance
    rel_close = reconciler.reconcile_fact_pair(fact_base, fact_close)
    assert rel_close.relationship == RelationshipType.CORROBORATED
    assert rel_close.value_comparison["within_tolerance"] is True

    # 3.0% difference exceeds 1% tolerance
    rel_div = reconciler.reconcile_fact_pair(fact_base, fact_divergent)
    assert rel_div.relationship == RelationshipType.CONTRADICTED
    assert rel_div.value_comparison["within_tolerance"] is False


def test_currency_isolation_no_implicit_conversion(db_session):
    """₹100 and $100 must NOT be treated as equal numeric claims."""
    doc = Document(id="doc_curr", filename="curr.pdf", file_path="fake_curr.pdf", file_hash="hash_curr", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    db_session.add(doc)
    db_session.commit()

    fact_inr = create_mock_fact("f_inr", "doc_curr", "Revenue was ₹100", currency="INR", raw_value="₹100", normalized_value=100.0)
    fact_usd = create_mock_fact("f_usd", "doc_curr", "Revenue was $100", currency="USD", raw_value="$100", normalized_value=100.0)
    db_session.add_all([fact_inr, fact_usd])
    db_session.commit()

    reconciler = ReconciliationService(db_session)
    rel = reconciler.reconcile_fact_pair(fact_inr, fact_usd)

    assert rel.relationship == RelationshipType.CONTEXTUALLY_DIFFERENT
    assert "currency" in rel.rationale.lower() or "currencies" in rel.rationale.lower()


def test_reconciliation_idempotency(db_session):
    """Running reconciliation repeatedly on the same pair updates existing record cleanly without duplicates."""
    doc = Document(id="doc_idem", filename="idem.pdf", file_path="fake_idem.pdf", file_hash="hash_idem", file_size=100, num_pages=1, status=DocumentStatus.PROCESSED)
    db_session.add(doc)
    db_session.commit()

    fact_a = create_mock_fact("f_idem_a", "doc_idem", "Revenue was 100M", normalized_value=100000000.0)
    fact_b = create_mock_fact("f_idem_b", "doc_idem", "Revenue was 100M", normalized_value=100000000.0)
    db_session.add_all([fact_a, fact_b])
    db_session.commit()

    reconciler = ReconciliationService(db_session)
    rel1 = reconciler.reconcile_fact_pair(fact_a, fact_b)
    rel2 = reconciler.reconcile_fact_pair(fact_a, fact_b)

    assert rel1.id == rel2.id
    total_rels = db_session.query(FactRelationship).filter(FactRelationship.id == rel1.id).count()
    assert total_rels == 1


def test_llm_schema_validation():
    """Validates that ReconciliationLLMResult strictly validates allowed labels and rejects arbitrary ones."""
    # Valid output
    valid_res = ReconciliationLLMResult(
        relationship=RelationshipType.CORROBORATED,
        confidence=0.92,
        rationale="Both documents report ₹8,142 Cr in FY2024."
    )
    assert valid_res.relationship == RelationshipType.CORROBORATED

    # Invalid relationship label must raise ValidationError
    with pytest.raises(ValidationError):
        ReconciliationLLMResult(
            relationship="COMPLETELY_IDENTICAL",  # Invalid arbitrary label
            confidence=0.9,
            rationale="Fake"
        )
