"""LLM module initialization."""
from app.services.llm.base import BaseLLMProvider
from app.services.llm.factory import get_llm_provider
from app.services.llm.prompts import (
    FACT_EXTRACTION_SYSTEM_PROMPT,
    FACT_COMPARISON_SYSTEM_PROMPT
)

__all__ = [
    "BaseLLMProvider",
    "get_llm_provider",
    "FACT_EXTRACTION_SYSTEM_PROMPT",
    "FACT_COMPARISON_SYSTEM_PROMPT",
]
