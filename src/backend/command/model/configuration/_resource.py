from schematics.models import Model

from ._fields import CMDResourceIdField, CMDVersionField


class CMDResource(Model):
    # properties as tags
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)

    class Options:
        _attributes = {"id", "version"}
