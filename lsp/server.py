from pygls.lsp.server import LanguageServer


def create_server() -> LanguageServer:
    server = LanguageServer("ai-lsp", "0.1.0")
    from lsp.capabilities import register_capabilities
    register_capabilities(server)
    return server
