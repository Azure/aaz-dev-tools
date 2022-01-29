from command.model.configuration import CMDStageField, CMDHelp
from command.model.configuration._fields import CMDCommandNameField
from schematics.models import Model
from schematics.types import ModelType, ListType, DictType

from ._fields import CMDResourceIdField, CMDVersionField


class CMDSpecsCommandTreeLeafResource(Model):
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)


class CMDSpecsCommandTreeLeafVersion(Model):
    version = CMDVersionField(required=True)
    stage = CMDStageField()
    resource = ModelType(CMDSpecsCommandTreeResource)


class CMDSpecsCommandTreeLeaf(Model):
    names = ListType(field=CMDCommandNameField(), min_size=1, required=True)  # full name of a command
    help = ModelType(CMDHelp, required=True)
    versions = ListType(ModelType(CMDSpecsCommandTreeLeafVersion), required=True, min_size=1)

    class Options:
        serialize_when_none = False


class CMDSpecsCommandTreeNode(Model):
    names = ListType(field=CMDCommandNameField(), required=True)  # full name of a command group
    stage = CMDStageField()
    help = ModelType(CMDHelp)

    command_groups = DictType(
        field=ModelType("CMDCommandTreeNode"),
        serialized_name='commandGroups',
        deserialize_from='commandGroups'
    )
    commands = DictType(
        field=ModelType(CMDCommandTreeLeaf)
    )

    class Options:
        serialize_when_none = False
