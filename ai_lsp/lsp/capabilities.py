from lsprotocol import types
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    LogMessageParams,
    MessageType,
)
from pygls.lsp.server import LanguageServer

from ai_lsp.ai import engine
from ai_lsp.ai.ollama_client import OllamaCOmpletionEngine
from ai_lsp.domain import completion
from ai_lsp.lsp.context_builder import CompletionContextBuilder
from ai_lsp.lsp.documents import DocumentStore


def register_capabilities(server: LanguageServer):
    documents = DocumentStore()
    context_builder = CompletionContextBuilder()
    engine = OllamaCOmpletionEngine()

    register_documents(server, documents)
    register_completion(server, documents, context_builder, engine)


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
    engine: OllamaCOmpletionEngine,
):
    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        # CompletionOptions(trigger_characters=[".", ":"], resolve_provider=False),
        CompletionOptions(trigger_characters=None, resolve_provider=False),
    )
    def on_completion(ls: LanguageServer, params: types.CompletionParams):
        uri = params.text_document.uri
        document = documents.get(uri)

        if not document:
            return CompletionList(is_incomplete=False, items=[])

        context = context_builder.build(document, params.position)

        try:
            completion = engine.complete(context)
        except Exception as e:
            message = LogMessageParams(
                type=MessageType.Error, message=f"Ollama error: {e}"
            )

            ls.window_log_message(message)
            return CompletionList(is_incomplete=False, items=[])

        if not completion:
            return CompletionList(is_incomplete=False, items=[])

        item = CompletionItem(
            label=completion.strip().splitlines()[0][:80],
            insert_text=completion,
            kind=CompletionItemKind.Text,
            detail="AI_LSP",
        )

        return CompletionList(is_incomplete=False, items=[item])
