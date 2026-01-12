from dataclasses import dataclass
from typing import List

@dataclass
class SuffixConstraints:
    must_not_repeat: List[str]
    must_close: List[str]
    forbidden_newlines: bool
    confidence: float
