from schematics.models import Model
from schematics.types import StringType, BooleanType, ListType
from ._fields import CMDTypeField, CMDVariantField


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
    client_flatten = BooleanType(default=False)


class CMDArrayOutput(CMDOutput):
    TYPE_VALUE = 'array'

    ref = CMDVariantField(required=True)
    client_flatten = BooleanType(default=False)
    next_link = CMDVariantField()


class CMDStringOutput(CMDOutput):
    TYPE_VALUE = 'string'

    value = StringType(required=True)
