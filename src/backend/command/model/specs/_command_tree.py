from command.model.configuration import CMDStageField, CMDHelp, CMDCommandExample
from command.model.configuration._fields import CMDCommandNameField, CMDVersionField
from schematics.models import Model
from schematics.types import ModelType, ListType, StringType

from ._resource import CMDSpecsResource


class CMDSpecsCommandVersion(Model):
    name = CMDVersionField(required=True)
    stage = CMDStageField()
    resources = ListType(ModelType(CMDSpecsResource), required=True, min_size=1)
    examples = ListType(ModelType(CMDCommandExample))


class CMDSpecsCommand(Model):
    names = ListType(field=CMDCommandNameField(), min_size=1, required=True)  # full name of a command
    help = ModelType(CMDHelp, required=True)
    versions = ListType(ModelType(CMDSpecsCommandVersion), required=True, min_size=1)

    class Options:
        serialize_when_none = False


class CMDSpecsCommandGroup(Model):
    names = ListType(field=CMDCommandNameField(), required=True, min_size=1)  # full name of a command group
    stage = CMDStageField()
    help = ModelType(CMDHelp)

    command_groups = ListType(
        field=ModelType("CMDSpecsCommandGroup"),
    )
    commands = ListType(
        field=ModelType(CMDSpecsCommand)
    )

    class Options:
        serialize_when_none = False
