from enum import Enum

class CompletionStrategy(str, Enum):
    NONE = "none"
    INLINE = "inline"
    BLOCK = "block"
    DOCSTRING = "docstring"
    REFACTOR_SNIPPET = "refactor_snippet"



