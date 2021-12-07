from schematics.types import ModelType, ListType

from ._command_group import CMDCommandGroup
from ._resource import CMDResource
from ._xml import XMLModel


class CMDConfiguration(XMLModel):
    # properties as nodes
    resources = ListType(ModelType(CMDResource), min_size=1, required=True)  # resources contained in configuration file
    command_group = ModelType(
        CMDCommandGroup,
        serialized_name='commandGroups',
        deserialize_from='commandGroups',
    )

    class Options:
        serialize_when_none = False
