from django import forms


def build_dict(**kwargs):
    """Build a dictionary from keyword arguments, excluding None values."""
    return {k: v for k, v in kwargs.items() if v is not None}


def form_to_json_schema(form_or_class):
    """
    Build a JSON Schema representation of a Django form's fields.

    Args:
        form_or_class: A Django ``forms.Form`` subclass or instance.

    Returns:
        Dict compatible with JSON Schema describing the form fields.
    """

    form = form_or_class() if isinstance(form_or_class, type) else form_or_class

    def _choices_to_enum(choices):
        values = []
        for value, _label in choices:
            value = str(value)
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
            schema["description"] = description

        return schema

    properties: dict[str, object] = {}
    required: list[str] = []

    for name, field in form.fields.items():
        properties[name] = _field_schema(field)
        if field.required:
            required.append(name)

    schema = build_dict(
        title=getattr(form, "title", form.__class__.__name__),
        type="object",
        properties=properties,
        required=required or None,
        additionalProperties=False,
    )

    return schema
