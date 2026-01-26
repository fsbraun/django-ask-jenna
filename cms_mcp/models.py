import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

import datetime


PREFIX = "cms_mcp_"
DEFAULT_DURATION = datetime.timedelta(days=30)

ALLOWED_SCHEMES = ("cms", "skill")


# Common, LLM-friendly, text-based MIME types
TEXT_MIME_TYPE_CHOICES = (
    ("text/markdown", _("text/markdown (Markdown)")),
    ("text/plain", _("text/plain (Plain text)")),
    ("text/html", _("text/html (HTML)")),
    ("text/csv", _("text/csv (CSV)")),
    ("application/json", _("JSON")),
    ("application/schema+json", _("JSON Schema")),
    ("application/yaml", _("YAML")),
    ("application/toml", _("TOML")),
    ("application/xml", _("XML")),
)


def generate_token() -> str:
    """Return a URL-safe random token string."""
    return PREFIX + secrets.token_urlsafe(32)


def get_default_expiry() -> datetime.datetime:
    return timezone.now() + DEFAULT_DURATION if DEFAULT_DURATION else None


class MCPToken(models.Model):
    """API token for MCP access bound to a single user with an expiry time."""

    key = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        default=generate_token,
        help_text=_(
            "Automatically generated secure token. Used for API authentication."
        ),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mcp_tokens"
    )
    revoked = models.BooleanField(
        default=False,
        help_text=_("When enabled, this token cannot be used for authentication."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        default=get_default_expiry,
        null=True,
        blank=True,
        help_text=_(
            "When the token expires and becomes invalid. Leave empty for no expiration."
        ),
    )

    class Meta:
        verbose_name = "MCP token"
        verbose_name_plural = "MCP tokens"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"MCP token for {self.user}"  # Helpful for admin/debug views

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_active(self) -> bool:
        return not self.is_expired


class MCPResource(models.Model):
    """Manually editable resource made available via the MCP server."""

    def validate_resource_uri(value: str):  # type: ignore[override]
        parsed = urlparse(value)
        if not parsed.scheme:
            raise ValidationError(_("URI must include a scheme, e.g. cms://pages"))
        if parsed.scheme not in ALLOWED_SCHEMES:
            raise ValidationError(
                _("Unsupported URI scheme: %(scheme)s"),
                params={"scheme": parsed.scheme},
            )
        if not (parsed.netloc or parsed.path):
            raise ValidationError(_("URI must include an authority or path"))
        if any(ch.isspace() for ch in value):
            raise ValidationError(_("URI must not contain whitespace"))

    uri = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Unique resource URI (e.g., cms://pages or cms://pages/123)."),
        validators=[validate_resource_uri],
    )
    name = models.CharField(
        max_length=200,
        help_text=_("Human-readable name for the resource."),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional description of the resource."),
    )
    mime_type = models.CharField(
        max_length=100,
        choices=TEXT_MIME_TYPE_CHOICES,
        default=TEXT_MIME_TYPE_CHOICES[0][0],
        help_text=_("MIME type of the resource content."),
    )
    enabled = models.BooleanField(
        default=True,
        help_text=_("If disabled, the resource will not be listed by MCP."),
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text=_("Arbitrary JSON content returned by the MCP resource."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MCP resource"
        verbose_name_plural = "MCP resources"
        ordering = ["uri"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.uri}"


class MCPPrompt(models.Model):
    """Manually editable prompt made available via the MCP server."""

    name = models.CharField(
        verbose_name=_("name"),
        max_length=200,
        unique=True,
        help_text=_("Unique prompt name (identifier used by clients)."),
    )
    description = models.TextField(
        verbose_name=_("description"),
        blank=True,
        help_text=_("Optional description of the prompt."),
    )
    content = models.TextField(
        verbose_name=_("content"),
        blank=False,
        help_text=_("The prompt content, preferably in Markdown format."),
    )
    enabled = models.BooleanField(
        verbose_name=_("enabled"),
        default=True,
        help_text=_("If disabled, the prompt will not be listed by MCP."),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("MCP prompt")
        verbose_name_plural = _("MCP prompts")
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name
