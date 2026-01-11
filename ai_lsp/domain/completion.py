from dataclasses import dataclass
from typing import List, Optional

from ai_lsp.agents.intent_types import EditIntent, EditIntentType
from ai_lsp.domain.semantics import PrefixSemantics

@dataclass
class CompletionContext:
    language: str
    file_path: str
    prefix: str
    suffix: str
    current_line: str
    previous_lines: List[str]
    next_lines: List[str]
    indentation: str
    line: int
    character: int
    intent: Optional[EditIntent] = None
    semantics: Optional[PrefixSemantics] = None
