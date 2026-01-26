# mcp_server.py

from mcp.server import Server

from django.conf import settings

server_name = getattr(settings, "MCP_SERVER_NAME", "managed-content-mcp")
instructions = getattr(
    settings,
    "MCP_SERVER_INSTRUCTIONS",
    """Provides programmatic access to the Content Management Platform including
content, configuration, project requirements, structure guidelines and style guidelines.
""",
)

server = Server(name=server_name, instructions=instructions)
