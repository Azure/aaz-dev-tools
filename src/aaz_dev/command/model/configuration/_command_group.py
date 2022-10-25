from schematics.models import Model
from schematics.types import ModelType, ListType

from ._command import CMDCommand
from ._fields import CMDCommandGroupNameField


class CMDCommandGroup(Model):
    # properties as tags
    name = CMDCommandGroupNameField(required=True)
    # stage = CMDStageField()

    # properties as nodes
    # help = ModelType(CMDHelp, required=True)
    commands = ListType(ModelType(CMDCommand))  # sub commands
    command_groups = ListType(
        ModelType("CMDCommandGroup"),
        serialized_name='commandGroups',
        deserialize_from='commandGroups',
    )  # sub command groups

    class Options:
        serialize_when_none = False

    def reformat(self, **kwargs):
        if self.command_groups:
            for group in self.command_groups:
                group.reformat(**kwargs)
            self.command_groups = sorted(
                [group for group in self.command_groups if group.commands or group.command_groups],
                key=lambda g: g.name
            )
        if self.commands:
            for command in self.commands:
                command.reformat(**kwargs)
        elif self.command_groups:
            if len(self.command_groups) == 1:
                sub_group = self.command_groups[0]
                self.name += ' ' + sub_group.name
                self.command_groups = sub_group.command_groups
                self.commands = sub_group.commands
                del sub_group

    def link(self):
        if self.commands:
            for command in self.commands:
                command.link()
        if self.command_groups:
            for group in self.command_groups:
                group.link()
