import logging

from backend.app.core.config import settings
from backend.app.extraction.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

_PROVIDERS = ("openai", "gemini")


def create_llm_provider() -> BaseLLMProvider:

    provider = settings.LLM_PROVIDER.lower()
    logger.info("Creating LLM provider=%s model=%s", provider, settings.LLM_MODEL)

    if provider == "openai":
        from backend.app.extraction.llm.providers.openai_provider import OpenAIProvider

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )

    if provider == "gemini":
        from backend.app.extraction.llm.providers.gemini_provider import GeminiProvider

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")

        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER='{provider}'. Supported: {_PROVIDERS}")
