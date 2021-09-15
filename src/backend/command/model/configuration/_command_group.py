from schematics.models import Model
from schematics.types import StringType, ModelType, ListType
from ._help import CMDHelp
from ._command import CMDCommand
from ._fields import CMDStageField


class CMDCommandGroup(Model):
    # properties as tags
    name = StringType(min_length=1, required=True)
    stage = CMDStageField()

    # properties as nodes
    help = ModelType(CMDHelp, required=True)
    commands = ListType(ModelType(CMDCommand))  # sub commands
    command_groups = ListType(
        ModelType("CMDCommandGroup"),
        serialized_name='commandGroups',
        deserialize_from='commandGroups'
    )  # sub command groups
