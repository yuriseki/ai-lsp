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


class PrefixAlignmentAgent(CompletionAgent):
    """
    Removes duplicated prefix/current line from LLM output, preserving
    indentation.
    """

    def after_generation(
        self, context: CompletionContext, completion: str
    ) -> Optional[str]:
        prefix = context.prefix or ""
        current_line = context.current_line or ""
        completion = completion or ""

        prefix_indent, prefix_code = _split_indent(prefix)
        line_indent, line_code = _split_indent(current_line)
        comp_indent, comp_code = _split_indent(completion)

        prefix_norm = prefix_code.strip()
        line_norm = line_code.strip()
        comp_norm = comp_code.lstrip()

        # Case 1: echoed prefix
        if prefix_norm and comp_norm.startswith(prefix_norm):
            remainder = comp_norm[len(prefix_norm) :].lstrip()
            return prefix_indent + remainder

        # Case 2: echoed whole line
        if line_norm and comp_norm.startswith(line_norm):
            remainder = comp_norm[len(line_norm) :].lstrip()
            return line_indent + remainder

        return completion
