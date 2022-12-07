from command.model.configuration._fields import CMDResourceIdField, CMDVersionField
from schematics.models import Model
from schematics.types import StringType
from utils.fields import PlaneField


class CMDSpecsResource(Model):
    plane = PlaneField(required=True)
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)
    subresource = StringType()

    class Options:
        serialize_when_none = False
