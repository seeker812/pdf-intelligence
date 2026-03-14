import logging

from backend.app.extraction.preprocessing.docling_parser import DoclingParser
from backend.app.extraction.preprocessing.markdown_cleaner import MarkdownCleaner
from backend.app.extraction.preprocessing.chunking import ChunkingService

from backend.app.extraction.embeddings.embedding_service import EmbeddingService
from backend.app.extraction.vector_store.qdrant_service import QdrantService

from backend.app.extraction.analysis.document_analyzer import DocumentAnalyzer

logger = logging.getLogger(__name__)


class DocumentPipeline:
    """
    Orchestrates the full document processing pipeline.
    """

    def __init__(self):

        self.parser = DoclingParser()
        self.cleaner = MarkdownCleaner()
        self.chunker = ChunkingService()

        self.embedder = EmbeddingService()
        self.vector_store = QdrantService()

        self.analyzer = DocumentAnalyzer()

    def process_document(self, file_path: str, document_id: str):
        logger.info("Starting document processing for %s", document_id)

        # 1️⃣ Parse document
        markdown = self.parser.parse(file_path)
        logger.info("Document parsed for %s", document_id)

        # 2️⃣ Clean markdown
        clean_text = self.cleaner.clean(markdown)
        logger.info("Markdown cleaned for %s", document_id)

        # 3️⃣ Chunk document
        chunks = self.chunker.chunk(clean_text)
        logger.info("Generated %s chunks for %s", len(chunks), document_id)

        # 4️⃣ Generate embeddings
        embeddings = self.embedder.embed_chunks(chunks)
        logger.info("Embeddings generated for %s", document_id)

        # 5️⃣ Store vectors
        self.vector_store.store_chunks(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings
        )
        logger.info("Chunks stored in vector database for %s", document_id)

        # 6️⃣ Run AI analysis
        analysis_result = self.analyzer.analyze(clean_text[:15000])
        logger.info("Document analysis completed for %s", document_id)

        return {
            "analysis": analysis_result,
            "chunk_count": len(chunks),
            "chunks": chunks,
        }
