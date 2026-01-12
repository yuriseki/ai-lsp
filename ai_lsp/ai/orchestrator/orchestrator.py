from abc import abstractclassmethod
from typing import Protocol

from ai_lsp.ai.orchestrator.decision import CompletionDecision
from ai_lsp.ai.orchestrator.decision_input import CompletionDecisionInput


class CompletionOrchestrator(Protocol):
    """
    Responsible for turning multiple analysis signals into a single completion
    decision.

    This layer must be deterministic and side-effect free.
    """

    @abstractclassmethod
    def decide(
        self,
        input: CompletionDecisionInput,
    ) -> CompletionDecision:
        raise NotImplementedError
