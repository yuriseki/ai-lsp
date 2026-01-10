from abc import ABC, abstractmethod
from typing import Optional

from ai_lsp.domain.completion import CompletionContext


class AgentDecision:
    def __init__(
        self,
        allowed: bool = True,
        reason: Optional[str] = None,
        modified_prompt: Optional[str] = None,
        stop_generation: bool = False,
    ):
        self.allowed = allowed
        self.reason = reason
        self.modified_prompt = modified_prompt
        self.stop_generation = stop_generation

class CompletionAgent(ABC):
    @abstractmethod
    def before_generation(
        self,
        context: CompletionContext,
    ) -> AgentDecision:
        return AgentDecision()
    
    def on_token(self, token: str) -> Optional[AgentDecision]:
        return None

    def after_generation(
        self,
        context: CompletionContext,
        completion: str,
    ) -> Optional[str]:
       return completion

