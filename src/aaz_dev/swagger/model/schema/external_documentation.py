from schematics.models import Model
from schematics.types import StringType, URLType


class ExternalDocumentation(Model):
    """Allows referencing an external resource for extended documentation."""

    description = StringType()  # A short description of the target documentation. GFM syntax can be used for rich text representation.
    url = URLType(required=True)  # The URL for the target documentation. Value MUST be in the format of a URL.
