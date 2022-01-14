from schematics.models import Model
from schematics.types import StringType, ModelType, UTCDateTimeType, ListType
from command.model.configuration._fields import CMDCommandNameField
from command.model.configuration import CMDStageField, CMDHelp, CMDResource


class CMDCommandTreeLeaf(Model):
    name = CMDCommandNameField(required=True)
    stage = CMDStageField()

    help = ModelType(CMDHelp)
    resources = ListType(ModelType(CMDResource), min_size=1)  # the azure resources used in this command

    class Options:
        serialize_when_none = False


class CMDCommandTreeNode(Model):
    name = CMDCommandNameField(required=True)
    stage = CMDStageField()

    help = ModelType(CMDHelp)
    command_groups = ListType(
        ModelType("CMDCommandTreeNode"),
        serialized_name='commandGroups',
        deserialize_from='commandGroups'
    )
    commands = ListType(
        ModelType(CMDCommandTreeLeaf)
    )

    class Options:
        serialize_when_none = False


class CMDEditorWorkspace(Model):
    version = UTCDateTimeType(required=True)  # this property updated when workspace saved in file.
    name = StringType(required=True)
    command_tree = ModelType(
        CMDCommandTreeNode,
        required=True,
        serialized_name='commandTree',
        deserialize_from='commandTree'
    )

    class Options:
        serialize_when_none = False
