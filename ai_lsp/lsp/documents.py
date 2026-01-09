from dataclasses import dataclass
from typing import Dict
from lsprotocol import types
from pygls.lsp.server import LanguageServer


@dataclass
class Document:
    uri: str
    language_id: str
    version: int
    text: str


class DocumentStore:
    def __init__(self):
        self._documents: Dict[str, Document] = {}

    def open(self, params: types.DidOpenTextDocumentParams) -> None:
        doc = params.text_document
        self._documents[doc.uri] = Document(
            uri=doc.uri,
            language_id=doc.language_id,
            version=doc.version,
            text=doc.text,
        )

    def update(
        self, params: types.DidChangeTextDocumentParams, ls: LanguageServer
    ) -> None:
        uri = params.text_document.uri
        text_doc = ls.workspace.get_text_document(uri)
        document = self._documents.get(uri)

        if not document:
            return

        document.text = text_doc.source
        document.version = params.text_document.version

    def get(self, uri: str) -> Document | None:
        return self._documents.get(uri)
