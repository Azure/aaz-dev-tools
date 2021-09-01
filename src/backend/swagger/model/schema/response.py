from schematics.models import Model
from schematics.types import BaseType, StringType, ModelType, DictType
from .schema import Schema
from .header import Header
from .types import XmsExamplesType, XmsErrorResponseType, XNullableType
from .reference import Linkable


class Response(Model, Linkable):
    """Describes a single response from an API Operation."""

    description = StringType(required=True)  # A short description of the response. GFM syntax can be used for rich text representation.
    schema = ModelType(Schema)  # A definition of the response structure. It can be a primitive, an array or an object. If this field does not exist, it means no content is returned as part of the response. As an extension to the Schema Object, its root type value may also be "file". This SHOULD be accompanied by a relevant produces mime-type.
    headers = DictType(ModelType(Header))  # A list of headers that are sent with the response.
    examples = DictType(BaseType())

    x_ms_examples = XmsExamplesType()
    x_ms_error_response = XmsErrorResponseType()

    x_nullable = XNullableType(default=False)  # when true, specifies that null is a valid value for the associated schema

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        if self.schema is not None:
            self.schema.link(swagger_loader, *self.traces, 'schema')

        # TODO: add support for examples and x_ms_examples

    @classmethod
    def _claim_polymorphic(cls, data):
        return isinstance(data, dict) and 'description' in data
