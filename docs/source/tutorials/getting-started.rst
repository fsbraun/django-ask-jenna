===============
Getting started
===============

This tutorial will guide you through installing django-ask-jenna and setting up your first AI-powered feature.

Prerequisites
=============

* Python 3.10+
* Django 5.2+
* An AI service API key (e.g., OpenAI)

Installation
============

Install django-ask-jenna using pip:

.. code-block:: bash

   pip install django-ask-jenna

Configuration
=============

Add ``ask_jenna`` to your ``INSTALLED_APPS``:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'ask_jenna',
   ]

Configure your AI service settings:

.. code-block:: python

   ASK_JENNA_API_KEY = "your-api-key"
   ASK_JENNA_SERVICE = "openai"
   ASK_JENNA_MODEL = "gpt-3.5-turbo"

Next steps
==========

Continue to :doc:`first-prompt` to create your first AI prompt.
