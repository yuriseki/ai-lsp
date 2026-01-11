from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ScopeType(str, Enum):
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    GLOBAL = "global"



@dataclass
class PrefixSemantics:
    variables: List[str]
    framework: Optional[str]
    scope: ScopeType
    language: str
