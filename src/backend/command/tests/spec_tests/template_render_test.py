from command.controller.workspace_manager import WorkspaceManager
from command.tests.common import CommandTestCase, workspace_name
from utils.plane import PlaneEnum
import os
import json
from utils import exceptions
from swagger.utils.tools import swagger_resource_path_to_resource_id
from command.templates import get_templates
from command.model.specs import CMDSpecsCommandTreeNode, CMDSpecsCommandTreeLeaf
from command.model.configuration import CMDHelp, CMDStageEnum


class TemplateRenderTest(CommandTestCase):

    def test_render_group_template(self):
        tmpl = get_templates()['group']
        command_group = CMDSpecsCommandTreeNode()
        command_group.names = ["edge-order", "order"]
        command_group.help = CMDHelp()
        command_group.help.short = "This is a short help."
        command_group.help.lines = [
            "Long help line 1",
            "Long help line 2",
            "Long help end of line"
        ]

        command_group.command_groups = []
        sub_group_1 = CMDSpecsCommandTreeNode()
        sub_group_1.names = ["edge-order", "order", "item"]
        sub_group_1.stage = CMDStageEnum.Preview
        sub_group_1.help = CMDHelp()
        sub_group_1.help.short = "Manager order item of edge."
        command_group.command_groups.append(sub_group_1)
        sub_group_2 = CMDSpecsCommandTreeNode()
        sub_group_2.names = ["edge-order", "order", "address"]
        sub_group_2.help = CMDHelp()
        sub_group_2.help.short = "Manager order address of edge."
        command_group.command_groups.append(sub_group_2)

        command_group.commands = []
        command_1 = CMDSpecsCommandTreeLeaf()
        command_1.names = ["edge-order", "order", "list"]
        command_1.help = CMDHelp()
        command_1.help.short = "List available orders of an edge."
        command_group.commands.append(command_1)

        command_2 = CMDSpecsCommandTreeLeaf()
        command_2.names = ["edge-order", "order", "show"]
        command_2.help = CMDHelp()
        command_2.help.short = "Show an order of an edge"
        command_group.commands.append(command_2)

        data = tmpl.render(group=command_group)

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "readme.md")
        with open(output_path, 'w') as f:
            f.write(data)


    def test_render_command_template(self):
        tmpl = get_templates()['command']
