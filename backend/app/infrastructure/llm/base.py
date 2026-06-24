from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMRequest:
    system_prompt: str | None
    user_prompt: str
    response_schema: dict[str, Any] | None = None
    temperature: float = 0.2


@dataclass(frozen=True)
class LLMResponse:
    content: str
    parsed_json: dict[str, Any] | None
    model: str
    provider: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: int | None = None


class LLMProvider(ABC):
    @abstractmethod
    def generate_json(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    def generate_text(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError

