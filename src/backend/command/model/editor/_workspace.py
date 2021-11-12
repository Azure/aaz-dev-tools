from schematics.models import Model
from schematics.types import StringType, ListType, DictType, ModelType, PolyModelType
from schematics.types.serializable import serializable
from ..configuration import CMDCommandGroup


class CMDEditorWorkspace(Model):

    namespace = StringType()

    command_groups = ListType(ModelType(CMDCommandGroup))   # command group

    # resource_index = DictType(ListType())

