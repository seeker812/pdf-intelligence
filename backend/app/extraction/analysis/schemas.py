from pydantic import BaseModel, Field


class Section(BaseModel):
    section_title: str = Field(
        description="Title or heading of this section as it appears in the document"
    )
    section_summary: str = Field(
        description="2 to 3 sentence summary of what this section covers"
    )


class Entities(BaseModel):
    people: list[str] = Field(
        default_factory=list,
        description="Full names of people mentioned — authors, executives, officials, etc.",
    )
    organizations: list[str] = Field(
        default_factory=list,
        description="Companies, institutions, agencies, or groups mentioned",
    )
    locations: list[str] = Field(
        default_factory=list,
        description="Countries, cities, regions, or specific places mentioned",
    )
    dates: list[str] = Field(
        default_factory=list,
        description="Specific dates, periods, or timeframes referenced",
    )
    monetary_values: list[str] = Field(
        default_factory=list,
        description="Currency amounts, budgets, prices, or financial figures",
    )
    other_entities: list[str] = Field(
        default_factory=list,
        description="Any other named entities that do not fit the above categories",
    )


class DocumentIntelligence(BaseModel):
    """
    Structured output schema for full document analysis.

    This is the single source of truth — both the LLM structured output
    parser and the prompt template derive their field contracts from this
    class so they can never drift apart.
    """

    document_type: str = Field(
        description=(
            "Specific type of document e.g. research paper, legal contract, "
            "financial report, invoice, policy document, technical manual"
        )
    )
    category: str = Field(
        description="High-level domain e.g. finance, healthcare, technology, legal, education"
    )
    sub_category: str = Field(
        description="More specific domain within the category e.g. investment banking, oncology, AI/ML"
    )
    short_summary: str = Field(
        description="Exactly one sentence summarising the entire document"
    )
    detailed_summary: str = Field(
        description=(
            "3 to 5 sentences covering the main argument, findings, purpose, "
            "and any significant conclusions"
        )
    )
    topics: list[str] = Field(
        description="Main topics or themes discussed — 3 to 8 items, specific to this document"
    )
    entities: Entities = Field(
        description="All named entities extracted from the document"
    )
    key_insights: list[str] = Field(
        description=(
            "3 to 8 specific, non-obvious insights. Each must be a concrete finding "
            "or implication, not a restatement of the summary"
        )
    )
    sections: list[Section] = Field(
        description="Major sections or chapters identified in the document, in order"
    )
