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
                    "temperature": 0,
                    "num_predict": 64,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        result = data.get("response", "").strip()

        # Debug: log context and raw result
        print(f"DEBUG: Context prefix: {repr(context.prefix)}")
        if result:
            print(f"DEBUG: Raw completion result: {repr(result)}")

        # Clean up the result: remove markdown code blocks, normalize whitespace, and remove prefix duplication
        result = self._clean_completion_result(result, context)

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
        if context.prefix:
            # Get the prefix without trailing whitespace for comparison
            prefix_clean = context.prefix.rstrip()
            prefix_no_indent = prefix_clean.lstrip()

            # Check various ways the prefix might appear in the completion
            if text.startswith(context.prefix):
                # Exact match with indentation
                text = text[len(context.prefix) :]
            elif text.startswith(prefix_clean):
                # Match without trailing whitespace
                text = text[len(prefix_clean) :]
            elif text.startswith(prefix_no_indent):
                # LLM stripped indentation from the prefix
                text = text[len(prefix_no_indent) :]
            elif context.identation and text.startswith(
                context.identation + prefix_no_indent
            ):
                # LLM used different indentation
                indented_prefix = context.identation + prefix_no_indent
                text = text[len(indented_prefix) :]

        # Step 3: Skip whitespace normalization for code (preserve structure)
        # Code indentation and newlines are important for proper formatting
        pass

        # Step 4: Final cleanup (preserve leading/trailing newlines for code structure)
        text = text.rstrip(" \t")  # Only remove trailing spaces/tabs

        return text
