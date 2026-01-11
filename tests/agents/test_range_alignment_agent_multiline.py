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
        current_line=current_line,
        previous_lines=previous_lines,
        next_lines=next_lines,
        indentation="",
        line=0,
        character=len(prefix),
    )


def test_multiline_removes_repeated_previous_lines():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="    ",
        current_line="    ",
        previous_lines=["if cond:"],
    )

    completion = "if cond:\n    do_something()"

    result = agent.after_generation(context, completion)

    assert result == "    do_something()"


def test_multiline_removes_overlap_with_next_lines():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="    ",
        current_line="    ",
        next_lines=["    cleanup()"],
    )

    completion = "    do_other()\n    cleanup()"

    result = agent.after_generation(context, completion)

    assert result == "    do_other()"


def test_multiline_partial_overlap():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="    ",
        current_line="    ",
        previous_lines=["return (", "    a +"],
        next_lines=["    b", ")"],
    )

    completion = "    a +\n    b\n)"

    result = agent.after_generation(context, completion)

    assert result == ""



