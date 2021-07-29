from schematics.models import Model
from schematics.types import StringType, URLType


class Contact(Model):
    """Contact information for the exposed API."""

    name = StringType(serialize_when_none=False)    # The identifying name of the contact person/organization.
    url = URLType(serialize_when_none=False)        # The URL pointing to the contact information. MUST be in the format of a URL.
    email = StringType(serialize_when_none=False)   # The email address of the contact person/organization. MUST be in the format of an email address.
