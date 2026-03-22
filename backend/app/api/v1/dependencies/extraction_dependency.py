from typing import TYPE_CHECKING

from backend.app.core.database import SessionLocal

if TYPE_CHECKING:
    from backend.app.api.v1.repository.chunk_repository import ChunkRepository
    from backend.app.api.v1.repository.document_repository import DocumentRepository
    from backend.app.api.v1.repository.insight_repository import InsightRepository
    from backend.app.extraction.embeddings.embedding_service import EmbeddingService
    from backend.app.extraction.pipeline.document_pipeline import DocumentPipeline
    from backend.app.extraction.rag.rag_service import RAGService
    from backend.app.extraction.vector_store.qdrant_service import QdrantService
    from backend.app.processors.document_processor import DocumentProcessor


class Container:

    def __init__(self) -> None:
        self._vector_store: "QdrantService | None" = None
        self._embedder: "EmbeddingService | None" = None
        self._document_repository: "DocumentRepository | None" = None
        self._chunk_repository: "ChunkRepository | None" = None
        self._insight_repository: "InsightRepository | None" = None
        self._pipeline: "DocumentPipeline | None" = None
        self._rag_service: "RAGService | None" = None
        self._document_processor: "DocumentProcessor | None" = None
        self._storage_service = None

    @property
    def document_repository(self) -> "DocumentRepository":
        if self._document_repository is None:
            from backend.app.api.v1.repository.document_repository import (
                DocumentRepository,
            )

            self._document_repository = DocumentRepository()
        return self._document_repository

    @property
    def chunk_repository(self) -> "ChunkRepository":
        if self._chunk_repository is None:
            from backend.app.api.v1.repository.chunk_repository import ChunkRepository

            self._chunk_repository = ChunkRepository()
        return self._chunk_repository

    @property
    def insight_repository(self) -> "InsightRepository":
        if self._insight_repository is None:
            from backend.app.api.v1.repository.insight_repository import (
                InsightRepository,
            )

            self._insight_repository = InsightRepository()
        return self._insight_repository

    @property
    def embedder(self) -> "EmbeddingService":
        if self._embedder is None:
            from backend.app.extraction.embeddings.embedding_service import (
                EmbeddingService,
            )
            from backend.app.extraction.llm_embedding.factory import (
                create_embedding_provider,
            )

            self._embedder = EmbeddingService(provider=create_embedding_provider())
        return self._embedder

    @property
    def vector_store(self) -> "QdrantService":
        if self._vector_store is None:
            from backend.app.extraction.vector_store.qdrant_service import QdrantService

            self._vector_store = QdrantService()
        return self._vector_store

    @property
    def pipeline(self) -> "DocumentPipeline":
        if self._pipeline is None:
            from backend.app.extraction.pipeline.document_pipeline import (
                DocumentPipeline,
            )
            from backend.app.extraction.preprocessing.docling_parser import (
                DoclingParser,
            )
            from backend.app.extraction.preprocessing.markdown_cleaner import (
                MarkdownCleaner,
            )
            from backend.app.extraction.preprocessing.chunking import ChunkingService
            from backend.app.extraction.analysis.document_analyzer import (
                DocumentAnalyzer,
            )
            from backend.app.extraction.llm.factory import create_llm_provider

            self._pipeline = DocumentPipeline(
                parser=DoclingParser(),
                cleaner=MarkdownCleaner(),
                chunker=ChunkingService(),
                embedder=self.embedder,  # ✅ property — triggers lazy init
                vector_store=self.vector_store,  # ✅ property — triggers lazy init
                analyzer=DocumentAnalyzer(llm_provider=create_llm_provider()),
            )
        return self._pipeline

    @property
    def document_processor(self) -> "DocumentProcessor":
        if self._document_processor is None:
            from backend.app.processors.document_processor import DocumentProcessor

            self._document_processor = DocumentProcessor(
                pipeline=self.pipeline,
                document_repository=self.document_repository,
                chunk_repository=self.chunk_repository,
                insight_repository=self.insight_repository,
                session_factory=SessionLocal,
            )
        return self._document_processor

    @property
    def rag_service(self) -> "RAGService":
        if self._rag_service is None:
            from backend.app.extraction.rag.rag_service import RAGService
            from backend.app.extraction.llm.factory import create_llm_provider

            self._rag_service = RAGService(
                chunk_repository=self.chunk_repository,
                llm_provider=create_llm_provider(),
                embedder=self.embedder,  # ✅ shared singleton
                vector_store=self.vector_store,  # ✅ shared singleton
            )
        return self._rag_service

    @property
    def storage_service(self):
        if self._storage_service is None:
            from backend.app.api.v1.services.storage.local_storage_service import (
                LocalStorageService,
            )

            self._storage_service = LocalStorageService()
        return self._storage_service


container = Container()
