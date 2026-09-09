"""Fact extraction service coordinating PDF parsing, LLM prompting, grounding validation, and semantic vector indexing."""
import uuid
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentPage, DocumentStatus
from app.models.fact import Fact, FactStatus, ValueStatus
from app.models.audit import ExtractionFailure
from app.schemas.fact import PageExtractionResult, ExtractedFactItem
from app.services.pdf_service import PDFService
from app.services.normalization_service import NormalizationService
from app.services.llm.factory import get_llm_provider
from app.services.llm.prompts import FACT_EXTRACTION_SYSTEM_PROMPT
from app.services.vector.embeddings import embedding_service, build_fact_semantic_representation
from app.services.vector.chroma_store import vector_store
from app.core.exceptions import DocumentNotFoundError, DocumentProcessingError
from app.core.logging import logger


class ExtractionService:
    """Orchestrates page-by-page extraction, strict grounding validation, normalization, and vector indexing."""

    def __init__(self, db: Session):
        self.db = db
        self.pdf_service = PDFService()
        self.normalizer = NormalizationService()
        self.llm_provider = get_llm_provider()
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def _normalize_whitespace(self, text: str) -> str:
        """Collapses all whitespace/newlines into single spaces for robust string matching."""
        return " ".join(text.split())

    def _verify_evidence_quote(self, quote: str, page_text: str) -> bool:
        """
        Verifies whether an evidence quote exists verbatim in the page text.
        Tolerates newline differences and minor punctuation whitespace.
        """
        if not quote or not quote.strip() or not page_text:
            return False

        clean_quote = quote.strip()
        
        # 1. Exact substring check
        if clean_quote in page_text:
            return True

        # 2. Whitespace-collapsed check
        norm_quote = self._normalize_whitespace(clean_quote).lower()
        norm_page = self._normalize_whitespace(page_text).lower()
        if norm_quote in norm_page:
            return True

        # 3. Punctuation-stripped check (for subtle layout differences)
        sub_quote = re.sub(r"[^\w\s]", "", norm_quote)
        sub_page = re.sub(r"[^\w\s]", "", norm_page)
        if len(sub_quote) > 15 and sub_quote in sub_page:
            return True

        return False

    async def process_and_extract_document(self, document_id: str) -> List[Fact]:
        """
        Processes an uploaded PDF end-to-end:
        1. Extract pages using PyMuPDF and store DocumentPage records.
        2. Run LLM structured extraction for each page.
        3. Strictly verify evidence grounding.
        4. Normalize values, units, currencies, and time periods.
        5. Persist facts and index them into vector database.
        6. Record extraction failures for ungrounded or ambiguous claims.
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        document.status = DocumentStatus.PROCESSING
        self.db.commit()

        created_facts: List[Fact] = []

        try:
            # Step 1: Extract Pages with PyMuPDF
            pages_data = self.pdf_service.extract_pages(document.file_path)
            document.num_pages = len(pages_data)

            # Store / update DocumentPage records
            existing_pages = {p.page_number: p for p in document.pages}
            db_pages_map: Dict[int, DocumentPage] = {}

            for pdata in pages_data:
                pnum = pdata["page_number"]
                if pnum in existing_pages:
                    db_page = existing_pages[pnum]
                    db_page.raw_text = pdata["raw_text"]
                    db_page.layout_blocks = pdata["layout_blocks"]
                    db_page.page_hash = pdata["page_hash"]
                else:
                    db_page = DocumentPage(
                        id=f"page_{uuid.uuid4().hex[:12]}",
                        document_id=document.id,
                        page_number=pnum,
                        raw_text=pdata["raw_text"],
                        layout_blocks=pdata["layout_blocks"],
                        page_hash=pdata["page_hash"]
                    )
                    self.db.add(db_page)
                db_pages_map[pnum] = db_page

            self.db.commit()

            # Step 2: Extract Facts Page-by-Page
            for page_num, db_page in db_pages_map.items():
                if not db_page.raw_text.strip():
                    continue

                prompt = (
                    f"Document: {document.filename} (Page {page_num})\n\n"
                    f"Page Text:\n{db_page.raw_text}\n---\n"
                    f"Extract all factual claims, metrics, and figures following strict grounding rules."
                )

                try:
                    extraction_result: PageExtractionResult = await self.llm_provider.generate_structured(
                        prompt=prompt,
                        response_schema=PageExtractionResult,
                        system_prompt=FACT_EXTRACTION_SYSTEM_PROMPT
                    )
                except Exception as e:
                    logger.error(f"LLM extraction error on page {page_num}: {e}")
                    failure = ExtractionFailure(
                        id=f"fail_{uuid.uuid4().hex[:12]}",
                        document_id=document.id,
                        page_number=page_num,
                        stage="LLM_EXTRACTION",
                        error_type="LLM_PARSING_ERROR",
                        error_message=str(e),
                        raw_content=db_page.raw_text[:500]
                    )
                    self.db.add(failure)
                    continue

                # Step 3 & 4: Grounding Verification and Normalization
                for item in extraction_result.facts:
                    is_grounded = self._verify_evidence_quote(item.evidence_quote, db_page.raw_text)

                    # Calculate visual bounding box if grounded
                    bbox = None
                    if is_grounded:
                        bbox = self.pdf_service.find_quote_bounding_box(
                            document.file_path, page_num, item.evidence_quote
                        )

                    # Normalize values and dates
                    norm_val = self.normalizer.normalize_value(item.raw_value)
                    norm_period = self.normalizer.normalize_time_period(item.time_period_raw)

                    # Context fields
                    fiscal_year = item.fiscal_year or norm_period.fiscal_year
                    quarter = item.quarter or norm_period.quarter
                    time_period_canonical = norm_period.standard_period or item.time_period_raw

                    # Determine fact status and uncertainty
                    if is_grounded:
                        fact_status = FactStatus.EXTRACTED
                        confidence = item.confidence
                        uncertainty_notes = item.uncertainty_notes if item.is_uncertain else None
                    else:
                        # Grounding failure: LLM returned quote not in text
                        fact_status = FactStatus.UNCERTAIN
                        confidence = min(0.3, item.confidence)
                        uncertainty_notes = (
                            f"Grounding failure: Evidence quote could not be located in page {page_num} text. "
                            f"{item.uncertainty_notes or ''}".strip()
                        )

                        failure = ExtractionFailure(
                            id=f"fail_{uuid.uuid4().hex[:12]}",
                            document_id=document.id,
                            page_number=page_num,
                            stage="GROUNDING_VERIFICATION",
                            error_type="EVIDENCE_QUOTE_NOT_FOUND",
                            error_message=f"Evidence quote was not found in page {page_num} text.",
                            raw_content=item.evidence_quote,
                            context_data={
                                "statement": item.statement,
                                "entity": item.entity,
                                "attribute": item.attribute,
                                "raw_value": item.raw_value
                            }
                        )
                        self.db.add(failure)

                    fact_id = f"fact_{uuid.uuid4().hex[:12]}"
                    fact = Fact(
                        id=fact_id,
                        document_id=document.id,
                        page_id=db_page.id,
                        page_number=page_num,
                        statement=item.statement,
                        entity=item.entity,
                        attribute=item.attribute,
                        raw_value=item.raw_value,
                        normalized_value=norm_val.numeric_value,
                        normalized_value_str=norm_val.formatted_value,
                        unit=norm_val.unit,
                        currency=norm_val.currency,
                        time_period=time_period_canonical,
                        fiscal_year=fiscal_year,
                        quarter=quarter,
                        geography=item.geography,
                        scope=item.scope,
                        definition=item.definition,
                        source_section=item.source_section,
                        value_status=item.value_status,
                        evidence_quote=item.evidence_quote,
                        bounding_box=bbox,
                        confidence=confidence,
                        status=fact_status,
                        uncertainty_notes=uncertainty_notes,
                        indexing_status="PENDING"
                    )

                    self.db.add(fact)
                    created_facts.append(fact)

            self.db.commit()

            # Step 5: Index Extracted Facts in Vector Database
            for f in created_facts:
                try:
                    sem_text = build_fact_semantic_representation(f)
                    emb = self.embedding_service.encode_text(sem_text)
                    meta = {
                        "fact_id": f.id,
                        "document_id": f.document_id,
                        "entity": f.entity or "",
                        "attribute": f.attribute or "",
                        "time_period": f.time_period or "",
                        "fiscal_year": f.fiscal_year or "",
                        "quarter": f.quarter or "",
                        "geography": f.geography or "",
                        "currency": f.currency or "",
                        "unit": f.unit or "",
                        "status": f.status.value if f.status else ""
                    }
                    self.vector_store.add_facts([{
                        "fact_id": f.id,
                        "embedding": emb,
                        "metadata": meta,
                        "document": sem_text
                    }])
                    f.embedding_id = f.id
                    f.indexing_status = "INDEXED"
                except Exception as e:
                    logger.error(f"Vector indexing failed for fact {f.id}: {e}")
                    f.indexing_status = "FAILED"
                    failure = ExtractionFailure(
                        id=f"fail_{uuid.uuid4().hex[:12]}",
                        document_id=document.id,
                        page_number=f.page_number,
                        stage="EMBEDDING",
                        error_type="INDEXING_FAILED",
                        error_message=f"Vector embedding indexing failed: {str(e)}",
                        raw_content=f.statement
                    )
                    self.db.add(failure)

            document.status = DocumentStatus.PROCESSED
            document.error_message = None
            self.db.commit()
            return created_facts

        except Exception as e:
            self.db.rollback()
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            self.db.commit()
            logger.error(f"Error processing document {document_id}: {e}")
            raise DocumentProcessingError(f"Processing failed: {str(e)}")
