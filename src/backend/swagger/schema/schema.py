from schematics.models import Model
from schematics.types import ListType, BaseType, DictType, ModelType, BooleanType, FloatType, IntType, StringType, PolyModelType
from .reference import ReferenceType
from .types import DataTypeFormatEnum, RegularExpressionType
from .xml import XML
from .external_documentation import ExternalDocumentation


class Schema(Model):
    """
    The Schema Object allows the definition of input and output data types. These types can be objects, but also primitives and arrays. This object is based on the JSON Schema Specification Draft 4 and uses a predefined subset of it. On top of this subset, there are extensions provided by this specification to allow for more complete documentation.
    Further information about the properties can be found in JSON Schema Core and JSON Schema Validation. Unless stated otherwise, the property definitions follow the JSON Schema specification as referenced here.
    """

    ref = ReferenceType(serialize_when_none=False)
    format = DataTypeFormatEnum(serialize_when_none=False)
    title = StringType(serialize_when_none=False)
    description = StringType(serialize_when_none=False)
    default = BaseType(serialize_when_none=False)

    # Validation keywords for numeric instances (number and integer)
    multipleOf = FloatType(min_value=0, serialize_when_none=False)
    maximum = FloatType(serialize_when_none=False)
    exclusiveMaximum = BooleanType(serialize_when_none=False)
    minimum = FloatType(serialize_when_none=False)
    exclusiveMinimum = BooleanType(serialize_when_none=False)

    # Validation keywords for strings
    maxLength = IntType(min_value=0, serialize_when_none=False)
    minLength = IntType(min_value=0, serialize_when_none=False)
    pattern = RegularExpressionType(serialize_when_none=False)

    # Validation keywords for arrays
    items = PolyModelType(
        ["Schema", ListType(ModelType("Schema"))],
        serialize_when_none=False
    )
    maxItems = IntType(min_value=0, serialize_when_none=False)
    minItems = IntType(min_value=0, serialize_when_none=False)
    uniqueItems = BooleanType(serialize_when_none=False)

    # Validation keywords for objects
    maxProperties = IntType(min_value=0, serialize_when_none=False)
    minProperties = IntType(min_value=0, serialize_when_none=False)
    required = ListType(StringType(), min_size=1, serialize_when_none=False)
    properties = DictType(
        ModelType("Schema"),
        serialize_when_none=False
    )
    additionalProperties = PolyModelType(
        [BooleanType(), "Schema"],
        serialize_when_none=False,
        default=True
    )
    discriminator = StringType(serialize_when_none=False)  # Adds support for polymorphism. The discriminator is the schema property name that is used to differentiate between other schema that inherit this schema. The property name used MUST be defined at this schema and it MUST be in the required property list. When used, the value MUST be the name of this schema or any schema that inherits it.

    # Validation keywords for any instance type
    enum = ListType(BaseType(), serialize_when_none=False)
    type = StringType(
        choices=["array", "boolean", "integer", "number", "null", "object", "string"],  # https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04#section-3.5
        required=True
    )
    allOf = ListType(
        ModelType("Schema"),
        serialize_when_none=False
    )

    readOnly = BooleanType(default=False, serialize_when_none=False)  # Relevant only for Schema "properties" definitions. Declares the property as "read only". This means that it MAY be sent as part of a response but MUST NOT be sent as part of the request. Properties marked as readOnly being true SHOULD NOT be in the required list of the defined schema. Default value is false.
    xml = ModelType(XML, serialize_when_none=False)  # This MAY be used only on properties schemas. It has no effect on root schemas. Adds Additional metadata to describe the XML representation format of this property.
    externalDocs = ModelType(ExternalDocumentation, serialize_when_none=False)  # Additional external documentation for this schema.
    example = BaseType(serialize_when_none=False)  # A free-form property to include an example of an instance for this schema.

