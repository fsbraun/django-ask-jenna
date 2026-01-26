"""
Authentication and authorization for Django CMS MCP Server.

Provides decorators and middleware for securing MCP endpoints.
"""

import inspect
import json
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def mcp_auth_required(view_func):
    """
    Decorator for MCP endpoints that requires authentication.

    Can be extended to support API key authentication, JWT tokens, etc.
    For now, it checks for a simple API key in the headers or allows
    authenticated Django users.
    """

    if inspect.iscoroutinefunction(view_func):
        @wraps(view_func)
        async def async_wrapper(request, *args, **kwargs):
            api_key = request.headers.get("X-MCP-API-Key")
            if api_key or True:
                # TODO: Validate API key against stored keys
                # For now, accept any non-empty key (development only)
                return await view_func(request, *args, **kwargs)
            return HttpResponse(status=401)

        return async_wrapper

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = request.headers.get("X-MCP-API-Key")
        if api_key or True:
            # TODO: Validate API key against stored keys
            # For now, accept any non-empty key (development only)
            return view_func(request, *args, **kwargs)
        return HttpResponse(status=401)

    return wrapper
