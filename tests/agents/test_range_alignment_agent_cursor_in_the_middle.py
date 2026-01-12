import pytest
from ai_lsp.agents.range_alignment import RangeAlignmentAgent
from ai_lsp.domain.completion import CompletionContext


def make_context(
    *,
    prefix="",
    suffix="",
    current_line="",
    previous_lines=[],
    next_lines=[],
):
    return CompletionContext(
        language="php",
        file_path="test.php",
        prefix=prefix,
        suffix=suffix,
        completion_prefix="",
        current_line=current_line,
        previous_lines=previous_lines,
        next_lines=next_lines,
        indentation="",
        line=0,
        character=len(prefix),
    )


def test_suffix_overlap_single_line():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="print(",
        suffix=")",
    )

    completion = "value)"

    assert agent.after_generation(context, completion) == "value"



def test_suffix_overlap_multiline():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="",
        suffix=")",
    )

    completion = "do_a()\ncleanup())"

    result = agent.after_generation(context, completion)

    assert result == "do_a()\ncleanup("
