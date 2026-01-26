"""
CMS Media tool handlers.

Provides functionality for listing and managing media files (Filer integration).
"""

from typing import Dict, Any


def handle_tool(tool_name: str, params: Dict[str, Any], request) -> Dict[str, Any]:
    """
    Route tool calls to the appropriate handler function.

    Args:
        tool_name: Name of the tool (e.g., 'cms_media_list')
        params: Tool parameters
        request: Django request object

    Returns:
        Tool execution result
    """
    if tool_name == "cms_media_list":
        return list_media(params, request)
    elif tool_name == "cms_media_upload":
        return upload_media(params, request)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def list_media(params: Dict[str, Any], request) -> Dict[str, Any]:
    """
    List media files from Filer.

    Args:
        params: Optional folder_id filter and limit
        request: Django request object

    Returns:
        List of media files with basic information
    """
    try:
        from filer.models import File, Image

        folder_id = params.get("folder_id")
        limit = params.get("limit", 100)

        # Start with all files
        files = File.objects.all()

        # Apply folder filter if provided
        if folder_id:
            files = files.filter(folder_id=folder_id)

        # Apply limit
        files = files[:limit]

        result = []
        for file in files:
            file_data = {
                "id": file.pk,
                "name": file.name,
                "original_filename": file.original_filename,
                "file_type": file.file_type,
                "mime_type": file.mime_type,
                "size": file.size,
                "url": file.url if hasattr(file, "url") else None,
                "uploaded_at": file.uploaded_at.isoformat()
                if file.uploaded_at
                else None,
                "folder_id": file.folder_id,
            }

            # Add image-specific data if it's an image
            if isinstance(file, Image):
                file_data.update(
                    {
                        "is_image": True,
                        "width": file.width,
                        "height": file.height,
                        "default_alt_text": file.default_alt_text,
                        "default_caption": file.default_caption,
                    }
                )
            else:
                file_data["is_image"] = False

            result.append(file_data)

        return {"files": result, "count": len(result)}

    except ImportError:
        return {"error": "Django Filer not installed", "files": [], "count": 0}
    except Exception as e:
        raise Exception(f"Error listing media: {str(e)}")


def upload_media(params: Dict[str, Any], request) -> Dict[str, Any]:
    """
    Upload a media file to Filer.

    Args:
        params: Must include file_path, optional folder_id, title
        request: Django request object

    Returns:
        Uploaded file information
    """
    file_path = params.get("file_path")

    if not file_path:
        raise ValueError("file_path is required")

    try:
        from filer.models import File, Folder, Image
        from django.core.files import File as DjangoFile
        import os

        # Get or create folder
        folder = None
        folder_id = params.get("folder_id")
        if folder_id:
            folder = Folder.objects.get(pk=folder_id)

        # Open the file
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            django_file = DjangoFile(f, name=os.path.basename(file_path))

            # Determine if it's an image
            file_ext = os.path.splitext(file_path)[1].lower()
            image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

            # Create File or Image instance
            if file_ext in image_extensions:
                file_obj = Image(
                    file=django_file,
                    folder=folder,
                    name=params.get("title", os.path.basename(file_path)),
                    owner=request.user if request.user.is_authenticated else None,
                )
            else:
                file_obj = File(
                    file=django_file,
                    folder=folder,
                    name=params.get("title", os.path.basename(file_path)),
                    owner=request.user if request.user.is_authenticated else None,
                )

            file_obj.save()

        result = {
            "id": file_obj.pk,
            "name": file_obj.name,
            "url": file_obj.url if hasattr(file_obj, "url") else None,
            "size": file_obj.size,
            "mime_type": file_obj.mime_type,
            "success": True,
        }

        return result

    except ImportError:
        raise Exception("Django Filer not installed")
    except Exception as e:
        raise Exception(f"Error uploading media: {str(e)}")


def get_all_media(request) -> Dict[str, Any]:
    """
    Get all media files as a resource.

    Args:
        request: Django request object

    Returns:
        All media data
    """
    return list_media({}, request)
