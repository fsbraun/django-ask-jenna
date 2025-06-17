# django-ask-jenna

A Django app that adds generative AI features to the Django admin and the Django CMS frontend editor. Django app developers can add prompts for their admin views by creating an `ask_jenna.py` file in their app directory, enabling prompt management and querying.

## Installation

```bash
pip install django-ask-jenna
```

Add `ask_jenna` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'ask_jenna',
]
```

## Usage

### Declaring Prompts in `ask_jenna.py`

To declare prompts, create or edit the `ask_jenna.py` file in your Django app. It should contain names
(which does not matter) that are assigned with dictionaries.

The keys are of the from `{app_name}.{model_name}:{view}, e.g., `"cms.pagecontent:change_view"`.

```python
PAGE_PROMPTS = {
    "cms.pagecontent:change_view": {
        "prompt": ...
    }
}
```


## License

MIT