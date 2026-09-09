"""Deterministic Mock LLM provider for grounded fact extraction without external API calls."""
import re
from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from app.services.llm.base import BaseLLMProvider
from app.schemas.fact import ExtractedFactItem, PageExtractionResult
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic rule-based mock LLM provider.
    Scans the provided document page text for sentences containing numerical metrics,
    financial figures, currencies, or dates, and returns strictly grounded ExtractedFactItems
    with exact verbatim evidence quotes from the actual page text.
    """

    def __init__(self):
        logger.info("Initialized MockLLMProvider (deterministic offline engine).")

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Mock LLM text response."

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None
    ) -> T:
        """
        Parses the prompt to extract facts grounded directly from the page text.
        """
        # If the requested schema is PageExtractionResult
        if response_schema == PageExtractionResult or issubclass(response_schema, PageExtractionResult):
            facts = self._extract_grounded_facts_from_prompt(prompt)
            return PageExtractionResult(page_number=1, facts=facts, parsing_issues=[])  # type: ignore

        # Fallback empty model instantiation if another schema is requested
        try:
            return response_schema()
        except Exception:
            raise NotImplementedError(f"MockProvider cannot dynamically instantiate {response_schema}")

    def _extract_grounded_facts_from_prompt(self, prompt: str) -> List[ExtractedFactItem]:
        """
        Extracts candidate facts by segmenting sentences in the page text that have numbers or key financial terms.
        """
        # Extract the page text section from the prompt
        page_text = prompt
        if "Page Text:" in prompt:
            page_text = prompt.split("Page Text:")[1].split("---")[0].strip()

        if not page_text:
            return []

        # Split into sentences (by period, newline, or semicolon)
        raw_sentences = [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", page_text) if s.strip()]
        extracted_facts: List[ExtractedFactItem] = []

        # Patterns for detecting factual sentences
        metric_pattern = re.compile(
            r"(\$|₹|€|£|\bUSD\b|\bINR\b|\bEUR\b|\bRs\.?\b|\%|\bcr\b|\bcrore\b|\blakh\b|\bbillion\b|\bmillion\b|\bthousand\b|\d{2,4}\b)",
            re.IGNORECASE
        )
        
        # Value extraction pattern
        value_pattern = re.compile(
            r"([$₹€£]?\s*[-+]?\s*\d[\d,]*(?:\.\d+)?\s*(?:%|billion|million|thousand|crores?|crs?|lakhs?|cr|lac|USD|INR|EUR)?)",
            re.IGNORECASE
        )

        for sent in raw_sentences:
            if len(sent) < 15 or len(sent) > 300:
                continue

            if metric_pattern.search(sent):
                # Verbatim quote is the exact sentence or substring
                evidence_quote = sent.strip()

                # Extract potential value
                raw_val = None
                val_match = value_pattern.search(sent)
                if val_match:
                    raw_val = val_match.group(1).strip()

                # Extract potential entity (e.g., words starting with capital letters)
                entity = None
                cap_words = re.findall(r"\b[A-Z][a-zA-Z0-9_\-\&]+(?:\s+[A-Z][a-zA-Z0-9_\-\&]+)*\b", sent)
                for cw in cap_words:
                    if cw.lower() not in ["the", "this", "total", "net", "in", "during", "for", "as", "of", "and", "q1", "q2", "q3", "q4", "fy2023", "fy2024", "december", "january", "march", "june", "september"]:
                        entity = cw
                        break

                # Extract potential time period
                time_period_raw = None
                period_match = re.search(r"\b(FY\s*\d{2,4}|Q[1-4]\s*(?:20\d{2}|FY\d{2})?|20\d{2}|December \d{1,2}, \d{4})\b", sent, re.IGNORECASE)
                if period_match:
                    time_period_raw = period_match.group(1).strip()

                # Extract attribute/topic
                attribute = None
                for attr_candidate in ["Revenue", "Net Sales", "Net Income", "Operating Margin", "Operating Income", "EBITDA", "Total Assets", "Employees", "Profit", "Cash Flow"]:
                    if re.search(rf"\b{re.escape(attr_candidate)}\b", sent, re.IGNORECASE):
                        attribute = attr_candidate
                        break

                extracted_facts.append(
                    ExtractedFactItem(
                        statement=sent,
                        entity=entity,
                        attribute=attribute,
                        raw_value=raw_val,
                        evidence_quote=evidence_quote,
                        time_period_raw=time_period_raw,
                        confidence=0.95,
                        is_uncertain=False,
                        uncertainty_notes=None
                    )
                )

                if len(extracted_facts) >= 10:
                    break

        return extracted_facts
