from sys import prefix
from typing import Optional
from ai_lsp.agents.base import CompletionAgent
from ai_lsp.domain.completion import CompletionContext
from ai_lsp.domain.semantics import PrefixSemantics, ScopeType
import re

_VAR_PATTERNS = {
    "php": re.compile(r"\$[a-zA-Z_][a-zA-Z0-9_]*"),
    "python": re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
}

def _extract_variables(context: CompletionContext) -> list[str]:
    pattern = _VAR_PATTERNS.get(context.language)
    if not pattern:
        return []

    vars = pattern.findall(context.prefix)
    return list(dict.fromkeys(vars)) # preserve order, remove duplication

def _detect_framework(context: CompletionContext) -> Optional[str]:
    if "\\Drupal::" in context.prefix or "use Drupal\\" in context.prefix:
        return "drupal"
    elif "Symfony\\" in context.prefix:
        return "symfony"

    return None

def _detect_scope(context: CompletionContext) -> ScopeType:
    if context.language == "python":
        if "def " in context.prefix:
            return ScopeType.FUNCTION
        elif "class " in context.prefix:
            return ScopeType.CLASS
    elif context.language == "php":
        if "function " in context.prefix:
            return ScopeType.FUNCTION
        elif "class " in context.prefix:
            return ScopeType.CLASS
    
    return ScopeType.GLOBAL

class PrefixSemanticAgent(CompletionAgent):
    def analyze(self, context: CompletionContext) -> PrefixSemantics:
        variables = _extract_variables(context)
        framework = _detect_framework(context)
        scope = _detect_scope(context)

        return PrefixSemantics(
            variables=variables,
            framework=framework,
            scope=scope,
            language=context.language or "",
        )
