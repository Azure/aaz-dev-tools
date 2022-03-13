import json
import os
import re
import shutil

from command.model.configuration import CMDConfiguration, CMDHelp, CMDCommandExample, XMLSerializer
from utils.base64 import b64encode_str
from utils.config import Config
from command.model.specs import CMDSpecsCommandTree, CMDSpecsCommandGroup, CMDSpecsCommand, CMDSpecsCommandVersion, CMDSpecsResource
from command.templates import get_templates
from utils import exceptions
from .cfg_reader import CfgReader
from .cfg_validator import CfgValidator


class AAZSpecsManager:
    COMMAND_TREE_ROOT_NAME = "aaz"

    REFERENCE_LINE = re.compile(r"^Reference\s*\[(.*) (.*)]\((.*)\)\s*$")

    def __init__(self):
        if not Config.AAZ_PATH or not os.path.exists(Config.AAZ_PATH) or not os.path.isdir(Config.AAZ_PATH):
            raise ValueError(f"aaz repo path is invalid: '{Config.AAZ_PATH}'")

        self.folder = Config.AAZ_PATH
        self.resources_folder = os.path.join(self.folder, "Resources")
        self.commands_folder = os.path.join(self.folder, "Commands")
        self.tree = None
        self._modified_command_groups = set()
        self._modified_commands = set()
        self._modified_resource_cfgs = {}

        tree_path = self.get_tree_file_path()
        if not os.path.exists(tree_path):
            self.tree = CMDSpecsCommandTree()
            self.tree.root = CMDSpecsCommandGroup({
                "names": [self.COMMAND_TREE_ROOT_NAME]
            })
            return

        if not os.path.isfile(tree_path):
            raise ValueError(f"Invalid Command Tree file path, expect a file: {tree_path}")

        with open(tree_path, 'r') as f:
            data = json.load(f)
            self.tree = CMDSpecsCommandTree(data)

    # Commands folder
    def get_tree_file_path(self):
        return os.path.join(self.commands_folder, "tree.json")

    def get_command_group_folder(self, *cg_names):
        # support len(cg_names) == 0
        return os.path.join(self.commands_folder, *cg_names)

    def get_command_group_readme_path(self, *cg_names):
        # when len(cg_names) == 0, the path will be the Commands/readme.md
        return os.path.join(self.get_command_group_folder(*cg_names), "readme.md")

    def get_command_readme_path(self, *cmd_names):
        if len(cmd_names) <= 1:
            raise ValueError(f"Invalid command names: '{' '.join(cmd_names)}'")
        return os.path.join(self.get_command_group_folder(*cmd_names[:-1]), f"_{cmd_names[-1]}.md")

    # resources
    def get_resource_plane_folder(self, plane):
        return os.path.join(self.resources_folder, plane)

    def get_resource_cfg_folder(self, plane, resource_id):
        return os.path.join(self.get_resource_plane_folder(plane), b64encode_str(resource_id))

    def get_resource_cfg_file_path(self, plane, resource_id, version):
        return os.path.join(self.get_resource_cfg_folder(plane, resource_id), f"{version}.xml")

    def get_resource_cfg_ref_file_path(self, plane, resource_id, version):
        return os.path.join(self.get_resource_cfg_folder(plane, resource_id), f"{version}.md")

    # Command Tree
    def find_command_group(self, *cg_names):
        node = self.tree.root
        idx = 0
        while idx < len(cg_names):
            name = cg_names[idx]
            if not node.command_groups or name not in node.command_groups:
                return None
            node = node.command_groups[name]
            idx += 1
        return node

    def find_command(self, *cmd_names):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid command name: '{' '.join(cmd_names)}'")

        node = self.find_command_group(*cmd_names[:-1])
        if not node:
            return None
        name = cmd_names[-1]
        if not node.commands or name not in node.commands:
            return None
        leaf = node.commands[name]
        return leaf

    def iter_command_groups(self, *root_cg_names):
        root = self.find_command_group(*root_cg_names)
        if root:
            nodes = [root]
            i = 0
            while i < len(nodes):
                yield nodes[i]
                for node in (nodes[i].command_groups or {}).values():
                    nodes.append(node)
                i += 1

    def iter_commands(self, *root_node_names):
        for node in self.iter_command_groups(*root_node_names):
            for leaf in (node.commands or {}).values():
                yield leaf

    def load_resource_cfg_reader(self, plane, resource_id, version):
        key = (plane, resource_id, version)
        if key in self._modified_resource_cfgs:
            return self._modified_resource_cfgs[key]

        path = self.get_resource_cfg_file_path(plane, resource_id, version)
        if not os.path.exists(path):
            ref_path = self.get_resource_cfg_ref_file_path(plane, resource_id, version)
            if not os.path.exists(ref_path):
                return None
            path = None
            with open(ref_path, 'r') as f:
                for line in f.readlines():
                    match = self.REFERENCE_LINE.fullmatch(line)
                    if match:
                        resource_id, version = match[1], match[2]
                        path = self.get_resource_cfg_file_path(plane, resource_id, version)
                        break
            if not path or not os.path.exists(path):
                raise ValueError(f"Invalid reference file: {ref_path}")

        if not os.path.isfile(path):
            raise ValueError(f"Invalid file path: {path}")

        with open(path, 'r') as f:
            cfg = XMLSerializer(CMDConfiguration).from_xml(f.read())
        return CfgReader(cfg)

    def load_resource_cfg_reader_by_command_with_version(self, cmd, version):
        if not isinstance(version, CMDSpecsCommandVersion):
            assert isinstance(version, str)
            version_name = version
            version = None
            for v in cmd.versions or []:
                if v.name == version_name:
                    version = v
                    break
        if not version:
            return None
        resource = version.resources[0]
        return self.load_resource_cfg_reader(resource.plane, resource.id, resource.version)

    # command tree
    def create_command_group(self, *cg_names):
        if len(cg_names) < 1:
            raise exceptions.InvalidAPIUsage(f"Invalid Command Group name: '{' '.join(cg_names)}'")
        node = self.tree.root
        idx = 0
        while idx < len(cg_names):
            name = cg_names[idx]
            if node.commands and name in node.commands:
                raise exceptions.InvalidAPIUsage(f"Invalid Command Group name: conflict with Command name: "
                                                 f"'{' '.join(cg_names[:idx+1])}'")
            if not node.command_groups or name not in node.command_groups:
                if not node.command_groups:
                    node.command_groups = {}
                names = [*cg_names[:idx+1]]
                node.command_groups[name] = CMDSpecsCommandGroup({
                    "names": names
                })
                self._modified_command_groups.add(cg_names[:idx+1])
            node = node.command_groups[name]
            idx += 1
        return node

    def update_command_group_by_ws(self, ws_node):
        command_group = self.create_command_group(*ws_node.names)
        if ws_node.help:
            if not command_group.help:
                command_group.help = CMDHelp()
            if ws_node.help.short:
                command_group.help.short = ws_node.help.short
            if ws_node.help.lines:
                command_group.help.lines = [*ws_node.help.lines]
        self._modified_command_groups.add(tuple([*ws_node.names]))
        return command_group

    def delete_command_group(self, *cg_names):
        for _ in self.iter_commands(*cg_names):
            raise exceptions.ResourceConflict("Cannot delete command group with commands")
        parent = self.find_command_group(*cg_names[:-1])
        name = cg_names[-1]
        if not parent or not parent.command_groups or name not in parent.command_groups:
            return False
        del parent.command_groups[name]
        if not parent.command_groups:
            parent.command_groups = None

        self._modified_command_groups.add(cg_names)
        return True

    def create_command(self, *cmd_names):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid Command name: '{' '.join(cmd_names)}'")
        node = self.create_command_group(*cmd_names[:-1])
        name = cmd_names[-1]
        if node.command_groups and name in node.command_groups:
            raise exceptions.InvalidAPIUsage(f"Invalid Command name: conflict with Command Group name: "
                                             f"'{' '.join(cmd_names)}'")
        if not node.commands:
            node.commands = {}
        elif name in node.commands:
            return node.commands[name]

        command = CMDSpecsCommand()
        command.names = list(cmd_names)
        node.commands[name] = command
        self._modified_commands.add(cmd_names)

        return command

    def delete_command(self, *cmd_names):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid Command name: '{' '.join(cmd_names)}'")
        parent = self.find_command_group(*cmd_names[:-1])
        name = cmd_names[-1]
        if not parent or not parent.commands or name not in parent.commands:
            return False
        command = parent.commands[name]
        if command.versions:
            raise exceptions.ResourceConflict("Cannot delete command with versions")
        del parent.commands[name]
        if not parent.commands:
            parent.commands = None

        self._modified_commands.add(cmd_names)
        return True

    def delete_command_version(self, *cmd_names, version):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid Command name: '{' '.join(cmd_names)}'")
        command = self.find_command(*cmd_names)
        if not command or not command.versions:
            return False
        match_idx = None
        for idx, v in enumerate(command.versions):
            if v.name == version:
                match_idx = idx
                break
        if not match_idx:
            return False

        command.versions = command.versions[:match_idx] + command.versions[match_idx+1:]

        self._modified_commands.add(cmd_names)
        return True

    def update_command_version(self, *cmd_names, plane, cfg_cmd):
        command = self.create_command(*cmd_names)

        version = None
        for v in (command.versions or []):
            if v.name == cfg_cmd.version:
                version = v
                break

        if not version:
            version = CMDSpecsCommandVersion()
            version.name = cfg_cmd.version
            if not command.versions:
                command.versions = []
            command.versions.append(version)

        # update version resources
        version.resources = []
        for r in cfg_cmd.resources:
            resource = CMDSpecsResource()
            resource.plane = plane
            resource.id = r.id
            resource.version = r.version
            version.resources.append(resource)

        self._modified_commands.add(cmd_names)

    def _remove_cfg(self, cfg):
        cfg_reader = CfgReader(cfg)

        # update resource cfg
        for resource in cfg_reader.resources:
            key = (cfg.plane, resource.id, resource.version)
            self._modified_resource_cfgs[key] = None

        # update command tree
        for cmd_names, cmd in cfg_reader.iter_commands():
            self.delete_command_version(*cmd_names, version=cmd.version)

    def update_resource_cfg(self, cfg):
        cfg_reader = CfgReader(cfg=cfg)

        cfg_verifier = CfgValidator(cfg_reader)
        # TODO: implement verify configuration
        cfg_verifier.verify()

        # remove previous cfg
        for resource in cfg_reader.resources:
            pre_cfg_reader = self.load_resource_cfg_reader(cfg.plane, resource_id=resource.id, version=resource.version)
            if pre_cfg_reader:
                self._remove_cfg(cfg)

        # add new command version
        for cmd_names, cmd in cfg_reader.iter_commands():
            self.update_command_version(*cmd_names, plane=cfg.plane, cfg_cmd=cmd)

        for resource in cfg_reader.resources:
            key = (cfg.plane, resource.id, resource.version)
            self._modified_resource_cfgs[key] = cfg

    def update_command_by_ws(self, ws_leaf):
        command = self.find_command(*ws_leaf.names)
        if not command:
            # make sure the command exist, if command not exist, then run update_resource_cfg first
            raise exceptions.InvalidAPIUsage(f"Command isn't exist: '{' '.join(ws_leaf.names)}'")

        cmd_version = None
        for v in (command.versions or []):
            if v.name == ws_leaf.version:
                cmd_version = v
                break
        if not cmd_version:
            raise exceptions.InvalidAPIUsage(f"Command in version isn't exist: "
                                             f"'{' '.join(ws_leaf.names)}' '{ws_leaf.version}'")

        # compare resources
        leaf_resources = {(r.id, r.version) for r in ws_leaf.resources}
        cmd_version_resources = {(r.id, r.version) for r in cmd_version.resources}
        if leaf_resources != cmd_version_resources:
            raise exceptions.InvalidAPIUsage(f"The resources in version don't match the resources of workspace leaf: "
                                             f"{leaf_resources} != {cmd_version_resources}")

        # update stage
        cmd_version.stage = ws_leaf.stage

        # update examples
        if ws_leaf.examples:
            cmd_version.examples = [CMDCommandExample(e.to_primitive()) for e in ws_leaf.examples]

        # update help
        if ws_leaf.help:
            if not command.help:
                command.help = CMDHelp()
            if ws_leaf.help.short:
                command.help.short = ws_leaf.help.short
            if ws_leaf.help.lines:
                command.help.lines = [*ws_leaf.help.lines]

        self._modified_commands.add(tuple(command.names))
        return command

    def verify_command_tree(self):
        details = {}
        for group in self.iter_command_groups():
            if group == self.tree.root:
                continue
            if not group.help or not group.help.short:
                details[' '.join(group.names)] = {
                    'type': 'group',
                    'help': "Miss short summery."
                }

        for cmd in self.iter_commands():
            if not cmd.help or not cmd.help.short:
                details[' '.join(cmd.names)] = {
                    'type': 'command',
                    'help': "Miss short summery."
                }
        if details:
            raise exceptions.VerificationError(message="Invalid Command Tree", details=details)

    def save(self):
        self.verify_command_tree()

        remove_files = []
        remove_folders = []
        update_files = {}
        command_groups = set()

        tree_path = self.get_tree_file_path()
        update_files[tree_path] = json.dumps(self.tree.to_primitive(), indent=2, sort_keys=True)

        # command
        for cmd_names in sorted(self._modified_commands):
            cmd = self.find_command(*cmd_names)
            file_path = self.get_command_readme_path(*cmd_names)
            if not cmd:
                # remove command file
                remove_files.append(file_path)
            else:
                update_files[file_path] = self.render_command_readme(cmd)

            command_groups.add(tuple(cmd_names[:-1]))

        for cg_names in sorted(self._modified_command_groups):
            command_groups.add(tuple(cg_names))
            command_groups.add(tuple(cg_names[:-1]))

        # command groups
        for cg_names in sorted(command_groups):
            cg = self.find_command_group(*cg_names)
            if not cg:
                # remove command group folder
                remove_folders.append(self.get_command_group_folder(*cg_names))
            else:
                # update command group readme
                file_path = self.get_command_group_readme_path(*cg_names)
                if cg == self.tree.root:
                    update_files[file_path] = self.render_command_tree_readme(self.tree)
                else:
                    update_files[file_path] = self.render_command_group_readme(cg)

        # cfg files
        for (plane, resource_id, version), cfg in self._modified_resource_cfgs.items():
            file_path = self.get_resource_cfg_file_path(plane, resource_id, version)
            ref_file_path = self.get_resource_cfg_ref_file_path(plane, resource_id, version)
            if not cfg:
                remove_files.append(file_path)
                remove_files.append(ref_file_path)
            else:
                main_resource = cfg.resources[0]
                if main_resource.id != resource_id or main_resource.version != version:
                    update_files[ref_file_path] = self.render_resource_ref_readme(
                        plane=cfg.plane, ref_resource_id=main_resource.id, ref_resource_version=main_resource.version)
                else:
                    update_files[file_path] = self.render_resource_cfg(cfg)

        for remove_file in remove_files:
            if os.path.exists(remove_file):
                os.remove(remove_file)

        for remove_folder in remove_folders:
            shutil.rmtree(remove_folder, ignore_errors=True)

        for file_path, data in update_files.items():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(data)

        self._modified_command_groups = set()
        self._modified_commands = set()
        self._modified_resource_cfgs = {}

    @staticmethod
    def render_command_readme(command):
        assert isinstance(command, CMDSpecsCommand)
        tmpl = get_templates()['command']
        return tmpl.render(command=command)

    @staticmethod
    def render_command_group_readme(command_group):
        assert isinstance(command_group, CMDSpecsCommandGroup)
        tmpl = get_templates()['group']
        return tmpl.render(group=command_group)

    @staticmethod
    def render_command_tree_readme(tree):
        assert isinstance(tree, CMDSpecsCommandTree)
        tmpl = get_templates()['tree']
        return tmpl.render(tree=tree)

    @staticmethod
    def render_resource_ref_readme(plane, ref_resource_id, ref_resource_version):
        ref_resource = CMDSpecsResource({
            "plane": plane,
            "id": ref_resource_id,
            "version": ref_resource_version
        })
        tmpl = get_templates()['resource_ref']
        return tmpl.render(ref_resource=ref_resource)

    @staticmethod
    def render_resource_cfg(cfg):
        return XMLSerializer(cfg).to_xml()
