from cms.app_base import CMSAppConfig


class CMSMCPConfig(CMSAppConfig):
    page_wizard_schema = {
        "title": "CreateCMSPageForm",
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Page type"},
            "title": {
                "type": "string",
                "maxLength": 255,
                "description": "Provide a title for the new page. This title will appear in the browser title bar and menus.",
            },
            "slug": {
                "type": "string",
                "maxLength": 255,
                "description": "Leave empty for automatic slug, or override as required.",
            },
            "parent_page": {"type": "string"},
            "content": {
                "type": "string",
                "description": "Optional. Contains markdown content for the new page. Include headings, especially the page title if it should be shown on the page itself.",
            },
        },
        "required": ["title"],
        "additionalProperties": False,
    }

    def __init__(self, *args, **kwargs):
        from cms.forms.wizards import CreateCMSPageForm

        CreateCMSPageForm._mcp_schema = self.page_wizard_schema
        super().__init__(*args, **kwargs)
