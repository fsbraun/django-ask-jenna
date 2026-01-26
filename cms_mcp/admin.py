from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django import forms

from .models import MCPToken, MCPResource, MCPPrompt


@admin.register(MCPToken)
class MCPTokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "expires_at", "created_at", "revoked", "is_active")
    list_filter = ("revoked", "expires_at", "created_at")
    search_fields = ("key", "user__username", "user__email")
    readonly_fields = ("key", "created_at")
    autocomplete_fields = ("user",)
    actions = ("revoke_tokens",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "key",
                    "user",
                    "expires_at",
                    "created_at",
                ),
            },
        ),
        (
            _("Revocation"),
            {
                "fields": ("revoked",),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make revoked field readonly if already revoked."""
        readonly = list(self.readonly_fields)
        if obj and obj.revoked:
            if "revoked" not in readonly:
                readonly.append("revoked")
        return readonly

    @admin.display(
        description="Active",
        boolean=True,
    )
    def is_active(self, obj):  # pragma: no cover - simple passthrough
        return obj.is_active

    @admin.action(description="Revoke selected tokens")
    def revoke_tokens(
        self, request, queryset
    ):  # pragma: no cover - trivial bulk update
        queryset.update(revoked=True)


@admin.register(MCPResource)
class MCPResourceAdmin(admin.ModelAdmin):
    list_display = ("uri", "name", "mime_type", "enabled", "updated_at")
    list_filter = ("enabled", "mime_type", "updated_at")
    search_fields = ("uri", "name", "description")
    readonly_fields = ("created_at", "updated_at")
    actions = ("enable_selected", "disable_selected")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "content":
            kwargs["widget"] = forms.Textarea(
                attrs={
                    "rows": 20,
                    "cols": 80,
                    "style": "font-family: monospace; font-size: 13px;",
                }
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.action(description=_("Enable selected resources"))
    def enable_selected(self, request, queryset):  # pragma: no cover
        queryset.update(enabled=True)

    @admin.action(description=_("Disable selected resources"))
    def disable_selected(self, request, queryset):  # pragma: no cover
        queryset.update(enabled=False)


@admin.register(MCPPrompt)
class MCPPromptAdmin(admin.ModelAdmin):
    list_display = ("name", "enabled", "updated_at")
    list_filter = ("enabled", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    actions = ("enable_selected", "disable_selected")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "content":
            kwargs["widget"] = forms.Textarea(
                attrs={
                    "rows": 20,
                    "cols": 80,
                    "style": "font-family: monospace; font-size: 13px;",
                }
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @admin.action(description=_("Enable selected prompts"))
    def enable_selected(self, request, queryset):  # pragma: no cover
        queryset.update(enabled=True)

    @admin.action(description=_("Disable selected prompts"))
    def disable_selected(self, request, queryset):  # pragma: no cover
        queryset.update(enabled=False)
