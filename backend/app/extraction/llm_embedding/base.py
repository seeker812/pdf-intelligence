from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def embed_query(self, query: str) -> list[float]: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...
