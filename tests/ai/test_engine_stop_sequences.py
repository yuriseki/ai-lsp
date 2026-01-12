import json
from typing import Any, Dict
from unittest.mock import patch, MagicMock

from ai_lsp.ai.ollama_client import OllamaCompletionEngine
from ai_lsp.domain.completion import CompletionContext


def make_context(*, suffix: str) -> CompletionContext:
    return CompletionContext(
        language="php",
        file_path="test.php",
        prefix="",
        suffix=suffix,
        completion_prefix="",
        current_line="",
        previous_lines=[],
        next_lines=[],
        indentation="",
        line=0,
        character=0,
    )


@patch("ai_lsp.ai.ollama_client.requests.post")
def test_engine_passes_stop_sequences_to_ollama(mock_post: MagicMock) -> None:
    # mock Ollama response
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = [
        json.dumps({"response": "do_something("}).encode()
    ]
    mock_post.return_value = mock_response

    engine: OllamaCompletionEngine = OllamaCompletionEngine()
    ctx: CompletionContext = make_context(suffix=")")

    for agent in engine.agents:
        if hasattr(agent, "analyze"):
            engine._blocking_complete(ctx, agent.analyze(ctx))  # type: ignore[arg-type]

            assert mock_post.called

            _, kwargs = mock_post.call_args
            payload: Dict[str, Any] = kwargs["json"]

            assert "options" in payload
            assert "stop" in payload["options"]
            assert ")" in payload["options"]["stop"]
