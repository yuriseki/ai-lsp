from ai_lsp.ai.orchestrator.default_orchestrator import DefaultCompletionOrchestrator
from ai_lsp.ai.orchestrator.strategy import CompletionStrategy
from ai_lsp.ai.orchestrator.decision_input import CompletionDecisionInput

from ai_lsp.domain.completion import CompletionContext
from ai_lsp.domain.semantics import PrefixSemantics, ScopeType
from ai_lsp.domain.constraints import SuffixConstraints
from ai_lsp.agents.intent_types import EditIntent, EditIntentType


def make_input(
    *,
    intent_type: EditIntentType,
    intent_confidence: float = 0.9,
    constraint_confidence: float = 0.9,
    forbidden_newlines: bool = False,
    must_close: list[str] | None = None,
    framework: str | None = None,
) -> CompletionDecisionInput:

    return CompletionDecisionInput(
        context=CompletionContext(
            language="python",
            file_path="example.py",
            prefix="foo(",
            suffix="",
            completion_prefix="",
            current_line="foo(",
            previous_lines=["def foo(bar):"],
            next_lines=[],
            indentation="    ",
            line=1,
            character=4,
        ),
        intent=EditIntent(
            type=intent_type,
            confidence=intent_confidence,
            reason="test",
        ),
        semantics=PrefixSemantics(
            variables=["foo"],
            framework=framework,
            scope=ScopeType.FUNCTION,
            language="python",
        ),
        constraints=SuffixConstraints(
            must_not_repeat=[],
            must_close=must_close or [],
            forbidden_newlines=forbidden_newlines,
            confidence=constraint_confidence,
        ),
    )


def test_low_intent_confidence_blocks_completion():
    orchestrator = DefaultCompletionOrchestrator()

    decision = orchestrator.decide(
        make_input(
            intent_type=EditIntentType.SYMBOL_COMPLETION,
            intent_confidence=0.1,
        )
    )

    assert decision.should_complete is False
    assert decision.strategy is CompletionStrategy.NONE


def test_inline_completion_default():
    orchestrator = DefaultCompletionOrchestrator()

    decision = orchestrator.decide(
        make_input(
            intent_type=EditIntentType.SYMBOL_COMPLETION,
        )
    )

    assert decision.should_complete is True
    assert decision.strategy is CompletionStrategy.INLINE
    assert decision.allow_multiline is False


def test_block_downgraded_when_newlines_forbidden():
    orchestrator = DefaultCompletionOrchestrator()

    decision = orchestrator.decide(
        make_input(
            intent_type=EditIntentType.BLOCK_COMPLETION,
            forbidden_newlines=True,
        )
    )

    assert decision.should_complete is True
    assert decision.strategy is CompletionStrategy.INLINE


def test_block_downgraded_when_must_close_present():
    orchestrator = DefaultCompletionOrchestrator()

    decision = orchestrator.decide(
        make_input(
            intent_type=EditIntentType.BLOCK_COMPLETION,
            must_close=[")"],
        )
    )

    assert decision.strategy is CompletionStrategy.INLINE


def test_docstring_requires_rag_when_framework_present():
    orchestrator = DefaultCompletionOrchestrator()

    decision = orchestrator.decide(
        make_input(
            intent_type=EditIntentType.DOCSTRING,
            framework="drupal",
        )
    )

    assert decision.should_complete is True
    assert decision.strategy is CompletionStrategy.DOCSTRING
    assert decision.require_rag is True
