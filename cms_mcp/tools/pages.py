"""
CMS Pages tool handlers.

Provides functionality for listing, creating, and managing CMS pages.
"""

from typing import Dict, Any


def handle_tool(tool_name: str, params: Dict[str, Any], request) -> Dict[str, Any]:
    """
    Route tool calls to the appropriate handler function.

    Args:
        tool_name: Name of the tool (e.g., 'cms_pages_list')
        params: Tool parameters
        request: Django request object

    Returns:
        Tool execution result
    """
    if tool_name == "cms_pages_list":
        return list_pages(params, request)
    elif tool_name == "cms_pages_get":
        return get_page(params, request)
    elif tool_name == "cms_pages_create":
        return create_page(params, request)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def list_pages(params: Dict[str, Any], request) -> Dict[str, Any]:
    """
    List all CMS pages.

    Args:
        params: Optional filters (site_id, language)
        request: Django request object

    Returns:
        List of pages with basic information
    """
    try:
        from cms.models import Page

        pages = Page.objects.all()

        # Apply filters if provided
        site_id = params.get("site_id")
        if site_id:
            pages = pages.filter(node__site_id=site_id)

        language = params.get("language")

        result = []
        for page in pages:
            page_data = {
                "id": page.pk,
                "node_id": page.node_id,
                "title": page.get_title(language) if language else page.get_title(),
                "path": page.get_path(language) if language else page.get_path(),
                "template": page.get_template(),
                "is_published": page.is_published(language) if language else False,
            }
            result.append(page_data)

        return {"pages": result, "count": len(result)}

    except ImportError:
        return {"error": "Django CMS not installed", "pages": [], "count": 0}
    except Exception as e:
        raise Exception(f"Error listing pages: {str(e)}")


def get_page(params: Dict[str, Any], request) -> Dict[str, Any]:
    """
    Get details of a specific CMS page.

    Args:
        params: Must include page_id, optional language
        request: Django request object

    Returns:
        Detailed page information
    """
    page_id = params.get("page_id")
    if not page_id:
        raise ValueError("page_id is required")

    try:
        from cms.models import Page, Placeholder

        page = Page.objects.get(pk=page_id)
        language = params.get("language")

        # Get placeholders
        placeholders = []
        for placeholder in page.get_placeholders():
            placeholders.append(
                {
                    "id": placeholder.pk,
                    "slot": placeholder.slot,
                    "default_width": placeholder.default_width,
                }
            )

        result = {
            "id": page.pk,
            "node_id": page.node_id,
            "title": page.get_title(language) if language else page.get_title(),
            "path": page.get_path(language) if language else page.get_path(),
            "template": page.get_template(),
            "is_published": page.is_published(language) if language else False,
            "creation_date": page.creation_date.isoformat()
            if page.creation_date
            else None,
            "changed_date": page.changed_date.isoformat()
            if page.changed_date
            else None,
            "placeholders": placeholders,
        }

        return result

    except ImportError:
        raise Exception("Django CMS not installed")
    except Exception as e:
        raise Exception(f"Error getting page: {str(e)}")


def create_page(params: Dict[str, Any], request) -> Dict[str, Any]:
    """
    Create a new CMS page.

    Args:
        params: Must include title, optional template, language, parent_id
        request: Django request object

    Returns:
        Created page information
    """
    title = params.get("title")
    if not title:
        raise ValueError("title is required")

    try:
        from cms.api import create_page as cms_create_page

        template = params.get("template", "INHERIT")
        language = params.get("language", "en")
        parent_id = params.get("parent_id")

        parent = None
        if parent_id:
            from cms.models import Page

            parent = Page.objects.get(pk=parent_id)

        page = cms_create_page(
            title=title,
            template=template,
            language=language,
            parent=parent,
            created_by=request.user if request.user.is_authenticated else None,
        )

        result = {
            "id": page.pk,
            "title": page.get_title(language),
            "path": page.get_path(language),
            "template": page.get_template(),
            "success": True,
        }

        return result

    except ImportError:
        raise Exception("Django CMS not installed")
    except Exception as e:
        raise Exception(f"Error creating page: {str(e)}")


def get_all_pages(request) -> Dict[str, Any]:
    """
    Get all pages as a resource.

    Args:
        request: Django request object

    Returns:
        All pages data
    """
    return list_pages({}, request)
