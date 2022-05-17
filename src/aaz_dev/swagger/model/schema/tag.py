from schematics.models import Model
from schematics.types import StringType, ModelType
from .external_documentation import ExternalDocumentation


class Tag(Model):
    """Allows adding meta data to a single tag that is used by the Operation Object. It is not mandatory to have a Tag Object per tag used there."""

    name = StringType(required=True)  # The name of the tag.
    description = StringType()  # A short description for the tag. GFM syntax can be used for rich text representation.
    external_docs = ModelType(
        ExternalDocumentation,
        serialized_name="externalDocs",
        deserialize_from="externalDocs"
    )  # Additional external documentation for this tag.
