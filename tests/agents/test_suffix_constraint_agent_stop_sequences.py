from ai_lsp.agents.constraints import SuffixConstraintAgent
from ai_lsp.domain.completion import CompletionContext
from ai_lsp.domain.constraints import SuffixConstraints


def make_context(
    *,
    suffix: str = "",
) -> CompletionContext:
    return CompletionContext(
        language="php",
        file_path="test.php",
        prefix="",
        suffix=suffix,
        current_line="",
        completion_prefix="",
        previous_lines=[],
        next_lines=[],
        indentation="",
        line=0,
        character=0,
    )


def test_paren_semicolon_produces_stop_sequences() -> None:
    ctx: CompletionContext = make_context(suffix=");")

    agent: SuffixConstraintAgent = SuffixConstraintAgent()
    constraints: SuffixConstraints = agent.analyze(ctx)

    assert ")" in constraints.stop_sequences
    assert ";" in constraints.stop_sequences
    assert "\n" in constraints.stop_sequences
    assert constraints.forbidden_newlines is True


def test_semicolon_only_does_not_forbid_newlines() -> None:
    ctx: CompletionContext = make_context(suffix=";")

    constraints: SuffixConstraints = SuffixConstraintAgent().analyze(ctx)

    assert ";" in constraints.stop_sequences
    assert "\n" not in constraints.stop_sequences
    assert constraints.forbidden_newlines is False


def test_empty_suffix_has_no_stop_sequences() -> None:
    ctx: CompletionContext = make_context(suffix="")

    constraints: SuffixConstraints = SuffixConstraintAgent().analyze(ctx)

    assert constraints.stop_sequences == []
    assert constraints.forbidden_newlines is False
