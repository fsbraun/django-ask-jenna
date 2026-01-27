from django import forms

from cms_mcp.helpers import form_to_json_schema


class SampleForm(forms.Form):
    name = forms.CharField(max_length=50, help_text="Your full name")
    email = forms.EmailField(required=False)
    age = forms.IntegerField()
    website = forms.URLField()
    newsletter = forms.BooleanField(required=False)
    color = forms.ChoiceField(choices=[("red", "Red"), ("", "---")])
    tags = forms.MultipleChoiceField(
        choices=[("a", "Option A"), ("b", "Option B")], required=False
    )
    when = forms.DateTimeField(required=False)
    rating = forms.DecimalField(required=False)


class OptionalForm(forms.Form):
    note = forms.CharField(required=False)


def test_form_to_json_schema_on_class():
    schema = form_to_json_schema(SampleForm)

    assert schema["type"] == "object"
    assert schema["properties"]["name"]["maxLength"] == 50
    assert schema["properties"]["name"]["description"] == "Your full name"
    assert schema["properties"]["email"]["format"] == "email"
    assert schema["properties"]["website"]["format"] == "uri"
    assert schema["properties"]["when"]["format"] == "date-time"
    assert schema["properties"]["age"]["type"] == "integer"
    assert schema["properties"]["newsletter"]["type"] == "boolean"
    assert schema["properties"]["rating"]["type"] == "number"
    assert schema["properties"]["color"]["enum"] == ["red"]
    assert schema["properties"]["tags"]["items"]["enum"] == ["a", "b"]
    assert set(schema["required"]) == {"name", "age", "website", "color"}
    assert schema["additionalProperties"] is False


def test_form_to_json_schema_on_instance_no_required():
    schema = form_to_json_schema(OptionalForm())

    assert "required" not in schema
    assert schema["properties"]["note"]["type"] == "string"
    assert schema["additionalProperties"] is False
