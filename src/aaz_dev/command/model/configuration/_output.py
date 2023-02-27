from schematics.models import Model
from schematics.types import StringType
from schematics.types.serializable import serializable

from ._fields import CMDVariantField, CMDBooleanField


class CMDOutput(Model):
    # properties as tags
    TYPE_VALUE = None  # types: "array", "object", "string",

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
        elif isinstance(data, CMDOutput):
            return data.TYPE_VALUE == cls.TYPE_VALUE
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

    # ref means get value from content
    ref = CMDVariantField()
    # use placeholder value as output
    value = StringType()
