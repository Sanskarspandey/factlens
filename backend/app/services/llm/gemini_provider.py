"""Google Gemini LLM provider implementation using google-genai SDK."""
from typing import Type, TypeVar, Optional
import json
from pydantic import BaseModel
from app.services.llm.base import BaseLLMProvider
from app.core.config import settings
from app.core.exceptions import LLMProviderError
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """Gemini API provider using google-genai SDK with structured JSON output support."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise LLMProviderError("Gemini API key is not configured.")

        from google import genai
        self.client = genai.Client(api_key=self.api_key)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            config = {}
            if system_prompt:
                config["system_instruction"] = system_prompt
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini generate_text error: {e}")
            raise LLMProviderError(f"Gemini API error: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None
    ) -> T:
        try:
            config = {
                "response_mime_type": "application/json",
                "response_schema": response_schema,
            }
            if system_prompt:
                config["system_instruction"] = system_prompt

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            raw_json = response.text
            if not raw_json:
                raise LLMProviderError("Empty response from Gemini structured output.")
            
            return response_schema.model_validate_json(raw_json)
        except Exception as e:
            logger.error(f"Gemini generate_structured error: {e}")
            raise LLMProviderError(f"Gemini structured generation error: {str(e)}")
