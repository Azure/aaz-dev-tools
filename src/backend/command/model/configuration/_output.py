from schematics.models import Model
from schematics.types import StringType
from ._fields import CMDTypeField, CMDVariantField, CMDBooleanField


class CMDOutput(Model):
    # properties as tags
    TYPE_VALUE = None

    # base types: "array", "object", "string",
    type_ = CMDTypeField(required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        return False


class CMDObjectOutput(CMDOutput):
    TYPE_VALUE = 'object'

    ref = CMDVariantField(required=True)
    client_flatten = CMDBooleanField(
        serialized_name='clientFlatten',
        deserialize_from='clientFlatten',
    )


class CMDArrayOutput(CMDOutput):
    TYPE_VALUE = 'array'

    ref = CMDVariantField(required=True)
    client_flatten = CMDBooleanField(
        serialized_name='clientFlatten',
        deserialize_from='clientFlatten',
    )
    next_link = CMDVariantField(
        serialized_name='nextLink',
        deserialize_from='nextLink',
    )


class CMDStringOutput(CMDOutput):
    TYPE_VALUE = 'string'

    value = StringType(required=True)
