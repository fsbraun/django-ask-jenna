from asgiref.sync import sync_to_async

from mcp.types import (
    Resource,
    TextContent,
)

from ..mcp_server import server
from ..models import MCPResource


@sync_to_async
def _load_resources() -> list[MCPResource]:
    return list(
        MCPResource.objects
        .filter(enabled=True)
        .only("name", "description", "uri")
    )


@server.list_resources()
async def list_resources() -> list[Resource]:
    rows = await _load_resources()
    return [
        Resource(
            uri=row.uri,
            name=row.name,
            description=row.description,
        ) for row in rows]


@sync_to_async
def _load_resource(uri: str) -> MCPResource:
    return (
        MCPResource.objects
        .filter(uri=uri, enabled=True)
        .only("content")
        .first()
    )


@server.read_resource()
async def read_resource(uri: str) -> Resource:
    print(f"===> Getting resource {uri}")
    resource = await _load_resource(uri)
    if resource is None:
        raise ValueError("Resource not available")
    print(resource.content)
    return resource.content
