# AI LSP

An AI-powered Language Server Protocol implementation for intelligent code completion.

## Features

- AI-powered code completion using Ollama
- Clean architecture with LSP/AI separation
- Python 3.12+ support
- Extensible agent system

## Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies and project
poetry install

# Run the server
poetry run ai-lsp

# Alternative: Run directly
python -m ai_lsp.main

# Development mode with auto-reload (recommended for development)
python dev_server.py

# Development mode with debugpy
python dev_server.py --debug

# Or run in background
poetry run ai-lsp &
```

## Development

See [AGENTS.md](AGENTS.md) for comprehensive development guidelines.