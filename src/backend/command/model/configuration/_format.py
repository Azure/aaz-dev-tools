from schematics.models import Model
from schematics.types import StringType, FloatType, IntType
from ._fields import CMDRegularExpressionField, CMDBooleanField


class CMDFormat(Model):

    def build_arg_fmt(self, builder):
        raise NotImplementedError()


# string
class CMDStringFormat(CMDFormat):
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

    def build_arg_fmt(self, builder):
        fmt = CMDStringFormat()
        fmt.pattern = self.pattern
        fmt.max_length = self.max_length
        fmt.min_length = self.min_length
        return fmt


# integer
class CMDIntegerFormat(CMDFormat):
    multiple_of = IntType(
        min_value=0,
        serialized_name='multipleOf',
        deserialize_from='multipleOf'
    )
    maximum = IntType()
    minimum = IntType()

    class Options:
        serialize_when_none = False

    def build_arg_fmt(self, builder):
        fmt = CMDIntegerFormat()
        fmt.multiple_of = self.multiple_of
        fmt.maximum = self.maximum
        fmt.minimum = self.minimum
        return fmt


# float
class CMDFloatFormat(CMDFormat):
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

    def build_arg_fmt(self, builder):
        fmt = CMDFloatFormat()
        fmt.multiple_of = self.multiple_of
        fmt.maximum = self.maximum
        fmt.exclusive_maximum = self.exclusive_maximum
        fmt.minimum = self.minimum
        fmt.exclusive_minimum = self.exclusive_minimum
        return fmt


# object
class CMDObjectFormat(CMDFormat):
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

    def build_arg_fmt(self, builder):
        fmt = CMDObjectFormat()
        fmt.max_properties = self.max_properties
        fmt.min_properties = self.min_properties
        return fmt


# array
class CMDArrayFormat(CMDFormat):
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

    str_format = StringType(
        choices=(
            "csv",  # default
            "ssv",
            "tsv",
            "pipes",
            "multi"
        ),
        serialized_name="strFormat",
        deserialize_from="strFormat",
    )   # the format convert an array instance to a string

    class Options:
        serialize_when_none = False

    def build_arg_fmt(self, builder):
        fmt = CMDArrayFormat()
        fmt.unique = self.unique
        fmt.max_length = self.max_length
        fmt.min_length = self.min_length
        fmt.str_format = self.str_format
        return fmt
