from cli.model.common._fields import CLIProfileNameField
from schematics.models import Model
from schematics.types import ModelType, DictType

from ._command_group import CLIAtomicCommandGroup


class CLIAtomicProfile(Model):
    name = CLIProfileNameField(required=True)
    command_groups = DictType(
        field=ModelType(CLIAtomicCommandGroup),
        serialized_name="commandGroups",
        deserialize_from="commandGroups"
    )

    class Options:
        serialize_when_none = False
