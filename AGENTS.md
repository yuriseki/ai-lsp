# AGENTS.md - Development Guidelines for AI LSP

This document provides comprehensive guidelines for development in the AI LSP project. It covers build, lint, and test commands, as well as detailed code style and architectural guidelines.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Build Commands](#build-commands)
3. [Test Commands](#test-commands)
4. [Lint and Format Commands](#lint-and-format-commands)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Architecture Guidelines](#architecture-guidelines)
7. [Import Organization](#import-organization)
8. [Error Handling](#error-handling)
9. [Type Hints](#type-hints)
10. [Naming Conventions](#naming-conventions)
11. [Documentation Standards](#documentation-standards)
12. [Commit Message Guidelines](#commit-message-guidelines)

## Development Environment Setup

This project uses Python 3.12+ with Poetry for dependency management.

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate

# Install dependencies and project
poetry install

# Install dev dependencies for debugging
poetry install --with dev

# Run the LSP server
poetry run ai-lsp

# Alternative: Run directly
python -m ai_lsp.main

# Debug mode: Run with debugpy (requires Neovim DAP attachment)
DEBUG_AI_LSP=1 python -m ai_lsp.main

# Development mode with auto-reload (recommended for development)
python dev_server.py

# Development mode with debugpy
python dev_server.py --debug

# Or run in background
poetry run ai-lsp &
```

**Note:** The virtual environment is located in `.venv/` and should be activated before running any Poetry commands.

## Build Commands

### Full Build
```bash
# Install all dependencies
poetry install

# Build the project (if needed for distribution)
poetry build
```

### Development Build
```bash
# Install development dependencies
poetry install --with dev

# Update dependencies
poetry update
```

## Test Commands

### Run All Tests
```bash
# Run complete test suite
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=ai_lsp --cov-report=html
```

### Run Single Test
```bash
# Run specific test file
poetry run pytest tests/test_file.py

# Run specific test function
poetry run pytest tests/test_file.py::test_function_name

# Run tests matching pattern
poetry run pytest -k "test_pattern"
```

### Test Options
```bash
# Run tests in verbose mode
poetry run pytest -v

# Run tests with detailed output
poetry run pytest -s

# Run tests and stop on first failure
poetry run pytest -x

# Run tests in parallel (if pytest-xdist is available)
poetry run pytest -n auto
```

## Lint and Format Commands

### Code Formatting
```bash
# Format code with Black
black .

# Check formatting without changes
black --check .

# Sort imports with isort
isort .

# Check import sorting
isort --check-only .
```

### Linting
```bash
# Lint with Ruff (fast, comprehensive)
ruff check .

# Lint and auto-fix issues
ruff check --fix .

# Lint specific file
ruff check path/to/file.py
```

### Type Checking
```bash
# Type check with mypy
mypy .

# Type check specific file
mypy path/to/file.py

# Strict type checking
mypy --strict .
```

### Combined Quality Checks
```bash
# Run all quality checks
black --check . && isort --check-only . && ruff check . && mypy .

# Auto-fix everything possible
black . && isort . && ruff check --fix .
```

## Debugging

### Debug the LSP Server

The AI LSP server can be debugged using Python's debugpy and Neovim DAP.

#### Setup
```bash
# Install debug dependencies
poetry install --with dev

# Start server in debug mode (waits for debugger attachment)
DEBUG_AI_LSP=1 python -m ai_lsp.main
```

#### In Neovim
1. Open any Python file in your project
2. Use `:DapContinue` or your DAP UI to attach to the LSP server
3. Select "Python: Attach to AI LSP" configuration
4. Set breakpoints in your LSP server code
5. The server will pause when breakpoints are hit

## Completion Processing

The LSP server automatically processes AI completions to ensure they integrate properly with the editor:

### Text Cleaning
- **Markdown Removal**: Strips code block markers (````) and language tags
- **Prefix Deduplication**: Removes text that duplicates what's already before the cursor
- **Indentation Handling**: Handles cases where LLM uses different indentation than existing code
- **Structure Preservation**: Maintains newlines and indentation for proper code formatting

### Example Processing
```
Input:  '```python\n  def sum(a, b):\n    return a + b\n```'
Prefix: '  def sum(a, b)'
Output: ':\n    return a + b'
```

**Processing Example:**
```
Input:  'def calculate(a, b):\n    return a + b'
Prefix: 'def calculate'
Output: Replaces 'def calculate' with full function definition
```

**TextEdit Replacement:**
```
Before:     def calculate|
After:      def calculate(a, b):
                return a + b
```

### Indentation Handling
The prefix removal logic intelligently handles indentation differences:
- **Exact match**: Removes identical prefix text
- **Indentation normalization**: Handles cases where LLM uses different indentation
- **Smart deduplication**: Only removes prefix when it clearly duplicates existing text

### Context-Aware Completion
The LSP server provides intelligent completion based on cursor context:
- **Normal text**: Standard prefix removal and insertion
- **Prefix deduplication**: Removes text that already exists before cursor
- **Intelligent Replacement**: Uses `textEdit` to replace appropriate text ranges
- **Multi-line Support**: Handles indented multi-line completions correctly
- **Indentation Adjustment**: Automatically adjusts continuation line indentation
- **Ghost Text Support**: Completions appear as inline faded suggestions
- **Trigger Characters**: Auto-complete on `.`, `:`, `(`, `"`, `'`

### Ghost Text Configuration

Completions appear as ghost text when configured in your editor:

```lua
-- In blink.cmp config
completion = {
  ghost_text = {
    show_with_menu = true,
    show_without_menu = true, -- Show even without completion menu
  },
  trigger = {
    show_on_keyword = true,
    show_on_trigger_character = true,
  },
}
```

### Debug Commands
```vim
:DapContinue          " Start/continue debugging
:DapStepOver          " Step over
:DapStepInto          " Step into
:DapStepOut           " Step out
:DapToggleBreakpoint  " Toggle breakpoint
:DapTerminate         " Stop debugging
```

### Development Server with Auto-Reload

The development server automatically restarts when you modify Python or Markdown files:

```bash
# Basic development mode (auto-reload)
python dev_server.py

# Debug mode with auto-reload (for DAP debugging)
python dev_server.py --debug

# Manual restart (if needed)
# Modify any .py or .md file in ai_lsp/ directory
```

**Features:**
- 🔄 Auto-restarts on file changes
- 📝 Watches `.py` and `.md` files
- 🐛 Supports debug mode for DAP
- 📊 Shows LSP server output
- 🛑 Graceful shutdown with Ctrl+C

## Code Style Guidelines

### Python Standards

- Follow PEP 8 style guidelines
- Use Black for consistent formatting (88 character line length)
- Use isort for import organization
- Use Ruff for fast, comprehensive linting
- Use mypy for static type checking

### Code Formatting Rules

```python
# Good: Black-formatted, clean
def calculate_completion_score(
    context: CompletionContext,
    suggestion: str,
    user_preferences: UserPrefs,
) -> float:
    """Calculate relevance score for completion suggestion."""
    base_score = len(suggestion) * 0.1
    context_bonus = 0.5 if context.has_imports else 0.0
    return base_score + context_bonus

# Bad: Poor formatting, hard to read
def calculate_completion_score(context,suggestion,user_preferences):
    base_score=len(suggestion)*0.1
    context_bonus=0.5 if context.has_imports else 0.0
    return base_score+context_bonus
```

### Import Organization

```python
# Standard library imports first
import asyncio
import json
from typing import Dict, List, Optional

# Third-party imports
from lsprotocol.types import CompletionItem
import ollama

# Local imports - grouped by package
from ai.engine import AIEngine
from domain.completion import CompletionRequest
from lsp.capabilities import register_capabilities
```

## Architecture Guidelines

### Project Structure

```
ai_lsp/
├── ai_lsp/                    # Main package
│   ├── __init__.py
│   ├── main.py               # Entry point
│   ├── lsp/                  # LSP protocol layer
│   │   ├── __init__.py
│   │   ├── server.py         # pygls setup
│   │   ├── capabilities.py   # LSP handlers
│   │   └── documents.py      # Text tracking
│   ├── domain/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── completion.py     # Completion models
│   │   └── context.py        # Context models
│   ├── agents/               # Reasoning agents layer
│   │   ├── __init__.py
│   │   ├── base.py           # Agent interfaces
│   │   ├── completion_agent.py
│   │   └── context_agent.py
│   └── ai/                   # AI integration layer
│       ├── __init__.py
│       ├── engine.py         # AI interface/port
│       ├── ollama_client.py  # Ollama adapter
│       └── prompts/          # Prompt templates
│           └── completion.md
├── pyproject.toml           # Project configuration
├── README.md               # Project documentation
├── AGENTS.md              # Development guidelines
└── poetry.lock            # Dependency lock file
```

### Clean Architecture Layers

This project follows clean architecture principles with strict separation of concerns:

### Key Architectural Rules

1. **LSP never knows about AI**: LSP layer handles JSON-RPC protocol only
2. **AI never knows about LSP**: AI layer provides generic completion interface
3. **Agents are reasoning units**: Each agent has single responsibility
4. **Domain models are pure**: No external dependencies in domain layer
5. **Dependencies flow inward**: Outer layers depend on inner layers, never vice versa

### Component Design

```python
# Good: Clear separation, single responsibility
class CompletionAgent:
    """Handles completion logic and decision making."""

    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine

    def get_completions(self, context: CompletionContext) -> List[CompletionItem]:
        """Get completion suggestions for given context."""
        # Agent logic here
        pass

# Bad: Mixed responsibilities, tight coupling
class CompletionHandler:
    """Bad example - mixes LSP, AI, and business logic."""

    def handle_completion(self, lsp_params):
        # Direct LSP handling
        # Direct AI calls
        # Business logic
        # Everything mixed together
        pass
```

## Import Organization

### Import Style Guidelines

```python
# 1. Standard library imports (alphabetically sorted)
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party imports (alphabetically sorted)
from lsprotocol.types import CompletionItem, CompletionList
import ollama

# 3. Local imports (grouped by package, then alphabetically)
# Domain models first
from domain.completion import CompletionRequest, CompletionResult
from domain.context import CompletionContext

# Then agents
from agents.completion_agent import CompletionAgent

# Then AI layer
from ai.engine import AIEngine

# Finally LSP layer (rarely imported in inner layers)
from lsp.capabilities import register_capabilities
```

### Import Anti-patterns to Avoid

```python
# Bad: Wildcard imports
from lsprotocol.types import *

# Bad: Relative imports in complex hierarchies
from ...domain.completion import CompletionRequest

# Bad: Circular imports
# file_a.py imports file_b.py
# file_b.py imports file_a.py

# Bad: Import at top level when only used in functions
import expensive_module  # Only used in one function
```

## Error Handling

### Exception Handling Patterns

```python
# Good: Specific exception handling
def get_completion_suggestions(context: CompletionContext) -> List[str]:
    """Get completion suggestions with proper error handling."""
    try:
        response = self.ai_engine.generate_completion(context)
        return self._parse_response(response)
    except ConnectionError as e:
        logger.warning(f"AI service unavailable: {e}")
        return self._get_fallback_suggestions(context)
    except ValidationError as e:
        logger.error(f"Invalid completion response: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in completion: {e}")
        return []

# Bad: Bare except clause
def bad_error_handling():
    try:
        # some code
        pass
    except:  # Never do this
        pass
```

### Custom Exceptions

```python
# Define custom exceptions in domain layer
class AIError(Exception):
    """Base class for AI-related errors."""
    pass

class AIServiceUnavailableError(AIError):
    """Raised when AI service is not available."""
    pass

class InvalidPromptError(AIError):
    """Raised when prompt validation fails."""
    pass
```

### Logging Guidelines

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Warning about potential issues")
logger.error("Error that doesn't stop execution")
logger.critical("Critical error requiring immediate attention")
```

## Type Hints

### Type Annotation Standards

```python
# Good: Comprehensive type hints
from typing import Dict, List, Optional, Union

def process_completion_request(
    request: CompletionRequest,
    timeout: Optional[float] = None,
) -> Union[CompletionResult, None]:
    """Process a completion request with timeout."""
    pass

class CompletionAgent:
    """Agent for handling code completions."""

    def __init__(self, ai_engine: AIEngine) -> None:
        self.ai_engine = ai_engine
        self._cache: Dict[str, List[str]] = {}

    def get_suggestions(
        self,
        context: CompletionContext,
        max_suggestions: int = 5,
    ) -> List[CompletionItem]:
        """Get completion suggestions."""
        pass
```

### Generic Types

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Result(Generic[T]):
    """Generic result container."""

    def __init__(self, value: T, error: Optional[str] = None):
        self.value = value
        self.error = error

    @property
    def is_success(self) -> bool:
        return self.error is None
```

## Naming Conventions

### General Naming Rules

```python
# Classes: PascalCase
class CompletionAgent:
class AIEngine:
class CompletionContext:

# Functions and methods: snake_case
def get_completion_suggestions():
def calculate_relevance_score():
def validate_completion_request():

# Variables: snake_case
completion_context = CompletionContext()
max_suggestions = 5
is_valid_request = True

# Constants: UPPER_SNAKE_CASE
MAX_COMPLETION_LENGTH = 100
DEFAULT_TIMEOUT = 5.0

# Private members: leading underscore
class CompletionAgent:
    def __init__(self):
        self._cache = {}
        self._ai_engine = None

    def _validate_context(self, context):
        pass
```

### File and Module Naming

```python
# Module files: snake_case
completion_agent.py
ai_engine.py
lsp_server.py

# Package directories: snake_case
ai_lsp/
├── agents/
├── domain/
├── lsp/
└── ai/

# Test files: test_*.py
tests/
├── test_completion_agent.py
├── test_ai_engine.py
└── test_lsp_server.py
```

### Domain-Specific Naming

```python
# LSP-related
completion_item: CompletionItem
completion_list: CompletionList
text_document: TextDocument

# AI-related
prompt_template: str
model_response: Dict
inference_config: InferenceConfig

# Agent-related
reasoning_context: ReasoningContext
decision_strategy: DecisionStrategy
```

## Documentation Standards

### Docstring Format

```python
def get_completion_suggestions(
    context: CompletionContext,
    max_suggestions: int = 5,
) -> List[CompletionItem]:
    """
    Get completion suggestions for the given context.

    Analyzes the completion context including cursor position,
    surrounding code, and available symbols to generate relevant
    code completion suggestions.

    Args:
        context: The completion context containing cursor position,
                file content, and language information.
        max_suggestions: Maximum number of suggestions to return.
                        Defaults to 5.

    Returns:
        List of CompletionItem objects representing the suggestions,
        sorted by relevance score.

    Raises:
        AIServiceUnavailableError: If the AI service is not available.
        InvalidContextError: If the completion context is invalid.

    Example:
        >>> context = CompletionContext(...)
        >>> suggestions = agent.get_completion_suggestions(context)
        >>> len(suggestions) <= 5
        True
    """
    pass

class CompletionAgent:
    """
    Intelligent agent for generating code completion suggestions.

    This agent coordinates between the LSP layer and AI engine to provide
    contextually relevant code completions. It analyzes the completion
    context, decides on the appropriate completion strategy, and filters
    suggestions for quality and relevance.

    Attributes:
        ai_engine: The AI engine used for generating completions.
        cache: Internal cache for performance optimization.
    """

    def __init__(self, ai_engine: AIEngine):
        """
        Initialize the completion agent.

        Args:
            ai_engine: Configured AI engine for completion generation.
        """
        pass
```

### Code Comments

```python
# Good: Explain why, not what
def calculate_relevance_score(suggestion: str, context: CompletionContext) -> float:
    """Calculate relevance score for a completion suggestion."""
    # Weight longer suggestions higher, as they're often more specific
    length_score = min(len(suggestion) / 20.0, 1.0)

    # Boost score if suggestion matches existing symbols
    symbol_bonus = 0.3 if suggestion in context.available_symbols else 0.0

    # Context relevance based on surrounding code patterns
    context_score = self._analyze_context_relevance(suggestion, context)

    return length_score + symbol_bonus + context_score

# Bad: Redundant comments
def calculate_score(suggestion, context):
    # Calculate the score
    score = len(suggestion) * 0.1  # Multiply length by 0.1
    return score  # Return the score
```

## Commit Message Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(completion): Add support for multi-line completions

Implement multi-line completion suggestions that span multiple
lines of code. This improves completion quality for complex
code constructs like function definitions and class declarations.

Closes #123

fix(ai-engine): Handle connection timeouts gracefully

Add proper timeout handling for Ollama API calls to prevent
the LSP server from hanging when the AI service is slow.

fix: Correct import statement in completion_agent.py

The import was incorrectly referencing a non-existent module.
```

### Commit Best Practices

- Keep subject line under 50 characters
- Use imperative mood ("Add" not "Added")
- Reference issues when applicable
- Separate subject from body with blank line
- Explain what and why, not just what

---

## Tool Configurations

### Black Configuration
```ini
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### isort Configuration
```ini
# pyproject.toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["ai_lsp"]
```

### mypy Configuration
```ini
# pyproject.toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = "lsprotocol.*"
ignore_missing_imports = true
```

### Ruff Configuration
```ini
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501", # line too long (handled by black)
    "B008", # do not perform function calls in argument defaults
    "C901", # too complex
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/**/*" = ["B011"]  # assert false
```

This comprehensive guide ensures consistent, maintainable, and high-quality code across the AI LSP project. Follow these guidelines to maintain the clean architecture and development standards established for this codebase.