import asyncio
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
                    "temperature": 0,
                    "seed": 42,
                    "num_predict": 128,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        result = data.get("response", "").strip()

        # Clean up the result: remove markdown code blocks, normalize whitespace, and remove prefix duplication
        result = self._clean_completion_result(result, context)

        # Adjust indentation for multi-line completions
        # result = self._adjust_completion_indentation(result, context)

        return result

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

    def _clean_completion_result(self, text: str, context: CompletionContext) -> str:
        """
        Clean up completion result by removing markdown formatting, normalizing whitespace,
        and removing duplicated prefix text that exists before the cursor.

        Requirements:
        1. Remove markdown code blocks (```)
        2. Normalize whitespace (multiple spaces/newlines -> single)
        3. Remove text that duplicates what's already before the cursor
        """
        if not text:
            return text

        # Step 1: Remove markdown code block markers
        text = re.sub(r"```\w*\n?", "", text)
        text = re.sub(r"```", "", text)

        # Step 2: Remove duplicated prefix text
        # if context.prefix:
        #     # Get the prefix without trailing whitespace for comparison
        #     prefix_clean = context.prefix.rstrip()
        #     prefix_no_indent = prefix_clean.lstrip()
        #
        #     # Check various ways the prefix might appear in the completion
        #     if text.startswith(context.prefix):
        #         # Exact match with indentation
        #         text = text[len(context.prefix) :]
        #     elif text.startswith(prefix_clean):
        #         # Match without trailing whitespace
        #         text = text[len(prefix_clean) :]
        #     elif text.startswith(prefix_no_indent):
        #         # LLM stripped indentation from the prefix
        #         text = text[len(prefix_no_indent) :]
        #     elif context.identation and text.startswith(
        #         context.identation + prefix_no_indent
        #     ):
        #         # LLM used different indentation
        #         indented_prefix = context.identation + prefix_no_indent
        #         text = text[len(indented_prefix) :]

        # Step 3: Skip whitespace normalization for code (preserve structure)
        # Code indentation and newlines are important for proper formatting
        pass

        # Step 4: Final cleanup (preserve leading/trailing newlines for code structure)
        text = text.rstrip(" \t")  # Only remove trailing spaces/tabs

        return text

    def _adjust_completion_indentation(
        self, text: str, context: CompletionContext
    ) -> str:
        """
        Adjust indentation for multi-line completions to match the current line's indentation.

        For multi-line completions, adds the current line's indentation to continuation lines.
        """
        if not text or "\n" not in text:
            return text

        # Get current line indentation
        current_indent = context.identation

        if not current_indent:
            return text

        # Split into lines
        lines = text.split("\n")

        # First line keeps original indentation (if any)
        # Continuation lines get current line indentation added
        adjusted_lines = [lines[0]]  # First line as-is

        for line in lines[1:]:
            # Add current indentation to continuation lines
            adjusted_lines.append(current_indent + line)

        return "\n".join(adjusted_lines)
