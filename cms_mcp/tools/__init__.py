"""
CMS MCP Tools package.

This package contains tool handlers for various Django CMS operations.
"""

from mcp import Tool
from . import create, plugins, placeholder, media, pool

__all__ = ["create", "plugins", "placeholder", "media"]


from ..mcp_server import server


@server.list_tools()
async def list_tools() -> list[Tool]:
    return list(pool.tools.values())


@server.call_tool()
async def call_tool(name: str, input_data: dict) -> dict:
    tool = pool.tools.get(name)
    if not tool:
        raise ValueError(f"Tool '{name}' not found")
    return await tool.call(input_data)
