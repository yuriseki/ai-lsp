from ai_lsp.agents.constraints import SuffixConstraintAgent
from ai_lsp.domain.completion import CompletionContext


def make_context(
    *,
    prefix="",
    suffix="",
    current_line="",
    previous_lines=[],
    next_lines=[],
    indentation="",
    language="",
):
    return CompletionContext(
        language=language,
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


def test_bracket_suffix():
    ctx = make_context(suffix="]")
    constraints = SuffixConstraintAgent().analyze(ctx)

    assert "]" in constraints.must_close
    assert constraints.forbidden_newlines is True


def test_paren_semicolon_suffix():
    ctx = make_context(suffix=");")
    constraints = SuffixConstraintAgent().analyze(ctx)

    assert ")" in constraints.must_not_repeat
    assert constraints.forbidden_newlines is True


def test_semicolon_does_not_forbid_newlines():
    ctx = make_context(suffix=";")
    constraints = SuffixConstraintAgent().analyze(ctx)

    assert constraints.forbidden_newlines is False

def test_empty_suffix():
    ctx = make_context(suffix="")
    constraints = SuffixConstraintAgent().analyze(ctx)

    assert constraints.forbidden_newlines is False
