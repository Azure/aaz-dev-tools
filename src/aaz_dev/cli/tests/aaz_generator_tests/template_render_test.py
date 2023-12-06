import os

from cli.templates import get_templates
from cli.tests.common import CommandTestCase
from cli.model.atomic import CLIAtomicCommandGroup, CLIAtomicCommand, CLIAtomicClient
from utils.stage import AAZStageEnum
from utils.plane import PlaneEnum
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
        with open(output_path, 'w', encoding='utf-8') as f:
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
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # workspace
    # create
    def test_render_create_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "create"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "workspace-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # show
    def test_render_show_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "show"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "workspace-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # delete
    def test_render_delete_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "delete"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "workspace-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # update
    def test_render_update_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "update"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "workspace-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # list
    def test_render_list_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "list"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "workspace-list.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # vnet-peering
    # create
    def test_render_vnet_peering_create_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "create"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].command_groups['vnet-peering'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "vnet-peering-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', 'vnet-peering', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", "vnet_peering", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # show
    def test_render_vnet_peering_show_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "show"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].command_groups['vnet-peering'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "vnet-peering-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', 'vnet-peering', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", "vnet_peering", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # delete
    def test_render_vnet_peering_delete_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "delete"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].command_groups['vnet-peering'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "vnet-peering-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', 'vnet-peering', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", "vnet_peering", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # update
    def test_render_vnet_peering_update_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "update"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].command_groups['vnet-peering'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "vnet-peering-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', 'vnet-peering', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", "vnet_peering", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # list
    def test_render_vnet_peering_list_cmd(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "list"

        cmd = tree.root.command_groups['databricks'].command_groups['workspace'].command_groups['vnet-peering'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "vnet-peering-list.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('databricks', 'workspace', 'vnet-peering', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "databricks", "workspace", "vnet_peering", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # sentinel
    # show
    def test_render_sentinel_automation_rule_show(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "show"

        cmd = tree.root.command_groups['sentinel'].command_groups['automation-rule'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples or []]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "sentinel-automation-rule-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('sentinel', 'automation-rule', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "sentinel", "automation_rule", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # create
    def test_render_sentinel_automation_rule_create(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "create"

        cmd = tree.root.command_groups['sentinel'].command_groups['automation-rule'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples or []]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "sentinel-automation-rule-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('sentinel', 'automation-rule', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "sentinel", "automation_rule", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # update
    def test_render_sentinel_automation_rule_update(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "update"

        cmd = tree.root.command_groups['sentinel'].command_groups['automation-rule'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples or []]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "sentinel-automation-rule-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('sentinel', 'automation-rule', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "sentinel", "automation_rule", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # delete
    def test_render_sentinel_automation_rule_delete(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "delete"

        cmd = tree.root.command_groups['sentinel'].command_groups['automation-rule'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples or []]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "sentinel-automation-rule-crud.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('sentinel', 'automation-rule', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "sentinel", "automation_rule", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

    # list
    def test_render_sentinel_automation_rule_list(self):
        tmpl = get_templates()['aaz']['command']['_cmd.py']

        tree_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "tree.json")
        with open(tree_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tree = CMDSpecsCommandTree(data)

        cmd_name = "list"

        cmd = tree.root.command_groups['sentinel'].command_groups['automation-rule'].commands[cmd_name]
        leaf = CLIAtomicCommand({
            "names": cmd.names,
            "help": {
                "short": cmd.help.short,
                "long": '\n'.join(cmd.help.lines) if cmd.help.lines else None,
                "examples": [e.to_primitive() for e in cmd.versions[0].examples or []]
            },
            "register_info": {
                "stage": cmd.versions[0].stage,
            },
            "version": cmd.versions[0].name,
            "resources": [r.to_primitive() for r in cmd.versions[0].resources],
        })

        cfg_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databricks", "sentinel-automation-rule-list.xml")

        with open(cfg_file_path, 'r', encoding='utf-8') as f:
            cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
        cfg_reader = CfgReader(cfg)
        leaf.cfg = cfg_reader.find_command('sentinel', 'automation-rule', cmd_name)

        client = CLIAtomicClient({
            "plane": PlaneEnum.Mgmt,
            "name": PlaneEnum.http_client(PlaneEnum.Mgmt),
            "registeredName": PlaneEnum.http_client(PlaneEnum.Mgmt),
        })
        data = tmpl.render(
            leaf=AzCommandGenerator(leaf, client)
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "output", "sentinel", "automation_rule", f"_{cmd_name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

