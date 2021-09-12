from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, BooleanType
from ._help import CMDHelp
from ._command import CMDCommand
from ._fields import CMDStageField


class CMDCommandGroup(Model):
    # properties as tags
    name = StringType(min_length=1, required=True)
    stage = CMDStageField()

    # properties as nodes
    help_ = ModelType(CMDHelp, required=True)
    commands = ListType(ModelType(CMDCommand))  # sub commands
    command_groups = ListType(ModelType("CMDCommandGroup"))  # sub command groups
