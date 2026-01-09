
Yesss 😄 Phase 3 is where this stops being “an LSP that works” and starts becoming **an AI-ready system**.

We’ll be very deliberate here, because this object will live *forever* in your architecture.

---

# Phase 3 – Completion Context Builder

## Goal (definition of done)

By the end of this phase, you will have:

* A **domain-level `CompletionContext`**
* Zero LSP types leaking into AI/agent layers
* A clean **context builder** that:

  * takes `(Document, Position)`
  * returns structured, AI-friendly data
* Completion handler using this context (still hardcoded completions)

👉 After this phase, plugging in Ollama is just a service call.

---

## 1. Design principles (important)

This is *not* an LSP object.

Rules:

* ❌ No `lsprotocol` types
* ❌ No pygls imports
* ❌ No Neovim assumptions
* ✅ Pure Python dataclasses
* ✅ Easy to serialize / log / store

Think:

> “If I dump this to JSON, an agent could reason over it.”

---

## 2. Define the domain model

Create `domain/completion.py`.

```python
# ai_lsp/domain/completion.py

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CompletionContext:
    language: str
    file_path: str
    prefix: str
    current_line: str
    previous_lines: List[str]
    next_lines: List[str]
    indentation: str
```

### Why these fields?

* `language` → model behavior
* `file_path` → framework hints
* `prefix` → what to complete
* `current_line` → formatting decisions
* `previous_lines` → local reasoning
* `next_lines` → optional, but useful
* `indentation` → snippet correctness

This is intentionally **LLM-shaped**, not editor-shaped.

---

## 3. Context builder (single responsibility)

Create `lsp/context_builder.py`.

```python
# ai_lsp/lsp/context_builder.py

from ai_lsp.domain.completion import CompletionContext
from ai_lsp.lsp.documents import Document
from lsprotocol import types
import os
import re


class CompletionContextBuilder:
    def __init__(self, max_lines: int = 10):
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

        indentation = self._extract_indentation(full_line)

        previous_lines = lines[
            max(0, line_index - self.max_lines) : line_index
        ]

        next_lines = lines[
            line_index + 1 : line_index + 1 + self.max_lines
        ]

        return CompletionContext(
            language=document.language_id,
            file_path=self._uri_to_path(document.uri),
            prefix=prefix,
            current_line=full_line,
            previous_lines=previous_lines,
            next_lines=next_lines,
            indentation=indentation,
        )

    def _extract_indentation(self, line: str) -> str:
        match = re.match(r"\s*", line)
        return match.group(0) if match else ""

    def _uri_to_path(self, uri: str) -> str:
        if uri.startswith("file://"):
            return uri.replace("file://", "")
        return uri
```

### Notes

* This is where LSP knowledge **ends**
* If later you want tree-sitter, it plugs here
* `max_lines` is a tunable knob

---

## 4. Wire context builder into completion

Now update your completion handler.

### Update `capabilities.py`

```python
from ai_lsp.lsp.context_builder import CompletionContextBuilder
```

Inside `register_capabilities`:

```python
context_builder = CompletionContextBuilder()
```

Update `register_completion` signature:

```python
def register_completion(
    server: LanguageServer,
    documents: DocumentStore,
    context_builder: CompletionContextBuilder,
):
```

Call it like this:

```python
register_completion(server, documents, context_builder)
```

---

### Updated completion handler

```python
def register_completion(server, documents, context_builder):

    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        CompletionOptions(trigger_characters=[".", ":"], resolve_provider=False),
    )
    def on_completion(ls, params):
        uri = params.text_document.uri
        document = documents.get(uri)

        if not document:
            return CompletionList(is_incomplete=False, items=[])

        context = context_builder.build(document, params.position)

        # Phase 3: prove context is correct
        items = [
            CompletionItem(
                label="debug_prefix",
                detail=context.prefix,
            ),
            CompletionItem(
                label="debug_indent",
                detail=repr(context.indentation),
            ),
            CompletionItem(
                label="debug_prev_lines",
                detail=str(len(context.previous_lines)),
            ),
        ]

        return CompletionList(is_incomplete=False, items=items)
```

---

## 5. Smoke test (very important)

Try these scenarios:

### Case 1

```python
user.na|
```

* `debug_prefix` → `user.na`
* `debug_indent` → `""`

### Case 2

```python
    user.na|
```

* `debug_indent` → `"    "`

### Case 3

Multi-line context:

```python
def foo():
    user.na|
```

* `debug_prev_lines` → `1`

If all pass → **Phase 3 complete** ✅

---

## 6. What we now have (this is big)

You now have a **clean boundary**:

```
LSP  →  DocumentStore
        → CompletionContextBuilder
            → CompletionContext (domain)
                → AI / Agents (next)
```

From here on:

* LSP doesn’t grow in complexity
* AI can evolve independently
* You can log, cache, diff, store contexts

This matches *exactly* how Sofia evolved — no surprise there 😉

---

## 7. Next step (natural and exciting)

### ▶ Phase 4 – Ollama AI Engine (no agents yet)

We will:

* Create `ai/engine.py` (LLM port)
* Create `ai/ollama_client.py` (adapter)
* Convert `CompletionContext → prompt`
* Return **one clean completion**

No agents yet — just correctness and latency.

Say:

> **“Let’s do Phase 4”**

or, if you want:

> **“I want to tweak the context model first”**

You’re building something *serious* here 🚀
