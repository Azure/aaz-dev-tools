from schematics.models import Model
from schematics.types import StringType, FloatType, IntType
from ._fields import CMDRegularExpressionField, CMDBooleanField


# string
class CMDStringFormat(Model):
    pattern = CMDRegularExpressionField()
    max_length = IntType(
        serialized_name="maxLength",
        deserialize_from="maxLength",
        min_value=0
    )
    min_length = IntType(
        serialized_name="minLength",
        deserialize_from="minLength",
        min_value=0
    )

    class Options:
        serialize_when_none = False


# integer
class CMDIntegerFormat(Model):
    multiple_of = IntType(
        min_value=0,
        serialized_name='multipleOf',
        deserialize_from='multipleOf'
    )
    maximum = IntType()
    minimum = IntType()

    class Options:
        serialize_when_none = False


# float
class CMDFloatFormat(Model):
    multiple_of = FloatType(
        min_value=0,
        serialized_name='multipleOf',
        deserialize_from='multipleOf'
    )
    maximum = FloatType()
    exclusive_maximum = CMDBooleanField(
        serialized_name='exclusiveMaximum',
        deserialize_from='exclusiveMaximum'
    )
    minimum = FloatType()
    exclusive_minimum = CMDBooleanField(
        serialized_name='exclusiveMinimum',
        deserialize_from='exclusiveMinimum'
    )

    class Options:
        serialize_when_none = False


# object
class CMDObjectFormat(Model):
    max_properties = IntType(
        min_value=0,
        serialized_name='maxProperties',
        deserialize_from='maxProperties'
    )
    min_properties = IntType(
        min_value=0,
        serialized_name='minProperties',
        deserialize_from='minProperties'
    )

    class Options:
        serialize_when_none = False


# array
class CMDArrayFormat(Model):
    unique = CMDBooleanField()
    max_length = IntType(
        min_value=0,
        serialized_name='maxLength',
        deserialize_from='maxLength'
    )
    min_length = IntType(
        min_value=0,
        serialized_name='minLength',
        deserialize_from='minLength'
    )

    string_format = StringType(
        choices=(
            "csv",
            "ssv",
            "tsv",
            "pipes",
            "multi"
        ),
        serialized_name="stringFormat",
        deserialize_from="stringFormat",
    )   # the format convert array to string

    class Options:
        serialize_when_none = False
