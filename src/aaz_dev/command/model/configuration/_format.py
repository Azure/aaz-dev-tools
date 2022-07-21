from schematics.models import Model
from schematics.types import StringType, FloatType, IntType
from ._fields import CMDRegularExpressionField, CMDBooleanField
from ._utils import CMDDiffLevelEnum


class CMDFormat(Model):

    class Options:
        serialize_when_none = False

    def build_arg_fmt(self, builder, ref_fmt):
        """Build argument format from schema format"""
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

    def build_arg_fmt(self, builder, ref_fmt):
        fmt = CMDStringFormat()
        fmt.pattern = self.pattern
        fmt.max_length = self.max_length
        fmt.min_length = self.min_length
        return fmt

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            # skip pattern difference, because it's hard to tell
            if self.max_length and (not old.max_length or old.max_length > self.max_length):
                diff["max_length"] = f"from {old.max_length} to {self.max_length}"
            if self.min_length and (not old.min_length or old.min_length < self.min_length):
                diff["min_length"] = f"from {old.min_length} to {self.min_length}"

        if level >= CMDDiffLevelEnum.Structure:
            if self.pattern != old.pattern:
                diff["pattern"] = f"{old.pattern} != {self.pattern}"
            if self.max_length != old.max_length:
                diff["max_length"] = f"{old.max_length} != {self.max_length}"
            if self.min_length != old.min_length:
                diff["min_length"] = f"{old.min_length} != {self.min_length}"
        return diff


class CMDResourceIdFormat(CMDFormat):
    template = StringType(required=True)

    def build_arg_fmt(self, builder, ref_fmt):
        fmt = CMDResourceIdFormat()
        fmt.template = self.template
        return fmt

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.template != old.template:
                diff['template'] = f"from {old.template} to {self.template}"
        return diff


# integer
class CMDIntegerFormat(CMDFormat):
    multiple_of = IntType(
        min_value=0,
        serialized_name='multipleOf',
        deserialize_from='multipleOf'
    )
    maximum = IntType()
    minimum = IntType()

    def build_arg_fmt(self, builder, ref_fmt):
        fmt = CMDIntegerFormat()
        fmt.multiple_of = self.multiple_of
        fmt.maximum = self.maximum
        fmt.minimum = self.minimum
        return fmt

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.multiple_of and (not old.multiple_of or
                                     self.multiple_of != 0 and old.multiple_of % self.multiple_of != 0):
                diff["multiple_of"] = f"from {old.multiple_of} to {self.multiple_of}"
            if self.maximum and (not old.maximum or old.maximum > self.maximum):
                diff["maximum"] = f"from {old.maximum} to {self.maximum}"
            if self.minimum and (not old.minimum or old.minimum < self.minimum):
                diff["minimum"] = f"from {old.minimum} to {self.minimum}"

        if level >= CMDDiffLevelEnum.Structure:
            if self.multiple_of != old.multiple_of:
                diff["multiple_of"] = f"{old.multiple_of} != {self.multiple_of}"
            if self.maximum != old.maximum:
                diff["maximum"] = f"{old.maximum} != {self.maximum}"
            if self.minimum != old.minimum:
                diff["minimum"] = f"{old.minimum} != {self.minimum}"
        return diff


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

    def build_arg_fmt(self, builder, ref_fmt):
        fmt = CMDFloatFormat()
        fmt.multiple_of = self.multiple_of
        fmt.maximum = self.maximum
        fmt.exclusive_maximum = self.exclusive_maximum
        fmt.minimum = self.minimum
        fmt.exclusive_minimum = self.exclusive_minimum
        return fmt

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.multiple_of and (not old.multiple_of or
                                     self.multiple_of != 0 and old.multiple_of % self.multiple_of != 0):
                diff["multiple_of"] = f"from {old.multiple_of} to {self.multiple_of}"
            if self.maximum and (not old.maximum or old.maximum > self.maximum):
                diff["maximum"] = f"from {old.maximum} to {self.maximum}"
            if self.maximum and self.maximum == old.maximum and self.exclusive_maximum != old.exclusive_maximum:
                diff["exclusive_maximum"] = f"from {old.exclusive_maximum} to {self.exclusive_maximum}"
            if self.minimum and (not old.minimum or old.minimum < self.minimum):
                diff["minimum"] = f"from {old.minimum} to {self.minimum}"
            if self.minimum and self.minimum == old.minimum and self.exclusive_minimum != old.exclusive_minimum:
                diff["exclusive_minimum"] = f"from {old.exclusive_minimum} to {self.exclusive_minimum}"

        if level >= CMDDiffLevelEnum.Structure:
            if self.multiple_of != old.multiple_of:
                diff["multiple_of"] = f"{old.multiple_of} != {self.multiple_of}"
            if self.maximum != old.maximum:
                diff["maximum"] = f"{old.maximum} != {self.maximum}"
            if self.exclusive_maximum != old.exclusive_maximum:
                diff["exclusive_maximum"] = f"{old.exclusive_maximum} != {self.exclusive_maximum}"
            if self.minimum != old.minimum:
                diff["minimum"] = f"{old.minimum} != {self.minimum}"
            if self.exclusive_minimum != old.exclusive_minimum:
                diff["exclusive_minimum"] = f"{old.exclusive_minimum} != {self.exclusive_minimum}"
        return diff


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

    def build_arg_fmt(self, builder, ref_fmt):
        fmt = CMDObjectFormat()
        fmt.max_properties = self.max_properties
        fmt.min_properties = self.min_properties
        return fmt

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.max_properties and (not old.max_properties or old.max_properties > self.max_properties):
                diff["max_properties"] = f"from {old.max_properties} to {self.max_properties}"
            if self.min_properties and (not old.min_properties or old.min_properties < self.min_properties):
                diff["min_properties"] = f"from {old.min_properties} to {self.min_properties}"

        if level >= CMDDiffLevelEnum.Structure:
            if self.max_properties != old.max_properties:
                diff["max_properties"] = f"{old.max_properties} != {self.max_properties}"
            if self.min_properties != old.min_properties:
                diff["min_properties"] = f"{old.min_properties} != {self.min_properties}"
        return diff


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

    def build_arg_fmt(self, builder, ref_fmt):
        fmt = CMDArrayFormat()
        fmt.unique = self.unique
        fmt.max_length = self.max_length
        fmt.min_length = self.min_length
        # ignore str_format, it's not required for argument
        return fmt

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.unique != old.unique:
                diff["unique"] = f"{old.unique} != {self.unique}"
            if self.str_format != old.str_format:
                diff["str_format"] = f"{old.str_format} != {self.str_format}"
            if self.max_length and (not old.max_length or old.max_length > self.max_length):
                diff["max_length"] = f"from {old.max_length} to {self.max_length}"
            if self.min_length and (not old.min_length or old.min_length < self.min_length):
                diff["min_length"] = f"from {old.min_length} to {self.min_length}"

        if level >= CMDDiffLevelEnum.Structure:
            if self.max_length != old.max_length:
                diff["max_length"] = f"{old.max_length} != {self.max_length}"
            if self.min_length != old.min_length:
                diff["min_length"] = f"{old.min_length} != {self.min_length}"
        return diff
