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


def split_indent(text: str) -> tuple[str, str]:
    """
    Returns (indent, rest)
    """
    match = re.match(r"^(\s*)(.*)$", text)
    if match:
        return match.group(1), match.group(2)

    return "", ""


def strip_duplicate_prefix(
    current_line: str,
    prefix: str,
    completion: str,
) -> str:
    """
    Removes duplicates prefix if the model echoed existing code.
    """

    # Split indentation
    prefix_indent, prefix_code = split_indent(prefix)
    line_inden, line_code = split_indent(current_line)
    comp_indent, comp_code = split_indent(completion)

    # Normalize whitespaces for comparison only
    prefix_norm = prefix_code.strip()
    line_norm = line_code.strip()
    comp_norm = comp_code.lstrip()

    # Case 1: model repeated the prefix
    if comp_norm.startswith(prefix_norm):
        remainder = comp_norm[len(prefix_norm) :].lstrip()
        return prefix_indent + remainder

    # Otherwhise, keep original completion
    return completion
