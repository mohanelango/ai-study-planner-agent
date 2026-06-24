from pathlib import Path


class PromptRenderer:
    def __init__(self, prompt_dir: Path | None = None) -> None:
        self.prompt_dir = prompt_dir or Path(__file__).resolve().parents[1] / "prompts"

    def load(self, prompt_name: str) -> str:
        safe_name = prompt_name.replace("..", "").replace("/", "").replace("\\", "")
        prompt_path = self.prompt_dir / safe_name
        return prompt_path.read_text(encoding="utf-8")

    def render(self, prompt_name: str, variables: dict[str, str]) -> str:
        rendered = self.load(prompt_name)
        for key, value in variables.items():
            rendered = rendered.replace("{{" + key + "}}", value)
        return rendered

