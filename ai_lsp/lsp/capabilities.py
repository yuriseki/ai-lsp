from lsprotocol import types
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    InsertTextMode,
    LogMessageParams,
    MessageType,
    Position,
    Range,
    TextEdit,
)
from pygls.lsp.server import LanguageServer

from ai_lsp.ai import engine
from ai_lsp.domain.completion import CompletionContext
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


def _calculate_replacement_range(context: CompletionContext, position: Position, completion: str) -> Range | None:
    """
    Calculate the text range that should be replaced by the completion.

    This implements intelligent diffing to find how much of the completion
    matches existing text before and after the cursor.
    """
    if not completion or not context.prefix:
        return None

    current_line = context.current_line

    # Clean completion (remove extra whitespace)
    completion = completion.strip()

    # Simple approach: replace from start of prefix match to cursor
    # This works well for most AI completion scenarios
    prefix = context.prefix.rstrip()

    if completion.startswith(prefix):
        # Replace from start of prefix to cursor
        start_char = position.character - len(prefix)
        if start_char >= 0:
            return Range(
                start=Position(line=position.line, character=start_char),
                end=Position(line=position.line, character=position.character)
            )

    return None


def register_completion(
    server: LanguageServer,
    documents: DocumentStore,
    context_builder: CompletionContextBuilder,
    engine: OllamaCOmpletionEngine,
):
    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        CompletionOptions(trigger_characters=[".", ":", "(", '"', "'"], resolve_provider=False),
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

        # Calculate intelligent replacement range
        replacement_range = _calculate_replacement_range(context, params.position, completion)

        if replacement_range:
            # Use textEdit for precise multi-line replacement
            item = CompletionItem(
                label=completion.strip().splitlines()[0][:80],
                kind=CompletionItemKind.Text,
                detail="AI_LSP\n" + completion.strip(),
                sort_text="000",
                preselect=True,
                text_edit=TextEdit(
                    range=replacement_range,
                    new_text=completion
                )
            )
        else:
            # Fallback to simple insert
            item = CompletionItem(
                label=completion.strip().splitlines()[0][:80],
                insert_text=completion,
                kind=CompletionItemKind.Text,
                detail="AI_LSP\n" + completion.strip(),
                sort_text="000",
                preselect=True,
            )

        return CompletionList(is_incomplete=False, items=[item])
