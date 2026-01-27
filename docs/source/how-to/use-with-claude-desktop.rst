=========================
Use with Claude Desktop
=========================

This guide shows how to connect Claude Desktop to your Django CMS site using
the MCP proxy, allowing Claude to read and modify CMS content directly.

Prerequisites
=============

Before starting, ensure you have:

* Claude Desktop installed (download from `claude.ai/download <https://claude.ai/download>`_)
* Python 3.10+ installed
* A running Django CMS site with ``cms_mcp`` configured
* The ``requests`` package installed (``pip install requests``)

Overview
========

Claude Desktop communicates with MCP servers via stdio (standard input/output).
Since Django CMS runs as an HTTP server, we use a proxy script that:

1. Receives JSON-RPC messages from Claude via stdin
2. Forwards them to your Django MCP endpoint via HTTP
3. Returns responses to Claude via stdout

Setting up the MCP Proxy
========================

The ``cms_mcp`` package includes an MCP proxy script at ``cms_mcp/mcp_proxy.py``.

First, configure the proxy to point to your Django CMS server. Edit the
``DJANGO_MCP_URL`` variable in the script or set it via environment variable:

.. code-block:: python

   DJANGO_MCP_URL = "http://localhost:8000/mcp/"

For production, use your actual server URL:

.. code-block:: python

   DJANGO_MCP_URL = "https://your-cms-site.com/mcp/"

Configuring Claude Desktop
==========================

1. Open Claude Desktop
2. Click **Claude** in the menu bar (macOS) or the hamburger menu (Windows)
3. Select **Settings**
4. Navigate to the **Developer** tab
5. Click **Edit Config** to open ``claude_desktop_config.json``

Add the following configuration:

macOS / Linux
-------------

.. code-block:: json

   {
     "mcpServers": {
       "django-cms": {
         "command": "python",
         "args": ["/path/to/your/project/cms_mcp/mcp_proxy.py"],
         "env": {
           "DJANGO_MCP_URL": "http://localhost:8000/mcp/"
         }
       }
     }
   }

Windows
-------

.. code-block:: json

   {
     "mcpServers": {
       "django-cms": {
         "command": "python",
         "args": ["C:\\path\\to\\your\\project\\cms_mcp\\mcp_proxy.py"],
         "env": {
           "DJANGO_MCP_URL": "http://localhost:8000/mcp/"
         }
       }
     }
   }

Replace the path with the actual location of your ``mcp_proxy.py`` file.

Configuration file locations
----------------------------

The ``claude_desktop_config.json`` file is located at:

* **macOS**: ``~/Library/Application Support/Claude/claude_desktop_config.json``
* **Windows**: ``%APPDATA%\Claude\claude_desktop_config.json``

Applying the configuration
==========================

After saving the configuration:

1. **Completely quit** Claude Desktop (not just close the window)

   * **macOS**: Right-click the Claude icon in the menu bar → Quit
   * **Windows**: Right-click the Claude icon in the system tray → Quit

2. Relaunch Claude Desktop

3. Look for the **tools icon** (hammer/wrench) in the bottom-right corner of
   the input box

4. Click the tools icon to verify "django-cms" appears in the list

Verifying the connection
========================

To test the connection, try asking Claude:

* "List all pages in the CMS"
* "Show me the content of the homepage"
* "What tools are available for managing CMS content?"

Claude should be able to use the MCP tools to interact with your CMS.

Using with authentication
=========================

If your MCP endpoint requires authentication, update the proxy to include
the token:

.. code-block:: json

   {
     "mcpServers": {
       "django-cms": {
         "command": "python",
         "args": ["/path/to/cms_mcp/mcp_proxy.py"],
         "env": {
           "DJANGO_MCP_URL": "https://your-cms-site.com/mcp/",
           "MCP_API_TOKEN": "your-api-token-here"
         }
       }
     }
   }

Then update the proxy script to include the Authorization header.

Troubleshooting
===============

Server not appearing in Claude
------------------------------

* Ensure the configuration JSON is valid (no trailing commas)
* Verify the Python path is correct
* Check that Claude Desktop was fully restarted
* Review logs at:

  * **macOS**: ``~/Library/Logs/Claude/mcp*.log``
  * **Windows**: ``%APPDATA%\Claude\logs\``

Connection errors
-----------------

* Verify your Django server is running
* Check that the MCP URL is accessible
* Test the endpoint manually with curl:

  .. code-block:: bash

     curl -X POST http://localhost:8000/mcp/ \
       -H "Content-Type: application/json" \
       -d '{"jsonrpc":"2.0","method":"initialize","id":1}'

Permission errors
-----------------

* Ensure your MCP token (if used) is valid and not expired
* Check Django admin for token status
* Verify the user has appropriate CMS permissions

Security considerations
=======================

* Only connect to trusted Django CMS instances
* Use HTTPS for production servers
* Keep your API tokens secure—never commit them to version control
* Consider restricting the MCP endpoint to specific IP addresses
* Review tool permissions before approving actions in Claude
