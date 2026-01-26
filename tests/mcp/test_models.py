from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.utils import timezone

from cms_mcp.admin import MCPTokenAdmin
from cms_mcp.models import MCPToken, PREFIX


def test_token_auto_prefix_and_length(db):
    user = get_user_model().objects.create_user(
        username="tokenuser", email="token@example.com", password="pw12345"
    )
    token = MCPToken.objects.create(user=user, expires_at=timezone.now() + timedelta(days=1))
    assert token.key.startswith(PREFIX)
    assert len(token.key) > len(PREFIX)
    assert token.revoked is False


def test_token_unique_generation(db):
    user = get_user_model().objects.create_user(
        username="tokenuser2", email="token2@example.com", password="pw12345"
    )
    token1 = MCPToken.objects.create(user=user, expires_at=timezone.now() + timedelta(days=1))
    token2 = MCPToken.objects.create(user=user, expires_at=timezone.now() + timedelta(days=2))
    assert token1.key != token2.key


def test_is_expired_and_is_active(db):
    user = get_user_model().objects.create_user(
        username="tokenuser3", email="token3@example.com", password="pw12345"
    )
    past = timezone.now() - timedelta(days=1)
    future = timezone.now() + timedelta(days=1)
    expired = MCPToken.objects.create(user=user, expires_at=past)
    active = MCPToken.objects.create(user=user, expires_at=future)
    assert expired.is_expired is True
    assert expired.is_active is False
    assert active.is_expired is False
    assert active.is_active is True


def test_admin_bulk_revoke_marks_tokens_revoked(db):
    user = get_user_model().objects.create_user(
        username="tokenuser4", email="token4@example.com", password="pw12345"
    )
    token1 = MCPToken.objects.create(user=user, expires_at=timezone.now() + timedelta(days=1))
    token2 = MCPToken.objects.create(user=user, expires_at=timezone.now() + timedelta(days=1))

    admin = MCPTokenAdmin(MCPToken, AdminSite())
    qs = MCPToken.objects.filter(pk__in=[token1.pk, token2.pk])

    admin.revoke_tokens(request=None, queryset=qs)

    token1.refresh_from_db()
    token2.refresh_from_db()
    assert token1.revoked is True
    assert token2.revoked is True
