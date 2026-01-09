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
    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        CompletionOptions(trigger_characters=[".", ":"], resolve_provider=False),
    )
    def on_completion(ls: LanguageServer, params: types.CompletionParams):
        items = [
            CompletionItem(label="hello_word", kind=CompletionItemKind.Text),
            CompletionItem(label="hello_ai", kind=CompletionItemKind.Text),
            CompletionItem(label="hello_lsp", kind=CompletionItemKind.Text),
        ]
        return CompletionList(is_incomplete=False, items=items)
