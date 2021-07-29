from schematics.models import Model
from schematics.types import StringType, ModelType
from .contact import Contact
from .license import License


class Info(Model):
    """The object provides metadata about the API. The metadata can be used by the clients if needed, and can be presented in the Swagger-UI for convenience."""

    title = StringType(required=True)       # The title of the application.
    version = StringType(required=True)     # Provides the version of the application API (not to be confused with the specification version)
    description = StringType(serialize_when_none=False)  # A short description of the application
    termsOfService = StringType(serialize_when_none=False)  # The Terms of Service for the API.
    contact = ModelType(Contact, serialize_when_none=False)  # The contact information for the exposed API.
    license = ModelType(License, serialize_when_none=False)  # The license information for the exposed API.
