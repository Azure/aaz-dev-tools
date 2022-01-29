from command.model.configuration import CMDStageField, CMDHelp, CMDCommandExample
from command.model.configuration._fields import CMDCommandNameField, CMDVersionField
from schematics.models import Model
from schematics.types import ModelType, ListType, StringType

from ._resource import CMDSpecsResource


class CMDSpecsCommandTreeLeafVersion(Model):
    name = CMDVersionField(required=True)
    stage = CMDStageField()
    resources = ListType(ModelType(CMDSpecsResource), required=True, min_size=1)
    examples = ListType(ModelType(CMDCommandExample))


class CMDSpecsCommandTreeLeaf(Model):
    names = ListType(field=CMDCommandNameField(), min_size=1, required=True)  # full name of a command
    help = ModelType(CMDHelp, required=True)
    versions = ListType(ModelType(CMDSpecsCommandTreeLeafVersion), required=True, min_size=1)

    class Options:
        serialize_when_none = False


class CMDSpecsCommandTreeNode(Model):
    names = ListType(field=CMDCommandNameField(), required=True, min_size=1)  # full name of a command group
    stage = CMDStageField()
    help = ModelType(CMDHelp)

    command_groups = ListType(
        field=ModelType("CMDSpecsCommandTreeNode"),
    )
    commands = ListType(
        field=ModelType(CMDSpecsCommandTreeLeaf)
    )

    class Options:
        serialize_when_none = False
