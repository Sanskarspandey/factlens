"""Factory for initializing configured LLM provider with fallback handling."""
from app.core.config import settings
from app.core.exceptions import LLMProviderError
from app.core.logging import logger
from app.services.llm.base import BaseLLMProvider
from app.services.llm.mock_provider import MockLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    """
    Returns the LLM provider instance based on application configuration.
    If real provider credentials are not present, gracefully falls back to MockLLMProvider.
    """
    provider_name = settings.LLM_PROVIDER.lower().strip()

    if provider_name == "mock":
        return MockLLMProvider()

    if provider_name == "gemini":
        if not settings.LLM_API_KEY or "your_gemini_api_key" in settings.LLM_API_KEY:
            logger.warning(
                "Gemini API key not configured or contains placeholder. "
                "Falling back to deterministic MockLLMProvider for offline execution."
            )
            return MockLLMProvider()
        try:
            from app.services.llm.gemini_provider import GeminiProvider
            return GeminiProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize GeminiProvider ({e}). Falling back to MockLLMProvider.")
            return MockLLMProvider()

    if provider_name == "openai":
        if not settings.LLM_API_KEY or "your_openai_api_key" in settings.LLM_API_KEY:
            logger.warning(
                "OpenAI API key not configured. Falling back to deterministic MockLLMProvider."
            )
            return MockLLMProvider()
        try:
            from app.services.llm.openai_provider import OpenAIProvider
            return OpenAIProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAIProvider ({e}). Falling back to MockLLMProvider.")
            return MockLLMProvider()

    logger.warning(f"Unrecognized LLM provider '{settings.LLM_PROVIDER}'. Using MockLLMProvider.")
    return MockLLMProvider()
