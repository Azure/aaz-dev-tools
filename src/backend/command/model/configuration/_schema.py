# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType, IntType, FloatType, ListType, PolyModelType
from ._fields import CMDTypeField, CMDVariantField, StringType, CMDSchemaClassField, CMDRegularExpressionField, CMDBooleanField
from ._enum import CMDEnum


class CMDSchemaBase(Model):
    # properties as tags
    TYPE_VALUE = None

    # base types: "array", "boolean", "integer", "float", "object", "string",
    type_ = CMDTypeField(required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        return False


class CMDSchema(CMDSchemaBase):
    # properties as tags

    name = StringType(required=True)
    arg = CMDVariantField()
    cls = CMDSchemaClassField()   # define a schema which can be used in other
    required = CMDBooleanField()
    readonly = CMDBooleanField()

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDSchema, cls)._claim_polymorphic(data):
            # distinguish with CMDArgBase and CMDArg
            return 'name' in data
        return False


# cls
class CMDClsSchemaBase(CMDSchemaBase):

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None and type_value.startswith("@"):
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


class CMDStringSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "string"

    format_ = ModelType(
        CMDStringSchemaFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    enum = ModelType(CMDEnum)


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


class CMDIntegerSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "integer"

    format_ = ModelType(
        CMDIntegerSchemaFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    enum = ModelType(CMDEnum)


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


class CMDFloatSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "float"

    format_ = ModelType(
        CMDFloatSchemaFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    enum = ModelType(CMDEnum)


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


# discriminator
class CMDObjectSchemaDiscriminator(Model):
    # properties as tags
    arg = CMDVariantField()
    value = StringType()    # TODO: check possible types of value

    # properties as nodes
    format_ = ModelType(
        CMDObjectSchemaFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    props = ListType(PolyModelType(CMDSchema, allow_subclasses=True))
    discriminators = ListType(ModelType('CMDObjectSchemaDiscriminator'))


class CMDObjectSchemaBase(CMDSchemaBase):
    TYPE_VALUE = "object"

    format_ = ModelType(
        CMDObjectSchemaFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    props = ListType(PolyModelType(CMDSchema, allow_subclasses=True))
    discriminators = ListType(ModelType(CMDObjectSchemaDiscriminator))


class CMDObjectSchema(CMDSchema, CMDObjectSchemaBase):
    pass


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


class CMDArraySchemaBase(CMDSchemaBase):
    TYPE_VALUE = "array"

    format_ = ModelType(
        CMDArraySchemaFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    item = PolyModelType(CMDSchemaBase, allow_subclasses=True)


class CMDArraySchema(CMDSchema, CMDArraySchemaBase):
    pass


# json
class CMDJson(Model):
    var = CMDVariantField()
    ref = CMDVariantField()

    type_ = CMDTypeField(required=True)  # "object"

    format_ = ModelType(
        CMDObjectSchemaFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    props = ListType(PolyModelType(CMDSchema, allow_subclasses=True))
    discriminators = ListType(ModelType(CMDObjectSchemaDiscriminator))

