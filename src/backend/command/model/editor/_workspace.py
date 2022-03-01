from schematics.models import Model
from schematics.types import StringType, ModelType, UTCDateTimeType, ListType, DictType
from command.model.configuration._fields import CMDCommandNameField, CMDVersionField
from command.model.configuration import CMDStageField, CMDHelp, CMDResource, CMDCommandExample
from utils.fields import PlaneField


class CMDCommandTreeLeaf(Model):
    names = ListType(field=CMDCommandNameField(), min_size=1, required=True)   # full name of a command
    stage = CMDStageField()
    version = CMDVersionField(required=True)

    help = ModelType(CMDHelp)
    resources = ListType(ModelType(CMDResource), min_size=1)  # the azure resources used in this command
    examples = ListType(ModelType(CMDCommandExample))

    class Options:
        serialize_when_none = False


class CMDCommandTreeNode(Model):
    names = ListType(field=CMDCommandNameField(), min_size=1, required=True)   # full name of a command group
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


class CMDEditorWorkspace(Model):
    version = UTCDateTimeType(required=True)  # this property updated when workspace saved in file.
    name = StringType(required=True)
    plane = PlaneField(required=True)
    command_tree = ModelType(
        CMDCommandTreeNode,
        required=True,
        serialized_name='commandTree',
        deserialize_from='commandTree'
    )   # the root node

    class Options:
        serialize_when_none = False
