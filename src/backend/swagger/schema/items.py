from schematics.models import Model
from schematics.types import BaseType, StringType, FloatType, ModelType, BooleanType, IntType, ListType
from .types import DataTypeFormatEnum, RegularExpressionType


class Items(Model):
    """A limited subset of JSON-Schema's items object. It is used by parameter definitions that are not located in "body"."""

    type = StringType(
        choices=("string", "number", "integer", "boolean", "array"),
        required=True
    )   # Required. The type of the object. The value MUST be one of "string", "number", "integer", "boolean", or "array".

    format = DataTypeFormatEnum()   # The extending format for the previously mentioned type. See Data Type Formats for further details.

    collectionFormat = StringType(
        choices=("csv", "ssv", "tsv", "pipes"),
        default="csv",
        serialize_when_none=False
    ) # Determines the format of the array if type array is used. Possible values are: csv - comma separated values foo,bar; ssv - space separated values foo bar; tsv - tab separated values foo\tbar; pipes - pipe separated values foo|bar.

    default = BaseType(serialize_when_none=False) # This keyword can be used to supply a default JSON value associated with a particular schema.  It is RECOMMENDED that a default value be valid against the associated schema.

    enum = ListType(BaseType(), serialize_when_none=False)

    # Validation keywords for numeric instances (number and integer)
    multipleOf = FloatType(min_value=0, serialize_when_none=False)  # The value of "multipleOf" MUST be a JSON number.  This number MUST be strictly greater than 0.
    maximum = FloatType(serialize_when_none=False)
    exclusiveMaximum = BooleanType(serialize_when_none=False)
    minimum = FloatType(serialize_when_none=False)
    exclusiveMinimum = BooleanType(serialize_when_none=False)

    # Validation keywords for strings
    maxLength = IntType(min_value=0, serialize_when_none=False)
    minLength = IntType(min_value=0, serialize_when_none=False)
    pattern = RegularExpressionType(serialize_when_none=False)

    # Validation keywords for arrays
    items = ModelType("Items", serialize_when_none=False)   # Required if type is "array". Describes the type of items in the array.
    maxItems = IntType(min_value=0, serialize_when_none=False)
    minItems = IntType(min_value=0, serialize_when_none=False)
    uniqueItems = BooleanType(serialize_when_none=False)
