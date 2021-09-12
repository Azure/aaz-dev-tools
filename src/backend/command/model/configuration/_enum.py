from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, BooleanType, BaseType
from ._fields import CMDJsonValueField


class CMDEnumItem(Model):
    # properties as tags
    name = StringType(required=True)
    hide = BooleanType(default=False)

    # properties as nodes
    value = CMDJsonValueField(required=True)


class CMDEnum(Model):
    # properties as tags

    # properties as nodes
    items = ListType(ModelType(CMDEnumItem), min_size=1)


