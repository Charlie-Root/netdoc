"""Schema validation for Device."""
from dcim.models import DeviceRole, DeviceType, Manufacturer, Site


def get_schema():
    """Return the JSON schema to validate Device data."""
    return {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "transform": ["toUpperCase"],
            },
            "device_role": {
                "type": "string",
                "enum": list(
                    DeviceRole.objects.all()
                    .order_by("name")
                    .values_list("name", flat=True)
                ),
            },
            "description": {
                "type": "string",
            },
            "manufacturer": {
                "type": "string",
                "enum": list(
                    Manufacturer.objects.all()
                    .order_by("name")
                    .values_list("name", flat=True)
                ),
            },
            "device_type": {
                "type": "string",
                "enum": list(
                    DeviceType.objects.all()
                    .order_by("name")
                    .values_list("name", flat=True)
                ),
            },
            "serial_number": {
                "type": "string",
            },
            "site": {
                "type": "string",
                "enum": list(
                    Site.objects.all().order_by("name").values_list("name", flat=True)
                ),
            },
        },
        "required": [
            "name",
            "device_role",
            "manufacturer",
            "device_type",
            "site",
        ],
    }
