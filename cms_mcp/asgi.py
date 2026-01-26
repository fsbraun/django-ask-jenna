"""
MCP Server ASGI Application.

Returns a fully-configured ASGI application for the MCP server with
streamable HTTP transport, session management, and all protocol support.
"""

import logging
from mcp.server.models import InitializationOptions
from mcp.server.transport_security import TransportSecuritySettings

from .mcp_handlers import server

logger = logging.getLogger(__name__)


def get_mcp_application():
    """
    Get a fully-configured ASGI application for the MCP server.

    Returns a Starlette ASGI app with:
    - StreamableHTTP protocol support (POST/GET/DELETE)
    - JSON-RPC message handling
    - Session management with MCP session IDs
    - SSE streaming for server-initiated messages
    - Transport security (DNS rebinding protection for localhost)
    - Debug logging enabled for development

    Usage:
        # Run with uvicorn:
        uvicorn cms_mcp.asgi:app

        # Or with daphne:
        daphne cms_mcp.asgi:app
    """

    # Configure transport security for local development
    # Auto-enables DNS rebinding protection for localhost (IPv4, IPv6)
    transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "127.0.0.1:*",
            "localhost:*",
            "[::1]:*",
        ],
        allowed_origins=[
            "http://127.0.0.1:*",
            "http://localhost:*",
            "http://[::1]:*",
        ],
    )

    # Build the streamable HTTP ASGI app with full protocol support
    mcp_app = server.streamable_http_app(
        streamable_http_path="/mcp/",      # Path where MCP protocol is served
        json_response=True,                # Use SSE streaming (True for JSON POST/response only)
        stateless_http=True,               # Stateful sessions (True for stateless init)
        event_store=None,                  # Optional: EventStore for event resumability
        retry_interval=None,               # Optional: SSE retry interval in ms
        transport_security=transport_security,
        host="127.0.0.1",
        auth=None,                         # Optional: AuthSettings for OAuth/bearer tokens
        token_verifier=None,               # Optional: TokenVerifier for auth
        auth_server_provider=None,         # Optional: OAuth server provider
        custom_starlette_routes=None,      # Optional: Additional routes
        debug=True,                        # Enable debug logging
    )

    logger.info("MCP Server ASGI app configured:")
    logger.info("  Path: /mcp/")
    logger.info("  Protocol: Streamable HTTP with JSON")
    logger.info("  Transport Security: DNS rebinding protection enabled")
    logger.info("  Sessions: Stateful")

    return mcp_app


mcp_app = get_mcp_application()


def rounte_mcp(func):
    async def wrapper(scope, receive, send):
        if scope['type'] == 'http' and scope.get('path') == '/mcp/' or scope['type'] == 'lifespan':
            return await mcp_app(scope, receive, send)
        # All other requests go to Django
        return await func(scope, receive, send)
    return wrapper
