==============
Authentication
==============

How to secure your MCP endpoints with token authentication.

Creating tokens
===============

Use the Django admin to create MCP tokens, or programmatically:

.. code-block:: python

   from cms_mcp.models import MCPToken

   token = MCPToken.objects.create(
       name="My AI Client",
       expires_at=timezone.now() + timedelta(days=30),
   )
   print(token.key)

Using tokens
============

Clients authenticate by including the token in the Authorization header:

.. code-block:: http

   Authorization: Bearer your-token-key

Revoking tokens
===============

.. code-block:: python

   token.is_revoked = True
   token.save()
