from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    CompletionList,
    CompletionItem,
    CompletionItemKind,
    CompletionOptions,
)
from lsprotocol import types

from ai_lsp.lsp.documents import DocumentStore


def register_capabilities(server: LanguageServer):
    documents = DocumentStore()

    register_documents(server, documents)
    register_completion(server, documents)


def register_documents(server: LanguageServer, documents: DocumentStore):
    @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams):
        documents.open(params)

    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: LanguageServer, params: types.DidChangeTextDocumentParams):
        documents.update(params)


def register_completion(server: LanguageServer, documents: DocumentStore):
    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        CompletionOptions(trigger_characters=[".", ":"], resolve_provider=False),
    )
    def on_completion(ls: LanguageServer, params: types.CompletionParams):
        uri = params.text_document.uri
        position = params.position

        document = documents.get(uri)
        if not document:
            return CompletionList(is_incomplete=False, items=[])

        # Extract current line
        lines = document.text.splitlines()
        line_index = min(position.line, len(lines) - 1)
        full_line = lines[line_index]
        char_index = min(position.character, len(full_line))
        prefix = full_line[:char_index]

        items = [
            CompletionItem(
                label="hello_word",
                kind=CompletionItemKind.Text,
                detail=f"Line: {prefix}",
            ),
            CompletionItem(
                label="hello_ai",
                kind=CompletionItemKind.Text,
                detail=f"Lang: {document.language_id}",
            ),
        ]

        return CompletionList(is_incomplete=False, items=items)
