import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.app.extraction.llm_embedding.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

EMBED_BATCH_SIZE = 100

EMBED_WORKERS = 4


class EmbeddingService:

    def __init__(self, provider: BaseEmbeddingProvider) -> None:
        self._provider = provider
        logger.info("EmbeddingService ready model=%s", provider.model_name)

    def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        """
        Embeds all chunks in parallel batches.
        Returns embeddings in the same order as the input chunks.
        """
        if not chunks:
            return []

        batches = self._make_batches(chunks)
        logger.info(
            "Embedding chunks=%d batches=%d workers=%d",
            len(chunks),
            len(batches),
            EMBED_WORKERS,
        )

        results: list[list[list[float]]] = [[] for _ in batches]

        with ThreadPoolExecutor(
            max_workers=EMBED_WORKERS,
            thread_name_prefix="embed",
        ) as executor:
            future_to_idx = {
                executor.submit(self._embed_batch, batch): idx
                for idx, batch in enumerate(batches)
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                    logger.debug("Batch %d/%d embedded", idx + 1, len(batches))
                except Exception as exc:
                    logger.exception("Embedding failed on batch=%d", idx + 1)
                    raise RuntimeError(
                        f"Embedding failed on batch {idx + 1}/{len(batches)}"
                    ) from exc

        # Flatten ordered batches → flat list matching chunk order
        return [vec for batch_result in results for vec in batch_result]

    def embed_query(self, query: str) -> list[float]:
        """
        Embeds a single user query for RAG vector search.
        Uses embed_query() (not embed_documents()) — providers apply
        different internal optimisations for query vs document embeddings.
        """
        return self._provider.embed_query(query)

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        """Embeds one batch — called from worker threads."""
        return self._provider.embed_documents(batch)

    def _make_batches(self, chunks: list[str]) -> list[list[str]]:
        return [
            chunks[i : i + EMBED_BATCH_SIZE]
            for i in range(0, len(chunks), EMBED_BATCH_SIZE)
        ]
