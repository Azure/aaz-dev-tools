from schematics.models import Model
from schematics.types import BaseType, StringType, FloatType, ModelType, BooleanType, IntType, ListType

from command.model.configuration import CMDIntegerFormat, CMDStringFormat, CMDFloatFormat, CMDArrayFormat, \
    CMDSchemaEnum, CMDSchemaEnumItem
from command.model.configuration import CMDSchemaDefault, \
    CMDStringSchemaBase, CMDStringSchema, \
    CMDIntegerSchemaBase, CMDIntegerSchema, \
    CMDInteger32SchemaBase, CMDInteger32Schema, \
    CMDInteger64SchemaBase, CMDInteger64Schema, \
    CMDFloatSchemaBase, CMDFloatSchema, \
    CMDFloat32SchemaBase, CMDFloat32Schema, \
    CMDFloat64SchemaBase, CMDFloat64Schema, \
    CMDBooleanSchemaBase, CMDBooleanSchema, \
    CMDArraySchemaBase, CMDArraySchema, \
    CMDByteSchemaBase, CMDByteSchema, \
    CMDBinarySchemaBase, CMDBinarySchema, \
    CMDDurationSchemaBase, CMDDurationSchema, \
    CMDDateSchemaBase, CMDDateSchema, \
    CMDDateTimeSchemaBase, CMDDateTimeSchema, \
    CMDUuidSchemaBase, CMDUuidSchema, \
    CMDPasswordSchemaBase, CMDPasswordSchema
from swagger.utils import exceptions
from .fields import DataTypeFormatEnum, RegularExpressionField, XNullableField
from .x_ms_enum import XmsEnumField


class Items(Model):
    """A limited subset of JSON-Schema's items object. It is used by parameter definitions that are not located in "body"."""

    type = StringType(
        choices=("string", "number", "integer", "boolean", "array"),
        required=True
    )  # Required. The type of the object. The value MUST be one of "string", "number", "integer", "boolean", or "array".

    format = DataTypeFormatEnum()  # The extending format for the previously mentioned type. See Data Type Formats for further details.

    collection_format = StringType(
        choices=("csv", "ssv", "tsv", "pipes"),  # default is csv
        serialized_name="collectionFormat",
        deserialize_from="collectionFormat",
    )  # Determines the format of the array if type array is used. Possible values are: csv - comma separated values foo,bar; ssv - space separated values foo bar; tsv - tab separated values foo\tbar; pipes - pipe separated values foo|bar.

    default = BaseType()  # This keyword can be used to supply a default JSON value associated with a particular schema.  It is RECOMMENDED that a default value be valid against the associated schema.

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
    pattern = RegularExpressionField()

    # Validation keywords for arrays
    items = ModelType("Items")  # Required if type is "array". Describes the type of items in the array.
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

    x_ms_enum = XmsEnumField()
    x_nullable = XNullableField()  # TODO: # when true, specifies that null is a valid value for the associated schema

    def _build_model(self, in_base):
        if self.type == "string":
            if self.format is None:
                if in_base:
                    model = CMDStringSchemaBase()
                else:
                    model = CMDStringSchema()
            elif self.format == "byte":
                if in_base:
                    model = CMDByteSchemaBase()
                else:
                    model = CMDByteSchema()
            elif self.format == "binary":
                if in_base:
                    model = CMDBinarySchemaBase()
                else:
                    model = CMDBinarySchema()
            elif self.format == "date":
                if in_base:
                    model = CMDDateSchemaBase()
                else:
                    model = CMDDateSchema()
            elif self.format == "date-time":
                if in_base:
                    model = CMDDateTimeSchemaBase()
                else:
                    model = CMDDateTimeSchema()
            elif self.format == "password":
                if in_base:
                    model = CMDPasswordSchemaBase()
                else:
                    model = CMDPasswordSchema()
            elif self.format == "duration":
                if in_base:
                    model = CMDDurationSchemaBase()
                else:
                    model = CMDDurationSchema()
            elif self.format == "uuid":
                if in_base:
                    model = CMDUuidSchemaBase()
                else:
                    model = CMDUuidSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=[self.type, self.format])
        elif self.type == "integer":
            if self.format is None:
                if in_base:
                    model = CMDIntegerSchemaBase()
                else:
                    model = CMDIntegerSchema()
            elif self.format == "int32":
                if in_base:
                    model = CMDInteger32SchemaBase()
                else:
                    model = CMDInteger32Schema()
            elif self.format == "int64":
                if in_base:
                    model = CMDInteger64SchemaBase()
                else:
                    model = CMDInteger64Schema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=[self.type, self.format])
        elif self.type == "boolean":
            if self.format is None:
                if in_base:
                    model = CMDBooleanSchemaBase()
                else:
                    model = CMDBooleanSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=[self.type, self.format])
        elif self.type == "number":
            if self.format is None:
                if in_base:
                    model = CMDFloatSchemaBase()
                else:
                    model = CMDFloatSchema()
            elif self.format == "float":
                if in_base:
                    model = CMDFloat32SchemaBase()
                else:
                    model = CMDFloat32Schema()
            elif self.format == "double":
                if in_base:
                    model = CMDFloat64SchemaBase()
                else:
                    model = CMDFloat64Schema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=[self.type, self.format])
        elif self.type == "array":
            if self.format is None:
                if in_base:
                    model = CMDArraySchemaBase()
                else:
                    model = CMDArraySchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=[self.type, self.format])
        else:
            raise exceptions.InvalidSwaggerValueError(
                f"type is not supported", key=[self.type])

        return model

    def to_cmd_param(self, mutability, in_base=False):
        model = self._build_model(in_base=in_base)

        if isinstance(model, CMDStringSchemaBase):
            model.fmt = self.build_cmd_string_format()
            model.enum = self.build_enum()
        elif isinstance(model, CMDIntegerSchemaBase):
            model.fmt = self.build_cmd_integer_format()
            model.enum = self.build_enum()
        elif isinstance(model, CMDBooleanSchemaBase):
            pass
        elif isinstance(model, CMDFloatSchemaBase):
            model.fmt = self.build_cmd_float_format()
            model.enum = self.build_enum()
        elif isinstance(model, CMDArraySchemaBase):
            model.fmt = self.build_cmd_array_format()
            if self.items:
                assert isinstance(self.items, Items)
                model.item = self.items.to_cmd_param(mutability=mutability, in_base=True)

        if self.default is not None:
            model.default = CMDSchemaDefault()
            model.default.value = self.default

        return model

    def build_cmd_string_format(self):
        assert self.type == "string"
        fmt_assigned = False

        fmt = CMDStringFormat()

        if self.pattern is not None:
            fmt.pattern = self.pattern
            fmt_assigned = True
        if self.max_length is not None:
            fmt.max_length = self.max_length
            fmt_assigned = True
        if self.min_length is not None:
            fmt.min_length = self.min_length
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_cmd_integer_format(self):
        assert self.type == "integer"
        fmt_assigned = False
        fmt = CMDIntegerFormat()

        if self.maximum is not None:
            fmt.maximum = int(self.maximum)
            if self.exclusive_maximum and fmt.maximum == self.maximum:
                fmt.maximum -= 1
            fmt_assigned = True

        if self.minimum is not None:
            fmt.minimum = int(self.minimum)
            if self.exclusive_minimum and fmt.minimum == self.minimum:
                fmt.minimum += 1
            fmt_assigned = True

        if self.multiple_of is not None:
            fmt.multiple_of = self.multiple_of
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_cmd_float_format(self):
        assert self.type == "number"
        fmt_assigned = False
        fmt = CMDFloatFormat()

        if self.maximum is not None:
            fmt.maximum = self.maximum
            if self.exclusive_maximum:
                fmt.exclusive_maximum = True
            fmt_assigned = True

        if self.minimum is not None:
            fmt.minimum = int(self.minimum)
            if self.exclusive_minimum:
                fmt.exclusive_minimum = True
            fmt_assigned = True

        if self.multiple_of is not None:
            fmt.multiple_of = self.multiple_of
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_cmd_array_format(self):
        assert self.type == "array"
        fmt_assigned = False
        fmt = CMDArrayFormat()

        if self.unique_items:
            fmt.unique = True
            fmt_assigned = True

        if self.max_length is not None:
            fmt.max_length = self.max_length
            fmt_assigned = True

        if self.min_length is not None:
            fmt.min_length = self.min_length
            fmt_assigned = True

        if self.collection_format is not None and self.collection_format != 'csv':
            fmt.str_format = self.collection_format
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_enum(self):
        if not self.enum and not (self.x_ms_enum and self.x_ms_enum.values):
            return None
        enum = CMDSchemaEnum()
        enum.items = []
        if self.x_ms_enum and self.x_ms_enum.values:
            for v in self.x_ms_enum.values:
                item = CMDSchemaEnumItem()
                item.value = v.value
                if v.name:
                    # TODO: the name should be used as display name for argument
                    pass
                enum.items.append(item)
        elif self.enum:
            for v in self.enum:
                item = CMDSchemaEnumItem()
                item.value = v
                enum.items.append(item)
        return enum
