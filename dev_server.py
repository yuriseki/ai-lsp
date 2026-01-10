#!/usr/bin/env python3
"""
Development script for AI LSP server with auto-reload on code changes.
"""

import os
import sys
import time
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class LSPRestartHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.restart_server()

    def restart_server(self):
        # Terminate existing process if running
        if self.process and self.process.poll() is None:
            print("🔄 Stopping LSP server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing LSP server...")
                self.process.kill()
                self.process.wait()

        # Start new process
        print("🚀 Starting LSP server...")
        env = os.environ.copy()
        if 'DEBUG_AI_LSP' in os.environ:
            env['DEBUG_AI_LSP'] = os.environ['DEBUG_AI_LSP']

        self.process = subprocess.Popen(
            self.command,
            shell=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Print output in a separate thread
        def print_output():
            if self.process and self.process.stdout:
                try:
                    while True:
                        line = self.process.stdout.readline()
                        if not line:  # EOF reached
                            break
                        if line.strip():  # Only print non-empty lines
                            print(f"[LSP] {line.rstrip()}")
                except (OSError, ValueError, AttributeError):
                    # Process might have ended or stdout closed
                    pass

        threading.Thread(target=print_output, daemon=True).start()

    def on_modified(self, event):
        if event.src_path.endswith(('.py', '.md')) and not event.src_path.endswith('__pycache__'):
            print(f"📝 File changed: {event.src_path}")
            self.restart_server()


def main():
    # Default command to run
    command = "python -m ai_lsp.main"

    # Check for debug mode
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        os.environ['DEBUG_AI_LSP'] = '1'
        print("🐛 Debug mode enabled - LSP server will wait for DAP attachment")

    print("🔍 AI LSP Development Server")
    print("📁 Watching for file changes in ai_lsp/ directory...")
    print("🛑 Press Ctrl+C to stop")
    print()

    observer = None
    event_handler = None

    try:
        # Setup file watcher
        event_handler = LSPRestartHandler(command)
        observer = Observer()
        observer.schedule(event_handler, path="ai_lsp", recursive=True)
        observer.start()

        # Main loop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")
    except Exception as e:
        print(f"❌ Error in development server: {e}")
    finally:
        # Cleanup
        if observer:
            observer.stop()
        if event_handler and event_handler.process and event_handler.process.poll() is None:
            print("🔄 Terminating LSP server...")
            event_handler.process.terminate()
            try:
                event_handler.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing LSP server...")
                event_handler.process.kill()
        if observer:
            observer.join()
        print("✅ Development server stopped")


if __name__ == "__main__":
    main()
