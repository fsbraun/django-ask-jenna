delta_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/schemas/page-delta.schema.json",
    "title": "ContentDelta",
    "type": "object",
    "required": ["placeholder_id", "language", "operations"],
    "additionalProperties": False,
    "properties": {
        "placeholder_id": {
            "type": "string",
            "description": "Identifier of the placeholder being edited",
        },
        "language": {
            "type": "string",
            "description": "Language code for the content (e.g. en, de, fr)",
        },
        "operations": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/operation"},
            "description": "Ordered list of delta operations applied sequentially",
        },
    },
    "$defs": {
        "operation": {
            "oneOf": [
                {"$ref": "#/$defs/replace_block"},
                {"$ref": "#/$defs/replace_section"},
                {"$ref": "#/$defs/insert_after"},
                {"$ref": "#/$defs/insert_before"},
                {"$ref": "#/$defs/insert_at_end"},
                {"$ref": "#/$defs/remove_block"},
                {"$ref": "#/$defs/replace_component"},
            ]
        },
        "target": {
            "type": "object",
            "required": ["kind", "match"],
            "additionalProperties": False,
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": [
                        "heading",
                        "paragraph",
                        "list",
                        "blockquote",
                        "image",
                        "table",
                        "code_block",
                        "component",
                    ],
                },
                "match": {
                    "type": "string",
                    "description": "Visible text used to identify the target node",
                },
                "level": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 6,
                    "description": "Heading level (required only for headings)",
                },
                "component_type": {
                    "type": "string",
                    "description": "Component type when kind=component (e.g. cta, card, hero)",
                },
            },
        },
        "replace_block": {
            "type": "object",
            "required": ["op", "target", "new_markdown"],
            "additionalProperties": False,
            "properties": {
                "op": {"const": "replace_block"},
                "target": {"$ref": "#/$defs/target"},
                "new_markdown": {
                    "type": "string",
                    "description": "Markdown content that fully replaces the block",
                },
            },
        },
        "replace_section": {
            "type": "object",
            "required": ["op", "section_title", "new_markdown"],
            "additionalProperties": False,
            "properties": {
                "op": {"const": "replace_section"},
                "section_title": {
                    "type": "string",
                    "description": "Exact visible text of the section heading",
                },
                "new_markdown": {
                    "type": "string",
                    "description": "Markdown for the entire replacement section",
                },
            },
        },
        "insert_after": {
            "type": "object",
            "required": ["op", "target", "new_markdown"],
            "additionalProperties": False,
            "properties": {
                "op": {"const": "insert_after"},
                "target": {"$ref": "#/$defs/target"},
                "new_markdown": {"type": "string"},
            },
        },
        "insert_before": {
            "type": "object",
            "required": ["op", "target", "new_markdown"],
            "additionalProperties": False,
            "properties": {
                "op": {"const": "insert_before"},
                "target": {"$ref": "#/$defs/target"},
                "new_markdown": {"type": "string"},
            },
        },
        "insert_at_end": {
            "type": "object",
            "required": ["op", "new_markdown"],
            "additionalProperties": False,
            "properties": {
                "op": {"const": "insert_at_end"},
                "section_title": {
                    "type": "string",
                    "description": "Optional section title to append to; otherwise page end",
                },
                "new_markdown": {"type": "string"},
            },
        },
        "remove_block": {
            "type": "object",
            "required": ["op", "target"],
            "additionalProperties": False,
            "properties": {
                "op": {"const": "remove_block"},
                "target": {"$ref": "#/$defs/target"},
            },
        },
    },
}
