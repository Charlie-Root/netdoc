"""Schema validation for DeviceRole."""


def get_schema():
    """Return the JSON schema to validate DeviceRole data."""
    return {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
            },
            "vm_role": {
                "type": "boolean",
            },
            "description": {
                "type": "string",
            },
        },
        "required": [
            "name",
        ],
    }
