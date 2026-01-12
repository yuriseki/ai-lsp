from dataclasses import dataclass

from ai_lsp.agents.intent_types import EditIntent
from ai_lsp.domain.completion import CompletionContext
from ai_lsp.domain.constraints import SuffixConstraints
from ai_lsp.domain.semantics import PrefixSemantics


@dataclass(frozen=True)
class CompletionDecisionInput:
    """
    Immutable input passed to the CompletionOrchestrator.
    """

    context: CompletionContext
    intent: EditIntent
    semantics: PrefixSemantics
    constraints: SuffixConstraints
