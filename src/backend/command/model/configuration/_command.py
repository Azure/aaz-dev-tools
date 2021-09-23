from schematics.models import Model
from schematics.types import ModelType, ListType, PolyModelType

from ._arg_group import CMDArgGroup
from ._condition import CMDCondition
from ._fields import CMDStageField, CMDVersionField, CMDCommandNameField
from ._help import CMDHelp
from ._operation import CMDOperation
from ._output import CMDOutput
from ._resource import CMDResource


class CMDCommand(Model):
    # properties as tags
    name = CMDCommandNameField(required=True)
    stage = CMDStageField()
    version = CMDVersionField(required=True)

    # properties as nodes
    resources = ListType(ModelType(CMDResource), min_size=1)  # the azure resources used in this command
    help = ModelType(CMDHelp, required=True)
    arg_groups = ListType(
        ModelType(CMDArgGroup),
        serialized_name='argGroups',
        deserialize_from='argGroups',
        serialize_when_none=False
    )
    conditions = ListType(ModelType(CMDCondition), serialize_when_none=False)
    operations = ListType(PolyModelType(CMDOperation, allow_subclasses=True), min_size=1)
    outputs = ListType(PolyModelType(CMDOutput, allow_subclasses=True), min_size=1)
