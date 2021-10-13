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
    CMDObjectArg, CMDObjectArgBase, \
    CMDClsArg, CMDClsArgBase
from ._fields import CMDVariantField, StringType, CMDClassField, CMDBooleanField, CMDPrimitiveField
from ._format import CMDStringFormat, CMDIntegerFormat, CMDFloatFormat, CMDObjectFormat, CMDArrayFormat


class CMDSchemaEnumItem(Model):
    arg = CMDVariantField(serialize_when_none=False)  # value will be used when specific argument is provided

    # properties as nodes
    value = CMDPrimitiveField(required=True)


class CMDSchemaEnum(Model):
    # properties as tags

    # properties as nodes
    items = ListType(ModelType(CMDSchemaEnumItem), min_size=1)


class CMDSchemaDefault(Model):
    """ The argument value if an argument is not used """

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null


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
    default = ModelType(CMDSchemaDefault, serialize_when_none=False)

    # base types: "array", "boolean", "integer", "float", "object", "string",

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


class CMDSchema(CMDSchemaBase):
    # properties as tags
    name = StringType(required=True)
    arg = CMDVariantField(serialize_when_none=False)

    description = StringType(serialize_when_none=False)

    skip_url_encoding = CMDBooleanField(
        serialized_name="skipUrlEncoding",
        deserialize_from="skipUrlEncoding",
    )  # used in path and query parameters

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDSchema, cls)._claim_polymorphic(data):
            if isinstance(data, dict):
                # distinguish with CMDSchemaBase and CMDSchema
                return 'name' in data
            else:
                return isinstance(data, CMDSchema)
        return False


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


# string
class CMDStringSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "string"
    ARG_TYPE = CMDStringArgBase

    fmt = ModelType(
        CMDStringFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDStringSchema(CMDSchema, CMDStringSchemaBase):
    ARG_TYPE = CMDStringArg


# byte: base64 encoded characters
class CMDByteSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "byte"
    ARG_TYPE = CMDByteArgBase


class CMDByteSchema(CMDStringSchema, CMDByteSchemaBase):
    ARG_TYPE = CMDByteArg


# binary: any sequence of octets
class CMDBinarySchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "binary"
    ARG_TYPE = CMDBinaryArgBase


class CMDBinarySchema(CMDStringSchema, CMDBinarySchemaBase):
    ARG_TYPE = CMDBinaryArg


# duration
class CMDDurationSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "duration"
    ARG_TYPE = CMDDurationArgBase


class CMDDurationSchema(CMDStringSchema, CMDDurationSchemaBase):
    ARG_TYPE = CMDDurationArg


# date: As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "date"
    ARG_TYPE = CMDDateArgBase


class CMDDateSchema(CMDStringSchema, CMDDateSchemaBase):
    ARG_TYPE = CMDDateArg


# date-time: As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateTimeSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "date-time"
    ARG_TYPE = CMDDateTimeArgBase


class CMDDateTimeSchema(CMDStringSchema, CMDDateTimeSchemaBase):
    ARG_TYPE = CMDDateTimeArg


# uuid
class CMDUuidSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "uuid"
    ARG_TYPE = CMDUuidArgBase


class CMDUuidSchema(CMDStringSchema, CMDUuidSchemaBase):
    ARG_TYPE = CMDUuidArg


# password
class CMDPasswordSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "password"
    ARG_TYPE = CMDPasswordArgBase


class CMDPasswordSchema(CMDStringSchema, CMDPasswordSchemaBase):
    ARG_TYPE = CMDPasswordArg


# integer
class CMDIntegerSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "integer"
    ARG_TYPE = CMDIntegerArgBase

    fmt = ModelType(
        CMDIntegerFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDIntegerSchema(CMDSchema, CMDIntegerSchemaBase):
    ARG_TYPE = CMDIntegerArg


# integer32
class CMDInteger32SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer32"
    ARG_TYPE = CMDInteger32ArgBase


class CMDInteger32Schema(CMDIntegerSchema, CMDInteger32SchemaBase):
    ARG_TYPE = CMDInteger32Arg


# integer64
class CMDInteger64SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer64"
    ARG_TYPE = CMDInteger64ArgBase


class CMDInteger64Schema(CMDIntegerSchema, CMDInteger64SchemaBase):
    ARG_TYPE = CMDInteger64Arg


# boolean
class CMDBooleanSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "boolean"
    ARG_TYPE = CMDBooleanArgBase


class CMDBooleanSchema(CMDSchema, CMDBooleanSchemaBase):
    ARG_TYPE = CMDBooleanArg


# float
class CMDFloatSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "float"
    ARG_TYPE = CMDFloatArgBase

    fmt = ModelType(
        CMDFloatFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDFloatSchema(CMDSchema, CMDFloatSchemaBase):
    ARG_TYPE = CMDFloatArg


# float32
class CMDFloat32SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float32"
    ARG_TYPE = CMDFloat32ArgBase


class CMDFloat32Schema(CMDFloatSchema, CMDFloat32SchemaBase):
    ARG_TYPE = CMDFloat32Arg


# float64
class CMDFloat64SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float64"
    ARG_TYPE = CMDFloat64ArgBase


class CMDFloat64Schema(CMDFloatSchema, CMDFloat64SchemaBase):
    ARG_TYPE = CMDFloat64Arg


# object

# discriminator
class CMDObjectSchemaDiscriminator(Model):
    ARG_TYPE = CMDObjectArg

    # properties as tags
    prop = StringType(required=True)
    value = StringType(required=True)
    frozen = CMDBooleanField()  # frozen schema will not be used

    # properties as nodes
    props = ListType(
        PolyModelType(CMDSchema, allow_subclasses=True),
        serialize_when_none=False
    )
    discriminators = ListType(
        ModelType('CMDObjectSchemaDiscriminator'),
        serialize_when_none=False,
    )


# additionalProperties
class CMDObjectSchemaAdditionalProperties(Model):
    # properties as tags
    read_only = CMDBooleanField(
        serialized_name="readOnly",
        deserialize_from="readOnly"
    )
    frozen = CMDBooleanField()

    # properties as nodes
    item = PolyModelType(CMDSchemaBase, allow_subclasses=True)


class CMDObjectSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "object"
    ARG_TYPE = CMDObjectArgBase

    fmt = ModelType(
        CMDObjectFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    props = ListType(
        PolyModelType(CMDSchema, allow_subclasses=True),
        serialize_when_none=False
    )
    discriminators = ListType(
        ModelType(CMDObjectSchemaDiscriminator),
        serialize_when_none=False,
    )
    additional_props = ModelType(
        CMDObjectSchemaAdditionalProperties,
        serialized_name="additionalProps",
        deserialize_from="additionalProps",
        serialize_when_none=False,
    )  # TODO:


class CMDObjectSchema(CMDSchema, CMDObjectSchemaBase):
    ARG_TYPE = CMDObjectArg

    # properties as tags
    client_flatten = CMDBooleanField(
        serialized_name="clientFlatten",
        deserialize_from="clientFlatten"
    )
    cls = CMDClassField(serialize_when_none=False)  # define a schema which can be used by others


# array
class CMDArraySchemaBase(CMDSchemaBase):
    TYPE_VALUE = "array"
    ARG_TYPE = CMDArrayArgBase

    # properties as nodes
    fmt = ModelType(
        CMDArrayFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False,
    )
    item = PolyModelType(CMDSchemaBase, allow_subclasses=True, required=True)

    def _get_type(self):
        return f"{self.TYPE_VALUE}<{self.item.type}>"


class CMDArraySchema(CMDSchema, CMDArraySchemaBase):
    ARG_TYPE = CMDArrayArg

    # properties as tags
    cls = CMDClassField(
        serialize_when_none=False)  # TODO: convert to arg # define a schema which can be used by others



