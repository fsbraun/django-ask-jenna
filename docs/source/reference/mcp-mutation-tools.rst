===================
MCP Mutation Tools
===================

This reference documents the mutation tools available through the MCP server for
modifying Django CMS page content. These tools allow AI agents to make structured,
auditable changes to pages using a delta-based approach.

Top-level Delta Schema
======================

This is the payload passed to a mutation tool (e.g. ``apply_page_delta``).

.. code-block:: json

   {
     "placeholder_id": "string",
     "language": "string",
     "operations": [
       { /* delta operation */ }
     ]
   }

Constraints
-----------

* ``operations`` is **ordered** and applied sequentially
* If **any operation fails**, the entire delta fails
* Delta is always scoped to **one placeholder + one language**

Target Specification
====================

Targets describe **what the editor is pointing at**, not how it's stored.
This specification is shared by most operations.

.. code-block:: json

   {
     "kind": "heading | paragraph | list | blockquote | image | table | code_block | component",
     "match": "string",
     "level": "number (optional, headings only)",
     "component_type": "string (optional, components only)"
   }

Semantics
---------

* ``match`` is matched against **visible text** (``text_content()`` / ``get_text()``)
* Matching must result in **exactly one node**
* 0 matches → error
* > 1 match → ambiguity error

Examples
--------

Paragraph:

.. code-block:: json

   {
     "kind": "paragraph",
     "match": "We offer fast delivery worldwide"
   }

Heading:

.. code-block:: json

   {
     "kind": "heading",
     "level": 2,
     "match": "Pricing"
   }

Component:

.. code-block:: json

   {
     "kind": "component",
     "component_type": "cta",
     "match": "Contact Sales"
   }

Delta Operations
================

This section documents the complete v1 action set for page mutations.

replace_block
-------------

Replace a single semantic block **entirely**.

.. code-block:: json

   {
     "op": "replace_block",
     "target": { /* target spec */ },
     "new_markdown": "string"
   }

**Semantics:**

* Replaces the entire block, including inline markup
* Any links/components must be explicitly included in ``new_markdown``
* Most common operation

**Example:**

.. code-block:: json

   {
     "op": "replace_block",
     "target": {
       "kind": "paragraph",
       "match": "We offer fast delivery worldwide"
     },
     "new_markdown": "We offer **fast, carbon-neutral delivery** worldwide."
   }

replace_section
---------------

Replace everything under a heading (until the next heading of same or higher level).

.. code-block:: json

   {
     "op": "replace_section",
     "section_title": "string",
     "new_markdown": "string"
   }

**Semantics:**

* Heading itself is replaced
* Content below it is replaced
* Extremely LLM-friendly and safe

**Example:**

.. code-block:: json

   {
     "op": "replace_section",
     "section_title": "Pricing",
     "new_markdown": "## Pricing\n\nEnterprise-ready plans with annual discounts."
   }

insert_after
------------

Insert new content **relative to an existing block**.

.. code-block:: json

   {
     "op": "insert_after",
     "target": { /* target spec */ },
     "new_markdown": "string"
   }

**Semantics:**

* Does not modify the target
* Inserts as a new sibling block
* Preferred over numeric positioning

**Example:**

.. code-block:: json

   {
     "op": "insert_after",
     "target": {
       "kind": "heading",
       "match": "Services"
     },
     "new_markdown": "All services include 24/7 customer support."
   }

insert_before
-------------

Same as ``insert_after``, but inserts before the target.

.. code-block:: json

   {
     "op": "insert_before",
     "target": { /* target spec */ },
     "new_markdown": "string"
   }

insert_at_end
-------------

Append content to the end of the page or section.

.. code-block:: json

   {
     "op": "insert_at_end",
     "new_markdown": "string"
   }

With optional section scope:

.. code-block:: json

   {
     "op": "insert_at_end",
     "section_title": "string",
     "new_markdown": "string"
   }

remove_block
------------

Explicitly delete a single semantic block.

.. code-block:: json

   {
     "op": "remove_block",
     "target": { /* target spec */ }
   }

**Semantics:**

* No implicit deletes
* Must match exactly one block
* Always auditable

**Example:**

.. code-block:: json

   {
     "op": "remove_block",
     "target": {
       "kind": "paragraph",
       "match": "Limited time offer"
     }
   }

replace_component
-----------------

Used only for **annotated Markdown components** (CTA, card, hero).

.. code-block:: json

   {
     "op": "replace_component",
     "component_type": "cta | card | hero",
     "match": "string",
     "new_markdown": "string"
   }

**Example:**

.. code-block:: json

   {
     "op": "replace_component",
     "component_type": "cta",
     "match": "Contact Sales",
     "new_markdown": "```component:cta\nlabel: Talk to an Expert\ntarget: /contact\n```"
   }

Global Invariants
=================

These rules are enforced by the mutation tools and must be followed by AI agents:

1. **No HTML in deltas** - All content must be valid Markdown
2. **Replacement owns the block completely** - Partial replacements are not supported
3. **Targets must resolve unambiguously** - Exactly one match required
4. **Operations apply in order** - Sequential processing of the operations array
5. **No implicit deletes** - Deletions must be explicit ``remove_block`` operations
6. **Markdown is not round-tripped** - Output may differ from input formatting
7. **Failures are explicit, not guessed** - Errors are raised, not silently ignored

Design Rationale
================

This delta schema is designed to be:

* **Small enough** for LLMs to learn reliably
* **Rich enough** for real editorial workflows
* **Safe** - No AST exposure or DOM manipulation by the LLM
* **Auditable** - Easy to validate, preview, and review changes

.. note::

   A delta is an ordered list of editorial intentions expressed in Markdown,
   resolved against a semantic index, and applied via constrained tools.
