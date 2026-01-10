from lsprotocol import types
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    LogMessageParams,
    MessageType,
    Position,
    Range,
    TextEdit,
)
from pygls.lsp.server import LanguageServer

from ai_lsp.domain.completion import CompletionContext
from ai_lsp.ai.ollama_client import OllamaCOmpletionEngine
from ai_lsp.lsp.context_builder import CompletionContextBuilder
from ai_lsp.lsp.documents import DocumentStore
import asyncio
from typing import Dict


def make_inline_edit(
    context: CompletionContext,
    completion_text: str,
) -> types.TextEdit:
    """
    Create a TextEdit suitable for inline (ghost text) completion.

    The edit inserts text at the cursor position without deleting existing
    content.
    """
    # start and end are the same for now.
    start = types.Position(
        line=context.line,
        character=context.character,
    )
    end = types.Position(
        line=context.line,
        character=context.character,
    )

    return types.TextEdit(
        range=types.Range(
            start=start,
            end=end,
        ),
        new_text=completion_text,
    )


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
    active_tasks: Dict[str, asyncio.Task] = {}

    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        CompletionOptions(
            trigger_characters=[".", ":", "(", '"', "'"], resolve_provider=False
        ),
    )
    async def on_completion(ls: LanguageServer, params: types.CompletionParams):
        uri = params.text_document.uri
        document = documents.get(uri)

        if not document:
            return CompletionList(is_incomplete=False, items=[])

        context = context_builder.build(document, params.position)

        # Guard: avoid LLM spam
        if len(context.prefix.strip()) < 2:
            return CompletionList(is_incomplete=True, items=[])

        # Cancel previous task for this document.
        previsous_task = active_tasks.get(uri)
        if previsous_task and not previsous_task.done():
            previsous_task.cancel()

        async def run_completion():
            return await engine.complete(context)

        task = asyncio.create_task(run_completion())
        active_tasks[uri] = task

        try:
            completion = await task
        except asyncio.CancelledError:
            return CompletionList(is_incomplete=True, items=[])
        except Exception as e:
            message = LogMessageParams(
                type=MessageType.Error, message=f"Ollama error: {e}"
            )

            ls.window_log_message(message)
            return CompletionList(is_incomplete=False, items=[])

        if not completion:
            return CompletionList(is_incomplete=False, items=[])

        edit = types.TextEdit(
            range=types.Range(
                start=types.Position(line=context.line, character=len(context.prefix)),
                end=types.Position(
                    line=context.line,
                    character=len(context.current_line),
                ),
            ),
            new_text=completion,
        )

        item = CompletionItem(
            label=completion.strip().splitlines()[0][:80],
            kind=CompletionItemKind.Text,
            detail="AI_LSP\n" + completion.strip(),
            sort_text="0", # Make it the first item.
            preselect=True,
            text_edit=edit,
            insert_text_format=types.InsertTextFormat.PlainText,
        )

        return CompletionList(is_incomplete=False, items=[item])
