from ai_lsp.agents.base import AgentDecision, CompletionAgent

from ai_lsp.agents.intent_types import EditIntent, EditIntentType
from ai_lsp.domain.completion import CompletionContext


class CompletionIntentAgent(CompletionAgent):
    MIN_PREFIX = 2

    def before_generation(self, context: CompletionContext) -> AgentDecision:
        prefix = context.prefix.strip()

        if len(prefix) < self.MIN_PREFIX:
            return AgentDecision(
                allowed=False,
                reason="Prefix too short",
            )

        if prefix.isdigit():
            return AgentDecision(
                allowed=False,
                reason="Numeric-only prefix",
            )

        return AgentDecision()


def is_argument_completion(context: CompletionContext) -> bool:
    prefix = context.prefix
    suffix = context.suffix
    # e.g., `foo(|bar)`
    return "(" in prefix and ")" in suffix and prefix.rfind("(") > prefix.rfind(")")


def _is_block_completion(context: CompletionContext) -> bool:
    # e.g.
    # def foo():
    #     |
    return (
        context.current_line.strip() == ""
        and len(context.indentation) > 0
        and not context.suffix.strip()
    )


def _is_docstring(context: CompletionContext) -> bool:
    if context.language == "python":
        return (
            '"""' in context.prefix
            and '"""' in context.suffix
            and context.prefix.count('"""') % 2 == 1
        )
    elif (
        context.language == "php"
        or context.language == "javascript"
        or context.language == "typescript"
    ):
        return "/**" in context.prefix and "*/" in context.suffix
    else:
        return False


def _is_symbol_completion(context: CompletionContext) -> bool:
    return context.prefix.rstrip().endswith((".", "->", "::", "$"))


class CursorWindowIntentAgent(CompletionAgent):
    def detect_intent(self, context: CompletionContext) -> EditIntent:
        if _is_docstring(context):
            return EditIntent(
                type=EditIntentType.DOCSTRING,
                confidence=0.9,
                reason="Cursor inside docstring block",
            )

        if is_argument_completion(context):
            return EditIntent(
                type=EditIntentType.ARGUMENT_COMPLETION,
                confidence=0.85,
                reason="Cursor inside parentheses",
            )

        if _is_block_completion(context):
            return EditIntent(
                type=EditIntentType.BLOCK_COMPLETION,
                confidence=0.8,
                reason="Empty indent line",
            )

        if _is_symbol_completion(context):
            return EditIntent(
                type=EditIntentType.SYMBOL_COMPLETION,
                confidence=0.7,
                reason="Member access or symbol trigger",
            )

        return EditIntent(
            type=EditIntentType.INLINE_COMPLETION,
            confidence=0.5,
            reason="Fallback inline completion",
        )
