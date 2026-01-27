"""
CMS Pages tool handlers.

Provides functionality for listing, creating, and managing CMS pages.
"""

from typing import Any

from asgiref.sync import sync_to_async
from mcp import MCPError, Tool

from django.contrib.auth.models import User
from django.forms import forms
from django.test import RequestFactory
from django.urls import reverse

from cms.utils.admin import get_site_from_request
from cms.wizards.views import WizardCreateView
from cms.wizards.wizard_base import get_entries

from .pool import tools

from .. import errors
from ..helpers import form_to_json_schema


def get_schema(form: type[forms.Form]) -> dict[str, Any]:
    """Convert a Django form into a JSON schema representation."""
    if not hasattr(form, "_mcp_schema"):
        form._mcp_schema = form_to_json_schema(form)  # Cache result of conversion
    return form._mcp_schema


_wizard_view = WizardCreateView.as_view()


@sync_to_async
def call_create_wizard(name: str, input_data: dict) -> dict:
    if name not in tools:
        raise ValueError(f"Wizard '{name}' not found")

    tool = tools[name]

    url = reverse("cms_wizard_create")
    request = RequestFactory().post(url, data=input_data)
    request.user = User.objects.filter(is_superuser=True).first()
    request.site = get_site_from_request(request)

    if not tool.wizard.user_has_add_permission(request.user):
        raise MCPError(
            code=errors.INVALID_TARGET,
            message="Create tool failed.",
            data={
                "tool": name,
                "error": "User does not have permission to add this content.",
            },
        )

    form = tool.wizard.form(
        data=input_data,
        wizard_page=None,
        wizard_site=request.site,
        wizard_language="en",
        wizard_request=request,
    )
    if not form.is_valid():
        raise MCPError(
            code=errors.INVALID_DATA,
            message="Create tool failed.",
            data={
                "tool": name,
                "field_errors": form.errors.get_json_data(),
                "overall_errors": [str(e) for e in form.non_field_errors()],
            },
        )
    form.save()


for wizard in get_entries():
    print(f"Registering wizard: {wizard}")

    title = wizard.get_title()
    name = title.lower().replace(" ", "_")
    description = wizard.get_description()
    input_schema = get_schema(wizard.form)

    tool = Tool(
        name=f"create_{name}",
        title=title,
        description=description,
        input_schema=input_schema,
    )
    tool.call = call_create_wizard
    tool.wizard = wizard
    tools[tool.name] = tool
