import requests
import re
from ai_lsp.ai.engine import CompletionEngine
from ai_lsp.domain.completion import CompletionContext


class OllamaCOmpletionEngine(CompletionEngine):
    def __init__(
        self,
        model: str = "codellama:7b",
        base_url: str = "http://localhost:11434",
        timeout: int = 10,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def complete(self, context: CompletionContext) -> str:
        prompt = self._build_prompt(context)

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 64,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        result = data.get("response", "").strip()

        # Debug: log raw result
        if result:
            print(f"DEBUG: Raw completion result: {repr(result)}")

        # Clean up the result: remove markdown code blocks and normalize whitespace
        result = self._clean_completion_result(result)

        # Debug: log cleaned result
        if result:
            print(f"DEBUG: Cleaned completion result: {repr(result)}")

        return result

    def _build_prompt(self, context: CompletionContext) -> str:
        previous = "\n".join(context.previous_lines)

        return f"""
You are a code autocomplete engine.
Return ONLY the completion text.
No explanations. No markdown. No code blocks.
Pure code only. Single line if possible.
Pretend you are the developer typing directly.

Language: {context.language}
File: {context.file_path}

Context:
{previous}

Current line:
{context.current_line}

Prefix:
{context.prefix}

Completion (just the code):
""".strip()

    def _clean_completion_result(self, text: str) -> str:
        """
        Clean up completion result by removing markdown formatting and normalizing whitespace.

        Handles cases like:
        - '```\nif __name__ == "__main__":\n```' -> 'if __name__ == "__main__":'
        - Multiple lines -> single line
        - Extra whitespace -> normalized
        """
        if not text:
            return text

        # Remove markdown code block markers (```)
        text = re.sub(r'```\w*\n?', '', text)
        text = re.sub(r'```', '', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text
