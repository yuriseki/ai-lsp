from ai_lsp.domain.completion import CompletionContext
from ai_lsp.lsp.documents import Document
from lsprotocol import types
import os
import re


class CompletionContextBuilder:
    def __init__(self, max_lines: int = 10) -> None:
        self.max_lines = max_lines

    def build(
        self,
        document: Document,
        position: types.Position,
    ) -> CompletionContext:
        lines = document.text.splitlines()

        line_index = min(position.line, len(lines) - 1)
        full_line = lines[line_index]

        char_index = min(position.character, len(full_line))
        prefix = full_line[:char_index]
        suffix = full_line[char_index:]

        indentation = self._extract_indentation(full_line)

        previous_lines = lines[max(0, line_index - self.max_lines) : line_index]
        next_lines = lines[line_index + 1 : line_index + 1 + self.max_lines]

        return CompletionContext(
            language=document.language_id,
            file_path=self._uri_to_path(document.uri),
            prefix=prefix,
            suffix=suffix,
            completion_prefix=self._extract_completion_prefix(prefix),
            current_line=full_line,
            previous_lines=previous_lines,
            next_lines=next_lines,
            indentation=indentation,
            line=position.line,
            character=position.character,
        )

    def _extract_indentation(self, line: str) -> str:
        match = re.match(r"^\s*", line)
        return match.group(0) if match else ""

    def _uri_to_path(self, uri: str) -> str:
        if uri.startswith("file://"):
            return uri.replace("file://", "")

        return uri

    def _extract_completion_prefix(self, line_prefix: str) -> str:
        match = re.search(r"[A-Za-z0-9_]+$", line_prefix)
        return match.group(0) if match else ""
