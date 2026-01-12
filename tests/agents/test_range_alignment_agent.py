import pytest
from ai_lsp.agents.range_alignment import RangeAlignmentAgent
from ai_lsp.domain.completion import CompletionContext


def make_context(
    *,
    prefix="",
    suffix="",
    current_line="",
):
    return CompletionContext(
        language="php",
        file_path="test.php",
        prefix=prefix,
        suffix=suffix,
        completion_prefix="",
        current_line=current_line,
        previous_lines=[],
        next_lines=[],
        indentation="",
        line=0,
        character=len(prefix),
    )


def test_removes_duplicated_prefix():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="    $a = ",
        current_line="    $a = ",
    )

    completion = "    $a = foo();"

    result = agent.after_generation(context, completion)

    assert result == "    foo();"


def test_removes_duplicated_full_line():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="    $a = ",
        current_line="    $a = bar();",
    )

    completion = "    $a = bar();"

    result = agent.after_generation(context, completion)

    assert result == "    "


def test_preserves_indentation():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="        $a = ",
        current_line="        $a = ",
    )

    completion = "        $a = service()->get();"

    result = agent.after_generation(context, completion) or ""

    assert result.startswith("        ")
    assert result.strip() == "service()->get();"


def test_removes_suffix_overlap():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="print(",
        suffix="value)",
        current_line="print(value)",
    )

    completion = "value)"

    result = agent.after_generation(context, completion)

    assert result == ""


def test_no_overlap_returns_completion():
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix="$a = ",
        suffix="",
        current_line="$a = ",
    )

    completion = "foo();"

    result = agent.after_generation(context, completion)

    assert result == "foo();"


@pytest.mark.parametrize(
    "prefix, suffix, completion",
    [
        ("", "", "foo"),
        ("", ")", ")"),
        ("$a = ", "", ""),
    ],
)
def test_defensive_cases(prefix, suffix, completion):
    agent = RangeAlignmentAgent()

    context = make_context(
        prefix=prefix,
        suffix=suffix,
        current_line=prefix + suffix,
    )

    result = agent.after_generation(context, completion)

    assert result is not None



