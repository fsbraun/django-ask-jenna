============
Architecture
============

django-ask-jenna consists of two main components that work together to bring AI capabilities to Django applications.

ask_jenna
=========

The ``ask_jenna`` package provides:

* **Prompt autodiscovery**: Automatically finds and registers prompts from ``ask_jenna.py`` files in installed apps
* **Template rendering**: Renders prompts using Django's template engine with model instance context
* **AI service integration**: Connects to AI providers (OpenAI, etc.) to generate responses

cms_mcp
=======

The ``cms_mcp`` package implements the Model Context Protocol:

* **MCP Server**: Exposes Django CMS content and operations via the standardized MCP protocol
* **Tools**: Provides read/write access to pages, plugins, placeholders, and media
* **Resources**: Exposes curated content as MCP resources
* **Authentication**: Token-based authentication for secure API access

How they work together
======================

1. AI agents connect to the MCP server
2. The server exposes available tools and resources
3. Agents can read CMS content and use prompts to generate suggestions
4. Agents can write changes back through the tool interface
