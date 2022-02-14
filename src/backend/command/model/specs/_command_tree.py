from command.model.configuration import CMDStageField, CMDHelp, CMDCommandExample
from command.model.configuration._fields import CMDCommandNameField, CMDVersionField
from schematics.models import Model
from schematics.types import ModelType, ListType, DictType

from ._resource import CMDSpecsResource


class CMDSpecsCommandVersion(Model):
    name = CMDVersionField(required=True)
    stage = CMDStageField()
    resources = ListType(ModelType(CMDSpecsResource), required=True, min_size=1)
    examples = ListType(ModelType(CMDCommandExample))

    class Options:
        serialize_when_none = False


class CMDSpecsCommand(Model):
    names = ListType(field=CMDCommandNameField(), min_size=1, required=True)  # full name of a command
    help = ModelType(CMDHelp, required=True)
    versions = ListType(ModelType(CMDSpecsCommandVersion), required=True, min_size=1)

    class Options:
        serialize_when_none = False


class CMDSpecsCommandGroup(Model):
    names = ListType(field=CMDCommandNameField(), min_size=1, required=True)  # full name of a command group
    help = ModelType(CMDHelp)

    command_groups = DictType(
        field=ModelType("CMDSpecsCommandGroup"),
        serialized_name="commandGroups",
        deserialize_from="commandGroups"
    )
    commands = DictType(
        field=ModelType(CMDSpecsCommand)
    )

    class Options:
        serialize_when_none = False


class CMDSpecsCommandTree(Model):
    root = ModelType(
        CMDSpecsCommandGroup
    )  # the root node

    class Options:
        serialize_when_none = False
