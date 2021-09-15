from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, PolyModelType
from ._help import CMDHelp
from ._fields import CMDStageField, CMDVersionField
from ._arg_group import CMDArgGroup
from ._condition import CMDCondition
from ._operation import CMDOperation
from ._output import CMDOutput
from ._resource import CMDResource


class CMDCommand(Model):

    # properties as tags
    name = StringType(min_length=1, required=True)
    stage = CMDStageField()
    version = CMDVersionField()

    # properties as nodes
    resources = ListType(ModelType(CMDResource))   # the azure resources used in this command
    help = ModelType(CMDHelp, required=True)
    arg_groups = ListType(
        ModelType(CMDArgGroup),
        serialized_name='argGroups',
        deserialize_from='argGroups'
    )
    conditions = ListType(ModelType(CMDCondition))
    operations = ListType(PolyModelType(CMDOperation, allow_subclasses=True))
    outputs = ListType(PolyModelType(CMDOutput, allow_subclasses=True))
