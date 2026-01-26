import pytest
from django.core.exceptions import ValidationError

from cms_mcp.models import MCPResource


@pytest.mark.parametrize(
    "uri",
    [
        "cms://pages",
        "cms://pages/",
        "cms://pages/123",
        "cms://plugins/list",
    ],
)
def test_valid_resource_uri(uri, db):
    res = MCPResource(
        uri=uri,
        name="Test",
        mime_type="application/json",
        content={"ok": True},
    )
    # Full clean should not raise
    res.full_clean()


@pytest.mark.parametrize(
    "uri",
    [
        "",  # empty
        "pages",  # no scheme
        "http://pages",  # unsupported scheme
        "cms://",  # no netloc and no path
        "cms:// pages",  # whitespace
        "cms://pages with space",  # whitespace
    ],
)
def test_invalid_resource_uri(uri, db):
    res = MCPResource(
        uri=uri,
        name="Invalid",
        mime_type="application/json",
        content=None,
    )
    with pytest.raises(ValidationError):
        res.full_clean()
