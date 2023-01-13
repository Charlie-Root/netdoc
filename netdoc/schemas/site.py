"""Schema validation for Site."""


def get_schema():
    """Return the JSON schema to validate Site data."""
    return {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
            },
            "description": {
                "type": "string",
            },
        },
        "required": [
            "name",
        ],
    }
