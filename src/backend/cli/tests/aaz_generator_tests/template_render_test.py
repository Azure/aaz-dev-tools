import os

from cli.templates import get_templates
from cli.tests.common import CommandTestCase
from cli.model.atomic import CLIAtomicCommandGroup, CLIAtomicCommand
from utils.stage import AAZStageEnum
from cli.controller.az_command_generator import AzCommandGenerator


class CliAAZGeneratorTemplateRenderTest(CommandTestCase):

    def test_render_cmd_group(self):
        tmpl = get_templates()['aaz']['group']['__cmd_group.py']
        node = CLIAtomicCommandGroup({
            "names": ['network', 'vnet'],
            "help": {
                "short": "Manage Azure Virtual Networks.",
                "long": "To learn more about Virtual Networks visit\nhttps://docs.microsoft.com/azure/virtual-network/virtual-network-manage-network."
            },
            "registerInfo": {
                "stage": AAZStageEnum.Experimental
            }
        })
        data = tmpl.render(
            node=node
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "vnet", "__cmd_group.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_group_init(self):
        tmpl = get_templates()['aaz']['group']['__init__.py']
        file_names = [
            '__init__.py',
            '__cmd_group.py',
            'test.json',
        ]
        data = tmpl.render(
            file_names=file_names
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "vnet", "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_show_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']
        leaf = CLIAtomicCommand({
            "names": ['network', 'vnet', 'show'],
            "help": {
                "short": "Get the details of a virtual network.",
                "long": "To learn more about Virtual Networks visit\nhttps://docs.microsoft.com/azure/virtual-network/virtual-network-manage-network.",
                "examples": [
                    {
                        "name": "Get details for MyVNet.",
                        "commands": [
                            "group create -n MyResourceGroup -l westus",
                            "network vnet show -g MyResourceGroup -n MyVNet",
                        ],
                    },
                    {
                        "name": "Get details by Id",
                        "commands": [
                            "group create -n MyResourceGroup -l westus",
                            "network vnet show --ids /subscription/sub/resourceGroup/mygroup"
                        ]
                    }
                ]
            },
            "registerInfo": {
                "stage": AAZStageEnum.Stable
            }
        })

        data = tmpl.render(
            leaf=AzCommandGenerator(leaf)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "vnet", "_show.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)
