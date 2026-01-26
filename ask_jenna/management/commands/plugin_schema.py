import json
from django.core.management.base import BaseCommand
from django.contrib.admin import site
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from cms.plugin_pool import plugin_pool

from ask_jenna.cms.schema import django_form_to_json_schema


class Command(BaseCommand):
    help = "Generiert JSON-Schemata aus Django CMS Plugins"

    def add_arguments(self, parser):
        parser.add_argument(
            "--plugin", type=str, help="Spezifisches Plugin zum Generieren (optional)"
        )

    def handle(self, *args, **options):
        try:
            if options["plugin"]:
                # Single plugins
                self.generate_single_plugin(options["plugin"], options)
            else:
                # All plugins
                self.generate_all_plugins(options)

            self.stdout.write(self.style.SUCCESS("Schemata erfolgreich  generiert"))

        except Exception:
            raise

    def generate_single_plugin(self, plugin_name, options):
        """Generiert Schema für ein einzelnes Plugin"""
        plugin = plugin_pool.get_plugin(plugin_name)
        request = HttpRequest()
        request.user = AnonymousUser()
        form = plugin(admin_site=site).get_form(request)
        self.stdout.write(
            json.dumps(django_form_to_json_schema(form), indent=2, ensure_ascii=False)
        )

    def generate_all_plugins(self, options):
        """Generate schema for all plugins"""
        plugins = plugin_pool.get_all_plugins()
        schemas = []

        for plugin in plugins:
            request = HttpRequest()
            request.user = AnonymousUser()
            form = plugin(admin_site=site).get_form(request)
            schema = django_form_to_json_schema(form)
            schemas.append(schema)

        self.stdout.write(json.dumps(schemas), indent=2, ensure_ascii=False)
