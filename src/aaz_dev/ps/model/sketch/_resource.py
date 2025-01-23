from schematics.models import Model
from schematics.types import StringType, ListType, ModelType
from command.model.configuration._fields import CMDResourceIdField, CMDVersionField
from cli.model.view import CLIViewCommand


class PSSketchResource(Model):

    id = CMDResourceIdField(required=True)
    path = StringType(required=True)
    cli_commands = ListType(
        ModelType(CLIViewCommand),
        serialized_name="cliCommands",
        deserialize_from="cliCommands",
    )
    subresources = ListType(StringType)

    class Options:
        serialize_when_none = False
