# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType, ListType, PolyModelType
from schematics.types.serializable import serializable

from ._fields import CMDVariantField, StringType, CMDSchemaClassField, CMDBooleanField, CMDPrimitiveField
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
    required = CMDBooleanField()
    readonly = CMDBooleanField()

    # properties as nodes
    default = ModelType(CMDSchemaDefault, serialize_when_none=False)

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
    pass


# string
class CMDStringSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "string"

    fmt = ModelType(
        CMDStringFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDStringSchema(CMDSchema, CMDStringSchemaBase):
    pass


# byte: base64 encoded characters
class CMDByteSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "byte"


class CMDByteSchema(CMDStringSchema, CMDByteSchemaBase):
    pass


# binary: any sequence of octets
class CMDBinarySchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "binary"


class CMDBinarySchema(CMDStringSchema, CMDBinarySchemaBase):
    pass


# duration
class CMDDurationSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "duration"


class CMDDurationSchema(CMDStringSchema, CMDDurationSchemaBase):
    pass


# date: As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "date"


class CMDDateSchema(CMDStringSchema, CMDDateSchemaBase):
    pass


# date-time: As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateTimeSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "date-time"


class CMDDateTimeSchema(CMDStringSchema, CMDDateTimeSchemaBase):
    pass


# uuid
class CMDUuidSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "uuid"


class CMDUuidSchema(CMDStringSchema, CMDUuidSchemaBase):
    pass


# password
class CMDPasswordSchemaBase(CMDStringSchemaBase):
    TYPE_VALUE = "password"


class CMDPasswordSchema(CMDStringSchema, CMDPasswordSchemaBase):
    pass


# integer
class CMDIntegerSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "integer"

    fmt = ModelType(
        CMDIntegerFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDIntegerSchema(CMDSchema, CMDIntegerSchemaBase):
    pass


# integer32
class CMDInteger32SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer32"


class CMDInteger32Schema(CMDIntegerSchema, CMDInteger32SchemaBase):
    pass


# integer64
class CMDInteger64SchemaBase(CMDIntegerSchemaBase):
    TYPE_VALUE = "integer64"


class CMDInteger64Schema(CMDIntegerSchema, CMDInteger64SchemaBase):
    pass


# boolean
class CMDBooleanSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "boolean"


class CMDBooleanSchema(CMDSchema, CMDBooleanSchemaBase):
    pass


# float
class CMDFloatSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "float"

    fmt = ModelType(
        CMDFloatFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDFloatSchema(CMDSchema, CMDFloatSchemaBase):
    pass


# float32
class CMDFloat32SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float32"


class CMDFloat32Schema(CMDFloatSchema, CMDFloat32SchemaBase):
    pass


# float64
class CMDFloat64SchemaBase(CMDFloatSchemaBase):
    TYPE_VALUE = "float64"


class CMDFloat64Schema(CMDFloatSchema, CMDFloat64SchemaBase):
    pass


# object

# discriminator
class CMDObjectSchemaDiscriminator(Model):
    # properties as tags
    prop = StringType(required=True)
    value = StringType(required=True)  # TODO: check possible types of value

    # properties as nodes
    props = ListType(
        PolyModelType(CMDSchema, allow_subclasses=True),
        serialize_when_none=False
    )
    discriminators = ListType(
        ModelType('CMDObjectSchemaDiscriminator'),
        serialize_when_none=False,
    )


class CMDObjectSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "object"

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


class CMDObjectSchema(CMDSchema, CMDObjectSchemaBase):
    # properties as tags
    client_flatten = CMDBooleanField(
        serialized_name="clientFlatten",
        deserialize_from="clientFlatten"
    )
    cls = CMDSchemaClassField(serialize_when_none=False)  # define a schema which can be used by others


# array
class CMDArraySchemaBase(CMDSchemaBase):
    TYPE_VALUE = "array"

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
    pass


# json
class CMDJson(Model):
    TYPE_VALUE = None

    # properties as tags
    var = CMDVariantField(serialize_when_none=False)
    ref = CMDVariantField(serialize_when_none=False)

    @serializable
    def type(self):
        return self._get_type()

    def _get_type(self):
        assert self.TYPE_VALUE is not None
        return self.TYPE_VALUE

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        elif isinstance(data, CMDJson):
            return data.TYPE_VALUE == cls.TYPE_VALUE
        return False


class CMDObjectJson(CMDJson):
    TYPE_VALUE = "object"

    # properties as tags
    cls = CMDSchemaClassField(serialize_when_none=False)  # define a schema which can be used by others

    # properties as nodes
    fmt = ModelType(
        CMDObjectFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False,
    )
    props = ListType(
        PolyModelType(CMDSchema, allow_subclasses=True),
        serialize_when_none=False,
    )
    discriminators = ListType(
        ModelType(CMDObjectSchemaDiscriminator),
        serialize_when_none=False,
    )


class CMDArrayJson(CMDJson):
    TYPE_VALUE = "array"

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
