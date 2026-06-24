import unittest

from app.modules.agents.services.prompt_renderer import PromptRenderer


class PromptRendererTestCase(unittest.TestCase):
    def test_loads_and_renders_study_plan_prompt(self) -> None:
        renderer = PromptRenderer()
        prompt = renderer.render("study_plan_explanation.md", {"PLAN_CONTEXT": '{"goal_title": "Exam"}'})
        self.assertIn("deterministic study plan", prompt)
        self.assertIn("Exam", prompt)
        self.assertNotIn("{{PLAN_CONTEXT}}", prompt)


if __name__ == "__main__":
    unittest.main()

