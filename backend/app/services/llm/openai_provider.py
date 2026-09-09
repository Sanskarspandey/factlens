"""OpenAI LLM provider implementation."""
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from app.services.llm.base import BaseLLMProvider
from app.core.config import settings
from app.core.exceptions import LLMProviderError
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider with structured schema output."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            raise LLMProviderError("OpenAI API key is not configured.")

        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generate_text error: {e}")
            raise LLMProviderError(f"OpenAI API error: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None
    ) -> T:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=response_schema,
                temperature=settings.LLM_TEMPERATURE
            )
            parsed = completion.choices[0].message.parsed
            if not parsed:
                raise LLMProviderError("Failed to parse structured response from OpenAI.")
            return parsed
        except Exception as e:
            logger.error(f"OpenAI generate_structured error: {e}")
            raise LLMProviderError(f"OpenAI structured generation error: {str(e)}")
