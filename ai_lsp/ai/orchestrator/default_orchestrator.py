from __future__ import annotations

from ai_lsp.agents.intent_types import EditIntentType
from ai_lsp.ai.orchestrator.decision import CompletionDecision
from ai_lsp.ai.orchestrator.decision_input import CompletionDecisionInput
from ai_lsp.ai.orchestrator.orchestrator import CompletionOrchestrator
from ai_lsp.ai.orchestrator.strategy import CompletionStrategy
from ai_lsp.domain.semantics import ScopeType


class DefaultCompletionOrchestrator(CompletionOrchestrator):
    """
    Deterministic orchestration layer that merges agent signals into a single
    completion decision.

    This class must:
    - be side-effect free
    - never call LLMs or RAG
    -- be fully unit-testable
    """

    MIN_INTENT_CONFIDENCE: float = 0.35
    MIN_CONSTRAINT_CONFIDENCE: float = 0.30

    def decide(self, input: CompletionDecisionInput) -> CompletionDecision:
        intent = input.intent
        semantics = input.semantics
        constraints = input.constraints

        # ----------------------------------------------------------------------
        # 1. Hard blockers (confidence based)
        # ----------------------------------------------------------------------
        if intent.confidence < self.MIN_INTENT_CONFIDENCE:
            return self._no_completion(intent.confidence, "Intent confidence too low")

        if constraints.confidence < self.MIN_CONSTRAINT_CONFIDENCE:
            return self._no_completion(
                constraints.confidence, "Suffix constraints confidence too low"
            )

        # ----------------------------------------------------------------------
        # 2. Intent -> strategy
        # ----------------------------------------------------------------------
        strategy = self._strategy_from_intent(intent.type)

        if strategy is CompletionStrategy.NONE:
            return self._no_completion(
                intent.confidence,
                "Intent does not map to a completion strategy",
            )
        #
        # ----------------------------------------------------------------------
        # 3. Defaults
        # ----------------------------------------------------------------------
        allow_multiline = strategy in {
            CompletionStrategy.BLOCK,
            CompletionStrategy.DOCSTRING,
        }

        max_tokens = self._default_max_tokens(strategy)

        # ----------------------------------------------------------------------
        # 4. Constraint enforcement (derived)
        # ----------------------------------------------------------------------
        if constraints.forbidden_newlines:
            allow_multiline = False
            if strategy is CompletionStrategy.BLOCK:
                strategy = CompletionStrategy.INLINE

        if constraints.must_close and strategy is CompletionStrategy.BLOCK:
            # Cursor in inside an open structure -> safer inline.
            strategy = CompletionStrategy.INLINE
            allow_multiline = False

        # ----------------------------------------------------------------------
        # 5. Semantic refinement
        # ----------------------------------------------------------------------
        if semantics.scope in {ScopeType.FUNCTION, ScopeType.METHOD}:
            max_tokens = min(max_tokens, 120)

        # ----------------------------------------------------------------------
        # 6. Rag hint (decision only)
        # ----------------------------------------------------------------------
        require_rag = (
            strategy in {CompletionStrategy.BLOCK, CompletionStrategy.DOCSTRING}
            and semantics.framework is not None
        )

        # ----------------------------------------------------------------------
        # 7. Final decision
        # ----------------------------------------------------------------------
        return CompletionDecision(
            should_complete=True,
            strategy=strategy,
            confidence=intent.confidence,
            max_tokens=max_tokens,
            allow_multiline=allow_multiline,
            require_rag=require_rag,
            explanation=self._explain(strategy, require_rag, intent.reason),
        )

    # ----------------------------------------------------------------------
    # Internal Helpers
    # ----------------------------------------------------------------------
    def _strategy_from_intent(
        self,
        intent_type: EditIntentType,
    ) -> CompletionStrategy:
        return {
            EditIntentType.SYMBOL_COMPLETION: CompletionStrategy.INLINE,
            EditIntentType.ARGUMENT_COMPLETION: CompletionStrategy.INLINE,
            EditIntentType.INLINE_COMPLETION: CompletionStrategy.INLINE,
            EditIntentType.BLOCK_COMPLETION: CompletionStrategy.BLOCK,
            EditIntentType.DOCSTRING: CompletionStrategy.DOCSTRING,
        }.get(intent_type, CompletionStrategy.NONE)

    def _default_max_tokens(
        self,
        strategy: CompletionStrategy,
    ) -> int:
        return {
            CompletionStrategy.INLINE: 24,
            CompletionStrategy.BLOCK: 160,
            CompletionStrategy.DOCSTRING: 200,
            CompletionStrategy.REFACTOR_SNIPPET: 120,
        }.get(strategy, 0)

    def _no_completion(
        self,
        confidence: float,
        reason: str,
    ) -> CompletionDecision:
        return CompletionDecision(
            should_complete=False,
            strategy=CompletionStrategy.NONE,
            confidence=confidence,
            max_tokens=0,
            allow_multiline=False,
            require_rag=False,
            explanation=reason,
        )

    def _explain(
        self,
        strategy: CompletionStrategy,
        require_rag: bool,
        intent_reason: str,
    ) -> str:
        base = f"{strategy.value} completion ({intent_reason})"
        if require_rag:
            return f"{base}; framework context detected"
        return base
