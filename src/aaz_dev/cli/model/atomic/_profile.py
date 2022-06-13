from cli.model.atomic._command_group import CLIAtomicCommandGroup
from cli.model.atomic._fields import CLIProfileNameField
from schematics.models import Model
from schematics.types import ModelType, DictType


class CLIAtomicProfile(Model):
    name = CLIProfileNameField(required=True)
    command_groups = DictType(
        field=ModelType(CLIAtomicCommandGroup),
        serialized_name="commandGroups",
        deserialize_from="commandGroups"
    )

    class Options:
        serialize_when_none = False
