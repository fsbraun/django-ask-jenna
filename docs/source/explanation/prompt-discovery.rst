================
Prompt discovery
================

How django-ask-jenna automatically discovers and registers prompts.

The discovery process
=====================

When Django starts, ``ask_jenna`` performs autodiscovery:

1. Iterates through all ``INSTALLED_APPS``
2. Attempts to import ``{app_name}.ask_jenna`` module
3. Scans the module for dictionary objects
4. Registers dictionaries as prompt definitions

Key format
==========

Prompts are keyed using the format::

   {app_label}.{model_name}:{view_name}

This allows the system to match prompts to specific admin views.

Example discovery
=================

Given this file structure::

   myapp/
   ├── models.py
   ├── admin.py
   └── ask_jenna.py

And this ``ask_jenna.py``::

   ARTICLE_PROMPTS = {
       "myapp.article:change_view": {...}
   }

The ``ARTICLE_PROMPTS`` dictionary will be discovered and its contents registered.

Why autodiscovery?
==================

This pattern follows Django conventions (like ``admin.py`` autodiscovery) and allows:

* Decoupled prompt definitions per app
* Easy override and customization
* No central configuration needed
