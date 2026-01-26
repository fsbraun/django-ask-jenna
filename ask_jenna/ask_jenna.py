from cms.toolbar.utils import get_object_preview_url


PAGE_PROMTS: dict = {
    "cms.pagecontent:change_view": {
        "title": {
            "type": "text",
            "prompt": """Generate a a JSON string with an engaging new title for this page in the language with the language code {{ instance.language|default:"en" }}""",
            "dynamic_content": lambda x: get_object_preview_url(x) if x else None,
        },
        "page_title": {
            "prompt": """Return a JSON string with one or two new words for the page title in the language with the language code {{ instance.language|default:"en" }}""",
            "dynamic_content": lambda x: get_object_preview_url(x) if x else None,
        },
        "menu_title": {
            "prompt": """Return a JSON string with one or two new words for the page title in the language with the language code {{ instance.language|default:"en" }}""",
            "dynamic_content": lambda x: get_object_preview_url(x) if x else None,
        },
        "meta_description": {
            "type": "text",
            "length": 280,
            "prompt": """
                Generate a JSON string for a meta description with an approximate length of {{ length }} characters for this page
                optimizing search engine results in the language with the language code {{ instance.language|default:"en" }}""",
            "dynamic_content": lambda x: get_object_preview_url(x) if x else None,
        }
    }
}

