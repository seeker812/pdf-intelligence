import logging

from langchain_openai import ChatOpenAI

from backend.app.extraction.llm.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):

    def __init__(
        self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0
    ) -> None:
        self._model = model
        self._llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
        )
        logger.info("OpenAIProvider initialised model=%s", model)

    @property
    def model_name(self) -> str:
        return self._model

    def invoke(self, prompt: str) -> LLMResponse:
        response = self._llm.invoke(prompt)
        return LLMResponse(
            content=response.content,
            model=self._model,
            input_tokens=(
                response.usage_metadata.get("input_tokens")
                if response.usage_metadata
                else None
            ),
            output_tokens=(
                response.usage_metadata.get("output_tokens")
                if response.usage_metadata
                else None
            ),
        )

    def invoke_structured(self, prompt: str, schema: type) -> object:
        structured_llm = self._llm.with_structured_output(schema)
        return structured_llm.invoke(prompt)
