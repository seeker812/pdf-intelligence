import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.app.extraction.analysis.schemas import DocumentIntelligence
from backend.app.extraction.analysis.prompts.document_analysis_prompt import (
    get_chunk_summary_prompt,
    get_document_analysis_prompt,
    get_synthesis_prompt,
)
from backend.app.extraction.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)


DIRECT_ANALYSIS_LIMIT = 12_000

CHUNK_CHAR_SIZE = 3_000

CHUNK_OVERLAP = 200

MAP_MAX_WORKERS = 4


class DocumentAnalyzer:

    def __init__(self, llm_provider: BaseLLMProvider) -> None:
        self._llm = llm_provider
        logger.info("DocumentAnalyzer ready provider=%s", llm_provider.model_name)

    def analyze(self, document_text: str) -> DocumentIntelligence:

        if len(document_text) <= DIRECT_ANALYSIS_LIMIT:
            return self._analyze_direct(document_text)
        return self._analyze_map_reduce(document_text)

    def _analyze_direct(self, document_text: str) -> DocumentIntelligence:
        logger.info(
            "Direct analysis chars=%d model=%s",
            len(document_text),
            self._llm.model_name,
        )
        prompt = get_document_analysis_prompt(document_text)
        result = self._llm.invoke_structured(prompt, DocumentIntelligence)
        logger.info("Direct analysis complete model=%s", self._llm.model_name)
        return result  # type: ignore[return-value]

    def _analyze_map_reduce(self, document_text: str) -> DocumentIntelligence:
        chunks = self._split_into_chunks(document_text)
        logger.info(
            "Map-reduce started total_chars=%d chunks=%d workers=%d model=%s",
            len(document_text),
            len(chunks),
            MAP_MAX_WORKERS,
            self._llm.model_name,
        )

        chunk_summaries: list[str] = [""] * len(chunks)

        with ThreadPoolExecutor(
            max_workers=MAP_MAX_WORKERS,
            thread_name_prefix="llm_map",
        ) as executor:
            future_to_index = {
                executor.submit(self._summarise_chunk, chunk, idx, len(chunks)): idx
                for idx, chunk in enumerate(chunks)
            }

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    chunk_summaries[idx] = future.result()
                    logger.debug("Chunk %d/%d summarised", idx + 1, len(chunks))
                except Exception as exc:
                    logger.exception("MAP phase failed on chunk %d", idx + 1)
                    raise RuntimeError(
                        f"MAP phase failed on chunk {idx + 1}/{len(chunks)}"
                    ) from exc

        synthesis_prompt = get_synthesis_prompt(chunk_summaries)
        result = self._llm.invoke_structured(synthesis_prompt, DocumentIntelligence)
        logger.info(
            "Map-reduce complete chunks=%d model=%s",
            len(chunks),
            self._llm.model_name,
        )
        return result  # type: ignore[return-value]

    def _summarise_chunk(self, chunk: str, idx: int, total: int) -> str:
        """Summarises one chunk — runs in a MAP worker thread."""
        prompt = get_chunk_summary_prompt(chunk, idx, total)
        response = self._llm.invoke(prompt)
        return response.content

    def _split_into_chunks(self, text: str) -> list[str]:
        """
        Splits text into fixed-size overlapping chunks.
        Overlap preserves context across chunk boundaries so sentences
        that span a boundary appear in both adjacent chunks.
        """
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = start + CHUNK_CHAR_SIZE
            chunks.append(text[start:end])
            start = end - CHUNK_OVERLAP
        return chunks
