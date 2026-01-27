===============
Dynamic content
===============

How to add dynamic content to your prompts using callable functions.

Using dynamic_content
=====================

The ``dynamic_content`` key accepts a callable that receives the model instance:

.. code-block:: python

   def get_related_articles(instance):
       related = instance.related_articles.all()[:5]
       return {
           "related_titles": [a.title for a in related],
           "category_context": instance.category.description,
       }

   PAGE_PROMPTS = {
       "blog.post:change_view": {
           "prompt": "Suggest tags based on: {{ instance.title }} and related: {{ related_titles }}",
           "dynamic_content": get_related_articles,
       }
   }

The returned dictionary is merged into the template context.
