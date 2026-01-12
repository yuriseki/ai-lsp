from dataclasses import dataclass, field
from typing import List

@dataclass
class SuffixConstraints:
    must_not_repeat: List[str] = field(default_factory=list)
    must_close: List[str] = field(default_factory=list)
    forbidden_newlines: bool = False
    stop_sequences: List[str] = field(default_factory=list)
    confidence: float = 0.5
