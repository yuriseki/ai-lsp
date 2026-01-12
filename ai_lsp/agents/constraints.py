import re
from ai_lsp.agents.base import CompletionAgent
from ai_lsp.domain.completion import CompletionContext
from ai_lsp.domain.constraints import SuffixConstraints

PAIRS = {
    ")": "(",
    "]": "[",
    "}": "{",
    '"': '"',
    "'": "'",
    "`": "`",
}

STRUCTURAL_CLOSERS = {")", "]", "}"}
NON_REPEATABLE_TOKENS = {")", "]", "}", ";", ","}


def _detect_closing_tokens(context: CompletionContext) -> list[str]:
    return [ch for ch in context.suffix if ch in STRUCTURAL_CLOSERS]

def _forbidden_newlines(context: CompletionContext) -> bool:
    return any(ch in STRUCTURAL_CLOSERS for ch in context.suffix)

def _extract_leading_tokens(context: CompletionContext) -> list[str]:
    tokens = []
    for ch in context.suffix:
        if ch in NON_REPEATABLE_TOKENS:
            tokens.append(ch)
        else:
            break  # stop at first non-token
    return tokens


class SuffixConstraintAgent(CompletionAgent):
    def analyze(self, context: CompletionContext) -> SuffixConstraints:
        must_close = _detect_closing_tokens(context)
        forbidden_newlines = _forbidden_newlines(context)
        must_not_repeat = _extract_leading_tokens(context)

        stop_sequences = []

        stop_sequences.extend(must_not_repeat)

        if forbidden_newlines:
            stop_sequences.append("\n")

        confidence = 0.9 if context.suffix.strip() else 0.5

        return SuffixConstraints(
            must_not_repeat=must_not_repeat,
            must_close=must_close,
            forbidden_newlines=forbidden_newlines,
            stop_sequences=stop_sequences,
            confidence=confidence,
        )
