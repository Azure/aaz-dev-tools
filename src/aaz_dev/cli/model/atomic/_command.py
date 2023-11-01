from cli.model.common._fields import CLICommandNameField, CLIVersionField, CLICommandConfigurationField
from schematics.models import Model
from schematics.types import ModelType, ListType, StringType, BooleanType
from utils.stage import AAZStageField

from ._help import CLICommandHelp
from ._resource import CLISpecsResource


class CLIAtomicCommandRegisterInfo(Model):
    stage = AAZStageField(required=True)  # the stage used in code, usually it should be consist with command.stage
    confirmation = StringType(min_length=1)

    # TODO: add support for deprecate_info

    class Options:
        serialize_when_none = False


class CLIAtomicCommand(Model):
    names = ListType(field=CLICommandNameField(), min_size=1, required=True)  # full name of a command
    stage = AAZStageField()  # the stage of command
    help = ModelType(CLICommandHelp, required=True)
    register_info = ModelType(
        CLIAtomicCommandRegisterInfo,
        serialized_name="registerInfo",
        deserialize_from="registerInfo"
    )  # register info in command table. If it's not registered in command table, this field is None

    version = CLIVersionField()  # the version of wait command is not required.
    resources = ListType(ModelType(CLISpecsResource), required=True, min_size=1)

    cfg = CLICommandConfigurationField()
    support_no_wait = BooleanType(
        serialized_name="supportNoWait",
        deserialize_from="supportNoWait",
    )

    class Options:
        serialize_when_none = False
