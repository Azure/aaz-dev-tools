from schematics.models import Model
from schematics.types import StringType, BooleanType, ModelType, PolyModelType
from .schema import Schema
from .items import Items
from .reference import Reference
from .x_ms_parameter_grouping import XmsParameterGroupingType
from .types import XmsSkipURLEncodingType
from .types import XmsParameterLocationType
from .types import XmsClientNameType, XmsClientFlatten, XmsClientDefaultType, XmsHeaderCollectionPrefixType
from .types import XmsClientRequestIdType


class _ParameterBase(Model):
    """Describes a single operation parameter.
    A unique parameter is defined by a combination of a name and location.
    There are five possible parameter types.
    """

    IN_VALUE = None
    name = StringType(required=True)    # The name of the parameter. Parameter names are case sensitive. If in is "path", the name field MUST correspond to the associated path segment from the path field in the Paths Object. See Path Templating for further information. For all other cases, the name corresponds to the parameter name used based on the in property.
    description = StringType()  # A brief description of the parameter. This could contain examples of use.
    required = BooleanType(default=False)  # Determines whether this parameter is mandatory. If the parameter is in "path", this property is required and its value MUST be true. Otherwise, the property MAY be included and its default value is false.
    _in = StringType(serialized_name="in", required=True)   # The location of the parameter. Possible values are "query", "header", "path", "formData" or "body".

    x_ms_parameter_grouping = XmsParameterGroupingType()
    x_ms_parameter_location = XmsParameterLocationType()
    x_ms_client_name = XmsClientNameType()
    x_ms_client_flatten = XmsClientFlatten()
    x_ms_client_default = XmsClientDefaultType()

    @classmethod
    def _claim_polymorphic(cls, data):
        in_value = data.get('in', None)
        return in_value is not None and in_value == cls.IN_VALUE


class QueryParameter(Items, _ParameterBase):
    """Parameters that are appended to the URL. For example, in /items?id=###, the query parameter is id."""

    IN_VALUE = "query"
    allowEmptyValue = BooleanType(default=False)  # Sets the ability to pass empty-valued parameters. This is valid only for either query or formData parameters and allows you to send a parameter with a name only or an empty value. Default value is false.
    collectionFormat = StringType(
        choices=("csv", "ssv", "tsv", "pipes", "multi"),
        default="csv",

    )  # multi - corresponds to multiple parameter instances instead of multiple values for a single instance foo=bar&foo=baz.


class HeaderParameter(Items, _ParameterBase):
    """Custom headers that are expected as part of the request."""
    IN_VALUE = "header"

    x_ms_header_collection_prefix = XmsHeaderCollectionPrefixType()  # Handle collections of arbitrary headers by distinguishing them with a specified prefix.
    x_ms_client_request_id = XmsClientRequestIdType()


class PathParameter(Items, _ParameterBase):
    """Used together with Path Templating, where the parameter value is actually part of the operation's URL. This does not include the host or base path of the API. For example, in /items/{itemId}, the path parameter is itemId."""

    IN_VALUE = "path"
    required = BooleanType(required=True, default=True)

    x_ms_skip_url_encoding = XmsSkipURLEncodingType()


class FormDataParameter(Items, _ParameterBase):
    """Used to describe the payload of an HTTP request when either application/x-www-form-urlencoded, multipart/form-data or both are used as the content type of the request (in Swagger's definition, the consumes property of an operation). This is the only parameter type that can be used to send files, thus supporting the file type. Since form parameters are sent in the payload, they cannot be declared together with a body parameter for the same operation. Form parameters have a different format based on the content-type used (for further details, consult http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4):
        - application/x-www-form-urlencoded - Similar to the format of Query parameters but as a payload. For example, foo=1&bar=swagger - both foo and bar are form parameters. This is normally used for simple parameters that are being transferred.
        - multipart/form-data - each parameter takes a section in the payload with an internal header. For example, for the header Content-Disposition: form-data; name="submit-name" the name of the parameter is submit-name. This type of form parameters is more commonly used for file transfers.
    """

    IN_VALUE = "formData"
    type = StringType(
        choices=("string", "number", "integer", "boolean", "array", "file"),
        required=True
    )   #  If type is "file", the consumes MUST be either "multipart/form-data", " application/x-www-form-urlencoded" or both
    allowEmptyValue = BooleanType(default=False)  # Sets the ability to pass empty-valued parameters. This is valid only for either query or formData parameters and allows you to send a parameter with a name only or an empty value. Default value is false.
    collectionFormat = StringType(
        choices=("csv", "ssv", "tsv", "pipes", "multi"),
        default="csv",

    ) # multi - corresponds to multiple parameter instances instead of multiple values for a single instance foo=bar&foo=baz.


class BodyParameter(_ParameterBase):
    """The payload that's appended to the HTTP request. Since there can only be one payload, there can only be one body parameter. The name of the body parameter has no effect on the parameter itself and is used for documentation purposes only. Since Form parameters are also in the payload, body and form parameters cannot exist together for the same operation."""

    IN_VALUE = "body"
    schema = ModelType(Schema, required=True)  # The schema defining the type used for the body parameter.


class ParameterType(PolyModelType):

    def __init__(self, support_reference, **kwargs):
        model_spec = [
            QueryParameter, HeaderParameter, PathParameter, FormDataParameter, BodyParameter
        ]
        if support_reference:
            model_spec.append(Reference)
        super(ParameterType, self).__init__(model_spec=model_spec, **kwargs)

