import re
from typing import Optional

FENCE_RE = re.compile(r"```(?:\w+)?\n(.*?)```", re.DOTALL)


def sanitize_completion(text: str) -> str:
    """
    Remove markdown code fences and language tags from LLM completion output.
    """
    text = text.strip()

    # Case 1: fenced code block.
    match = FENCE_RE.search(text)
    if match:
        return match.group(1).strip()

    # Case 2: stray backticks.
    text = text.replace("```", "").strip()

    return text
