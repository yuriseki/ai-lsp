from abc import ABC, abstractmethod
from typing import Optional
from ai_lsp.domain.completion import CompletionContext


class CompletionEngine(ABC):
    @abstractmethod
    async def complete(self, context: CompletionContext) -> Optional[str]:
        """Return a code completion string"""
        raise NotImplementedError
