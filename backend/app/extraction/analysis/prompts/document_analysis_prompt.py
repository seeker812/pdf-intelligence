from backend.app.extraction.analysis.schemas import DocumentIntelligence


def _build_field_contract() -> str:
    """
    Generates the field contract string directly from DocumentIntelligence.
    Called once at import time — result is a module-level constant so we
    never rebuild it per request.
    """
    lines = []
    for name, field in DocumentIntelligence.model_fields.items():
        desc = field.description or ""
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)


_FIELD_CONTRACT = _build_field_contract()


def get_document_analysis_prompt(document_text: str) -> str:
    """
    Prompt for direct structured analysis of a document that fits
    within the model's context window.

    The field contract is auto-generated from DocumentIntelligence so
    this prompt is always in sync with the schema — no manual maintenance.
    """
    return f"""You are an expert document intelligence system.

Analyse the document below and return a structured response with exactly these fields:

{_FIELD_CONTRACT}

Rules:
- short_summary: exactly one sentence
- detailed_summary: 3 to 5 sentences
- key_insights: 3 to 8 items, each a concrete specific finding — not a restatement of the summary
- topics: 3 to 8 items specific to this document's content
- sections: list the major sections in the order they appear
- entities: extract only entities that are explicitly named — do not infer
- document_type / category / sub_category: concise single labels

Document:

{document_text}
"""


def get_chunk_summary_prompt(
    chunk_text: str, chunk_index: int, total_chunks: int
) -> str:
    """
    MAP phase — summarises one chunk independently.
    Returns a plain-text summary (not structured output) because the
    REDUCE step will synthesise all summaries into the final schema.
    """
    return f"""You are analysing part {chunk_index + 1} of {total_chunks} of a larger document.

From this chunk extract:

1. A concise summary (2 to 3 sentences)
2. Key facts, claims, figures, or findings
3. Named entities: people, organisations, locations, dates, monetary values
4. Any notable insights or implications specific to this section

Be factual and precise. Do not infer beyond what is written.
Do not reference other parts of the document — analyse only what is here.

Chunk:

{chunk_text}
"""


def get_synthesis_prompt(chunk_summaries: list[str]) -> str:
    """
    REDUCE phase — synthesises all chunk summaries into a single
    DocumentIntelligence covering the full document.

    Uses the same field contract as get_document_analysis_prompt so
    the structured output parser receives exactly what it expects.
    """
    summaries_block = "\n\n---\n\n".join(
        f"Part {i + 1} of {len(chunk_summaries)}:\n{summary}"
        for i, summary in enumerate(chunk_summaries)
    )

    return f"""You are an expert document intelligence system.

The document was too long to analyse in one pass. It was split into \
{len(chunk_summaries)} parts, each summarised independently.
Your task is to synthesise these part summaries into a single coherent analysis \
of the complete document.

Return a structured response with exactly these fields:

{_FIELD_CONTRACT}

Rules:
- short_summary: exactly one sentence covering the whole document
- detailed_summary: 3 to 5 sentences covering the whole document
- key_insights: 3 to 8 items representing the most important findings across all parts
- topics: themes present across the full document — 3 to 8 items
- sections: reconstruct the major sections from all parts in order
- entities: merge entities from all parts, deduplicate
- document_type / category / sub_category: based on the whole document

Part summaries:

{summaries_block}
"""
