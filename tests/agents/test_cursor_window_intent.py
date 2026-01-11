import pytest
from ai_lsp.agents import semantics
from ai_lsp.agents.intent import CursorWindowIntentAgent
from ai_lsp.agents.intent_types import EditIntentType
from ai_lsp.agents.range_alignment import RangeAlignmentAgent
from ai_lsp.domain.completion import CompletionContext


def make_context(
    *,
    prefix="",
    suffix="",
    current_line="",
    previous_lines=[],
    next_lines=[],
    indentation=""
):
    return CompletionContext(
        language="php",
        file_path="test.php",
        prefix=prefix,
        suffix=suffix,
        current_line=current_line,
        previous_lines=previous_lines,
        next_lines=next_lines,
        indentation=indentation,
        line=0,
        character=len(prefix),
    )


def test_argument_completion():
    ctx = make_context(prefix="foo(", suffix="bar)")
    intent = CursorWindowIntentAgent().detect_intent(ctx)
    assert intent.type == EditIntentType.ARGUMENT_COMPLETION


def test_block_completion():
    ctx = make_context(
        current_line="    ",
        prefix="    ",
        suffix="",
        indentation="    ",
    )
    intent = CursorWindowIntentAgent().detect_intent(ctx)
    assert intent.type == EditIntentType.BLOCK_COMPLETION


def test_docstring():
    ctx = make_context(prefix='/**', suffix='*/')
    intent = CursorWindowIntentAgent().detect_intent(ctx)
    assert intent.type == EditIntentType.DOCSTRING


def test_symbol_completion():
    ctx = make_context(prefix="$this->", suffix="")
    intent = CursorWindowIntentAgent().detect_intent(ctx)
    assert intent.type == EditIntentType.SYMBOL_COMPLETION
