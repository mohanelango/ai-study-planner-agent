from app.infrastructure.llm.base import LLMProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    return OpenAIProvider()

