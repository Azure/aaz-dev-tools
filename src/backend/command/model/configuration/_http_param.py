from schematics.types import StringType, ModelType

from ._fields import CMDVariantField, CMDBooleanField
from ._schema import CMDSchemaBase, CMDSchemaDefault, CMDStringSchemaBase, CMDIntegerSchemaBase, CMDFloatSchemaBase, \
    CMDBooleanSchemaBase, CMDArraySchemaBase, CMDByteSchemaBase, CMDBinarySchemaBase, CMDDurationSchemaBase, \
    CMDDateSchemaBase, CMDDateTimeSchemaBase, CMDUuidSchemaBase, CMDPasswordSchemaBase, CMDInteger32SchemaBase, \
    CMDInteger64SchemaBase, CMDFloat32SchemaBase, CMDFloat64SchemaBase


class CMDHttpParam(CMDSchemaBase):
    # properties as tags
    name = StringType(required=True)
    arg = CMDVariantField()
    required = CMDBooleanField()
    readonly = CMDBooleanField()  # it is required for const

    skip_url_encoding = CMDBooleanField(
        serialized_name="skipUrlEncoding",
        deserialize_from="skipUrlEncoding",
    )

    # properties as nodes
    default = ModelType(CMDSchemaDefault, serialize_when_none=False)  # it is required for const

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDHttpParam, cls)._claim_polymorphic(data):
            if isinstance(data, dict):
                # distinguish with CMDSchemaBase and CMDHttpParam
                return 'name' in data
            else:
                return isinstance(data, CMDHttpParam)
        return False


# string
class CMDHttpStringParam(CMDHttpParam, CMDStringSchemaBase):
    pass


class CMDHttpByteParam(CMDHttpStringParam, CMDByteSchemaBase):
    pass


class CMDHttpBinaryParam(CMDHttpStringParam, CMDBinarySchemaBase):
    pass


class CMDHttpDurationParam(CMDHttpStringParam, CMDDurationSchemaBase):
    pass


class CMDHttpDateParam(CMDHttpStringParam, CMDDateSchemaBase):
    pass


class CMDHttpDateTimeParam(CMDHttpStringParam, CMDDateTimeSchemaBase):
    pass


class CMDHttpUuidParam(CMDHttpStringParam, CMDUuidSchemaBase):
    pass


class CMDHttpPasswordParam(CMDHttpStringParam, CMDPasswordSchemaBase):
    pass


# integer
class CMDHttpIntegerParam(CMDHttpParam, CMDIntegerSchemaBase):
    pass


class CMDHttpInteger32Param(CMDHttpIntegerParam, CMDInteger32SchemaBase):
    pass


class CMDHttpInteger64Param(CMDHttpIntegerParam, CMDInteger64SchemaBase):
    pass


# float
class CMDHttpFloatParam(CMDHttpParam, CMDFloatSchemaBase):
    pass


class CMDHttpFloat32Param(CMDHttpFloatParam, CMDFloat32SchemaBase):
    pass


class CMDHttpFloat64Param(CMDHttpFloatParam, CMDFloat64SchemaBase):
    pass


# boolean
class CMDHttpBooleanParam(CMDHttpParam, CMDBooleanSchemaBase):
    pass


# array
class CMDHttpArrayParam(CMDHttpParam, CMDArraySchemaBase):
    pass
