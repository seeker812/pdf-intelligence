from langchain_openai import OpenAIEmbeddings
from backend.app.extraction.llm_embedding.base import BaseEmbeddingProvider


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):

    def __init__(self, api_key: str, model: str) -> None:
        self._model_name = model
        self._model = OpenAIEmbeddings(
            model=model,
        )

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.embed_documents(texts)

    def embed_query(self, query: str) -> list[float]:
        return self._model.embed_query(query)
