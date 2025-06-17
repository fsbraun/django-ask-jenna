# django-ask-jenna

A Django app for managing and querying prompts using `ask_jenna.py`.

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