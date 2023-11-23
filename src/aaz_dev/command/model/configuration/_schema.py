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
    CMDTimeArg, CMDTimeArgBase, \
    CMDUuidArg, CMDUuidArgBase, \
    CMDPasswordArg, CMDPasswordArgBase, \
    CMDResourceIdArg, CMDResourceIdArgBase, \
    CMDResourceLocationArg, CMDResourceLocationArgBase, \
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
from ._format import CMDStringFormat, CMDIntegerFormat, CMDFloatFormat, CMDObjectFormat, CMDArrayFormat, \
    CMDResourceIdFormat
from ._utils import CMDDiffLevelEnum
from utils import exceptions

import logging
import re

logger = logging.getLogger('backend')


class CMDSchemaEnumItem(Model):
    arg = CMDVariantField()  # value will be used when specific argument is provided

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null

    class Options:
        serialize_when_none = False

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

    def reformat(self, **kwargs):
        try:
            self.items = sorted(self.items, key=lambda it: it.value)
        except:
            # some of the value main not support sort
            pass


class CMDSchemaDefault(Model):
    """ The argument value if an argument is not used """

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null

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
    read_only = CMDBooleanField(
        serialized_name="readOnly",
        deserialize_from="readOnly"
    )
    frozen = CMDBooleanField()  # frozen schema will not be used
    const = CMDBooleanField()  # when a schema is const it's default value is not None.

    # properties as nodes
    default = ModelType(CMDSchemaDefault)
    nullable = CMDBooleanField()  # whether null value is supported

    # base types: "array", "boolean", "integer", "float", "object", "string",

    class Options:
        serialize_when_none = False

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
            if (not self.read_only) != (not old.read_only):
                diff["read_only"] = f"{old.read_only} != {self.read_only}"
            if (not self.const) != (not old.const):
                diff['const'] = f"{old.const} != {self.const}"
            if self.default:
                default_diff = self.default.diff(old.default, level)
                if default_diff:
                    diff["default"] = default_diff
        return diff

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        if self.frozen and old.frozen:
            return None
        diff = {}
        diff = self._diff_base(old, level, diff)
        return diff

    def _reformat_base(self, **kwargs):
        pass

    def reformat(self, **kwargs):
        if self.frozen:
            return
        self._reformat_base(**kwargs)


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

    def find_model(self, data):
        if self.claim_function:
            kls = self.claim_function(self, data)
            if not kls:
                raise Exception("Input for polymorphic field did not match any model")
            return kls

        fallback = None
        matching_classes = set()
        for kls in self._get_candidates():
            if issubclass(kls, CMDSchema):
                continue

            try:
                kls_claim = kls._claim_polymorphic
            except AttributeError:
                if not fallback:
                    fallback = kls
            else:
                if kls_claim(data):
                    matching_classes.add(kls)

        if not matching_classes and fallback:
            return fallback
        elif len(matching_classes) != 1:
            raise Exception("Got ambiguous input for polymorphic field")

        return matching_classes.pop()


class CMDSchema(CMDSchemaBase):
    # properties as tags
    name = StringType(required=True)
    arg = CMDVariantField()
    required = CMDBooleanField()

    description = CMDDescriptionField()

    skip_url_encoding = CMDBooleanField(
        serialized_name="skipUrlEncoding",
        deserialize_from="skipUrlEncoding",
    )  # used in path and query parameters

    secret = CMDBooleanField()

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
            if self.required and not old.required:
                diff["required"] = f"it's required now."
            if (not self.skip_url_encoding) != (not old.skip_url_encoding):  # None should be same as false
                diff["skip_url_encoding"] = f"{old.skip_url_encoding} != {self.skip_url_encoding}"
            if not self.secret and old.secret:
                diff["secret"] = f"it's not secret property now."

        if level >= CMDDiffLevelEnum.Structure:
            if (not self.required) != (not old.required):
                diff["required"] = f"{old.required} != {self.required}"
            if self.secret != old.secret:
                diff["secret"] = f"{old.secret} != {self.secret}"

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

    def _reformat(self, **kwargs):
        pass

    def reformat(self, **kwargs):
        if self.frozen:
            return
        self._reformat_base(**kwargs)
        self._reformat(**kwargs)


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

    def _get_type(self):
        return self._type

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implement = None

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None and type_value.startswith("@"):
                return True
        elif isinstance(data, CMDClsSchemaBase):
            return True
        return False

    @classmethod
    def build_from_schema_base(cls, schema_base, implement):
        assert isinstance(schema_base, (CMDObjectSchemaBase, CMDArraySchemaBase))
        assert getattr(schema_base, 'cls', None)
        cls_schema = cls()
        cls_schema._type = f"@{schema_base.cls}"
        cls_schema.read_only = schema_base.read_only
        cls_schema.frozen = schema_base.frozen
        cls_schema.const = schema_base.const
        cls_schema.default = schema_base.default
        cls_schema.implement = implement
        return cls_schema

    def get_unwrapped(self, **kwargs):
        if self.implement is None:
            return
        assert isinstance(self.implement, CMDSchemaBase)
        if isinstance(self.implement, CMDObjectSchemaBase):
            cls = CMDObjectSchema if isinstance(self, CMDClsSchema) else CMDObjectSchemaBase
        elif isinstance(self.implement, CMDArraySchemaBase):
            cls = CMDArraySchema if isinstance(self, CMDClsSchema) else CMDArraySchemaBase
        else:
            raise NotImplementedError()
        data = {k: v for k, v in self.implement.to_native().items() if k in cls._schema.valid_input_keys}
        data.update(kwargs)
        unwrapped = cls(data)
        return unwrapped


class CMDClsSchema(CMDClsSchemaBase, CMDSchema):
    ARG_TYPE = CMDClsArg

    # properties as tags
    client_flatten = CMDBooleanField(
        serialized_name="clientFlatten",
        deserialize_from="clientFlatten"
    )

    def _diff(self, old, level, diff):
        # TODO: Handle Cls Schema compare with other Schema classes
        diff = super(CMDClsSchema, self)._diff(old, level, diff)
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (not self.client_flatten) != (not old.client_flatten):
                diff["client_flatten"] = f"from {old.client_flatten} to {self.client_flatten}"

        return diff

    @classmethod
    def build_from_schema(cls, schema, implement):
        assert isinstance(schema, (CMDObjectSchema, CMDArraySchema))
        cls_schema = cls.build_from_schema_base(schema, implement)
        cls_schema.name = schema.name
        cls_schema.arg = schema.arg
        cls_schema.required = schema.required
        cls_schema.description = schema.description
        cls_schema.skip_url_encoding = schema.skip_url_encoding
        if isinstance(schema, CMDObjectSchema):
            cls_schema.client_flatten = schema.client_flatten
        return cls_schema

    def get_unwrapped(self, **kwargs):
        uninherent = {
            "name": self.name,
            "arg": self.arg,
            "required": self.required,
            "description": self.description,
            "skip_url_encoding": self.skip_url_encoding,
        }
        if isinstance(self.implement, CMDObjectSchema):
            uninherent["client_flatten"] = self.client_flatten
        uninherent.update(kwargs)
        return super().get_unwrapped(**uninherent)


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

    def _diff_base(self, old, level, diff):
        diff = super(CMDStringSchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        enum_diff = _diff_enum(self.enum, old.enum, level)
        if enum_diff:
            diff["enum"] = enum_diff

        return diff

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.enum:
            self.enum.reformat(**kwargs)


class CMDStringSchema(CMDStringSchemaBase, CMDSchema):
    ARG_TYPE = CMDStringArg


# byte: base64 encoded characters
class CMDByteSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "byte"
    ARG_TYPE = CMDByteArgBase


class CMDByteSchema(CMDByteSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDByteArg


# binary: any sequence of octets
class CMDBinarySchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "binary"
    ARG_TYPE = CMDBinaryArgBase


class CMDBinarySchema(CMDBinarySchemaBase, CMDStringSchema):
    ARG_TYPE = CMDBinaryArg


# duration
class CMDDurationSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "duration"
    ARG_TYPE = CMDDurationArgBase


class CMDDurationSchema(CMDDurationSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDDurationArg


# date: As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "date"
    ARG_TYPE = CMDDateArgBase


class CMDDateSchema(CMDDateSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDDateArg


# date-time: As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateTimeSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "dateTime"
    ARG_TYPE = CMDDateTimeArgBase


class CMDDateTimeSchema(CMDDateTimeSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDDateTimeArg


class CMDTimeSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "time"
    ARG_TYPE = CMDTimeArgBase


class CMDTimeSchema(CMDTimeSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDTimeArg


# uuid
class CMDUuidSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "uuid"
    ARG_TYPE = CMDUuidArgBase


class CMDUuidSchema(CMDUuidSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDUuidArg


# password
class CMDPasswordSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "password"
    ARG_TYPE = CMDPasswordArgBase


class CMDPasswordSchema(CMDPasswordSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDPasswordArg


# ResourceId
class CMDResourceIdSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "ResourceId"
    ARG_TYPE = CMDResourceIdArgBase

    fmt = ModelType(
        CMDResourceIdFormat,
        serialized_name='format',
        deserialize_from='format'
    )


class CMDResourceIdSchema(CMDResourceIdSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDResourceIdArg


# ResourceLocation
class CMDResourceLocationSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "ResourceLocation"
    ARG_TYPE = CMDResourceLocationArgBase


class CMDResourceLocationSchema(CMDResourceLocationSchemaBase, CMDStringSchema):
    ARG_TYPE = CMDResourceLocationArg


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

    def _diff_base(self, old, level, diff):
        diff = super(CMDIntegerSchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        enum_diff = _diff_enum(self.enum, old.enum, level)
        if enum_diff:
            diff["enum"] = enum_diff

        return diff

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.enum:
            self.enum.reformat(**kwargs)


class CMDIntegerSchema(CMDIntegerSchemaBase, CMDSchema):
    ARG_TYPE = CMDIntegerArg


# integer32
class CMDInteger32SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer32"
    ARG_TYPE = CMDInteger32ArgBase


class CMDInteger32Schema(CMDInteger32SchemaBase, CMDIntegerSchema):
    ARG_TYPE = CMDInteger32Arg


# integer64
class CMDInteger64SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer64"
    ARG_TYPE = CMDInteger64ArgBase


class CMDInteger64Schema(CMDInteger64SchemaBase, CMDIntegerSchema):
    ARG_TYPE = CMDInteger64Arg


# boolean
class CMDBooleanSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "boolean"
    ARG_TYPE = CMDBooleanArgBase


class CMDBooleanSchema(CMDBooleanSchemaBase, CMDSchema):
    ARG_TYPE = CMDBooleanArg


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

    def _diff_base(self, old, level, diff):
        diff = super(CMDFloatSchemaBase, self)._diff_base(old, level, diff)

        fmt_diff = _diff_fmt(self.fmt, old.fmt, level)
        if fmt_diff:
            diff["fmt"] = fmt_diff

        enum_diff = _diff_enum(self.enum, old.enum, level)
        if enum_diff:
            diff["enum"] = enum_diff

        return diff

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.enum:
            self.enum.reformat(**kwargs)


class CMDFloatSchema(CMDFloatSchemaBase, CMDSchema):
    ARG_TYPE = CMDFloatArg


# float32
class CMDFloat32SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float32"
    ARG_TYPE = CMDFloat32ArgBase


class CMDFloat32Schema(CMDFloat32SchemaBase, CMDFloatSchema):
    ARG_TYPE = CMDFloat32Arg


# float64
class CMDFloat64SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float64"
    ARG_TYPE = CMDFloat64ArgBase


class CMDFloat64Schema(CMDFloat64SchemaBase, CMDFloatSchema):
    ARG_TYPE = CMDFloat64Arg


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
    property = StringType(required=True)
    value = StringType(required=True)
    frozen = CMDBooleanField()  # frozen schema will not be used

    # properties as nodes
    props = ListType(CMDSchemaField())
    discriminators = ListType(CMDObjectSchemaDiscriminatorField(model_spec='CMDObjectSchemaDiscriminator'))

    class Options:
        serialize_when_none = False

    def diff(self, old, level):
        if self.frozen and old.frozen:
            return None
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.property != old.property:
                diff["property"] = f"{old.property} != {self.property}"
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

    def reformat(self, **kwargs):
        if self.frozen:
            return
        if self.props:
            for prop in self.props:
                prop.reformat(**kwargs)
            self.props = sorted(self.props, key=lambda p: p.name)
        if self.discriminators:
            for disc in self.discriminators:
                disc.reformat(**kwargs)
            self.discriminators = sorted(self.discriminators, key=lambda disc: disc.value)

    def get_safe_value(self):
        """Some value may contain special characters such as Microsoft.db/mysql, it will cause issues. This function will replase them by `_`
        """
        safe_value = re.sub(r'[^A-Za-z0-9_-]', '_', self.value)
        return safe_value


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
    any_type = CMDBooleanField(
        serialized_name="anyType",
        deserialize_from="anyType"
    )

    def diff(self, old, level):
        if self.frozen and old.frozen:
            return None
        diff = {}

        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.read_only and not old.read_only:
                diff["read_only"] = f"it's read_only now."
            if not self.any_type and old.any_type:
                diff["any_type"] = f"it's not any_type now"

        if level >= CMDDiffLevelEnum.Structure:
            if self.any_type:
                if not old.any_type:
                    diff["any_type"] = f"Now support any_type"

        item_diff = _diff_item(self.item, old.item, level)
        if item_diff:
            diff["item"] = item_diff

        return diff

    def reformat(self, **kwargs):
        if self.frozen:
            return
        if self.item:
            if self.any_type:
                raise exceptions.VerificationError(
                    "InvalidAdditionalPropertiesDefinition",
                    details="Additional property defined 'item' and 'any_type'."
                )
            self.item.reformat(**kwargs)


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

    # define a schema cls which can be used by others,
    # cls definition will not include properties in CMDSchema only, such as following properties:
    #  - name
    #  - arg
    #  - required
    #  - description
    #  - skip_url_encoding
    #  - client_flatten
    cls = CMDClassField()

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
                    diff["additional_props"] = f"Miss additional props"

        if level >= CMDDiffLevelEnum.Structure:
            if self.additional_props:
                if not old.additional_props:
                    diff["additional_props"] = f"New additional props"

        if self.additional_props and old.additional_props:
            additional_diff = self.additional_props.diff(old.additional_props, level)
            if additional_diff:
                diff["additional_props"] = additional_diff

        return diff

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.props:
            for prop in self.props:
                prop.reformat(**kwargs)
            self.props = sorted(self.props, key=lambda prop: prop.name)
        if self.discriminators:
            for disc in self.discriminators:
                disc.reformat(**kwargs)
            self.discriminators = sorted(self.discriminators, key=lambda disc: disc.value)
        if self.additional_props:
            self.additional_props.reformat(**kwargs)


class CMDObjectSchema(CMDObjectSchemaBase, CMDSchema):
    ARG_TYPE = CMDObjectArg

    # properties as tags
    client_flatten = CMDBooleanField(
        serialized_name="clientFlatten",
        deserialize_from="clientFlatten"
    )

    def _diff(self, old, level, diff):
        diff = super(CMDObjectSchema, self)._diff(old, level, diff)
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (not self.client_flatten) != (not old.client_flatten):
                diff["client_flatten"] = f"from {old.client_flatten} to {self.client_flatten}"

        cls_diff = _diff_cls(self.cls, old.cls, level)
        if cls_diff:
            diff["cls"] = cls_diff

        return diff


class CMDIdentityObjectSchemaBase(CMDObjectSchemaBase):
    """ And identity object which contains 'userAssignedIdentities' property and 'type' property
    with "SystemAssigned", "UserAssigned", "SystemAssigned, UserAssigned" and "None" enum values.
    """
    TYPE_VALUE = "IdentityObject"
    ARG_TYPE = CMDObjectArgBase


class CMDIdentityObjectSchema(CMDIdentityObjectSchemaBase, CMDObjectSchema):
    ARG_TYPE = CMDObjectArg


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

    # used to indentify item in array
    identifiers = ListType(StringType())

    # properties as tags
    # define a schema which can be used by others
    # cls definition will not include properties in CMDSchema only, such as following properties:
    #  - name
    #  - arg
    #  - required
    #  - description
    #  - skip_url_encoding
    cls = CMDClassField()

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

        if level >= CMDDiffLevelEnum.Structure:
            if old.identifiers:
                if not self.identifiers:
                    diff["identifiers"] = f"Miss Identifiers"
                elif set(old.identifiers) != set(self.identifiers):
                    diff["identifiers"] = f"Identifier different"
            elif self.identifiers:
                diff["identifiers"] = f"New identifiers"

        return diff

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        self.item.reformat(**kwargs)
        if self.identifiers:
            identifiers = sorted(self.identifiers, key=lambda i: (len(i), i))
            item_instance = self.item
            if isinstance(item_instance, CMDClsSchemaBase):
                item_instance = item_instance.implement
            if not isinstance(item_instance, CMDObjectSchemaBase):
                raise exceptions.InvalidAPIUsage(
                    f"Identifiers should be used in 'array of object'"
                )
            item_prop_names = {p.name for p in item_instance.props}
            new_identifiers = []
            for identifier in identifiers:
                if identifier not in item_prop_names:
                    if '/' in identifier:
                        # not support identifier with '/' right now
                        logger.info(f"identifier '{identifier}' is not supported yet")
                        continue
                    raise exceptions.InvalidAPIUsage(
                        f"identifier property '{identifier}' not exist"
                    )
                new_identifiers.append(identifier)
            self.identifiers = new_identifiers or None


class CMDArraySchema(CMDArraySchemaBase, CMDSchema):
    ARG_TYPE = CMDArrayArg

    def _diff(self, old, level, diff):
        diff = super(CMDArraySchema, self)._diff(old, level, diff)

        cls_diff = _diff_cls(self.cls, old.cls, level)
        if cls_diff:
            diff["cls"] = cls_diff

        return diff


# diff functions

def _diff_fmt(self_fmt, old_fmt, level):
    fmt_diff = None

    if level >= CMDDiffLevelEnum.Structure:
        if old_fmt:
            if not self_fmt:
                fmt_diff = f"Miss property"

    if self_fmt and old_fmt:
        fmt_diff = self_fmt.diff(old_fmt, level)

    return fmt_diff


def _diff_enum(self_enum, old_enum, level):
    enum_diff = None

    if level >= CMDDiffLevelEnum.Structure:
        if old_enum:
            if not self_enum:
                enum_diff = f"Miss property"

    if self_enum and old_enum:
        enum_diff = self_enum.diff(old_enum, level)

    return enum_diff


def _diff_props(self_props, old_props, level):
    props_diff = {}
    if level >= CMDDiffLevelEnum.BreakingChange:
        props_dict = {prop.name: prop for prop in self_props} if self_props else {}
        if old_props:
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
        old_props_dict = {prop.name: prop for prop in old_props} if old_props else {}
        if self_props:
            for prop in self_props:
                if prop.name not in old_props_dict:
                    if not prop.frozen:
                        props_diff[prop.name] = "New property"
    return props_diff


def _diff_discriminators(self_discriminators, old_discriminators, level):
    discs_diff = {}
    if level >= CMDDiffLevelEnum.BreakingChange:
        discs_dict = {disc.value: disc for disc in self_discriminators} if self_discriminators else {}
        if old_discriminators:
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
        old_discs_dict = {disc.value: disc for disc in old_discriminators} if old_discriminators else {}
        if self_discriminators:
            for disc in self_discriminators:
                if disc.value not in old_discs_dict:
                    if not disc.frozen:
                        discs_diff[disc.value] = "New discriminator value"

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
