from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:

    content: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class BaseLLMProvider(ABC):

    @abstractmethod
    def invoke(self, prompt: str) -> LLMResponse:
        """Send a prompt and return a plain text response."""
        ...

    @abstractmethod
    def invoke_structured(self, prompt: str, schema: type) -> object:
        """
        Send a prompt and return a response parsed into `schema`.
        `schema` is a Pydantic model class.
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The model identifier string (e.g. 'gpt-4o-mini')."""
        ...
