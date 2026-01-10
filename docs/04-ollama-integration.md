
Alright 😄 Phase 4 is where the magic *enters* the system — **carefully, politely, and behind a clean interface**.

We’re going to add Ollama in a way that:

* keeps your LSP fast
* keeps AI swappable
* keeps agents possible (but not yet)
* stays debuggable

No clever tricks yet. Just **correctness + boundaries**.

---

# Phase 4 – Ollama-powered completion (no agents yet)

## Goal (definition of done)

By the end of this phase:

* `CompletionContext` is converted into a prompt
* An **AI Engine interface** exists
* An **Ollama adapter** implements it
* LSP autocomplete returns **LLM-generated text**
* Still works in Neovim with `.` / `:`

---

## 1. Architectural rule (very important)

From now on:

```
LSP → CompletionContext → AI Engine → Ollama
```

### Hard rule

❌ LSP code must NOT know:

* model name
* temperature
* Ollama URLs
* prompt wording

All of that lives in `ai/`.

---

## 2. AI Engine port (interface)

Create `ai/engine.py`.

```python
# ai_lsp/ai/engine.py

from abc import ABC, abstractmethod
from ai_lsp.domain.completion import CompletionContext


class CompletionEngine(ABC):
    @abstractmethod
    def complete(self, context: CompletionContext) -> str:
        """Return a code completion string"""
        raise NotImplementedError
```

This is your **port**.
Everything else is replaceable.

---

## 3. Ollama adapter (HTTP client)

Create `ai/ollama_client.py`.

```python
# ai_lsp/ai/ollama_client.py

import requests
from ai_lsp.ai.engine import CompletionEngine
from ai_lsp.domain.completion import CompletionContext


class OllamaCompletionEngine(CompletionEngine):
    def __init__(
        self,
        model: str = "codellama:7b",
        base_url: str = "http://localhost:11434",
        timeout: int = 10,
    ):
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def complete(self, context: CompletionContext) -> str:
        prompt = self._build_prompt(context)

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 64,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "").strip()

    def _build_prompt(self, context: CompletionContext) -> str:
        previous = "\n".join(context.previous_lines)

        return f"""
You are a code autocomplete engine.
Return ONLY the completion text.
No explanations. No markdown.

Language: {context.language}
File: {context.file_path}

Context:
{previous}

Current line:
{context.current_line}

Prefix:
{context.prefix}

Completion:
""".strip()
```

### Notes

* `stream: False` keeps things simple
* Low temperature = deterministic
* `num_predict` small = fast
* Prompt is intentionally **boring and strict**

We’ll improve it later.

---

## 4. Wire AI engine into the LSP

Now we connect the dots.

### Update `capabilities.py`

Add imports:

```python
from ai_lsp.ai.ollama_client import OllamaCompletionEngine
```

Inside `register_capabilities`:

```python
engine = OllamaCompletionEngine()
```

Update registration calls:

```python
register_completion(server, documents, context_builder, engine)
```

---

### Update completion handler signature

```python
def register_completion(
    server,
    documents,
    context_builder,
    engine,
):
```

---

### Replace hardcoded completions

```python
def on_completion(ls, params):
    uri = params.text_document.uri
    document = documents.get(uri)

    if not document:
        return CompletionList(is_incomplete=False, items=[])

    context = context_builder.build(document, params.position)

    try:
        completion = engine.complete(context)
    except Exception as e:
        ls.show_message_log(f"Ollama error: {e}")
        return CompletionList(is_incomplete=False, items=[])

    if not completion:
        return CompletionList(is_incomplete=False, items=[])

    item = CompletionItem(
        label=completion.strip().splitlines()[0][:80],
        insert_text=completion,
        kind=CompletionItemKind.Text,
    )

    return CompletionList(is_incomplete=False, items=[item])
```

---

## 5. Add dependency

```bash
poetry add requests
```

---

## 6. Smoke test (critical)

### Preconditions

* Ollama running:

  ```bash
  ollama serve
  ```
* Model pulled:

  ```bash
  ollama pull codellama:7b
  ```

### Test in Neovim

```python
user.
```

Expected:

* 0.5–2s delay (normal)
* A **real completion**
* Inserted exactly where cursor is

If yes → **Phase 4 complete** ✅🔥

---

## 7. Known limitations (intentional)

Right now:

* ❌ blocking HTTP call (we’ll async later)
* ❌ single suggestion
* ❌ no filtering / validation
* ❌ no cancellation
* ❌ no agents

This is *correct* for this phase.

---

## 8. What you’ve built so far (zoom out)

You now have:

```
Neovim
  → LSP (pygls v2)
      → DocumentStore
          → CompletionContextBuilder
              → CompletionContext
                  → AI Engine
                      → Ollama
```

This is **production-grade architecture**, even if the behavior is still simple.

---

## Next step (where it becomes “your” system)

### ▶ Phase 5 – Agents for completion reasoning

We’ll introduce:

* a `CompletionAgent`
* optional sub-agents:

  * context pruning
  * intent detection
  * safety filter
* multi-step reasoning **without bloating the LSP**

Alternatively, if you prefer:

* async + cancellation
* streaming completions
* Neovim UX improvements (ghost text)

Say the word:

> **“Let’s do Phase 5 (agents)”**
> or
> **“Let’s fix latency + async first”**

You’re doing *excellent* work here.
