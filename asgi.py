"""
Main ASGI application for Django + MCP Server.

Routes /mcp to the MCP ASGI app, all other paths to Django.
Run with: uvicorn asgi:application --reload
"""

import os
import django
from django.core.asgi import get_asgi_application

from cms_mcp.asgi import app as mcp_app

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ask_jenna.settings")
django.setup()

django_app = get_asgi_application()


async def application(scope, receive, send):
    """
    ASGI application that routes between Django and MCP server.

    - /mcp -> MCP Server (with full lifespan support)
    - Everything else -> Django
    """
    if scope["type"] == "lifespan":
        # Forward lifespan events to MCP app to initialize session manager
        await mcp_app(scope, receive, send)
    elif scope["type"] == "http" and scope["path"].startswith("/mcp"):
        await mcp_app(scope, receive, send)
    else:
        await django_app(scope, receive, send)
