from backend.app.extraction.llm_embedding.base import BaseEmbeddingProvider
from backend.app.core.config import settings


def create_embedding_provider() -> BaseEmbeddingProvider:
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        from backend.app.extraction.llm_embedding.providers.apenai_embedding_provider import (
            OpenAIEmbeddingProvider,
        )

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY required when LLM_PROVIDER=openai")
        return OpenAIEmbeddingProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL,
        )

    if provider == "gemini":
        from backend.app.extraction.llm_embedding.providers.gemini_embedding_provider import (
            GeminiEmbeddingProvider,
        )

        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY required when LLM_PROVIDER=gemini")
        return GeminiEmbeddingProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.EMBEDDING_MODEL,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER='{provider}'")
