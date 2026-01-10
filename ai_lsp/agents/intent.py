from ai_lsp.agents.base import AgentDecision, CompletionAgent

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
