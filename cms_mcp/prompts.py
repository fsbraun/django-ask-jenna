from asgiref.sync import sync_to_async

from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptMessage,
    TextContent,
)

from .mcp_server import server
from .models import MCPPrompt


@sync_to_async(thread_sensitive=True)
def _load_prompts() -> list[MCPPrompt]:
    return list(MCPPrompt.objects.filter(enabled=True).only("name", "description"))


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    rows = await _load_prompts()
    return [
        Prompt(
            name=row.name,
            description=row.description,
        )
        for row in rows
    ]


@sync_to_async(thread_sensitive=True)
def _load_prompt(name: str) -> MCPPrompt:
    return MCPPrompt.objects.filter(name=name, enabled=True).first()


@server.get_prompt()
async def get_prompt(name: str) -> GetPromptResult:
    prompt = await _load_prompt(name)
    return GetPromptResult(
        description=prompt.description,
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=prompt.content,
                ),
            )
        ],
    )
