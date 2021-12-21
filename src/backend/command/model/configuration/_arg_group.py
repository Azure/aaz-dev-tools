from schematics.models import Model
from schematics.types import StringType, PolyModelType, ListType

from ._arg import CMDArg


class CMDArgGroup(Model):
    # properties as tags
    name = StringType(required=True)

    # properties as nodes
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True), min_size=1)

    class Options:
        _attributes = {"name"}
