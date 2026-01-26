import json
from django import forms

def django_form_to_json_schema(form):
    """
    Wandelt ein Django-Formular (Form-Instanz oder Klasse) in ein JSON Schema um.
    """
    if isinstance(form, type):
        form_instance = form()
    else:
        form_instance = form

    properties = {}
    required = []

    for name, field in form_instance.fields.items():
        field_schema = {}

        # Typ-Mapping
        if isinstance(field, forms.CharField):
            field_schema["type"] = "string"
        elif isinstance(field, forms.IntegerField):
            field_schema["type"] = "integer"
        elif isinstance(field, forms.BooleanField):
            field_schema["type"] = "boolean"
        elif isinstance(field, forms.FloatField):
            field_schema["type"] = "number"
        elif isinstance(field, forms.DateField):
            field_schema["type"] = "string"
            field_schema["format"] = "date"
        elif isinstance(field, forms.DateTimeField):
            field_schema["type"] = "string"
            field_schema["format"] = "date-time"
        else:
            field_schema["type"] = "string"

        # Optionen
        if hasattr(field, "max_length"):
            field_schema["maxLength"] = field.max_length
        if hasattr(field, "min_length"):
            field_schema["minLength"] = field.min_length
        if hasattr(field, "choices") and field.choices:
            field_schema["enum"] = [choice[0] for choice in field.choices]

        properties[name] = field_schema

        if field.required:
            required.append(name)

    schema = {
        "type": "object",
        "properties": properties,
        "required": required,
        "title": form_instance.__class__.__name__
    }
    return schema

# Beispiel:
# from .forms import MyForm
# print(json.dumps(django_form_to_json_schema(MyForm), indent=2))