from cli.model.atomic._command import CLIAtomicCommand
from cli.model.atomic._fields import CLICommandNameField
from cli.model.atomic._help import CLICommandGroupHelp
from schematics.models import Model
from schematics.types import ModelType, ListType, DictType
from utils.stage import AAZStageField


class CLIAtomicCommandGroupRegisterInfo(Model):
    stage = AAZStageField(required=True)    # the stage of command group used in code
    # TODO: add support for deprecate_info


class CLIAtomicCommandGroup(Model):
    names = ListType(field=CLICommandNameField(), min_size=1, required=True)  # full name of a command group
    help = ModelType(CLICommandGroupHelp, required=True)
    register_info = ModelType(
        CLIAtomicCommandGroupRegisterInfo,
        required=False,
        serialized_name="registerInfo",
        deserialize_from="registerInfo"
    )  # register info in command group table. If it's not registered in command group table, this field is None

    command_groups = DictType(
        field=ModelType("CLIAtomicCommandGroup"),
        serialized_name="commandGroups",
        deserialize_from="commandGroups"
    )
    commands = DictType(
        field=ModelType(CLIAtomicCommand)
    )

    class Options:
        serialize_when_none = False
