from dataclasses import dataclass
from enum import Enum


class EditIntentType(str, Enum):
    INLINE_COMPLETION = "inline_completion"
    ARGUMENT_COMPLETION = "argument_completion"
    BLOCK_COMPLETION = "block_completion"
    DOCSTRING = "docstring"
    SYMBOL_COMPLETION = "symbol_completion"
    UNKNOW = "unknow"


@dataclass
class EditIntent:
    type: EditIntentType
    confidence: float
    reason: str
