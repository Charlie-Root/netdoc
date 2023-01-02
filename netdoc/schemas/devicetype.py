"""Schema validation for DeviceType."""


def get_schema():
    """Return the JSON schema to validate DeviceType data."""
    return {
        "type": "object",
        "properties": {
            "manufacturer": {
                "type": "string",
            },
            "model": {
                "type": "string",
            },
            "description": {
                "type": "string",
            },
        },
        "required": [
            "manufacturer",
            "model",
        ],
    }
