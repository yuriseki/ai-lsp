from typing import Optional

from ai_lsp.agents.base import AgentDecision, CompletionAgent
from ai_lsp.domain.completion import CompletionContext


class OutputGuardAgent(CompletionAgent):
    def before_generation(self, context: CompletionContext) -> AgentDecision:
        # This agent does not block or modify generation upfront.
        return AgentDecision()

    def on_token(self, token: str) -> Optional[AgentDecision]:
        if "```" in token:
            return AgentDecision(stop_generation=True)
        return None
