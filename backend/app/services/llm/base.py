"""Abstract base class for configurable LLM providers."""
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Dict, Any, List
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Generic interface for LLM providers (Gemini, OpenAI, Anthropic, Ollama, Mock)."""

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates raw text response for a given prompt."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None
    ) -> T:
        """Generates a structured Pydantic object using schema enforcement/JSON mode."""
        pass
