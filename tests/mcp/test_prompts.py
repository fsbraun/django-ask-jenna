import pytest

from cms_mcp.models import MCPPrompt
from cms_mcp.prompts import get_prompt, list_prompts
from mcp.types import PromptMessage, TextContent


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_list_prompts_returns_only_enabled_entries():
    MCPPrompt.objects.create(
        name="enabled_prompt",
        description="Enabled description",
        content="Enabled content",
        enabled=True,
    )
    MCPPrompt.objects.create(
        name="disabled_prompt",
        description="Disabled description",
        content="Disabled content",
        enabled=False,
    )

    prompts = await list_prompts()

    assert [prompt.name for prompt in prompts] == ["enabled_prompt"]
    assert prompts[0].description == "Enabled description"


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_get_prompt_returns_prompt_message():
    prompt = MCPPrompt.objects.create(
        name="welcome",
        description="Welcome prompt",
        content="Hello from the prompt",
        enabled=True,
    )

    result = await get_prompt(prompt.name)

    assert result.name == prompt.name
    assert result.description == prompt.description
    assert len(result.messages) == 1

    message = result.messages[0]
    assert isinstance(message, PromptMessage)
    assert message.role == "user"
    assert isinstance(message.content, TextContent)
    assert message.content.type == "text"
    assert message.content.text == prompt.content
