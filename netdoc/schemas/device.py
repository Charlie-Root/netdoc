"""Schema validation for Device."""
from dcim.models import Manufacturer, Site


def get_schema():
    """Return the JSON schema to validate Device data."""
    return {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "transform": ["toUpperCase"],
            },
            "manufacturer": {
                "type": "string",
                "enum": list(
                    Manufacturer.objects.all()
                    .order_by("name")
                    .values_list("name", flat=True)
                ),
            },
            "serial": {
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
            "manufacturer",
            "site",
        ],
    }
