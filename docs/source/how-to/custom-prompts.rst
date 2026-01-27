==============
Custom prompts
==============

How to create and customize AI prompts for your Django models.

Prompt structure
================

Each prompt is defined as a dictionary with the following keys:

.. code-block:: python

   {
       "myapp.mymodel:view_name": {
           "prompt": "Your prompt template with {{ instance.field }}",
           "dynamic_content": lambda instance: get_extra_context(instance),
       }
   }

Using Django template syntax
============================

Prompts support Django template syntax:

.. code-block:: python

   PAGE_PROMPTS = {
       "blog.post:change_view": {
           "prompt": """
           Summarize this blog post:
           Title: {{ instance.title }}
           Content: {{ instance.body }}
           {% if instance.category %}Category: {{ instance.category }}{% endif %}
           """,
       }
   }
