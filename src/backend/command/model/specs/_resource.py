from command.model.configuration._fields import CMDResourceIdField, CMDVersionField
from schematics.models import Model
from utils.fields import PlaneField


class CMDSpecsResource(Model):
    plane = PlaneField(required=True)
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)

    class Options:
        serialize_when_none = False
