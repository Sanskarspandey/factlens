"""Unit tests for fact extraction, evidence grounding verification, and failure tracking."""
import pytest
import tempfile
import os
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentStatus
from app.models.fact import Fact, FactStatus
from app.models.audit import ExtractionFailure
from app.services.extraction_service import ExtractionService
from app.services.pdf_service import PDFService
from app.schemas.fact import ExtractedFactItem, PageExtractionResult
from app.services.llm.base import BaseLLMProvider


class MockHallucinatingLLMProvider(BaseLLMProvider):
    """LLM provider that intentionally returns one grounded fact and one hallucinated fact."""
    async def generate_text(self, prompt: str, system_prompt=None) -> str:
        return ""

    async def generate_structured(self, prompt: str, response_schema, system_prompt=None):
        return PageExtractionResult(
            page_number=1,
            facts=[
                # Fact 1: Real Grounded Quote from Page 1
                ExtractedFactItem(
                    statement="Acme Corporation reported revenue of $383.29 billion in FY2023.",
                    entity="Acme Corporation",
                    attribute="Revenue",
                    raw_value="$383.29 billion",
                    evidence_quote="In fiscal year 2023, Acme Corporation reported total revenue of $383.29 billion.",
                    time_period_raw="FY2023",
                    confidence=0.98,
                    is_uncertain=False
                ),
                # Fact 2: Hallucinated / Fabricated Quote (NOT in text)
                ExtractedFactItem(
                    statement="Acme Corporation announced acquisition of BetaTech for $50 billion.",
                    entity="Acme Corporation",
                    attribute="Acquisition",
                    raw_value="$50 billion",
                    evidence_quote="Acme Corporation has entered a definitive agreement to acquire BetaTech for $50 billion.",
                    time_period_raw="2024",
                    confidence=0.90,
                    is_uncertain=False
                )
            ]
        )


@pytest.mark.asyncio
async def test_grounding_and_evidence_failure_handling(db_session: Session, sample_pdf_bytes):
    # Save PDF to temporary file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(sample_pdf_bytes)
        pdf_path = f.name

    try:
        pdf_service = PDFService()
        file_hash = pdf_service.calculate_file_hash(sample_pdf_bytes)

        # Create document in DB
        doc = Document(
            id="doc_test_grounding",
            filename="sample_financial.pdf",
            file_path=pdf_path,
            file_hash=file_hash,
            file_size=len(sample_pdf_bytes),
            num_pages=2,
            status=DocumentStatus.PENDING
        )
        db_session.add(doc)
        db_session.commit()

        # Instantiate extraction service with the hallucinating provider
        extractor = ExtractionService(db_session)
        extractor.llm_provider = MockHallucinatingLLMProvider()

        facts = await extractor.process_and_extract_document(doc.id)

        assert len(facts) >= 2

        # 1. Grounded fact verification
        grounded_fact = next(f for f in facts if f.entity == "Acme Corporation" and f.attribute == "Revenue")
        assert grounded_fact.status == FactStatus.EXTRACTED
        assert grounded_fact.confidence > 0.8
        assert grounded_fact.bounding_box is not None
        assert grounded_fact.normalized_value == 383290000000.0
        assert grounded_fact.currency == "USD"
        assert grounded_fact.time_period == "FY2023"

        # 2. Ungrounded / Hallucinated quote verification
        hallucinated_fact = next(f for f in facts if f.attribute == "Acquisition")
        assert hallucinated_fact.status == FactStatus.UNCERTAIN
        assert hallucinated_fact.confidence <= 0.3
        assert hallucinated_fact.bounding_box is None
        assert "Grounding failure" in hallucinated_fact.uncertainty_notes

        # 3. Check that an ExtractionFailure record was created
        failures = db_session.query(ExtractionFailure).filter(ExtractionFailure.document_id == doc.id).all()
        assert len(failures) >= 1
        fail = failures[0]
        assert fail.stage == "GROUNDING_VERIFICATION"
        assert fail.error_type == "EVIDENCE_QUOTE_NOT_FOUND"
        assert "BetaTech" in fail.raw_content

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
