from cli.model.atomic._command import CLIAtomicCommand
from cli.model.atomic._fields import CLICommandNameField, CLIStageField
from cli.model.atomic._help import CLICommandGroupHelp
from schematics.models import Model
from schematics.types import ModelType, ListType, DictType


class CLIAtomicCommandGroupRegisterInfo(Model):
    stage = CLIStageField(required=True)
    # TODO: add support for deprecate_info


class CLIAtomicCommandGroup(Model):
    names = ListType(field=CLICommandNameField(), min_size=1, required=True)  # full name of a command group
    help = ModelType(CLICommandGroupHelp, required=True)
    register_info = ModelType(CLIAtomicCommandGroupRegisterInfo, required=False)  # register info in command group table. If it's not registered in command group table, this field is None

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
