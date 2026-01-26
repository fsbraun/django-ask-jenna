from importlib import import_module
import logging

from django.apps import apps
from django.db import models
from django.template import Context, Template


logger = logging.getLogger(__name__)


class Prompts:
    def __init__(self):
        self.prompts = {}

    def register(self, prompt):
        self.prompts.update(prompt)

    def get(
        self, view, opts: models.options.Options, instance: models.Model | None = None
    ):
        key = f"{opts.app_label}.{opts.model_name}:{view}"
        print(f"Fetching prompt for key: {key}")
        prompt = self.prompts.get(key, {})
        for field, field_prompt in prompt.items():
            if callable(field_prompt.get("dynamic_content")):
                field_prompt["dynamic_content"] = field_prompt["dynamic_content"](
                    instance
                )
            field_prompt["prompt"] = Template(field_prompt["prompt"]).render(
                Context(
                    {
                        "instance": instance,
                        **field_prompt,
                    }
                )
            )
        return prompt

    def all(self):
        return self.prompts

    def __bool__(self):
        return bool(self.prompts)


prompts = Prompts()

if not prompts:
    for app_config in apps.get_app_configs():
        # Attempt to import the app's module.
        try:
            module = import_module("{}.{}".format(app_config.name, "ask_jenna"))
            for name, prompt in module.__dict__.items():
                if isinstance(prompt, dict):
                    # Register the prompt
                    prompts.register(prompt)
        except (ImportError, AttributeError):
            # Handle import errors or attribute errors gracefully
            # This is useful for apps that may not have the ask_jenna module
            # or if the module does not contain the expected attributes.
            pass
        # Catch any other exceptions that might occur during import
        except Exception as e:
            logger.exception(
                f"Error importing prompts from {app_config.name}.ask_jenna",
                exc_info=e,
                stack_info=True,
                stacklevel=2,
            )
