from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, PolyModelType
from ._help import CMDHelp
from ._fields import CMDStageField
from ._arg_group import CMDArgGroup
from ._condition import CMDCondition
from ._operation import CMDOperation
from ._output import CMDOutput


class CMDCommand(Model):

    # properties as tags
    name = StringType(min_length=1, required=True)
    stage = CMDStageField()
    # TODO: version

    # properties as nodes
    help_ = ModelType(CMDHelp, required=True)
    arg_groups = ListType(ModelType(CMDArgGroup))
    conditions = ListType(ModelType(CMDCondition))
    operations = ListType(PolyModelType(CMDOperation, allow_subclasses=True))
    outputs = ListType(PolyModelType(CMDOutput, allow_subclasses=True))
