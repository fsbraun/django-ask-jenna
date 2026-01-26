from typing import Optional
from django import template
from django.db import models
from django.template.defaultfilters import json_script
from django.template import Context, Template

from ask_jenna.prompts import prompts

register = template.Library()

@register.simple_tag
def ask_jenna_scripts(view: str, opts: models.options.Options, instance: Optional[models.Model]) -> str:
    if view and opts:
        # Replace this with actual logic as needed
        return json_script(prompts.get(view, opts, instance), "ask_jenna_scripts")
    return ""

@register.simple_tag
def ask_jenna_config() -> str:
    from ask_jenna.config import ASK_JENNA_API_KEY, ASK_JENNA_MODEL, ASK_JENNA_SERVICE

    return json_script({
        "service": ASK_JENNA_SERVICE,       # LLM service provider
        "apiKey": ASK_JENNA_API_KEY,        # apiKey
        "model": ASK_JENNA_MODEL,           # Specific model
        "max_tokens": 1000,                 # Maximum response length
        "temperature": 0.7,                 # "Creativity" (0-2)
        "stream": False,                    # Enable streaming
        "extended": False,                   # Extended responses with metadata
        "messages": [],                     # message history
        "json": True,                       # Return JSON responses
        }, "ask_jenna_settings")