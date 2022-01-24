from schematics.models import Model
from schematics.types import ModelType, ListType

from ._command import CMDCommand
from ._fields import CMDStageField, CMDCommandGroupNameField
from ._help import CMDHelp


class CMDCommandGroup(Model):
    # properties as tags
    name = CMDCommandGroupNameField(required=True)
    # stage = CMDStageField()

    # properties as nodes
    # help = ModelType(CMDHelp, required=True)
    commands = ListType(ModelType(CMDCommand))  # sub commands
    command_groups = ListType(
        ModelType("CMDCommandGroup"),
        serialized_name='commandGroups',
        deserialize_from='commandGroups',
    )  # sub command groups

    class Options:
        serialize_when_none = False

