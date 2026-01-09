import os
import sys
from ai_lsp.lsp.server import create_server


def main():
    # Check if we're in debug mode
    if os.getenv("DEBUG_AI_LSP"):
        print("🔧 AI LSP Server starting in DEBUG mode")
        print("📡 Waiting for debugger to attach on port 5678...")
        # Enable debugpy if in debug mode
        try:
            import debugpy  # type: ignore
            debugpy.listen(("127.0.0.1", 5678))
            debugpy.wait_for_client()
            print("🎯 Debugger attached! Continuing...")
        except ImportError:
            print("❌ debugpy not available - install with: poetry install --with dev")

    server = create_server()
    server.start_io()


if __name__ == "__main__":
    main()
