from schematics.models import Model
from schematics.types import BaseType, StringType, ModelType, DictType
from .schema import Schema
from .header import Header


class Response(Model):
    """Describes a single response from an API Operation."""

    description = StringType(required=True)  # A short description of the response. GFM syntax can be used for rich text representation.
    schema = ModelType(Schema, serialize_when_none=False)  # A definition of the response structure. It can be a primitive, an array or an object. If this field does not exist, it means no content is returned as part of the response. As an extension to the Schema Object, its root type value may also be "file". This SHOULD be accompanied by a relevant produces mime-type.
    headers = DictType(Header, serialize_when_none=False)  # A list of headers that are sent with the response.
    examples = DictType(BaseType(), serialize_when_none=False)
