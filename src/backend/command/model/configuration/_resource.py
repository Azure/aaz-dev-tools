from schematics.models import Model
from ._fields import CMDResourceIdField, CMDVersionField


class CMDResource(Model):
    # properties as tags
    id_ = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)
