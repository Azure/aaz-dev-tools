from schematics.models import Model
from schematics.types import BaseType, StringType, ModelType, DictType

from command.model.configuration import CMDHttpResponse, CMDHttpResponseHeader, CMDHttpJsonBody, CMDObjectSchemaBase, \
    CMDArraySchemaBase, CMDHttpResponseHeaderItem
from command.model.configuration import CMDJson, CMDBooleanSchemaBase, CMDStringSchemaBase, CMDFloatSchemaBase, \
    CMDIntegerSchemaBase
from swagger.model.schema.fields import MutabilityEnum
from swagger.utils import exceptions
from .fields import XmsExamplesField, XmsErrorResponseField, XNullableField
from .header import Header
from .reference import Linkable
from .schema import Schema


class Response(Model, Linkable):
    """Describes a single response from an API Operation."""

    description = StringType(required=True)  # A short description of the response. GFM syntax can be used for rich text representation.
    schema = ModelType(Schema)  # A definition of the response structure. It can be a primitive, an array or an object. If this field does not exist, it means no content is returned as part of the response. As an extension to the Schema Object, its root type value may also be "file". This SHOULD be accompanied by a relevant produces mime-type.
    headers = DictType(ModelType(Header))  # A list of headers that are sent with the response.
    examples = DictType(BaseType())  # TODO:

    x_ms_examples = XmsExamplesField()  # TODO:
    x_ms_error_response = XmsErrorResponseField()

    x_nullable = XNullableField(default=False)  # TODO: # when true, specifies that null is a valid value for the associated schema

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        if self.schema is not None:
            self.schema.link(swagger_loader, *self.traces, 'schema')

        # TODO: add support for examples and x_ms_examples

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            return 'description' in data
        elif isinstance(data, Response):
            return True
        return False

    def to_cmd_model(self):
        response = CMDHttpResponse()

        if self.description:
            response.description = self.description
        if self.x_ms_error_response:
            response.is_error = True

        if self.headers:
            response.header = CMDHttpResponseHeader()
            response.header.items = []
            for name in sorted(self.headers):
                header = CMDHttpResponseHeaderItem()
                header.name = name
                response.header.items.append(header.name)

        if self.schema:
            v = self.schema.to_cmd_schema(traces_route=[], mutability=MutabilityEnum.Read, in_base=True)
            if isinstance(v, (
                    CMDStringSchemaBase,
                    CMDObjectSchemaBase,
                    CMDArraySchemaBase,
                    CMDBooleanSchemaBase,
                    CMDFloatSchemaBase,
                    CMDIntegerSchemaBase
            )):
                model = CMDJson()
                model.schema = v
            else:
                if v is None:
                    raise exceptions.InvalidSwaggerValueError(
                        msg="Invalid Response",
                        key=self.traces,
                        value=v
                    )
                else:
                    raise exceptions.InvalidSwaggerValueError(
                        msg="Invalid Response type",
                        key=self.traces,
                        value=v.type
                    )

            if isinstance(model, CMDJson):
                response.body = CMDHttpJsonBody()
                response.body.json = model
            else:
                raise NotImplementedError()

        return response
