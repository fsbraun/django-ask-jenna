"""
CMS MCP Tools package.

This package contains tool handlers for various Django CMS operations.
"""

from mcp import Tool
from . import create, plugins, placeholder, pool

__all__ = ["create", "plugins", "placeholder"]


from ..mcp_server import server

print("Register tools")


@server.list_tools()
async def list_tools() -> list[Tool]:
    try:
        tools = await pool.get_tools()
        mcp_tools = [tool.tool for tool in tools.values()]
        print("TOOLS ==> ", mcp_tools)
    except Exception:
        from traceback import print_exc

        print_exc()
        raise
    return mcp_tools


@server.call_tool()
async def call_tool(name: str, input_data: dict) -> dict:
    try:
        tool_obj = await pool.get_tools()
        tool = tool_obj.get(name)
        print(f"{name} ==> {tool}")
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        result = await tool.call(name, input_data)
        print("RESULT ==> ", result)
    except Exception:
        from traceback import print_exc

        print_exc()
        raise
    return result
