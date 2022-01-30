from command.controller.workspace_manager import WorkspaceManager
from command.tests.common import CommandTestCase, workspace_name
from utils.plane import PlaneEnum
import os
import json
from utils import exceptions
from swagger.utils.tools import swagger_resource_path_to_resource_id
from command.templates import get_templates
from command.model.specs import CMDSpecsCommandGroup, CMDSpecsCommand, CMDSpecsCommandVersion, CMDSpecsResource
from command.model.configuration import CMDHelp, CMDStageEnum, CMDCommandExample


class TemplateRenderTest(CommandTestCase):

    def test_render_group_template(self):
        tmpl = get_templates()['group']
        command_group = CMDSpecsCommandGroup()
        command_group.names = ["edge-order", "order"]
        command_group.help = CMDHelp()
        command_group.help.short = "This is a short help."
        command_group.help.lines = [
            "Long help line 1",
            "Long help line 2",
            "Long help end of line"
        ]

        command_group.command_groups = []
        sub_group_1 = CMDSpecsCommandGroup()
        sub_group_1.names = ["edge-order", "order", "item"]
        sub_group_1.stage = CMDStageEnum.Preview
        sub_group_1.help = CMDHelp()
        sub_group_1.help.short = "Manager order item of edge."
        command_group.command_groups.append(sub_group_1)
        sub_group_2 = CMDSpecsCommandGroup()
        sub_group_2.names = ["edge-order", "order", "address"]
        sub_group_2.help = CMDHelp()
        sub_group_2.help.short = "Manager order address of edge."
        command_group.command_groups.append(sub_group_2)

        command_group.commands = []
        command_1 = CMDSpecsCommand()
        command_1.names = ["edge-order", "order", "list"]
        command_1.help = CMDHelp()
        command_1.help.short = "List available orders of an edge."
        command_group.commands.append(command_1)

        command_2 = CMDSpecsCommand()
        command_2.names = ["edge-order", "order", "show"]
        command_2.help = CMDHelp()
        command_2.help.short = "Show an order of an edge"
        command_group.commands.append(command_2)

        data = tmpl.render(group=command_group)

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "command_group.md")
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_command_template(self):
        tmpl = get_templates()['command']
        command = CMDSpecsCommand()
        command.names = ["edge-order", "order", "list"]
        
        command.help = CMDHelp()
        command.help.short = "List order"
        command.help.lines = [
            "Long help line 1",
            "Long help line 2",
            "Long help end of line"
        ]
        
        command.versions = []
        v_1 = CMDSpecsCommandVersion()
        v_1.name = "2021-12-01"
        v_1.resources = [
            CMDSpecsResource(
                {
                    "plane": PlaneEnum.Mgmt,
                    "id": "/subscriptions/{}/providers/microsoft.edgeorder/orders",
                    "version": "2021-12-01",
                }
            ),
            CMDSpecsResource(
                {
                    "plane": PlaneEnum.Mgmt,
                    "id": "/subscriptions/{}/resourcegroups/{}/providers/microsoft.edgeorder/orders",
                    "version": "2021-12-01",
                }
            ),
        ]
        v_1.examples = [
            CMDCommandExample(
                {
                    "name": "List order of current subscription",
                    "lines": [
                        "edge-order order list"
                    ]
                }
            ),
            CMDCommandExample(
                {
                    "name": "List order of a resource group",
                    "lines": [
                        "edge-order order list \\",
                        "-g {resource_group_name}"
                    ]
                }
            )
        ]
        command.versions.append(v_1)

        v_2 = CMDSpecsCommandVersion()
        v_2.name = "2020-12-01-preview"
        v_2.stage = CMDStageEnum.Preview
        v_2.resources = [
            CMDSpecsResource(
                {
                    "plane": PlaneEnum.Mgmt,
                    "id": "/subscriptions/{}/providers/microsoft.edgeorder/orders",
                    "version": "2020-12-01-preview",
                }
            ),
            CMDSpecsResource(
                {
                    "plane": PlaneEnum.Mgmt,
                    "id": "/subscriptions/{}/resourcegroups/{}/providers/microsoft.edgeorder/orders",
                    "version": "2020-12-01-preview",
                }
            ),
        ]
        v_2.examples = [
            CMDCommandExample(
                {
                    "name": "List order of current subscription",
                    "lines": [
                        "edge-order order list"
                    ]
                }
            ),
            CMDCommandExample(
                {
                    "name": "List order of a resource group",
                    "lines": [
                        "edge-order order list \\",
                        "-g {resource_group_name}"
                    ]
                }
            )
        ]
        command.versions.append(v_2)

        data = tmpl.render(command=command)
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "command.md")
        with open(output_path, 'w') as f:
            f.write(data)
