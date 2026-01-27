from typing import Any
from django import forms
from django.utils.encoding import force_str
import re
from markdown import markdown as _markdown_to_html


def build_dict(**kwargs):
    """Build a dictionary from keyword arguments, excluding None values."""
    return {k: v for k, v in kwargs.items() if v is not None}


def form_to_json_schema(form: type[forms.Form] | forms.Form) -> dict[str, Any]:
    """
    Build a JSON Schema representation of a Django form's fields.

    Args:
        form: A Django ``forms.Form`` subclass or instance.

    Returns:
        Dict compatible with JSON Schema describing the form fields.
    """

    # Support being passed either a form class or instance
    if isinstance(form, forms.Form):
        form_class = form.__class__
        form_fields = getattr(form, "fields", form_class.base_fields)
    else:
        form_class = form
        form_fields = form_class.base_fields

    def _choices_to_enum(choices):
        values = []
        for value, _label in choices:
            value = force_str(value)
            if value == "":
                continue
            values.append(value)
        return values or None

    def _field_schema(field: forms.Field):
        schema: dict[str, object] = {}

        if isinstance(field, forms.BooleanField):
            schema["type"] = "boolean"
        elif isinstance(field, (forms.FloatField, forms.DecimalField)):
            schema["type"] = "number"
        elif isinstance(field, (forms.IntegerField, forms.DurationField)):
            schema["type"] = "integer"
        elif isinstance(field, forms.EmailField):
            schema.update({"type": "string", "format": "email"})
        elif isinstance(field, forms.URLField):
            schema.update({"type": "string", "format": "uri"})
        elif isinstance(field, forms.DateTimeField):
            schema.update({"type": "string", "format": "date-time"})
        elif isinstance(field, forms.DateField):
            schema.update({"type": "string", "format": "date"})
        elif isinstance(field, forms.TimeField):
            schema.update({"type": "string", "format": "time"})
        elif isinstance(field, forms.MultipleChoiceField):
            enum_values = _choices_to_enum(field.choices)
            schema.update(
                {
                    "type": "array",
                    "items": build_dict(type="string", enum=enum_values),
                }
            )
        else:
            schema["type"] = "string"

        if hasattr(field, "max_length") and field.max_length:
            schema["maxLength"] = field.max_length

        if getattr(field, "choices", None):
            enum_values = _choices_to_enum(field.choices)
            if enum_values:
                schema["enum"] = enum_values

        description = field.help_text or field.label
        if description:
            schema["description"] = force_str(description)

        return schema

    properties: dict[str, object] = {}
    required: list[str] = []

    for name, field in form_fields.items():
        properties[name] = _field_schema(field)
        if field.required:
            required.append(name)

    schema = build_dict(
        title=getattr(form_class, "title", form_class.__name__),
        type="object",
        properties=properties,
        required=required or None,
        additionalProperties=False,
    )

    return schema


def is_likely_markdown(value: str) -> bool:
    """
    Heuristically determine if a string is likely Markdown.

    Checks common Markdown patterns (headings, links, images, lists,
    code fences, inline code, blockquotes, tables) and returns True
    if any are present.
    """
    if not value:
        return False

    # Recognize paragraph breaks (double new-lines) as Markdown-like structure
    if re.search(r"(?:\r?\n)\s*(?:\r?\n)", value):
        # Ensure there are at least two non-empty paragraphs
        paragraphs = [p.strip() for p in re.split(r"(?:\r?\n)\s*(?:\r?\n)", value)]
        if sum(1 for p in paragraphs if p) >= 2:
            return True

    patterns = [
        r"^\s{0,3}#{1,6}\s",  # headings
        r"\[[^\]]+\]\([^\)]+\)",  # links
        r"!\[[^\]]*\]\([^\)]+\)",  # images
        r"^\s{0,3}[-*+]\s",  # unordered list
        r"^\s{0,3}\d+\.\s",  # ordered list
        r"^\s*>\s",  # blockquote
        r"^\s*```",  # code fence
        r"`[^`]+`",  # inline code
        r"^\s*\|.*\|\s*$",  # table row
        r"\*\*[^*]+\*\*|__[^_]+__",  # bold
        r"\*[^*]+\*|_[^_]+_",  # italics
    ]

    lines = value.splitlines()
    for line in lines:
        for pat in patterns:
            if re.search(pat, line):
                return True
    return False


def convert_markdown_fields(
    data: dict[str, Any], *, keys: list[str] | None = None
) -> dict[str, Any]:
    """
    Convert Markdown-like string values in a dict to HTML.

    Args:
        data: Input dictionary whose string values may contain Markdown.
        keys: Optional subset of keys to process; if omitted, all string values are checked.

    Returns:
        A new dict with Markdown-like strings converted to HTML; non-markdown strings unchanged.
    """
    result: dict[str, Any] = {}
    for k, v in data.items():
        if keys is not None and k not in keys:
            result[k] = v
            continue
        if isinstance(v, str) and is_likely_markdown(v):
            # Use common extensions to support tables and extras
            html = _markdown_to_html(v, extensions=["extra", "tables"])
            result[k] = html
        else:
            result[k] = v
    return result
