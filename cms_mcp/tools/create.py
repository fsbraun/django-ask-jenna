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
from django.utils.encoding import force_str

from cms.models import Page
from cms.utils.admin import get_site_from_request
from cms.utils.permissions import set_current_user
from cms.wizards.forms import WizardStep2BaseForm
from cms.wizards.wizard_base import get_entries

from .pool import tools, MCPTool

from .. import errors
from ..helpers import convert_markdown_fields, form_to_json_schema


def get_schema(form: type[forms.Form]) -> dict[str, Any]:
    """Convert a Django form into a JSON schema representation."""
    if not hasattr(form, "_mcp_schema"):
        form._mcp_schema = form_to_json_schema(form)  # Cache result of conversion
    form._mcp_schema["properties"]["wizard_language"] = {
        "type": "string",
        "description": "2-letter code of the language of the content, for example 'en' for English.",
    }
    if "wizard_language" not in form._mcp_schema["required"]:
        form._mcp_schema["required"].append("wizard_language")
    return form._mcp_schema


@sync_to_async(thread_sensitive=True)
def call_create_wizard(name: str, input_data: dict) -> dict:
    if name not in tools:
        raise ValueError(f"Tool '{name}' not found")

    tool = tools[name]

    url = reverse("cms_wizard_create")
    request = RequestFactory().post(url, data=input_data)
    # TODO: Authentication!!
    request.user = User.objects.filter(is_superuser=True).first()
    request.site = get_site_from_request(request)
    set_current_user(request.user)  # a django CMS hack - not sure if anybody uses it
    wizard = tool.related
    print("===> PERMISSIONS")
    print(request.user.username)
    print(wizard.user_has_add_permission(request.user))
    if not wizard.user_has_add_permission(request.user):
        raise MCPError(
            code=errors.INVALID_TARGET,
            message=f"Insufficient permission for {name}.",
            data={
                "tool": name,
                "user": request.user.username,
                "error": "User does not have permission to add this content.",
            },
        )

    form_cls = type("CreateForm", (WizardStep2BaseForm, wizard.form), {})
    print("FORM CLASS ==> ", form_cls)
    language = input_data.pop("wizard_language", "en")
    form = form_cls(
        data=convert_markdown_fields(input_data),
        wizard_page=Page.objects.filter(
            is_home=True
        ).first(),  # TODO: Replace by none, once permission issue is fixed
        wizard_site=request.site,
        wizard_language=language,
        wizard_request=request,
    )

    if not form.is_valid():
        raise MCPError(
            code=errors.INVALID_DATA,
            message="Create tool failed because of invalid data. Please check the form fields.",
            data={
                "tool": name,
                "field_errors": form.errors.get_json_data(),
                "overall_errors": [str(e) for e in form.non_field_errors()],
            },
        )
    result = form.save()
    return {
        "status": "ok",
        name: {
            "pk": getattr(result, "pk", None),
            "title": str(result),
            "language": "en",
            "state": "draft",
        },
    }


def register_tools():
    print("Registering create tools")
    for wizard in get_entries():
        print(f"Registering wizard: {wizard}")

        title = force_str(wizard.get_title())
        name = "create_" + title.lower().replace(" ", "_")
        description = force_str(wizard.get_description())
        input_schema = get_schema(wizard.form)

        tool = MCPTool(
            tool=Tool(
                name=name,
                title=title,
                description=description,
                input_schema=input_schema,
            ),
            call=call_create_wizard,
            related=wizard,
        )
        tools[name] = tool
