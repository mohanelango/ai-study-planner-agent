import unittest

from app.infrastructure.llm.base import LLMProvider, LLMRequest, LLMResponse
from app.infrastructure.llm.exceptions import LLMResponseValidationError
from app.modules.agents.schemas.responses import StudyPlanExplanationPayload


class MockLLMProvider(LLMProvider):
    def __init__(self, parsed_json: dict | None) -> None:
        self.parsed_json = parsed_json

    def generate_json(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content="{}", parsed_json=self.parsed_json, model="mock", provider="mock")

    def generate_text(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(content="text", parsed_json=None, model="mock", provider="mock")


class StudyPlanExplanationServiceUnitTestCase(unittest.TestCase):
    def test_mock_llm_returns_valid_structured_response(self) -> None:
        payload = {
            "headline": "Good plan",
            "summary": "Follow it.",
            "priority_rationale": ["Hard topics first"],
            "schedule_rationale": ["Uses availability"],
            "risk_warnings": [],
            "next_best_actions": ["Start today"],
        }
        response = MockLLMProvider(payload).generate_json(LLMRequest(system_prompt=None, user_prompt="x"))
        validated = StudyPlanExplanationPayload.model_validate(response.parsed_json)
        self.assertEqual(validated.headline, "Good plan")

    def test_invalid_llm_json_fails_cleanly(self) -> None:
        with self.assertRaises(Exception):
            StudyPlanExplanationPayload.model_validate({"headline": "Missing fields"})

    def test_response_validation_error_type_exists(self) -> None:
        self.assertEqual(LLMResponseValidationError().code, "LLM_RESPONSE_VALIDATION_ERROR")


if __name__ == "__main__":
    unittest.main()

