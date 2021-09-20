from schematics.models import Model
from schematics.types import BaseType, StringType, FloatType, ModelType, BooleanType, IntType, ListType
from .types import DataTypeFormatEnum, RegularExpressionType, XNullableType
from .x_ms_enum import XmsEnumType


class Items(Model):
    """A limited subset of JSON-Schema's items object. It is used by parameter definitions that are not located in "body"."""

    type = StringType(
        choices=("string", "number", "integer", "boolean", "array"),
        required=True
    )   # Required. The type of the object. The value MUST be one of "string", "number", "integer", "boolean", or "array".

    format = DataTypeFormatEnum()   # The extending format for the previously mentioned type. See Data Type Formats for further details.

    collection_format = StringType(
        choices=("csv", "ssv", "tsv", "pipes"),
        default="csv",
        serialized_name="collectionFormat",
        deserialize_from="collectionFormat",
    )  # Determines the format of the array if type array is used. Possible values are: csv - comma separated values foo,bar; ssv - space separated values foo bar; tsv - tab separated values foo\tbar; pipes - pipe separated values foo|bar.

    default = BaseType() # This keyword can be used to supply a default JSON value associated with a particular schema.  It is RECOMMENDED that a default value be valid against the associated schema.

    enum = ListType(BaseType())

    # Validation keywords for numeric instances (number and integer)
    multiple_of = FloatType(
        min_value=0,
        serialized_name="multipleOf",
        deserialize_from="multipleOf",
    )  # The value of "multipleOf" MUST be a JSON number.  This number MUST be strictly greater than 0.
    maximum = FloatType()
    exclusive_maximum = BooleanType(
        serialized_name="exclusiveMaximum",
        deserialize_from="exclusiveMaximum",
    )
    minimum = FloatType()
    exclusive_minimum = BooleanType(
        serialized_name="exclusiveMinimum",
        deserialize_from="exclusiveMinimum"
    )

    # Validation keywords for strings
    max_length = IntType(
        min_value=0,
        serialized_name="maxLength",
        deserialize_from="maxLength"
    )
    min_length = IntType(
        min_value=0,
        serialized_name="minLength",
        deserialize_from="minLength"
    )
    pattern = RegularExpressionType()

    # Validation keywords for arrays
    items = ModelType("Items")   # Required if type is "array". Describes the type of items in the array.
    max_items = IntType(
        min_value=0,
        serialized_name="maxItems",
        deserialize_from="maxItems"
    )
    min_items = IntType(
        min_value=0,
        serialized_name="minItems",
        deserialize_from="minItems"
    )
    unique_items = BooleanType(
        serialized_name="uniqueItems",
        deserialize_from="uniqueItems"
    )

    x_ms_enum = XmsEnumType()
    x_nullable = XNullableType(default=False)  # when true, specifies that null is a valid value for the associated schema
