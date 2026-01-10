from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class CompletionContext:
    language: str
    file_path: str
    prefix: str
    current_line: str
    previous_lines: List[str]
    next_lines: List[str]
    identation: str
    line: int
    character: int
