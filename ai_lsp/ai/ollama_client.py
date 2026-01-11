import asyncio
import json
from typing import Optional

import requests

from ai_lsp.agents.base import CompletionAgent
from ai_lsp.agents.context import ContextPruningAgent
from ai_lsp.agents.guard import OutputGuardAgent
from ai_lsp.agents.intent import CompletionIntentAgent, CursorWindowIntentAgent
from ai_lsp.agents.range_alignment import RangeAlignmentAgent
from ai_lsp.ai.engine import CompletionEngine
from ai_lsp.ai.sanitize import sanitize_completion
from ai_lsp.domain.completion import CompletionContext


class OllamaCompletionEngine(CompletionEngine):
    def __init__(
        self,
        model: str = "codellama:7b",
        base_url: str = "http://localhost:11434",
        timeout: int = 10,
        agents: list[CompletionAgent] | None = None,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

        self.agents = agents or [
            CompletionIntentAgent(),
            ContextPruningAgent(),
            RangeAlignmentAgent(),
            OutputGuardAgent(),
        ]

        self.intent_agent = CursorWindowIntentAgent

    async def complete(self, context: CompletionContext) -> Optional[str]:
        for agent in self.agents:
            intent = self.intent_agent.detect_intent(context)
            context.in
            decision = agent.before_generation(context)
            if not decision.allowed:
                return None

        return await asyncio.to_thread(self._blocking_complete, context)

    def _blocking_complete(self, context: CompletionContext) -> Optional[str]:
        prompt = self._build_prompt(context)

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": 0,
                    "seed": 42,
                    "num_predict": 128,
                },
            },
            stream=True,
            timeout=self.timeout,
        )

        buffer: list[str] = []
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            token = data.get("response")
            if not token:
                continue

            for agent in self.agents:
                decision = agent.on_token(token)
                if decision and decision.stop_generation:
                    final = "".join(buffer)
                    return self._finalize(context, final)

            buffer.append(token)

            if data.get("done"):
                break

        final = "".join(buffer)
        return self._finalize(context, final)

    def _finalize(self, context: CompletionContext, text: str) -> Optional[str]:
        text = sanitize_completion(text).strip()
        for agent in self.agents:
            result = agent.after_generation(context, text)
            if result is None:
                return None
            text = result

        return text.strip()

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
