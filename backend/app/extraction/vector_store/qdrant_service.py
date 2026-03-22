import logging
import uuid
from itertools import islice
from typing import Iterator

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from backend.app.core.config import settings
from backend.app.extraction.vector_store.client import get_qdrant_client
from backend.app.extraction.vector_store.models import ChunkPayload, SearchResult

logger = logging.getLogger(__name__)


def _batched(iterable, n: int) -> Iterator:
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk


class QdrantService:
    """
    Handles storage and semantic retrieval of document chunk embeddings.

    Depends on:
        client.py  — for the QdrantClient singleton
        models.py  — for ChunkPayload and SearchResult

    The collection is created lazily on first use (_collection_ready flag)
    so application startup is never blocked by a Qdrant connection attempt.
    """

    def __init__(self, client: QdrantClient | None = None) -> None:
        self._client = client or get_qdrant_client()
        self._collection_name = settings.QDRANT_COLLECTION_NAME
        self._vector_size = settings.QDRANT_VECTOR_SIZE
        self._batch_size = settings.QDRANT_UPSERT_BATCH_SIZE
        self._collection_ready = False

    def store_chunks(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        """
        Upserts chunk embeddings into Qdrant in batches.
        Batching avoids hitting gRPC/HTTP payload size limits on large docs.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch"
            )

        self._ensure_collection()

        points = [
            rest.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=ChunkPayload(
                    document_id=document_id,
                    chunk_index=idx,
                    chunk_text=chunk,
                ).__dict__,
            )
            for idx, (chunk, vector) in enumerate(zip(chunks, embeddings))
        ]

        total = 0
        for batch in _batched(points, self._batch_size):
            self._client.upsert(
                collection_name=self._collection_name,
                points=batch,
                wait=True,
            )
            total += len(batch)
            logger.debug(
                "Upserted batch document_id=%s points=%d/%d",
                document_id,
                total,
                len(points),
            )

        logger.info(
            "Stored embeddings document_id=%s total_points=%d", document_id, total
        )

    def search(
        self,
        query_embedding: list[float],
        document_id: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Searches for the top-k most similar chunks scoped to one document.
        Uses query_points() — compatible with qdrant-client >= 1.7.0.
        Returns typed SearchResult objects — never raw Qdrant objects.
        """
        self._ensure_collection()

        response = self._client.query_points(
            collection_name=self._collection_name,
            query=query_embedding,
            limit=top_k,
            query_filter=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="document_id",
                        match=rest.MatchValue(value=document_id),
                    )
                ]
            ),
            with_payload=True,
        )

        results = [
            SearchResult(
                chunk_text=hit.payload["chunk_text"],
                chunk_index=hit.payload["chunk_index"],
                document_id=hit.payload["document_id"],
                score=hit.score,
            )
            for hit in response.points
            if hit.payload
        ]

        logger.debug(
            "Search document_id=%s top_k=%d results=%d",
            document_id,
            top_k,
            len(results),
        )
        return results

    def delete_document_chunks(self, document_id: str) -> None:
        """
        Deletes all vectors belonging to a document.
        Call this when a document is deleted from the system.
        """
        self._ensure_collection()

        self._client.delete(
            collection_name=self._collection_name,
            points_selector=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="document_id",
                        match=rest.MatchValue(value=document_id),
                    )
                ]
            ),
        )
        logger.info("Deleted vectors document_id=%s", document_id)

    def _ensure_collection(self) -> None:
        """
        Creates the collection if it does not already exist.
        Result is cached so Qdrant is only queried once per service lifetime.
        """
        if self._collection_ready:
            return

        existing = {c.name for c in self._client.get_collections().collections}

        if self._collection_name not in existing:
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=rest.VectorParams(
                    size=self._vector_size,
                    distance=rest.Distance.COSINE,
                ),
            )
            logger.info(
                "Created Qdrant collection name=%s vector_size=%d",
                self._collection_name,
                self._vector_size,
            )
        else:
            logger.debug("Qdrant collection '%s' already exists", self._collection_name)

        self._collection_ready = True
