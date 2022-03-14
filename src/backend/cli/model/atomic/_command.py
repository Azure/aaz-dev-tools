from cli.model.atomic._fields import CLICommandNameField, CLIVersionField, CLICommandConfigurationField
from cli.model.atomic._help import CLICommandHelp
from cli.model.atomic._resource import CLISpecsResource
from schematics.models import Model
from utils.stage import AAZStageField
from schematics.types import ModelType, ListType


class CLIAtomicCommandRegisterInfo(Model):
    stage = AAZStageField(required=True)    # the stage used in code, usually it should be consist with command.stage
    # TODO: add support for deprecate_info


class CLIAtomicCommand(Model):
    names = ListType(field=CLICommandNameField(), min_size=1, required=True)  # full name of a command
    stage = AAZStageField()     # the stage of command
    help = ModelType(CLICommandHelp, required=True)
    register_info = ModelType(
        CLIAtomicCommandRegisterInfo,
        serialized_name="registerInfo",
        deserialize_from="registerInfo"
    )  # register info in command table. If it's not registered in command table, this field is None

    version = CLIVersionField(required=True)
    resources = ListType(ModelType(CLISpecsResource), required=True, min_size=1)

    cfg = CLICommandConfigurationField()

    class Options:
        serialize_when_none = False
