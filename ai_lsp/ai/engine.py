from abc import ABC, abstractmethod
from ai_lsp.domain.completion import CompletionContext

class CompletionEngine(ABC):
    @abstractmethod
    async def complete(self, context: CompletionContext) -> str:
        """Return a code completion string"""
        raise NotImplementedError
