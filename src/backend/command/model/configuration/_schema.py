# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType, ListType, PolyModelType
from schematics.types.serializable import serializable

from ._arg import CMDStringArg, CMDStringArgBase, \
    CMDByteArg, CMDByteArgBase, \
    CMDBinaryArg, CMDBinaryArgBase, \
    CMDDurationArg, CMDDurationArgBase, \
    CMDDateArg, CMDDateArgBase, \
    CMDDateTimeArg, CMDDateTimeArgBase, \
    CMDUuidArg, CMDUuidArgBase, \
    CMDPasswordArg, CMDPasswordArgBase, \
    CMDBooleanArg, CMDBooleanArgBase, \
    CMDIntegerArg, CMDIntegerArgBase, \
    CMDInteger32Arg, CMDInteger32ArgBase, \
    CMDInteger64Arg, CMDInteger64ArgBase, \
    CMDFloatArg, CMDFloatArgBase, \
    CMDFloat32Arg, CMDFloat32ArgBase, \
    CMDFloat64Arg, CMDFloat64ArgBase, \
    CMDArrayArg, CMDArrayArgBase, \
    CMDObjectArg, CMDObjectArgBase, CMDObjectArgAdditionalProperties, \
    CMDClsArg, CMDClsArgBase
from ._fields import CMDVariantField, StringType, CMDClassField, CMDBooleanField, CMDPrimitiveField, CMDDescriptionField
from ._format import CMDStringFormat, CMDIntegerFormat, CMDFloatFormat, CMDObjectFormat, CMDArrayFormat
from ._utils import CMDDiffLevelEnum


class CMDSchemaEnumItem(Model):
    arg = CMDVariantField()  # value will be used when specific argument is provided

    # properties as nodes
    value = CMDPrimitiveField(required=True)

    class Options:
        serialize_when_none = False
        _attributes = {"arg"}

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.value != old.value:
                diff["value"] = f"{old.value} != {self.value}"

        if level >= CMDDiffLevelEnum.Associate:
            if self.arg != old.arg:
                diff["arg"] = f"{old.arg} != {self.arg}"

        return diff


class CMDSchemaEnum(Model):
    # properties as tags

    # properties as nodes
    items = ListType(ModelType(CMDSchemaEnumItem), min_size=1)

    class Options:
        _attributes = set()

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = []

        if level >= CMDDiffLevelEnum.BreakingChange:
            # old.items should be the subset of self.items
            for old_item in old.items:
                matched = False
                for item in self.items:
                    if old_item.value == item.value:
                        matched = True
                        item_diff = item.diff(old_item, level)
                        if item_diff:
                            diff.append(item_diff)
                        break
                if not matched:
                    diff.append(f"MissEnumItem: {old_item.value}")

        if level >= CMDDiffLevelEnum.Structure:
            for item in self.items:
                matched = False
                for old_item in old.items:
                    if item.value == old_item.value:
                        matched = True
                        break
                if not matched:
                    diff.append(f"NewEnumItem: {item.value}")
        return diff


class CMDSchemaDefault(Model):
    """ The argument value if an argument is not used """

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null

    class Options:
        _attributes = set()

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.value != old.value:
                diff["value"] = f"{old.value} != {self.value}"
        return diff


class CMDSchemaBase(Model):
    TYPE_VALUE = None
    ARG_TYPE = None

    # properties as tags
    required = CMDBooleanField()
    read_only = CMDBooleanField(
        serialized_name="readOnly",
        deserialize_from="readOnly"
    )
    frozen = CMDBooleanField()  # frozen schema will not be used
    const = CMDBooleanField()   # when a schema is const it's default value is not None.

    # properties as nodes
    default = ModelType(CMDSchemaDefault)

    # base types: "array", "boolean", "integer", "float", "object", "string",

    class Options:
        serialize_when_none = False
        _attributes = {"required", "read_only", "frozen", "const", "type"}

    @serializable
    def type(self):
        return self._get_type()

    def _get_type(self):
        assert self.TYPE_VALUE is not None
        return self.TYPE_VALUE

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.TYPE_VALUE is None:
            return False

        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        elif isinstance(data, CMDSchemaBase):
            return data.TYPE_VALUE == cls.TYPE_VALUE
        return False

    def _diff_base(self, old, level, diff):
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.type != old.type:
                diff["type"] = f"{old.type} != {self.type}"
            if self.required and not old.required:
                diff["required"] = f"it's required now."
            if self.read_only and not old.read_only:
                diff["read_only"] = f"it's read_only now."
            if self.const and not old.const:
                diff["const"] = f"it's const now."
            if old.default:
                if not self.default:
                    diff["default"] = f"miss default now."
                else:
                    default_diff = self.default.diff(old.default, level)
                    if default_diff:
                        diff["default"] = default_diff

        if level >= CMDDiffLevelEnum.Structure:
            if self.required != old.required:
                diff["required"] = f"{old.required} != {self.required}"
            if self.read_only != old.read_only:
                diff["read_only"] = f"{old.read_only} != {self.read_only}"
            if self.const != old.const:
                diff['const'] = f"{old.const} != {self.const}"
            if self.default:
                default_diff = self.default.diff(old.default, level)
                if default_diff:
                    diff["default"] = default_diff
        return diff


class CMDSchemaBaseField(PolyModelType):

    def __init__(self, **kwargs):
        super(CMDSchemaBaseField, self).__init__(
            model_spec=CMDSchemaBase,
            allow_subclasses=True,
            serialize_when_none=False,
            **kwargs
        )

    def export(self, value, format, context=None):
        if value.frozen:
            # frozen schema base will be ignored
            return None
        return super(CMDSchemaBaseField, self).export(value, format, context)


class CMDSchema(CMDSchemaBase):
    # properties as tags
    name = StringType(required=True)
    arg = CMDVariantField()

    description = CMDDescriptionField()

    skip_url_encoding = CMDBooleanField(
        serialized_name="skipUrlEncoding",
        deserialize_from="skipUrlEncoding",
    )  # used in path and query parameters

    class Options:
        _attributes = CMDSchemaBase.Options._attributes | {"name", "arg", "description", "skip_url_encoding"}

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDSchema, cls)._claim_polymorphic(data):
            if isinstance(data, dict):
                # distinguish with CMDSchemaBase and CMDSchema
                return 'name' in data
            else:
                return isinstance(data, CMDSchema)
        return False

    def _diff(self, old, level, diff):
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.name != old.name:
                diff["name"] = f"{old.name} != {self.name}"
            if (not self.skip_url_encoding) != (not old.skip_url_encoding):  # None should be same as false
                diff["skip_url_encoding"] = f"{old.skip_url_encoding} != {self.skip_url_encoding}"

        if level >= CMDDiffLevelEnum.Associate:
            if self.arg != old.arg:
                diff["arg"] = f"{old.arg} != {self.arg}"

        if level >= CMDDiffLevelEnum.All:
            if self.description != old.description:
                diff["description"] = f"'{old.description}' != '{self.description}'"
        return diff

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        if self.frozen and old.frozen:
            return None
        diff = {}
        diff = self._diff_base(old, level, diff)
        diff = self._diff(old, level, diff)
        return diff


class CMDSchemaField(PolyModelType):

    def __init__(self, **kwargs):
        super(CMDSchemaField, self).__init__(
            model_spec=CMDSchema,
            allow_subclasses=True,
            serialize_when_none=False,
            **kwargs
        )

    def export(self, value, format, context=None):
        if value.frozen:
            # frozen schema base will be ignored
            return None
        return super(CMDSchemaField, self).export(value, format, context)


# cls
class CMDClsSchemaBase(CMDSchemaBase):
    ARG_TYPE = CMDClsArgBase

    _type = StringType(
        deserialize_from='type',
        serialized_name='type',
        required=True
    )

    class Options:
        _attributes = CMDSchemaBase.Options._attributes

    def _get_type(self):
        return self._type

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None and type_value.startswith("@"):
                return True
        elif isinstance(data, CMDClsSchemaBase):
            return True
        return False


class CMDClsSchema(CMDSchema, CMDClsSchemaBase):
    ARG_TYPE = CMDClsArg

    class Options:
        _attributes = CMDSchema.Options._attributes | CMDClsSchemaBase.Options._attributes


# string
class CMDStringSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "string"
    ARG_TYPE = CMDStringArgBase

    fmt = ModelType(
        CMDStringFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    enum = ModelType(CMDSchemaEnum)

    class Options:
        _attributes = CMDSchemaBase.Options._attributes

    def _diff_base(self, old, level, diff):
        diff = super(CMDStringSchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        enum_diff = _diff_enum(self.enum, old.enum, level)
        if enum_diff:
            diff["enum"] = enum_diff

        return diff


class CMDStringSchema(CMDSchema, CMDStringSchemaBase):
    ARG_TYPE = CMDStringArg

    class Options:
        _attributes = CMDSchema.Options._attributes | CMDStringSchemaBase.Options._attributes


# byte: base64 encoded characters
class CMDByteSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "byte"
    ARG_TYPE = CMDByteArgBase

    class Options:
        _attributes = CMDStringSchemaBase.Options._attributes


class CMDByteSchema(CMDStringSchema, CMDByteSchemaBase):
    ARG_TYPE = CMDByteArg

    class Options:
        _attributes = CMDStringSchema.Options._attributes | CMDByteSchemaBase.Options._attributes


# binary: any sequence of octets
class CMDBinarySchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "binary"
    ARG_TYPE = CMDBinaryArgBase

    class Options:
        _attributes = CMDStringSchemaBase.Options._attributes


class CMDBinarySchema(CMDStringSchema, CMDBinarySchemaBase):
    ARG_TYPE = CMDBinaryArg

    class Options:
        _attributes = CMDStringSchema.Options._attributes | CMDClsSchemaBase.Options._attributes


# duration
class CMDDurationSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "duration"
    ARG_TYPE = CMDDurationArgBase

    class Options:
        _attributes = CMDStringSchemaBase.Options._attributes


class CMDDurationSchema(CMDStringSchema, CMDDurationSchemaBase):
    ARG_TYPE = CMDDurationArg

    class Options:
        _attributes = CMDStringSchema.Options._attributes | CMDDurationSchemaBase.Options._attributes


# date: As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "date"
    ARG_TYPE = CMDDateArgBase

    class Options:
        _attributes = CMDStringSchemaBase.Options._attributes


class CMDDateSchema(CMDStringSchema, CMDDateSchemaBase):
    ARG_TYPE = CMDDateArg

    class Options:
        _attributes = CMDStringSchema.Options._attributes | CMDDateSchemaBase.Options._attributes


# date-time: As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateTimeSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "date-time"
    ARG_TYPE = CMDDateTimeArgBase

    class Options:
        _attributes = CMDStringSchemaBase.Options._attributes


class CMDDateTimeSchema(CMDStringSchema, CMDDateTimeSchemaBase):
    ARG_TYPE = CMDDateTimeArg

    class Options:
        _attributes = CMDStringSchema.Options._attributes | CMDDateTimeSchemaBase.Options._attributes


# uuid
class CMDUuidSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "uuid"
    ARG_TYPE = CMDUuidArgBase

    class Options:
        _attributes = CMDStringSchemaBase.Options._attributes


class CMDUuidSchema(CMDStringSchema, CMDUuidSchemaBase):
    ARG_TYPE = CMDUuidArg

    class Options:
        _attributes = CMDStringSchema.Options._attributes | CMDUuidSchemaBase.Options._attributes


# password
class CMDPasswordSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "password"
    ARG_TYPE = CMDPasswordArgBase

    class Options:
        _attributes = CMDStringSchemaBase.Options._attributes


class CMDPasswordSchema(CMDStringSchema, CMDPasswordSchemaBase):
    ARG_TYPE = CMDPasswordArg

    class Options:
        _attributes = CMDStringSchema.Options._attributes | CMDPasswordSchemaBase.Options._attributes


# integer
class CMDIntegerSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "integer"
    ARG_TYPE = CMDIntegerArgBase

    fmt = ModelType(
        CMDIntegerFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDSchemaEnum)

    class Options:
        _attributes = CMDSchemaBase.Options._attributes

    def _diff_base(self, old, level, diff):
        diff = super(CMDIntegerSchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        enum_diff = _diff_enum(self.enum, old.enum, level)
        if enum_diff:
            diff["enum"] = enum_diff

        return diff


class CMDIntegerSchema(CMDSchema, CMDIntegerSchemaBase):
    ARG_TYPE = CMDIntegerArg

    class Options:
        _attributes = CMDSchema.Options._attributes | CMDIntegerSchemaBase.Options._attributes


# integer32
class CMDInteger32SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer32"
    ARG_TYPE = CMDInteger32ArgBase

    class Options:
        _attributes = CMDIntegerSchemaBase.Options._attributes


class CMDInteger32Schema(CMDIntegerSchema, CMDInteger32SchemaBase):
    ARG_TYPE = CMDInteger32Arg

    class Options:
        _attributes = CMDIntegerSchema.Options._attributes | CMDInteger32SchemaBase.Options._attributes


# integer64
class CMDInteger64SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer64"
    ARG_TYPE = CMDInteger64ArgBase

    class Options:
        _attributes = CMDIntegerSchemaBase.Options._attributes


class CMDInteger64Schema(CMDIntegerSchema, CMDInteger64SchemaBase):
    ARG_TYPE = CMDInteger64Arg

    class Options:
        _attributes = CMDIntegerSchema.Options._attributes | CMDInteger64SchemaBase.Options._attributes


# boolean
class CMDBooleanSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "boolean"
    ARG_TYPE = CMDBooleanArgBase

    class Options:
        _attributes = CMDSchemaBase.Options._attributes


class CMDBooleanSchema(CMDSchema, CMDBooleanSchemaBase):
    ARG_TYPE = CMDBooleanArg

    class Options:
        _attributes = CMDSchema.Options._attributes | CMDBooleanSchemaBase.Options._attributes


# float
class CMDFloatSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "float"
    ARG_TYPE = CMDFloatArgBase

    fmt = ModelType(
        CMDFloatFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDSchemaEnum)

    class Options:
        _attributes = CMDSchemaBase.Options._attributes

    def _diff_base(self, old, level, diff):
        diff = super(CMDFloatSchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        enum_diff = _diff_enum(self.enum, old.enum, level)
        if enum_diff:
            diff["enum"] = enum_diff

        return diff


class CMDFloatSchema(CMDSchema, CMDFloatSchemaBase):
    ARG_TYPE = CMDFloatArg

    class Options:
        _attributes = CMDSchema.Options._attributes | CMDFloatSchemaBase.Options._attributes


# float32
class CMDFloat32SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float32"
    ARG_TYPE = CMDFloat32ArgBase

    class Options:
        _attributes = CMDFloatSchemaBase.Options._attributes


class CMDFloat32Schema(CMDFloatSchema, CMDFloat32SchemaBase):
    ARG_TYPE = CMDFloat32Arg

    class Options:
        _attributes = CMDFloatSchema.Options._attributes | CMDFloat32SchemaBase.Options._attributes


# float64
class CMDFloat64SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float64"
    ARG_TYPE = CMDFloat64ArgBase

    class Options:
        _attributes = CMDFloatSchemaBase.Options._attributes


class CMDFloat64Schema(CMDFloatSchema, CMDFloat64SchemaBase):
    ARG_TYPE = CMDFloat64Arg

    class Options:
        _attributes = CMDFloatSchema.Options._attributes | CMDFloat64SchemaBase.Options._attributes


# object

# discriminator

class CMDObjectSchemaDiscriminatorField(ModelType):

    def __init__(self, model_spec=None, **kwargs):
        super(CMDObjectSchemaDiscriminatorField, self).__init__(
            model_spec=model_spec or CMDObjectSchemaDiscriminator,
            serialize_when_none=False,
            **kwargs
        )

    def export(self, value, format, context=None):
        if hasattr(value, 'frozen') and value.frozen:
            # frozen schema base will be ignored
            return None
        return super(CMDObjectSchemaDiscriminatorField, self).export(value, format, context)


class CMDObjectSchemaDiscriminator(Model):
    ARG_TYPE = CMDObjectArg

    # properties as tags
    prop = StringType(required=True)
    value = StringType(required=True)
    frozen = CMDBooleanField()  # frozen schema will not be used

    # properties as nodes
    props = ListType(CMDSchemaField())
    discriminators = ListType(CMDObjectSchemaDiscriminatorField(model_spec='CMDObjectSchemaDiscriminator'))

    class Options:
        serialize_when_none = False
        _attributes = {"prop", "value", "frozen"}

    def diff(self, old, level):
        if self.frozen and old.frozen:
            return None
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.prop != old.prop:
                diff["prop"] = f"{old.prop} != {self.prop}"
            if self.value != old.value:
                diff["value"] = f"{old.value} != {self.value}"

        props_diff = _diff_props(
            self.props or [],
            old.props or [],
            level
        )
        if props_diff:
            diff["props"] = props_diff

        discs_diff = _diff_discriminators(
            self.discriminators or [],
            old.discriminators or [],
            level
        )
        if discs_diff:
            diff["discriminators"] = discs_diff

        return diff


# additionalProperties
class CMDObjectSchemaAdditionalProperties(Model):
    ARG_TYPE = CMDObjectArgAdditionalProperties

    # properties as tags
    read_only = CMDBooleanField(
        serialized_name="readOnly",
        deserialize_from="readOnly"
    )
    frozen = CMDBooleanField()

    # properties as nodes
    item = CMDSchemaBaseField()

    class Options:
        _attributes = {"ready_only", "frozen"}

    def diff(self, old, level):
        if self.frozen and old.frozen:
            return None
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.read_only and not old.read_only:
                diff["read_only"] = f"it's read_only now."

        item_diff = _diff_item(self.item, old.item, level)
        if item_diff:
            diff["item"] = item_diff

        return diff


class CMDObjectSchemaAdditionalPropertiesField(ModelType):

    def __init__(self, **kwargs):
        super(CMDObjectSchemaAdditionalPropertiesField, self).__init__(
            model_spec=CMDObjectSchemaAdditionalProperties,
            serialized_name="additionalProps",
            deserialize_from="additionalProps",
            serialize_when_none=False,
            **kwargs
        )

    def export(self, value, format, context=None):
        if value.frozen:
            return None
        return super(CMDObjectSchemaAdditionalPropertiesField, self).export(value, format, context)


class CMDObjectSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "object"
    ARG_TYPE = CMDObjectArgBase

    fmt = ModelType(
        CMDObjectFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    props = ListType(CMDSchemaField())
    discriminators = ListType(CMDObjectSchemaDiscriminatorField())
    additional_props = CMDObjectSchemaAdditionalPropertiesField()

    class Options:
        _attributes = CMDSchemaBase.Options._attributes

    def _diff_base(self, old, level, diff):
        diff = super(CMDObjectSchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        props_diff = _diff_props(
            self.props or [],
            old.props or [],
            level
        )
        if props_diff:
            diff["props"] = props_diff

        discs_diff = _diff_discriminators(
            self.discriminators or [],
            old.discriminators or [],
            level
        )
        if discs_diff:
            diff["discriminators"] = discs_diff

        if level >= CMDDiffLevelEnum.BreakingChange:
            if old.additional_props:
                if not self.additional_props:
                    additional_diff = f"Miss additional props"
                else:
                    additional_diff = self.additional_props.diff(old.additional_props, level)
                if additional_diff:
                    diff["additional_props"] = additional_diff

        if level >= CMDDiffLevelEnum.Structure:
            if self.additional_props:
                if not old.additional_props:
                    additional_diff = f"New additional props"
                else:
                    additional_diff = self.additional_props.diff(old.additional_props, level)
                if additional_diff:
                    diff["additional_props"] = additional_diff

        return diff


class CMDObjectSchema(CMDSchema, CMDObjectSchemaBase):
    ARG_TYPE = CMDObjectArg

    # properties as tags
    client_flatten = CMDBooleanField(
        serialized_name="clientFlatten",
        deserialize_from="clientFlatten"
    )
    cls = CMDClassField()  # define a schema which can be used by others

    class Options:
        _attributes = CMDSchema.Options._attributes | CMDObjectSchemaBase.Options._attributes | {"client_flatten", "cls"}

    def _diff(self, old, level, diff):
        diff = super(CMDObjectSchema, self)._diff(old, level, diff)
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.client_flatten != old.client_flatten:
                diff["client_flatten"] = f"from {old.client_flatten} to {self.client_flatten}"

        cls_diff = _diff_cls(self.cls, old.cls, level)
        if cls_diff:
            diff["cls"] = cls_diff

        return diff


# array
class CMDArraySchemaBase(CMDSchemaBase):
    TYPE_VALUE = "array"
    ARG_TYPE = CMDArrayArgBase

    # properties as nodes
    fmt = ModelType(
        CMDArrayFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    item = CMDSchemaBaseField()

    class Options:
        _attributes = CMDSchemaBase.Options._attributes

    def _get_type(self):
        return f"{self.TYPE_VALUE}<{self.item.type}>"

    def _diff_base(self, old, level, diff):
        diff = super(CMDArraySchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        item_diff = _diff_item(self.item, old.item, level)
        if item_diff:
            diff["item"] = item_diff

        return diff


class CMDArraySchema(CMDSchema, CMDArraySchemaBase):
    ARG_TYPE = CMDArrayArg

    # properties as tags
    cls = CMDClassField()  # define a schema which can be used by others # TODO: convert to arg

    class Options:
        _attributes = CMDSchema.Options._attributes | CMDArraySchemaBase.Options._attributes | {"cls"}

    def _diff(self, old, level, diff):
        diff = super(CMDArraySchema, self)._diff(old, level, diff)

        cls_diff = _diff_cls(self.cls, old.cls, level)
        if cls_diff:
            diff["cls"] = cls_diff

        return diff


# diff functions

def _diff_fmt(self_fmt, old_fmt, level):
    fmt_diff = None
    if level >= CMDDiffLevelEnum.BreakingChange:
        if self_fmt:
            fmt_diff = self_fmt.diff(old_fmt, level)

    if level >= CMDDiffLevelEnum.Structure:
        if old_fmt:
            if not self_fmt:
                fmt_diff = f"Miss property"
            else:
                fmt_diff = self_fmt.diff(old_fmt, level)
    return fmt_diff


def _diff_enum(self_enum, old_enum, level):
    enum_diff = None
    if level >= CMDDiffLevelEnum.BreakingChange:
        if self_enum:
            enum_diff = self_enum.diff(old_enum, level)

    if level >= CMDDiffLevelEnum.Structure:
        if old_enum:
            if not self_enum:
                enum_diff = f"Miss property"
            else:
                enum_diff = self_enum.diff(old_enum, level)

    return enum_diff


def _diff_props(self_props, old_props, level):
    props_diff = {}
    if level >= CMDDiffLevelEnum.BreakingChange:
        props_dict = {prop.name: prop for prop in self_props}
        for old_prop in old_props:
            if old_prop.name not in props_dict:
                if not old_prop.frozen:
                    props_diff[old_prop.name] = "Miss property"
            else:
                prop = props_dict.pop(old_prop.name)
                diff = prop.diff(old_prop, level)
                if diff:
                    props_diff[old_prop.name] = diff
        for prop in props_dict.values():
            if prop.frozen:
                continue
            if prop.required:
                props_diff[prop.name] = "New required property"

    if level >= CMDDiffLevelEnum.Structure:
        old_props_dict = {prop.name: prop for prop in old_props}
        for prop in self_props:
            if prop.name not in old_props_dict:
                if not prop.frozen:
                    props_diff[prop.name] = "New property"
            else:
                old_prop = old_props_dict.pop(prop.name)
                diff = prop.diff(old_prop, level)
                if diff:
                    props_diff[prop.name] = diff
    return props_diff


def _diff_discriminators(self_discriminators, old_discriminators, level):
    discs_diff = {}
    if level >= CMDDiffLevelEnum.BreakingChange:
        discs_dict = {disc.value: disc for disc in self_discriminators}
        for old_disc in old_discriminators:
            if old_disc.value not in discs_dict:
                if not old_disc.frozen:
                    discs_diff[old_disc.value] = "Miss discriminator value"
            else:
                disc = discs_dict.pop(old_disc.value)
                diff = disc.diff(old_disc, level)
                if diff:
                    discs_diff[old_disc.value] = diff

    if level >= CMDDiffLevelEnum.Structure:
        old_discs_dict = {disc.value: disc for disc in old_discriminators}
        for disc in self_discriminators:
            if disc.value not in old_discs_dict:
                if not disc.frozen:
                    discs_diff[disc.value] = "New discriminator value"
            else:
                old_disc = old_discs_dict.pop(disc.value)
                diff = disc.diff(old_disc, level)
                if diff:
                    discs_diff[disc.value] = diff
    return discs_diff


def _diff_item(self_item, old_item, level):
    item_diff = {}

    if self_item is None and old_item is None:
        return item_diff

    if level >= CMDDiffLevelEnum.BreakingChange:
        if type(self_item) is not type(old_item):
            item_diff = f"Type: {type(old_item)} != {type(self_item)}"
        elif not (self_item.frozen and old_item.frozen):
            item_diff = {}
            item_diff = self_item._diff_base(old_item, level, item_diff)

    return item_diff


def _diff_cls(self_cls, old_cls, level):
    cls_diff = None

    if level >= CMDDiffLevelEnum.Structure:
        if (self_cls is not None) != (old_cls is not None):
            cls_diff = f"from {old_cls} to {self_cls}"

    if level >= CMDDiffLevelEnum.All:
        if self_cls != old_cls:
            cls_diff = f"{old_cls} != {self_cls}"
    return cls_diff

