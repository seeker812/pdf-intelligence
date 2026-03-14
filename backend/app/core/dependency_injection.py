from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.api.v1.repository.chunk_repository import ChunkRepository
    from backend.app.api.v1.repository.document_repository import DocumentRepository
    from backend.app.api.v1.repository.insight_repository import InsightRepository
    from backend.app.extraction.pipeline.document_pipeline import DocumentPipeline
    from backend.app.extraction.rag.rag_service import RAGService
    from backend.app.processors.document_processor import DocumentProcessor


class Container:
    """
    Central dependency container.
    """

    def __init__(self) -> None:
        self._document_repository: "DocumentRepository | None" = None
        self._chunk_repository: "ChunkRepository | None" = None
        self._insight_repository: "InsightRepository | None" = None
        self._pipeline: "DocumentPipeline | None" = None
        self._rag_service: "RAGService | None" = None
        self._document_processor: "DocumentProcessor | None" = None

    @property
    def document_repository(self) -> "DocumentRepository":
        if self._document_repository is None:
            from backend.app.api.v1.repository.document_repository import DocumentRepository

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
            from backend.app.api.v1.repository.insight_repository import InsightRepository

            self._insight_repository = InsightRepository()
        return self._insight_repository

    @property
    def pipeline(self) -> "DocumentPipeline":
        if self._pipeline is None:
            from backend.app.extraction.pipeline.document_pipeline import DocumentPipeline

            self._pipeline = DocumentPipeline()
        return self._pipeline

    @property
    def rag_service(self) -> "RAGService":
        if self._rag_service is None:
            from backend.app.extraction.rag.rag_service import RAGService

            self._rag_service = RAGService(chunk_repository=self.chunk_repository)
        return self._rag_service

    @property
    def document_processor(self) -> "DocumentProcessor":
        if self._document_processor is None:
            from backend.app.processors.document_processor import DocumentProcessor

            self._document_processor = DocumentProcessor(
                pipeline=self.pipeline,
                document_repository=self.document_repository,
                chunk_repository=self.chunk_repository,
                insight_repository=self.insight_repository,
            )
        return self._document_processor


container = Container()
