from langchain_openai import ChatOpenAI
from backend.app.extraction.analysis.schemas import DocumentIntelligence
from backend.app.extraction.analysis.prompts.document_analysis_prompt import (
    get_document_analysis_prompt
)
from backend.app.extraction.analysis.prompts.insights_prompt import get_insights_prompt


class DocumentAnalyzer:

    """
    Performs AI-based document understanding.
    """

    def __init__(self):

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        self.structured_llm = self.llm.with_structured_output(
            DocumentIntelligence
        )

    def analyze(self, document_text: str) -> DocumentIntelligence:

        prompt = get_document_analysis_prompt(document_text)

        result = self.structured_llm.invoke(prompt)

        return result

    def extract_insights(self, document_text: str):

        prompt = get_insights_prompt(document_text)

        response = self.llm.invoke(prompt)

        return response.content