import re
from typing import Optional


from ai_lsp.agents.base import CompletionAgent
from ai_lsp.domain.completion import CompletionContext


def _split_indent(text: str) -> tuple[str, str]:
    """
    Returns (indent, rest)
    """
    match = re.match(r"^(\s*)(.*)$", text)
    if match:
        return match.group(1), match.group(2)

    return "", ""


def _trim_leading_line_overlap(
    completion_lines: list[str],
    previous_lines: list[str],
) -> list[str]:
    norm_prev = [l.strip() for l in previous_lines]

    result = []
    skipping = True
    for line in completion_lines:
        if skipping and line.strip() in norm_prev:
            continue
        skipping = False
        result.append(line)

    return result


def _trim_trailing_line_overlap(
    completion_lines: list[str],
    next_lines: list[str],
) -> list[str]:
    norm_next = [l.strip() for l in next_lines]

    result = []
    skipping = True
    for line in reversed(completion_lines):
        if skipping and line.strip() in norm_next:
            continue
        skipping = False
        result.append(line)

    return result



class RangeAlignmentAgent(CompletionAgent):
    """
    Removes duplicated prefix/current line from LLM output, preserving
    indentation.
    """

    def after_generation(
        self, context: CompletionContext, completion: str
    ) -> Optional[str]:
        prefix = context.prefix or ""
        suffix = context.suffix or ""
        current_line = context.current_line or ""
        text = completion or ""
        previous_lines = context.previous_lines or []
        next_lines = context.next_lines or []

        # -- Step 1: remove prefix/line
        prefix_indent, prefix_code = _split_indent(prefix)
        line_indent, line_code = _split_indent(current_line)
        comp_indent, comp_code = _split_indent(text)

        prefix_norm = prefix_code.strip()
        line_norm = line_code.strip()
        comp_norm = comp_code.lstrip()

        # Case 1: echoed prefix
        if prefix_norm and comp_norm.startswith(prefix_norm):
            remainder = comp_norm[len(prefix_norm) :].lstrip()
            text = prefix_indent + remainder

        # Case 2: echoed whole line
        if line_norm and comp_norm.startswith(line_norm):
            remainder = comp_norm[len(line_norm) :].lstrip()
            text = line_indent + remainder

        # -- Step 2: remove overlapping suffix
        suffix_norm = suffix.strip()
        if suffix_norm and text.strip().endswith(suffix_norm):
            text = text[: -len(suffix_norm)].rstrip()

        # -- Step 3: echoed multiline completion
        completion_lines = text.splitlines()
        if len(completion_lines) > 1 and previous_lines:
            text = _trim_leading_line_overlap(completion_lines, previous_lines)
            text = "\n".join(text)

        completion_lines = text.splitlines()
        if len(completion_lines) > 1 and next_lines:
            text = _trim_trailing_line_overlap(completion_lines, next_lines)
            text = "\n".join(text)

        return text
