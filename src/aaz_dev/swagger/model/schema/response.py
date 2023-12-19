from schematics.models import Model
from schematics.types import BaseType, StringType, ModelType, DictType, PolyModelType

from command.model.configuration import CMDHttpResponse, CMDHttpResponseHeader, CMDHttpResponseJsonBody, \
    CMDObjectSchemaBase, CMDArraySchemaBase, CMDHttpResponseHeaderItem, CMDClsSchemaBase, CMDResponseJson, \
    CMDBooleanSchemaBase, CMDStringSchemaBase, CMDFloatSchemaBase, CMDIntegerSchemaBase
from swagger.model.schema.fields import MutabilityEnum
from swagger.utils import exceptions
from utils.error_format import AAZErrorFormatEnum
from .example_item import XmsExamplesField
from .fields import XmsErrorResponseField, XNullableField
from .header import Header
from .reference import Linkable
from .schema import Schema, ReferenceSchema, schema_and_reference_schema_claim_function


class Response(Model, Linkable):
    """Describes a single response from an API Operation."""

    description = StringType(
        required=True)  # A short description of the response. GFM syntax can be used for rich text representation.
    schema = PolyModelType(
        [ModelType(Schema), ModelType(ReferenceSchema)],
        claim_function=schema_and_reference_schema_claim_function
    )  # A definition of the response structure. It can be a primitive, an array or an object. If this field does not exist, it means no content is returned as part of the response. As an extension to the Schema Object, its root type value may also be "file". This SHOULD be accompanied by a relevant produces mime-type.
    headers = DictType(ModelType(Header))  # A list of headers that are sent with the response.
    examples = DictType(BaseType())  # TODO:

    x_ms_examples = XmsExamplesField()  # TODO:
    x_ms_error_response = XmsErrorResponseField()

    x_nullable = XNullableField(
        default=False)  # TODO: # when true, specifies that null is a valid value for the associated schema

    def link(self, swagger_loader, *traces, **kwargs):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        if self.schema is not None:
            self.schema.link(swagger_loader, *self.traces, 'schema')

        # assign resource id template to the schema and it's ref instance
        resource_id_template = kwargs.get('resource_id_template', None)
        if resource_id_template and self.schema:
            if isinstance(self.schema, Schema):
                self.schema.resource_id_templates.add(resource_id_template)
            if self.schema.ref_instance and isinstance(self.schema.ref_instance, Schema):
                self.schema.ref_instance.resource_id_templates.add(resource_id_template)

        # TODO: add support for examples and x_ms_examples

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            return 'description' in data
        elif isinstance(data, Response):
            return True
        return False

    def to_cmd(self, builder, is_error=False, status_codes=None, **kwargs):
        is_error = self.x_ms_error_response or is_error
        response = CMDHttpResponse()
        response.is_error = is_error
        response.status_codes = sorted(status_codes or [])
        builder.setup_description(response, self)

        if self.headers:
            response.header = CMDHttpResponseHeader()
            response.header.items = []
            for name in sorted(self.headers):
                header = CMDHttpResponseHeaderItem()
                header.name = name
                response.header.items.append(header)

        if self.schema:
            v = builder(
                self.schema,
                mutability=MutabilityEnum.Read,
                in_base=True,
                support_cls_schema=True,
            )
            if v.frozen:
                raise exceptions.InvalidSwaggerValueError(
                    msg="Invalid Response Schema. It's None.",
                    key=self.traces,
                )

            if isinstance(v, (
                    CMDStringSchemaBase,
                    CMDObjectSchemaBase,
                    CMDArraySchemaBase,
                    CMDBooleanSchemaBase,
                    CMDFloatSchemaBase,
                    CMDIntegerSchemaBase,
                    CMDClsSchemaBase,
            )):
                model = CMDResponseJson()
                if is_error:
                    error_format = AAZErrorFormatEnum.classify_error_format(builder, v)
                    if error_format:
                        err_schema = CMDClsSchemaBase()
                        err_schema.read_only = v.read_only
                        err_schema.frozen = v.frozen
                        err_schema._type = f"@{error_format}"
                        v = err_schema
                    else:
                        raise exceptions.InvalidSwaggerValueError(
                            msg="Error response schema is not supported yet.",
                            key=self.traces,
                        )
                model.schema = v
            else:
                raise exceptions.InvalidSwaggerValueError(
                    msg="Invalid Response type",
                    key=self.traces,
                    value=v.type
                )

            if isinstance(model, CMDResponseJson):
                response.body = CMDHttpResponseJsonBody()
                response.body.json = model
            else:
                raise NotImplementedError()

        return response
