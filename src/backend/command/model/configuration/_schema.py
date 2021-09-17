# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType, IntType, FloatType, ListType, PolyModelType
from schematics.types.serializable import serializable
from ._fields import CMDVariantField, StringType, CMDSchemaClassField, CMDRegularExpressionField, CMDBooleanField, CMDPrimitiveField


class CMDSchemaEnumItem(Model):
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
                # distinguish with CMDArgBase and CMDArg
                return 'name' in data
            else:
                return isinstance(data, CMDSchema)
        return False


# cls  TODO: add support for cls
class CMDClsSchemaBase(CMDSchemaBase):

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
class CMDStringSchemaFormat(Model):
    pattern = CMDRegularExpressionField()
    max_length = IntType(
        min_value=0,
        serialized_name='maxLength',
        deserialize_from='maxLength',
    )
    min_length = IntType(
        min_value=0,
        serialized_name='minLength',
        deserialize_from='minLength',
    )

    class Options:
        serialize_when_none = False


class CMDStringSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "string"

    fmt = ModelType(
        CMDStringSchemaFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDStringSchema(CMDSchema, CMDStringSchemaBase):
    pass


# integer
class CMDIntegerSchemaFormat(Model):
    bits = IntType(choices=(32, 64), default=32)
    multiple_of = IntType(
        min_value=0,
        serialized_name='multipleOf',
        deserialize_from='multipleOf'
    )
    maximum = IntType()
    minimum = IntType()

    class Options:
        serialize_when_none = False


class CMDIntegerSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "integer"

    fmt = ModelType(
        CMDIntegerSchemaFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDIntegerSchema(CMDSchema, CMDIntegerSchemaBase):
    pass


# boolean
class CMDBooleanSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "boolean"


class CMDBooleanSchema(CMDSchema, CMDBooleanSchemaBase):
    pass


# float
class CMDFloatSchemaFormat(Model):
    bits = IntType(choices=(32, 64), default=32)
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


class CMDFloatSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "float"

    fmt = ModelType(
        CMDFloatSchemaFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDSchemaEnum, serialize_when_none=False)


class CMDFloatSchema(CMDSchema, CMDFloatSchemaBase):
    pass


# object

class CMDObjectSchemaFormat(Model):
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


# discriminator
class CMDObjectSchemaDiscriminator(Model):
    # properties as tags
    arg = CMDVariantField(required=True)
    value = StringType(serialize_when_none=False)    # TODO: check possible types of value

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
        CMDObjectSchemaFormat,
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
    cls = CMDSchemaClassField(serialize_when_none=False)   # define a schema which can be used by others


# array
class CMDArraySchemaFormat(Model):
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

    class Options:
        serialize_when_none = False


class CMDArraySchemaBase(CMDSchemaBase):
    TYPE_VALUE = "array"

    # properties as nodes
    fmt = ModelType(
        CMDArraySchemaFormat,
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
    cls = CMDSchemaClassField(serialize_when_none=False)   # define a schema which can be used by others

    # properties as nodes
    fmt = ModelType(
        CMDObjectSchemaFormat,
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
        CMDArraySchemaFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False,
    )
    item = PolyModelType(CMDSchemaBase, allow_subclasses=True, required=True)

    def _get_type(self):
        return f"{self.TYPE_VALUE}<{self.item.type}>"
