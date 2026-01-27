==========
MCP server
==========

How to set up and configure the Model Context Protocol server.

Installation
============

Add ``cms_mcp`` to your ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'cms_mcp',
   ]

Run migrations:

.. code-block:: bash

   python manage.py migrate cms_mcp


Configuration
=============

Configure the MCP server in your settings:

.. code-block:: python

   MCP_SERVER_NAME = "my-django-mcp"
   MCP_SERVER_INSTRUCTIONS = "Server for accessing Django CMS content"
