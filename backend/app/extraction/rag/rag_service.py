import logging

from langchain_openai import ChatOpenAI
from sqlalchemy.orm import Session

from backend.app.api.v1.repository.chunk_repository import ChunkRepository
from backend.app.extraction.embeddings.embedding_service import EmbeddingService
from backend.app.extraction.vector_store.qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class RAGService:
    """
    Handles question answering over document content using RAG.
    """

    def __init__(self, chunk_repository: ChunkRepository):

        self.embedder = EmbeddingService()
        self.vector_store = QdrantService()
        self.chunk_repository = chunk_repository

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

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

    def ask(self, db: Session, document_id: str, question: str):
        logger.info("Running hybrid RAG for %s", document_id)

        # Step 1 — embed user question
        query_embedding = self.embedder.embed_query(question)

        # Step 2 — retrieve relevant chunks from vector store
        vector_results = self.vector_store.search(
            query_embedding=query_embedding,
            document_id=document_id,
            top_k=5
        )
        vector_chunks = [result.payload["chunk_text"] for result in vector_results]

        # Step 3 — retrieve exact matches from SQL
        keyword_results = self.chunk_repository.search_chunks_by_keyword(
            db=db,
            document_id=document_id,
            query=question,
        )
        keyword_chunks = [chunk.chunk_text for chunk in keyword_results]

        combined_chunks = self._merge_chunks(vector_chunks=vector_chunks, keyword_chunks=keyword_chunks)
        context = "\n\n".join(combined_chunks)
        logger.info(
            "Hybrid retrieval for %s returned %s vector chunks and %s keyword chunks",
            document_id,
            len(vector_chunks),
            len(keyword_chunks),
        )

        prompt = f"""
You are an AI assistant analyzing a document.

Use ONLY the provided context to answer the question.

If the answer is not present in the context,
respond with:
"I cannot find this information in the document."

Context:
{context}

Question:
{question}
"""

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content,
            "sources": combined_chunks,
        }
