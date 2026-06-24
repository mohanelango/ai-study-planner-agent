from app.core.exceptions.base import AppException


class LLMConfigurationError(AppException):
    def __init__(self, message: str = "OpenAI API key is not configured") -> None:
        super().__init__(message, code="LLM_CONFIGURATION_ERROR", status_code=503)


class LLMProviderError(AppException):
    def __init__(self, message: str = "LLM provider request failed") -> None:
        super().__init__(message, code="LLM_PROVIDER_ERROR", status_code=502)


class LLMResponseValidationError(AppException):
    def __init__(self, message: str = "LLM response validation failed") -> None:
        super().__init__(message, code="LLM_RESPONSE_VALIDATION_ERROR", status_code=502)

