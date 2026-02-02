from typing import Any
from collections.abc import Callable

from mcp import Tool
from asgiref.sync import sync_to_async
from dataclasses import dataclass


@dataclass
class MCPTool:
    tool: Tool
    call: Callable[[str, dict[str, Any]], Any]
    related: Any


tools: dict[str, MCPTool] = {}


@sync_to_async(thread_sensitive=True)
def get_tools() -> dict[str, MCPTool]:
    if not tools:
        from . import __all__

        for module in __all__:
            mod = __import__(f"cms_mcp.tools.{module}", fromlist=[module])
            # Execute register_tools() in the module if it exists
            if hasattr(mod, "register_tools") and callable(
                getattr(mod, "register_tools")
            ):
                mod.register_tools()

    return tools
