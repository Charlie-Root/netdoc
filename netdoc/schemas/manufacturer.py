"""Schema validation for Manufacturer."""


def get_schema():
    """Return the JSON schema to validate Manufacturer data."""
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
