from schematics.models import Model
from schematics.types import StringType, ListType, ModelType
from ._fields import CMDPrimitiveField, CMDBooleanField


class CMDEnumItem(Model):
    # properties as tags
    name = StringType(required=True)
    hide = CMDBooleanField()    # used in arguments

    # properties as nodes
    value = CMDPrimitiveField(required=True)


class CMDEnum(Model):
    # properties as tags

    # properties as nodes
    items = ListType(ModelType(CMDEnumItem), min_size=1)


