import logging

from backend.app.extraction.preprocessing.docling_parser import DoclingParser
from backend.app.extraction.preprocessing.markdown_cleaner import MarkdownCleaner
from backend.app.extraction.preprocessing.chunking import ChunkingService
from backend.app.extraction.embeddings.embedding_service import EmbeddingService
from backend.app.extraction.vector_store.qdrant_service import QdrantService
from backend.app.extraction.analysis.document_analyzer import DocumentAnalyzer
from backend.app.extraction.analysis.schemas import DocumentIntelligence

logger = logging.getLogger(__name__)


class DocumentPipeline:

    def __init__(
        self,
        parser: DoclingParser,
        cleaner: MarkdownCleaner,
        chunker: ChunkingService,
        embedder: EmbeddingService,
        vector_store: QdrantService,
        analyzer: DocumentAnalyzer,
    ) -> None:
        self.parser = parser
        self.cleaner = cleaner
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.analyzer = analyzer

    def parse_and_chunk(self, file_path: str, document_id: str) -> dict:
        """
        Parses the file and splits text into chunks.

        Returns clean_text and chunks without embedding so the processor
        can immediately hand chunks to the DB-save thread while the
        embed thread runs concurrently.
        """
        logger.info("Parsing document_id=%s", document_id)
        markdown = self.parser.parse(file_path)

        clean_text = self.cleaner.clean(markdown)
        logger.info(
            "Cleaned document_id=%s char_count=%d",
            document_id,
            len(clean_text),
        )

        chunks = self.chunker.chunk(clean_text)
        logger.info(
            "Chunked document_id=%s chunk_count=%d",
            document_id,
            len(chunks),
        )

        return {"clean_text": clean_text, "chunks": chunks}

    def embed_and_store(self, chunks: list[str], document_id: str) -> None:
        """
        Embeds chunks in parallel batches then stores vectors in Qdrant.

        Called from a worker thread in the processor — runs concurrently
        with the DB chunk save. No DB session needed here.
        """
        logger.info("Embedding document_id=%s chunks=%d", document_id, len(chunks))
        embeddings = self.embedder.embed_chunks(chunks)

        self.vector_store.store_chunks(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings,
        )
        logger.info("Vectors stored document_id=%s", document_id)

    def run_phase_two(self, clean_text: str, document_id: str) -> DocumentIntelligence:
        """
        Runs LLM analysis on the full document text.
        DocumentAnalyzer selects direct or map-reduce strategy automatically.
        """
        logger.info(
            "Phase 2 started document_id=%s char_count=%d",
            document_id,
            len(clean_text),
        )
        analysis = self.analyzer.analyze(clean_text)
        logger.info("Phase 2 complete document_id=%s", document_id)
        return analysis
