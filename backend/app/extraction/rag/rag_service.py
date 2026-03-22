import logging

from sqlalchemy.orm import Session

from backend.app.api.v1.repository.chunk_repository import ChunkRepository
from backend.app.extraction.analysis.prompts.rag_prompt import get_rag_prompt
from backend.app.extraction.embeddings.embedding_service import EmbeddingService
from backend.app.extraction.llm.base import BaseLLMProvider
from backend.app.extraction.vector_store.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class RAGService:
    """
    Answers user questions over document content using hybrid retrieval.

    Retrieval strategy — two passes, results merged and deduplicated:

    1. Vector search (Qdrant)
       Embeds the question and finds the top-k semantically similar chunks.
       Catches paraphrased or conceptually related content even when the
       exact words differ.

    2. Keyword search (Postgres)
       Scans chunk_text with ILIKE for terms from the question.
       Catches exact matches that vector search can rank lower when a
       rare term (a name, a code, a number) happens to be numerically
       distant from the query embedding.

    Combining both gives better recall than either alone — this is
    intentional hybrid retrieval, not a redundancy.

    The merged chunks become the context for a single LLM call that
    generates a grounded answer.
    """

    def __init__(
        self,
        chunk_repository: ChunkRepository,
        llm_provider: BaseLLMProvider,  # ✅ injected — no hardcoded model
        embedder: EmbeddingService,  # ✅ injected — shared singleton
        vector_store: QdrantService,  # ✅ injected — shared singleton
    ) -> None:
        self.chunk_repository = chunk_repository
        self._llm = llm_provider
        self._embedder = embedder
        self._vector_store = vector_store

    def ask(
        self,
        db: Session,
        document_id: str,
        question: str,
    ) -> dict[str, object]:
        logger.info("Hybrid RAG started document_id=%s", document_id)

        query_embedding = self._embedder.embed_query(question)

        vector_results = self._vector_store.search(
            query_embedding=query_embedding,
            document_id=document_id,
            top_k=5,
        )
        vector_chunks = [result.chunk_text for result in vector_results]

        keyword_results = self.chunk_repository.search_chunks_by_keyword(
            db=db,
            document_id=document_id,
            query=question,
        )
        keyword_chunks = [chunk.chunk_text for chunk in keyword_results]

        combined_chunks = self._merge_chunks(
            vector_chunks=vector_chunks,
            keyword_chunks=keyword_chunks,
        )

        logger.info(
            "Hybrid retrieval complete document_id=%s "
            "vector=%d keyword=%d combined=%d",
            document_id,
            len(vector_chunks),
            len(keyword_chunks),
            len(combined_chunks),
        )

        context = "\n\n---\n\n".join(combined_chunks)
        prompt = get_rag_prompt(question=question, context=context)
        response = self._llm.invoke(prompt)

        logger.info("RAG answer generated document_id=%s", document_id)

        return {
            "answer": response.content,
            "sources": combined_chunks,
        }

    def _merge_chunks(
        self,
        vector_chunks: list[str],
        keyword_chunks: list[str],
    ) -> list[str]:

        seen: set[str] = set()
        merged: list[str] = []

        for chunk in [*vector_chunks, *keyword_chunks]:
            if chunk and chunk not in seen:
                seen.add(chunk)
                merged.append(chunk)

        return merged
