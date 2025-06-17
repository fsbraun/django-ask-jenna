from django import template
from django.db import models
from django.template.defaultfilters import json_script
from django.template import Context, Template

from cms.toolbar.utils import get_object_preview_url

register = template.Library()

@register.simple_tag
def ask_jenna_scripts(instance: models.Model) -> str:
    # Replace this with actual logic as needed
    jenna_prompts: dict = {
        "meta_description": {
            "type": "text",
            "length": 160,
            "prompt": """
                Generate a meta description with an approximate length of {{ length }} characters for this page
                optimizing search engine results in the language with the language code {{ instance.language }}""",
            "dynamic_content": get_object_preview_url(instance) if instance else "",
        }
    }
    prompt = Template(jenna_prompts["meta_description"]["prompt"]).render(context=Context({
        "instance": instance,
        **jenna_prompts["meta_description"],
        }))
    jenna_prompts["meta_description"]["prompt"] = prompt
    return json_script(jenna_prompts, "ask_jenna_scripts")


@register.simple_tag
def ask_jenna_config() -> str:
    from ask_jenna.config import ASK_JENNA_API_KEY, ASK_JENNA_MODEL, ASK_JENNA_SERVICE

    return json_script({
        "service": ASK_JENNA_SERVICE,       # LLM service provider
        "apiKey": ASK_JENNA_API_KEY,        # apiKey
        "model": ASK_JENNA_MODEL,           # Specific model
        "max_tokens": 1000,                 # Maximum response length
        "temperature": 0.7,                 # "Creativity" (0-2)
        "stream": False,                     # Enable streaming
        "extended": True,                   # Extended responses with metadata
        "messages": [],                     # message history
        }, "ask_jenna_settings")