===================
Your first prompt
===================

This tutorial shows how to create your first AI prompt for a Django model.

Creating a prompt file
======================

Create an ``ask_jenna.py`` file in your Django app:

.. code-block:: python

   # myapp/ask_jenna.py

   PAGE_PROMPTS = {
       "myapp.article:change_view": {
           "prompt": "Generate a compelling title for this article about: {{ instance.content }}",
       }
   }

The prompt will be automatically discovered when Django starts.

Testing your prompt
===================

1. Navigate to the Django admin
2. Edit an Article instance
3. Look for the AI-powered suggestion button

Next steps
==========

See :doc:`../how-to/custom-prompts` for more advanced prompt configuration.
