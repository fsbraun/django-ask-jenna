"""
CMS Placeholder tool handlers.

Provides functionality for listing and managing CMS placeholders.
"""

from typing import Any


def handle_tool(tool_name: str, params: dict[str, Any], request) -> dict[str, Any]:
    """
    Route tool calls to the appropriate handler function.

    Args:
        tool_name: Name of the tool (e.g., 'cms_placeholder_list')
        params: Tool parameters
        request: Django request object

    Returns:
        Tool execution result
    """
    if tool_name == "cms_placeholder_list":
        return list_placeholders(params, request)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def list_placeholders(params: dict[str, Any], request) -> dict[str, Any]:
    """
    List placeholders for a page or all placeholders.

    Args:
        params: Optional page_id filter
        request: Django request object

    Returns:
        List of placeholders with basic information
    """
    try:
        from cms.models import Placeholder, Page

        page_id = params.get("page_id")

        result = []

        if page_id:
            # Get placeholders for a specific page
            page = Page.objects.get(pk=page_id)
            placeholders = page.get_placeholders()
        else:
            # Get all placeholders
            placeholders = Placeholder.objects.all()

        for placeholder in placeholders:
            # Get plugin count
            plugin_count = placeholder.get_plugins().count()

            placeholder_data = {
                "id": placeholder.pk,
                "slot": placeholder.slot,
                "default_width": placeholder.default_width,
                "plugin_count": plugin_count,
            }

            # Try to get associated page info if available
            if hasattr(placeholder, "page") and placeholder.page:
                placeholder_data["page_id"] = placeholder.page.pk
                placeholder_data["page_title"] = placeholder.page.get_title()

            result.append(placeholder_data)

        return {"placeholders": result, "count": len(result)}

    except ImportError:
        return {"error": "Django CMS not installed", "placeholders": [], "count": 0}
    except Exception as e:
        raise Exception(f"Error listing placeholders: {str(e)}")
