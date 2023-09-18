import logging

from command.model.configuration import CMDRequestJson, CMDBooleanSchema, CMDStringSchema, CMDObjectSchema, \
    CMDArraySchema, CMDFloatSchema, CMDIntegerSchema
from schematics.models import Model
from schematics.types import StringType, BooleanType, ModelType, PolyModelType, BaseType
from swagger.utils import exceptions

from .fields import XmsClientNameField, XmsClientFlattenField, XmsClientDefaultField
from .fields import XmsClientRequestIdField, XNullableField, XPublishField, XRequiredField, XClientNameField, \
    XNewPatternField, XPreviousPatternField, XCommentField
from .fields import XmsParameterLocationField, XmsApiVersionField, XmsSkipUrlEncodingField, XmsArmIdDetailsField
from .fields import XmsSkipURLEncodingField, XAccessibilityField, XmsHeaderCollectionPrefix, XOriginalNameField
from .items import Items
from .reference import Reference, Linkable
from .schema import Schema, ReferenceSchema, schema_and_reference_schema_claim_function
from .x_ms_parameter_grouping import XmsParameterGroupingField

logger = logging.getLogger('backend')


class ParameterBase(Model):
    """Describes a single operation parameter.
    A unique parameter is defined by a combination of a name and location.
    There are five possible parameter types.
    """

    IN_VALUE = None

    name = StringType(
        required=True)  # The name of the parameter. Parameter names are case sensitive. If in is "path", the name field MUST correspond to the associated path segment from the path field in the Paths Object. See Path Templating for further information. For all other cases, the name corresponds to the parameter name used based on the in property.
    description = StringType()  # A brief description of the parameter. This could contain examples of use.
    required = BooleanType(
        default=False)  # Determines whether this parameter is mandatory. If the parameter is in "path", this property is required and its value MUST be true. Otherwise, the property MAY be included and its default value is false.
    _in = StringType(
        serialized_name="in",
        deserialize_from="in",
        required=True
    )  # The location of the parameter. Possible values are "query", "header", "path", "formData" or "body".

    x_ms_parameter_grouping = XmsParameterGroupingField()  # TODO:
    x_ms_parameter_location = XmsParameterLocationField()  # TODO:
    x_ms_client_name = XmsClientNameField()  # TODO:
    x_ms_client_flatten = XmsClientFlattenField()  # TODO:
    x_ms_client_default = XmsClientDefaultField()
    x_ms_arm_id_details = XmsArmIdDetailsField()  # TODO: Add support for it, can be used for resource id template

    # specific properties
    _x_accessibility = XAccessibilityField()  # only used in ContainerRegistry Data plane
    _x_required = XRequiredField()  # only used in ContainerRegistry Data plane
    _x_publish = XPublishField()  # only used in Maps Data Plane
    _x_example = BaseType(serialized_name='x-example', deserialize_from='x-example')  # deprecated
    _x_examples = BaseType(serialized_name='x-examples', deserialize_from='x-examples')  # deprecated
    _x_client_name = XClientNameField()  # Only used in Maps Data Plane
    _x_new_pattern = XNewPatternField()  # Only used in FrontDoor Mgmt Plane
    _x_previous_pattern = XPreviousPatternField()  # Only used in FrontDoor Mgmt Plane
    _x_comment = XCommentField()  # Only used in IoTCenter Mgmt Plane
    _x_original_name = XOriginalNameField()  # Only used in Marketplane Catalog Data Plane

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            in_value = data.get('in', None)
            return in_value is not None and in_value == cls.IN_VALUE
        elif isinstance(data, ParameterBase):
            return data.IN_VALUE == cls.IN_VALUE
        return False


class QueryParameter(Items, ParameterBase):
    """Parameters that are appended to the URL. For example, in /items?id=###, the query parameter is id."""
    IN_VALUE = "query"

    allow_empty_value = BooleanType(
        default=False,
        serialized_name="allowEmptyValue",
        deserialize_from="allowEmptyValue",
    )  # Sets the ability to pass empty-valued parameters. This is valid only for either query or formData parameters and allows you to send a parameter with a name only or an empty value. Default value is false.

    collection_format = StringType(
        choices=("csv", "ssv", "tsv", "pipes", "multi"),  # default is csv
        serialized_name="collectionFormat",
        deserialize_from="collectionFormat",
    )  # multi - corresponds to multiple parameter instances instead of multiple values for a single instance foo=bar&foo=baz.

    x_ms_api_version = XmsApiVersionField()
    x_ms_skip_url_encoding = XmsSkipUrlEncodingField()

    def to_cmd(self, builder, **kwargs):
        model = super().to_cmd(builder, **kwargs)

        model.name = self.name
        model.required = self.required
        builder.setup_description(model, self)

        if self.x_ms_skip_url_encoding:
            model.skip_url_encoding = False

        return model


class HeaderParameter(Items, ParameterBase):
    """Custom headers that are expected as part of the request."""
    IN_VALUE = "header"

    x_ms_client_request_id = XmsClientRequestIdField()

    # specific properties, will not support
    x_ms_header_collection_prefix = XmsHeaderCollectionPrefix()  # only used in Storage Data plane

    def _new_param(self):
        pass

    def to_cmd(self, builder, **kwargs):
        model = super().to_cmd(builder, **kwargs)
        model.name = self.name
        model.required = self.required

        builder.setup_description(model, self)
        return model


class PathParameter(Items, ParameterBase):
    """Used together with Path Templating, where the parameter value is actually part of the operation's URL. This does not include the host or base path of the API. For example, in /items/{itemId}, the path parameter is itemId."""
    IN_VALUE = "path"

    required = BooleanType(required=True, default=True)

    x_ms_skip_url_encoding = XmsSkipURLEncodingField()

    def to_cmd(self, builder, **kwargs):
        model = super().to_cmd(builder, **kwargs)
        model.name = self.name
        model.required = self.required

        builder.setup_description(model, self)

        if self.x_ms_skip_url_encoding:
            model.skip_url_encoding = True

        return model


class FormDataParameter(Items, ParameterBase):
    """Used to describe the payload of an HTTP request when either application/x-www-form-urlencoded, multipart/form-data or both are used as the content type of the request (in Swagger's definition, the consumes property of an operation). This is the only parameter type that can be used to send files, thus supporting the file type. Since form parameters are sent in the payload, they cannot be declared together with a body parameter for the same operation. Form parameters have a different format based on the content-type used (for further details, consult http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4):
        - application/x-www-form-urlencoded - Similar to the format of Query parameters but as a payload. For example, foo=1&bar=swagger - both foo and bar are form parameters. This is normally used for simple parameters that are being transferred.
        - multipart/form-data - each parameter takes a section in the payload with an internal header. For example, for the header Content-Disposition: form-data; name="submit-name" the name of the parameter is submit-name. This type of form parameters is more commonly used for file transfers.
    """

    IN_VALUE = "formData"

    type = StringType(
        choices=("string", "number", "integer", "boolean", "array", "file"),
        required=True
    )  # If type is "file", the consumes MUST be either "multipart/form-data", " application/x-www-form-urlencoded" or both
    allow_empty_value = BooleanType(
        default=False,
        serialized_name="allowEmptyValue",
        deserialize_from="allowEmptyValue",
    )  # Sets the ability to pass empty-valued parameters. This is valid only for either query or formData parameters and allows you to send a parameter with a name only or an empty value. Default value is false.
    collection_format = StringType(
        choices=("csv", "ssv", "tsv", "pipes", "multi"),  # default is csv
        serialized_name="collectionFormat",
        deserialize_from="collectionFormat",
    )  # multi - corresponds to multiple parameter instances instead of multiple values for a single instance foo=bar&foo=baz.

    def to_cmd(self, builder, **kwargs):
        # TODO:
        raise exceptions.InvalidSwaggerValueError(
            msg="FormData Parameter is not supported",
            key=[self.name, self.type, self.format]
        )


class BodyParameter(ParameterBase, Linkable):
    """The payload that's appended to the HTTP request. Since there can only be one payload, there can only be one body parameter. The name of the body parameter has no effect on the parameter itself and is used for documentation purposes only. Since Form parameters are also in the payload, body and form parameters cannot exist together for the same operation."""

    IN_VALUE = "body"

    schema = PolyModelType(
        [ModelType(Schema), ModelType(ReferenceSchema)],
        claim_function=schema_and_reference_schema_claim_function,
        required=True
    )  # The schema defining the type used for the body parameter.

    x_nullable = XNullableField(
        default=False)  # TODO: # when true, specifies that null is a valid value for the associated schema

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        self.schema.link(swagger_loader, *self.traces, 'schema')

    def to_cmd(self, builder, **kwargs):
        v = builder(self.schema, in_base=False, support_cls_schema=True)
        v.name = self.name
        if self.required:
            # A required body parameter cannot be frozen.
            # This can help to create an empty payload.
            v.frozen = False
        if v.frozen:
            logger.warning(
                msg=f"Request Body Parameter is None: {self.traces}"
            )
            return None
        if isinstance(v, (
                CMDStringSchema,
                CMDObjectSchema,
                CMDArraySchema,
                CMDBooleanSchema,
                CMDFloatSchema,
                CMDIntegerSchema
        )):
            model = CMDRequestJson()
            model.schema = v
            v.required = self.required
            if isinstance(v, CMDObjectSchema):
                # flatten body parameter
                v.client_flatten = True
        else:
            raise exceptions.InvalidSwaggerValueError(
                msg="Invalid Request type",
                key=self.traces,
                value=v.type
            )
        return model


class ParameterField(PolyModelType):

    def __init__(self, support_reference, **kwargs):
        model_spec = [
            QueryParameter, HeaderParameter, PathParameter, FormDataParameter, BodyParameter
        ]
        if support_reference:
            model_spec.append(Reference)
        super(ParameterField, self).__init__(model_spec=model_spec, **kwargs)
