
Nice 😄 that’s the *exact* milestone you want before moving forward.
Now we level up in a **non-flashy but crucial** way.

---

# Phase 2 – Document & text tracking (pygls v2–correct)

## Goal (definition of done)

By the end of this phase, your LSP will:

* Track opened documents
* Track incremental text changes
* Know **current file text**
* Know **cursor position**
* Be able to extract **surrounding context**

👉 Still **no AI**, but now the LSP actually *understands* what the user is editing.

This phase is what separates “autocomplete toy” from “AI-ready system”.

---

## 1. Architectural intent (why this phase matters)

Autocomplete requests (`textDocument/completion`) do **not** include full document text.

The LSP model is:

* Text is pushed via:

  * `didOpen`
  * `didChange`
* Completion *pulls* context from **your internal state**

So we need:

```
LSP Events ──▶ DocumentStore ──▶ Completion Context
```

---

## 2. Document storage strategy (simple & correct)

We’ll introduce a **DocumentStore**, responsible for:

* Holding full document text
* Updating on changes
* Exposing read-only helpers

### Design rules

* One responsibility
* No LSP types leaking outside
* Easy to swap later (tree-sitter, rope, etc.)

---

## 3. Implement `documents.py`

```python
# ai_lsp/lsp/documents.py

from dataclasses import dataclass
from typing import Dict
from lsprotocol import types


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

    def update(self, params: types.DidChangeTextDocumentParams) -> None:
        uri = params.text_document.uri
        document = self._documents.get(uri)

        if not document:
            return

        # Phase 2: assume full text sync
        for change in params.content_changes:
            document.text = change.text

        document.version = params.text_document.version

    def get(self, uri: str) -> Document | None:
        return self._documents.get(uri)
```

### Important (intentional simplification)

* We assume **full document sync**
* This matches Neovim’s default behavior
* Incremental ranges come later *if needed*

---

## 4. Register document lifecycle handlers

Now we wire this into pygls.

### Update `capabilities.py`

```python
# ai_lsp/lsp/capabilities.py

from pygls.lsp.server import LanguageServer
from pygls.lsp.types import (
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
```

Now your server is **stateful**.

---

## 5. Use document context in completion

Let’s minimally *prove* it works.

### Update completion handler

```python
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
        line = lines[position.line] if position.line < len(lines) else ""

        items = [
            CompletionItem(
                label="hello_world",
                kind=CompletionItemKind.Text,
                detail=f"Line: {line.strip()}",
            ),
            CompletionItem(
                label="hello_ai",
                kind=CompletionItemKind.Text,
                detail=f"Lang: {document.language_id}",
            ),
        ]

        return CompletionList(is_incomplete=False, items=items)
```

---

## 6. Smoke test (important)

Open a file, type:

```python
user.
```

Trigger completion.

You should now see:

* Completion items
* With `detail` reflecting:

  * current line text
  * language ID

If yes → **document tracking works** ✅

---

## 7. What we have now (this is big)

At this point, your LSP knows:

* ✔ Which file is open
* ✔ Its full content
* ✔ Cursor position
* ✔ Language
* ✔ When text changes

This is **everything an AI needs** to reason.

---

## 8. What we *still* are not doing (on purpose)

* ❌ Symbol extraction
* ❌ AST parsing
* ❌ Project-wide context
* ❌ LLM calls
* ❌ Agents

We’re still building the spine.

---

## Next step (strong recommendation)

### 🔥 Phase 3 – Completion Context Builder

This is where we:

* formalize a `CompletionContext` domain object
* extract:

  * prefix token
  * surrounding lines
  * indentation
  * file path
* **prepare the exact input** an LLM or agent will consume

After Phase 3, plugging Ollama becomes trivial.

Say:

* **“Let’s do Phase 3”**
  or
* **“I want to adjust the document model first”**

We’re right on track 🚀
