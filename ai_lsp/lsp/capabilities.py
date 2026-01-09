from lsprotocol import types
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
)
from pygls.lsp.server import LanguageServer

from ai_lsp.lsp.context_builder import CompletionContextBuilder
from ai_lsp.lsp.documents import DocumentStore


def register_capabilities(server: LanguageServer):
    documents = DocumentStore()
    context_builder = CompletionContextBuilder()

    register_documents(server, documents)
    register_completion(server, documents, context_builder)


def register_documents(server: LanguageServer, documents: DocumentStore):
    @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
    def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams):
        documents.open(params)

    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(ls: LanguageServer, params: types.DidChangeTextDocumentParams):
        documents.update(params, ls)


def register_completion(
    server: LanguageServer,
    documents: DocumentStore,
    context_builder: CompletionContextBuilder,
):
    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        CompletionOptions(trigger_characters=[".", ":", "a"], resolve_provider=False),
    )
    def on_completion(ls: LanguageServer, params: types.CompletionParams):
        uri = params.text_document.uri
        document = documents.get(uri)

        if not document:
            return CompletionList(is_incomplete=False, items=[])

        context = context_builder.build(document, params.position)

        items = [
            CompletionItem(
                label="debug_prefix",
                detail="debug_prefix:" + context.prefix,
            ),
            CompletionItem(
                label="debug_ident",
                detail="debug_ident:" + repr(context.identation),
            ),
            CompletionItem(
                label="debug_prev_lines",
                detail="debug_prev_lines:" + str(len(context.previous_lines)),
            ),
        ]

        return CompletionList(is_incomplete=False, items=items)
