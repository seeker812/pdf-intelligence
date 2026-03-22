import logging
from google import genai
from google.genai import types

from backend.app.extraction.llm_embedding.base import BaseEmbeddingProvider
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider(BaseEmbeddingProvider):

    def __init__(self, api_key: str, model: str) -> None:
        self._model_name = model
        self._client = genai.Client(api_key=api_key)
        logger.info("GeminiEmbeddingProvider initialised model=%s", model)

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self._client.models.embed_content(
            model=self._model_name,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",  # ✅ optimised for indexing
                output_dimensionality=settings.QDRANT_VECTOR_SIZE,
            ),
        )
        return [embedding.values for embedding in result.embeddings]

    def embed_query(self, query: str) -> list[float]:
        result = self._client.models.embed_content(
            model=self._model_name,
            contents=[query],
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",  # ✅ optimised for search
                output_dimensionality=settings.QDRANT_VECTOR_SIZE,
            ),
        )
        return result.embeddings[0].values
