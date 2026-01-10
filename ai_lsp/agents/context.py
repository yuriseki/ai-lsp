from ai_lsp.agents.base import AgentDecision, CompletionAgent
from ai_lsp.domain.completion import CompletionContext


class ContextPruningAgent(CompletionAgent):
    MAX_PREV_LINES = 20

    def before_generation(self, context: CompletionContext) -> AgentDecision:
        context.previous_lines = context.previous_lines[-self.MAX_PREV_LINES :]

        return AgentDecision()
