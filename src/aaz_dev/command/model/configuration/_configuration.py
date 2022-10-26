from schematics.models import Model
from schematics.types import ModelType, ListType, UTCDateTimeType
from utils.fields import PlaneField

from ._command_group import CMDCommandGroup
from ._resource import CMDResource


class CMDConfiguration(Model):
    # properties as nodes
    plane = PlaneField(required=True)

    resources = ListType(ModelType(CMDResource), min_size=1, required=True)  # resources contained in configuration file
    command_groups = ListType(
        ModelType(CMDCommandGroup),
        serialized_name='commandGroups',
        deserialize_from='commandGroups',
    )

    class Options:
        serialize_when_none = False

    def reformat(self, **kwargs):
        self.resources = sorted(self.resources, key=lambda r: r.id)
        for group in self.command_groups:
            group.reformat(**kwargs)
        self.command_groups = sorted(
            [group for group in self.command_groups if group.commands or group.command_groups],
            key=lambda g: g.name
        )

    def link(self):
        """Link cls reference with definition"""
        for group in self.command_groups:
            group.link()
