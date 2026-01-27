======================
Model Context Protocol
======================

This document explains how the Model Context Protocol (MCP) enables AI agents to
work with Django CMS content in a safe, predictable, and auditable way.

What is MCP?
============

The Model Context Protocol (MCP) is a standardized protocol for AI agents to
interact with external systems. It provides:

* **Tools**: Actions the agent can perform
* **Resources**: Data the agent can read
* **Prompts**: Predefined prompt templates

MCP uses JSON-RPC over HTTP for communication.

MCP and CMS Editing
===================

This implementation treats Django CMS as a **domain system**, not a UI or HTML
editor. Content is exposed to AI agents through **intent-driven tools and semantic
projections** rather than raw structure.

Tool Guidelines
===============

How the AI agent is allowed to act:

* **All mutations happen via tools**, never by editing resources directly.
* Tools encode **editorial intent**, not CRUD or form submission.

  * e.g. ``replace_block``, ``replace_section``, ``insert_after``, ``remove_block``

* Tools operate on **draft content only**; publishing is always explicit.
* Tools are **small, typed, and auditable** (one clear action per call).
* Destructive actions (delete, publish, nav changes) are explicit and constrained.
* No tool accepts or returns raw HTML.


Semantic Approach
=================

What the AI agent sees when reading CMS content.

Read Model
----------

* Pages and placeholders are exposed as **Markdown projections** optimized for reasoning.
* The markdown represents **editorial meaning**, not layout or rendering. Links are preserved.
* Important non-text elements are optionally exposed via **annotated Markdown
  components** (e.g. ``cta``, ``card``, ``hero``) — only when they represent
  clear editorial intent.

Semantic Index
--------------

HTML is parsed internally to build a **semantic index** of editorial units:

* headings (``h1``–``h6``)
* paragraphs (``p``)
* lists (``ul``/``ol``)
* blockquotes
* images / figures
* tables
* code blocks

Inline tags (``a``, ``em``, ``span``, etc.) and layout tags (``div``, ``nav``,
``footer``) are **not indexed**.

Matching is done on **visible text**, not DOM paths or IDs.


Delta Model
===========

How changes are expressed by AI agents.

* The AI proposes changes as **deltas**: ordered lists of semantic operations
  (see :doc:`../reference/mcp-mutation-tools` for the full schema).
* Deltas are **intent descriptions**, not diffs or plugin patches.
* Replacement operations fully replace the targeted block. Inline markup (links, emphasis)
  is preserved **only if explicitly included** in the new Markdown.
* Optional preview/dry-run tool can show what would change before applying.

.. note::

   If you replace something, you own it completely.

Changes to django CMS
====================

* All changes are routed through django CMS edit endpoints/admin logic.
* Validation errors are returned to the LLM.
* Permissions are enforced by django CMS as with human editors.

Process Flow
============

How changes flow through the system:

1. HTML → semantic index
2. Resolve delta targets via semantic matching
3. Convert Markdown → sanitized HTML fragments
4. Perform localized DOM replacement
5. Persist via existing CMS/admin logic

Key points:

* Markdown is **not** the source of truth — it's a projection for reasoning.
* Admin permissions, validation, hooks, and audit logs remain authoritative.
* Navs, footers, and other global structures are exposed (if at all) as
  **separate, tightly scoped domain objects**, not page content.

Design Benefits
===============

This approach:

* Keeps the AI operating in **editorial language**, not implementation details
* Avoids plugin tree or plugin restriction exposure while remaining structurally safe
* Makes behavior predictable, reviewable, and auditable
* Scales from "copilot" usage to more advanced automation without redesign

.. pull-quote::

   **Markdown is what the AI reads.
   Deltas are what it decides.
   Tools are how it acts.**
