
You’re absolutely right to notice the mismatch — the *official docs on the repo and PyPI* are still strongly reflecting **pygls v1.x**, and the examples there don’t match the **v2 API** exactly. There *is* a fresh **version 2.0.0 released** with updated internals and updated handlers, and its docs are still stabilizing. ([pygls.readthedocs.io][1])

So before we go further, let’s **sync your Phase 1 implementation to the real pygls v2 API** as of the current stable release (2.0.0).

---

## 📌 Core differences in pygls v2 vs v1

The biggest APIs that shifted in version 2 are:

### 🧱 1. Handler registration

In v1 you did:

```python
@server.feature(COMPLETION, CompletionOptions(…))
def completions(params):
    …
```

In **v2 the recommended handler signature includes the server explicitly** and uses the new type definitions from `lsprotocol.types`.
That looks more like:

```python
@server.feature(types.TEXT_DOCUMENT_COMPLETION, CompletionOptions(...))
def on_completion(ls: LanguageServer, params: types.CompletionParams):
    …
```

This matches the snippet from the PyPI “quickstart” example. ([GitHub][2])

---

## 🛠 Updated Phase 1 Implementation (pygls v2)

Here’s a corrected, up-to-date skeleton for your project.

---

### 📦 1. Dependencies

Install pygls 2 and its required LSP types package:

```bash
poetry add pygls==2.0.0 lsprotocol
```

*`lsprotocol` is a peer dependency for LSP type definitions used in v2.* ([PyPI][3])

---

### 🧠 2. `main.py` — entry point

Same as before:

```python
# ai_lsp/main.py

from ai_lsp.lsp.server import create_server

def main():
    server = create_server()
    server.start_io()

if __name__ == "__main__":
    main()
```

---

### 🌀 3. `lsp/server.py`

```python
# ai_lsp/lsp/server.py

from pygls.lsp.server import LanguageServer

def create_server() -> LanguageServer:
    return LanguageServer("ai-lsp", "0.1.0")
```

No subclassing needed for now.

---

### 🚀 4. `lsp/capabilities.py` (complete for v2)

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

def register_capabilities(server: LanguageServer):

    @server.feature(types.TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=[".", ":"], resolve_provider=False))
    def on_completion(ls: LanguageServer, params: types.CompletionParams):
        items = [
            CompletionItem(label="hello_world", kind=CompletionItemKind.Text),
            CompletionItem(label="hello_ai", kind=CompletionItemKind.Text),
            CompletionItem(label="hello_lsp", kind=CompletionItemKind.Text),
        ]
        return CompletionList(is_incomplete=False, items=items)
```

Key notes here:

* We switched to use `types.TEXT_DOCUMENT_COMPLETION` from `lsprotocol.types`.
* Handler takes `(ls, params)` matching the v2 API. ([GitHub][2])

---

### 📁 5. Register handlers in your server

Update your bootstrap to actually import the handler code:

```python
# ai_lsp/lsp/server.py

from pygls.lsp.server import LanguageServer

def create_server() -> LanguageServer:
    server = LanguageServer("ai-lsp", "0.1.0")
    from ai_lsp.lsp.capabilities import register_capabilities
    register_capabilities(server)
    return server
```

---

## 🛠 Neovim Setup (unchanged)

Here’s the minimal `lspconfig` snippet again (same as before):

```lua
local lspconfig = require("lspconfig")
local configs = require("lspconfig.configs")

-- Check if the config already exists to prevent errors
if not configs.ai_lsp then
  configs.ai_lsp = {
    default_config = {
      cmd = {
        "/bin/bash",
        "-c",
        "cd /home/yuri/ssd2/project-files/Yuri/ai_lsp && source .venv/bin/activate && poetry run ai-lsp",
      },
      filetypes = { "python", "lua", "javascript", "typescript", "php" },
      root_dir = lspconfig.util.root_pattern(".git"), -- Marks the project root
      single_file_support = true,
      name = "ai_lsp",
    },
  }
end

require("lspconfig").ai_lsp.setup({
  -- Add any specific settings or on_attach function here
  on_attach = function(client, bufnr)
    -- Keymaps and other buffer-specific settings can go here
    -- Example: vim.keymap.set("n", "K", vim.lsp.buf.hover, { buffer = bufnr })
  end,
  capabilities = require("blink.cmp").get_lsp_capabilities(), -- If using blink.cmp
})```

---

## 🔍 Smoke Test Checklist (v2)

1. Start your server:

   ```bash
   poetry run ai-lsp
   ```

2. In Neovim, open any file and type something like:

   ```python
   foo.
   ```

3. Trigger completion (`<C-x><C-o>` or via nvim-cmp).
   You should see:

   ```
   hello_world
   hello_ai
   hello_lsp
   ```

---

## ✅ Verification you’re on pygls v2

Check that your installed version is exactly:

```bash
python - <<EOF
import pygls
print(pygls.__version__)
EOF
```

…and it outputs `2.0.0`. ([PyPI][3])

---

If you want, next we can:

✨ Build *document tracking* (`didOpen`, `didChange`),
✨ Add context gathering utilities,
✨ Wire up actual LLM responses via Ollama — all with *pygls v2 mechanics* solidly in place.

Just say the word — your AI LSP adventure continues 🚀✨

[1]: https://pygls.readthedocs.io/en/latest/changelog.html?utm_source=chatgpt.com "Changelog - pygls v2.0.0"
[2]: https://github.com/openlawlibrary/pygls?utm_source=chatgpt.com "GitHub - openlawlibrary/pygls: A pythonic generic language server"
[3]: https://pypi.org/project/pygls/?utm_source=chatgpt.com "pygls · PyPI"
