import asyncio
import requests
import json
from ai_lsp.ai.engine import CompletionEngine
from ai_lsp.domain.completion import CompletionContext
from ai_lsp.ai.sanitize import sanitize_completion


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

    async def complete(self, context: CompletionContext) -> str:
        return await asyncio.to_thread(self._blocking_complete, context)

    def _blocking_complete(self, context: CompletionContext) -> str:
        prompt = self._build_prompt(context)

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "stream": True,
                    "temperature": 0,
                    "seed": 42,
                    "num_predict": 128,
                },
            },
            stream=True,
            timeout=self.timeout,
        )

        text = ""
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if "response" in data:
                text += data["response"]

        clean_text = sanitize_completion(text)

        return clean_text.strip()

    def _build_prompt(self, context: CompletionContext) -> str:
        previous = "\n".join(context.previous_lines)

        return f"""
You are a code autocomplete engine.
Return ONLY the completion text.
No explanations. No markdown. No code blocks.
Pure code only.
The code should be as the developer is typing directly.

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
