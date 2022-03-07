import os

from cli.templates import get_templates
from cli.tests.common import CommandTestCase
from cli.model.atomic import CLIAtomicCommandGroup, CLIAtomicCommand
from utils.stage import AAZStageEnum
import json
from command.model.specs import CMDSpecsCommandTree
from command.model.configuration import CMDConfiguration, XMLSerializer
from command.controller.cfg_reader import CfgReader
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

    # create
    def test_render_create_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        create_cmd = tree.root.command_groups['databricks'].command_groups['workspace'].commands['create']
        leaf = CLIAtomicCommand({
            "names": create_cmd.names,
            "help": {
                "short": create_cmd.help.short,
                "long": '\n'.join(create_cmd.help.lines) if create_cmd.help.lines else None,
                "examples": [e.to_primitive() for e in create_cmd.versions[0].examples]
            },
            "register_info": {
                "stage": create_cmd.versions[0].stage,
            },
            "version": create_cmd.versions[0].name,
            "resources": [r.to_primitive() for r in create_cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "workspace-crud.xml")

        with open(cfg_file_path, 'r') as f:
            cfg = XMLSerializer(CMDConfiguration).from_xml(f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', 'create')

        data = tmpl.render(
            leaf=AzCommandGenerator(leaf)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", "_create.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    # show
    # delete
    # list
    # update
