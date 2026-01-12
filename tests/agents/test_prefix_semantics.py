import pytest
from ai_lsp.agents.semantics import PrefixSemanticAgent
from ai_lsp.domain.completion import CompletionContext
from ai_lsp.lsp.capabilities import make_inline_edit


def make_context(
    *,
    prefix="",
    suffix="",
    current_line="",
    previous_lines=[],
    next_lines=[],
    indentation="",
    language="",
    completion_prefix="",
):
    return CompletionContext(
        language=language,
        file_path="test.php",
        prefix=prefix,
        suffix=suffix,
        completion_prefix=completion_prefix,
        current_line=current_line,
        previous_lines=previous_lines,
        next_lines=next_lines,
        indentation=indentation,
        line=0,
        character=len(prefix),
    )


def test_php_variable_extraction():
    ctx = make_context(
        prefix="$a = $node->getTitle(); $b = ",
        language="php",
    )

    semantics = PrefixSemanticAgent().analyze(ctx)

    assert "$a" in semantics.variables
    assert "$node" in semantics.variables


def test_drupal_detection():
    ctx = make_context(
        prefix="\\Drupal::service('foo')",
        language="php",
    )

    semantics = PrefixSemanticAgent().analyze(ctx)

    assert semantics.framework == "drupal"


def test_scope_detection():
    ctx = make_context(
        prefix="class A {\n    function foo() {",
        language="php",
    )

    semantics = PrefixSemanticAgent().analyze(ctx)

    assert semantics.scope == "function"


def test_completion_replaces_only_token():
    ctx = make_context(
        prefix="CompletionStrategy.B",
        completion_prefix="B",
    )

    edit = make_inline_edit(ctx, "BLOCK")

    assert edit.range.start.character == len("CompletionStrategy.")
