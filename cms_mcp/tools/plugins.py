"""
CMS Plugins tool handlers.

Provides functionality for listing, creating, and managing CMS plugins.
"""

from typing import Any


def handle_tool(tool_name: str, params: dict[str, Any], request) -> dict[str, Any]:
    """
    Route tool calls to the appropriate handler function.

    Args:
        tool_name: Name of the tool (e.g., 'cms_plugins_list')
        params: Tool parameters
        request: Django request object

    Returns:
        Tool execution result
    """
    if tool_name == "cms_plugins_list":
        return list_plugins(params, request)
    elif tool_name == "cms_plugins_create":
        return create_plugin(params, request)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def list_plugins(params: dict[str, Any], request) -> dict[str, Any]:
    """
    List plugins in a placeholder or all plugins.

    Args:
        params: Optional placeholder_id filter
        request: Django request object

    Returns:
        List of plugins with basic information
    """
    try:
        from cms.models import CMSPlugin

        plugins = CMSPlugin.objects.all()

        # Apply filters if provided
        placeholder_id = params.get("placeholder_id")
        if placeholder_id:
            plugins = plugins.filter(placeholder_id=placeholder_id)

        result = []
        for plugin in plugins:
            plugin_data = {
                "id": plugin.pk,
                "plugin_type": plugin.plugin_type,
                "placeholder_id": plugin.placeholder_id,
                "position": plugin.position,
                "language": plugin.language,
                "parent_id": plugin.parent_id,
            }
            result.append(plugin_data)

        return {"plugins": result, "count": len(result)}

    except ImportError:
        return {"error": "Django CMS not installed", "plugins": [], "count": 0}
    except Exception as e:
        raise Exception(f"Error listing plugins: {str(e)}")


def create_plugin(params: dict[str, Any], request) -> dict[str, Any]:
    """
    Create a new CMS plugin.

    Args:
        params: Must include placeholder_id, plugin_type, optional language, position, data
        request: Django request object

    Returns:
        Created plugin information
    """
    placeholder_id = params.get("placeholder_id")
    plugin_type = params.get("plugin_type")

    if not placeholder_id or not plugin_type:
        raise ValueError("placeholder_id and plugin_type are required")

    try:
        from cms.api import add_plugin
        from cms.models import Placeholder

        placeholder = Placeholder.objects.get(pk=placeholder_id)
        language = params.get("language", "en")
        position = params.get("position", "last-child")
        plugin_data = params.get("data", {})

        plugin = add_plugin(
            placeholder=placeholder,
            plugin_type=plugin_type,
            language=language,
            position=position,
            **plugin_data,
        )

        result = {
            "id": plugin.pk,
            "plugin_type": plugin.plugin_type,
            "placeholder_id": plugin.placeholder_id,
            "position": plugin.position,
            "language": plugin.language,
            "success": True,
        }

        return result

    except ImportError:
        raise Exception("Django CMS not installed")
    except Exception as e:
        raise Exception(f"Error creating plugin: {str(e)}")


def get_all_plugins(request) -> dict[str, Any]:
    """
    Get all plugins as a resource.

    Args:
        request: Django request object

    Returns:
        All plugins data
    """
    return list_plugins({}, request)
