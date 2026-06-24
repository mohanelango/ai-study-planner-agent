import json
import time

from openai import OpenAI, OpenAIError

from app.core.config.settings import settings
from app.infrastructure.llm.base import LLMProvider, LLMRequest, LLMResponse
from app.infrastructure.llm.exceptions import LLMConfigurationError, LLMProviderError, LLMResponseValidationError


class OpenAIProvider(LLMProvider):
    provider = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        if not self.api_key:
            raise LLMConfigurationError()
        self.client = OpenAI(api_key=self.api_key, timeout=30.0)

    def generate_json(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=request.temperature,
                response_format={"type": "json_object"},
                messages=self._messages(request),
            )
        except OpenAIError as exc:
            raise LLMProviderError("OpenAI request failed") from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        content = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMResponseValidationError("OpenAI did not return valid JSON") from exc

        usage = response.usage
        return LLMResponse(
            content=content,
            parsed_json=parsed,
            model=self.model,
            provider=self.provider,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            latency_ms=latency_ms,
        )

    def generate_text(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=request.temperature,
                messages=self._messages(request),
            )
        except OpenAIError as exc:
            raise LLMProviderError("OpenAI request failed") from exc

        usage = response.usage
        return LLMResponse(
            content=response.choices[0].message.content or "",
            parsed_json=None,
            model=self.model,
            provider=self.provider,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    @staticmethod
    def _messages(request: LLMRequest) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.user_prompt})
        return messages

