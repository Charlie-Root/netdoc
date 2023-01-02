"""Schema validation for DeviceType."""
from dcim.models import Model


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
                "enum": list(
                    Model.objects.all().order_by("name").values_list("name", flat=True)
                ),
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
