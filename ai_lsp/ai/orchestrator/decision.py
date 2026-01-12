from dataclasses import dataclass

from ai_lsp.ai.orchestrator.strategy import CompletionStrategy

@dataclass(frozen=True)
class CompletionDecision:
    """
    Final, inspectable decision produced by the orchestration layer.
    """
    should_complete: bool
    strategy: CompletionStrategy
    confidence: float # 0.0 - 1.0
    max_tokens: int
    allow_multiline: bool
    require_rag: bool
    explanation: str
    



