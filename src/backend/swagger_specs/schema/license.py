from schematics.models import Model
from schematics.types import StringType, URLType


class License(Model):
    """License information for the exposed API."""

    name = StringType(required=True)  # The license name used for the API.
    url = URLType()  # A URL to the license used for the API. MUST be in the format of a URL.
