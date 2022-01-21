import json
import logging
import os
import shutil
from datetime import datetime

from command.model.configuration import CMDConfiguration, CMDCommandGroup, CMDHelp
from command.model.editor import CMDEditorWorkspace, CMDCommandTreeNode, CMDCommandTreeLeaf
from utils import exceptions
from utils.base64 import b64encode_str
from utils.config import Config

logger = logging.getLogger('backend')


class WorkspaceManager:
    COMMAND_TREE_ROOT_NAME = "aaz"

    @classmethod
    def list_workspaces(cls):
        workspaces = []
        if not os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER):
            return workspaces

        for name in os.listdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            if not os.path.isdir(os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)):
                continue
            manager = cls(name)
            if os.path.exists(manager.path) and os.path.isfile(manager.path):
                workspaces.append({
                    "name": name,
                    "folder": manager.folder,
                    "updated": os.path.getmtime(manager.path)
                })
        return workspaces

    @classmethod
    def new(cls, name, plane):
        manager = cls(name)
        if os.path.exists(manager.path):
            raise exceptions.ResourceConflict(f"Workspace conflict: Workspace json file path exists: {manager.path}")
        manager.ws = CMDEditorWorkspace({
            "name": name,
            "plane": plane,
            "version": datetime.utcnow(),
            "commandTree": {
                "name": cls.COMMAND_TREE_ROOT_NAME,
            }
        })
        return manager

    def __init__(self, name):
        self.name = name
        if os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER) and not os.path.isdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            raise ValueError(
                f"Invalid AAZ_DEV_WORKSPACE_FOLDER: Expect a folder path: {Config.AAZ_DEV_WORKSPACE_FOLDER}")
        self.folder = os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)
        if os.path.exists(self.folder) and not os.path.isdir(self.folder):
            raise ValueError(f"Invalid workspace folder: Expect a folder path: {self.folder}")
        self.path = os.path.join(self.folder, 'ws.json')

        self.ws = None
        self._modified_cfgs = {}

    def load(self):
        # TODO: handle exception
        if not os.path.exists(self.path) or not os.path.isfile(self.path):
            raise exceptions.ResourceNotFind(f"Workspace json file not exist: {self.path}")
        with open(self.path, 'r') as f:
            data = json.load(f)
            self.ws = CMDEditorWorkspace(raw_data=data)
        self._modified_cfgs = {}

    def delete(self):
        if os.path.exists(self.path):
            # make sure ws.json exist in folder
            if not os.path.isfile(self.path):
                raise exceptions.ResourceConflict(f"Workspace conflict: Is not file path: {self.path}")
            shutil.rmtree(self.folder)  # remove the whole folder
            return True
        return False

    def save(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        update_files = []
        remove_folders = []
        used_resources = set()
        for resource_id, cfg in self._modified_cfgs.items():
            if cfg is None:
                assert resource_id not in used_resources
                remove_folders.append(self.get_resource_cfg_folder(resource_id))
                used_resources.add(resource_id)
            elif isinstance(cfg, CMDConfiguration):
                cfg.resources = sorted(cfg.resources, key=lambda r: r.id)
                main_resource = cfg.resources[0]
                update_files.append((
                    self.get_resource_cfg_path(main_resource.id),
                    json.dumps(cfg.to_primitive(), ensure_ascii=False)))
                assert main_resource.id not in used_resources
                used_resources.add(main_resource.id)
                for resource in cfg.resources[1:]:
                    assert resource.version == main_resource.version
                    update_files.append((
                        self.get_resource_cfg_path(resource.id),
                        json.dumps({"$ref": main_resource.id}, ensure_ascii=False)))
                    assert resource.id not in used_resources
                    used_resources.add(resource.id)
        for resource_id in self._modified_cfgs:
            assert resource_id in used_resources

        # verify ws timestamps
        # TODO: add write lock for path file
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                data = json.load(f)
                pre_ws = CMDEditorWorkspace(data)
            if pre_ws.version != self.ws.version:
                raise exceptions.InvalidAPIUsage(f"Workspace Changed after: {self.ws.version}")

        self.ws.version = datetime.utcnow()
        with open(self.path, 'w') as f:
            data = json.dumps(self.ws.to_primitive(), ensure_ascii=False)
            f.write(data)

        for folder in remove_folders:
            shutil.rmtree(folder)

        for file_name, data in update_files:
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, 'w') as f:
                f.write(data)

        self._modified_cfgs = {}

    def find_command_tree_node(self, *node_names):
        node = self.ws.command_tree
        idx = 0
        while idx < len(node_names):
            name = node_names[idx]
            if not node.command_groups or name not in node.command_groups:
                return None
            node = node.command_groups[name]
            idx += 1
        return node

    def find_command_tree_leaf(self, *leaf_names):
        if len(leaf_names) < 1:
            raise exceptions.InvalidAPIUsage(f"Invalid command name: '{' '.join(leaf_names)}'")

        node = self.find_command_tree_node(*leaf_names[:-1])
        if not node:
            return None
        name = leaf_names[-1]
        if name not in node.commands:
            return None
        leaf = node.commands[name]
        return leaf

    def iter_command_tree_nodes(self, *root_node_names):
        root = self.find_command_tree_node(*root_node_names)
        if root:
            nodes = [root]  # add root node
            i = 0
            while i < len(nodes):
                for node in (nodes[i].command_groups or {}).values():
                    nodes.append(node)
                    yield node
                i += 1

    def iter_command_tree_leaves(self, *root_node_names):
        for node in self.iter_command_tree_nodes(*root_node_names):
            for leaf in (node.commands or {}).values():
                yield leaf

    def create_command_tree_nodes(self, *node_names):
        node = self.ws.command_tree
        idx = 0
        while idx < len(node_names):
            name = node_names[idx]
            if not node.command_groups or name not in node.command_groups:
                if not node.command_groups:
                    node.command_groups = {}
                node.command_groups[name] = CMDCommandTreeNode({
                    "name": " ".join(node_names[:idx+1]),
                    "stage": node.stage,
                })
            node = node.command_groups[name]
            idx += 1
        return node

    def delete_command_tree_node(self, *node_names):
        for _ in self.iter_command_tree_nodes(*node_names):
            raise exceptions.ResourceConflict("Cannot delete command group with commands")
        parent = self.find_command_tree_node(*node_names[:-1])
        name = node_names[-1]
        if not parent or not parent.command_groups or name not in parent.command_groups:
            return False
        del parent.command_groups[name]
        if not parent.command_groups:
            parent.command_groups = None
        return True

    def check_resource_exist(self, resource_id, *root_node_names):
        for leaf in self.iter_command_tree_leaves(*root_node_names):
            for resource in leaf.resources:
                if resource.id == resource_id:
                    return True
        return False

    def add_resource_cfg(self, cfg):
        cfg.resources = sorted(cfg.resources, key=lambda r: r.id)
        main_resource = cfg.resources[0]
        for resource in cfg.resources[1:]:
            self._modified_cfgs[resource.id] = {
                "$ref": main_resource.id
            }
        self._modified_cfgs[main_resource.id] = cfg

        # update command tree
        groups = [(cfg.command_group.name.split(" "), cfg.command_group)]
        idx = 0
        while idx < len(groups):
            node_names, command_group = groups[idx]
            assert isinstance(command_group, CMDCommandGroup)
            node = self.create_command_tree_nodes(*node_names)
            if command_group.commands:
                for command in command_group.commands:
                    if node.commands is None:
                        node.commands = {}
                    assert command.name not in node.commands
                    node.commands[command.name] = CMDCommandTreeLeaf({
                        "name": f'{node.name} {command.name}',
                        "stage": node.stage,
                        "help": command.help.to_primitive(),
                        "version": command.version,
                        "resources": [r.to_primitive() for r in command.resources]
                    })

            if command_group.command_groups:
                for group in command_group.command_groups:
                    groups.append(([*node_names, *group.name.split(" ")], group))
            idx += 1

    def remove_resource_cfg(self, cfg):
        for resource in cfg.resources:
            self._modified_cfgs[resource.id] = None

        # update command tree
        groups = [(cfg.command_group.name.split(" "), cfg.command_group)]
        idx = 0
        while idx < len(groups):
            node_names, command_group = groups[idx]
            assert isinstance(command_group, CMDCommandGroup)
            node = self.find_command_tree_node(*node_names)
            if command_group.commands:
                for command in command_group.commands:
                    if command.name in node.commands:
                        del node.commands[command.name]

            if command_group.command_groups:
                for group in command_group.command_groups:
                    groups.append(([*node_names, *group.name.split(" ")], group))

            idx += 1

    def get_resource_cfg_folder(self, resource_id):
        return os.path.join(self.folder, "Resources", b64encode_str(resource_id))

    def get_resource_cfg_path(self, resource_id):
        return os.path.join(self.get_resource_cfg_folder(resource_id), f"cfg.json")

    def load_resource_cfg(self, resource_id, version):
        if resource_id in self._modified_cfgs:
            # load from modified dict
            return self._modified_cfgs[resource_id]

        path = self.get_resource_cfg_path(resource_id)
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            if '$ref' in data:
                ref_resource_id = data['$ref']
                if ref_resource_id in self._modified_cfgs:
                    # load from modified dict
                    return self._modified_cfgs[ref_resource_id]
                path = self.get_resource_cfg_path(ref_resource_id)
                with open(path, 'r') as f:
                    data = json.load(f)
            cfg = CMDConfiguration(data)
            for resource in cfg.resources:
                if resource.id == resource_id and resource.version != version:
                    raise ValueError(
                        f"Resource version not match error: {resource_id} : {version} != {resource.version}")
            return cfg
        except Exception as e:
            logger.error(f"load workspace resource cfg failed: {e}: {self.name} {resource_id} {version}")
            return None

    def load_command_cfg(self, cmd):
        return self.load_resource_cfg(cmd.resources[0].id, cmd.resources[0].version)

    def find_command_in_cfg(self, cfg, command_name):
        assert isinstance(cfg, CMDConfiguration)
        name = command_name
        prefix = cfg.command_group.name + " "
        if not name.startswith(prefix):
            return None

        name = name[len(prefix):]
        command_group = cfg.command_group
        while " " in name:
            if not command_group.command_groups:
                return None
            find = False
            for sub_group in command_group.command_groups:
                prefix = sub_group.name + " "
                if name.startswith(prefix):
                    name = name[len(prefix):]
                    command_group = sub_group
                    find = True
            if not find:
                return None
        for command in command_group.commands:
            if command.name == name:
                return command
        return None

    def update_command_tree_node_help(self, node, help):
        if isinstance(help, CMDHelp):
            help = help.to_primitive()
        else:
            assert isinstance(help, dict)
        node.help = CMDHelp(help)

    def update_command_tree_node_stage(self, node, stage):
        if node.stage == stage:
            return
        node.stage = stage
        if node.command_groups:
            for sub_node in node.command_groups.values():
                self.update_command_tree_node_stage(sub_node, stage)
        if node.commands:
            for leaf in node.commands.values():
                self.update_command_tree_leaf_stage(leaf, stage)

    def update_command_tree_leaf_stage(self, leaf, stage):
        if leaf.stage == stage:
            return
        cfg = self.load_command_cfg(leaf)

        command = self.find_command_in_cfg(cfg, leaf.name)
        if command is None:
            raise exceptions.ResourceConflict(f"Cannot find definition for command '{leaf.name}'")
        leaf.stage = stage
        command.stage = stage

        # update cfg into modified cfg
        cfg.resources = sorted(cfg.resources, key=lambda r: r.id)
        main_resource = cfg.resources[0]
        for resource in cfg.resources[1:]:
            self._modified_cfgs[resource.id] = {
                "$ref": main_resource.id
            }
        self._modified_cfgs[main_resource.id] = cfg

