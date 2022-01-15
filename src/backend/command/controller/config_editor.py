from command.model.editor import CMDEditorWorkspace, CMDCommandTreeNode, CMDCommandTreeLeaf
from command.model.configuration import CMDConfiguration
from swagger.controller.specs_manager import SwaggerSpecsManager
from swagger.controller.command_generator import CommandGenerator
from .specs_manager import AAZSpecsManager
from utils.config import Config
import os
import json
from utils import exceptions
from utils.base64 import b64encode_str, b64decode_str
from datetime import datetime
import shutil
import logging

logger = logging.getLogger('backend')


class ConfigEditorWorkspaceManager:

    COMMAND_TREE_ROOT_NAME = "aaz"

    @staticmethod
    def get_ws_folder(name):
        if os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER) and not os.path.isdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            raise ValueError(
                f"Invalid AAZ_DEV_WORKSPACE_FOLDER: Expect a folder path: {Config.AAZ_DEV_WORKSPACE_FOLDER}")
        ws_folder = os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)
        return ws_folder

    @classmethod
    def get_ws_json_file_path(cls, name):
        ws_folder = cls.get_ws_folder(name)
        if os.path.exists(ws_folder) and not os.path.isdir(ws_folder):
            raise ValueError(f"Invalid workspace folder: Expect a folder path: {ws_folder}")
        return os.path.join(ws_folder, 'ws.json')

    @classmethod
    def list_workspaces(cls):
        workspaces = []
        if not os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER):
            return workspaces

        for name in os.listdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            if not os.path.isdir(os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)):
                continue
            path = cls.get_ws_json_file_path(name)
            if os.path.exists(path) and os.path.isfile(path):
                workspaces.append({
                    "name": name,
                    "file": path,
                    "updated": os.path.getmtime(path)
                })
        return workspaces

    @classmethod
    def load_workspace(cls, name):
        # TODO: handle exceptions
        path = cls.get_ws_json_file_path(name)
        if not os.path.exists(path) or not os.path.isfile(path):
            raise exceptions.ResourceNotFind(f"Workspace json file not exist: {path}")
        with open(path, 'r') as f:
            data = json.load(f)
            ws = CMDEditorWorkspace(raw_data=data)
        return ws

    @classmethod
    def save_workspace(cls, name, ws):
        folder = cls.get_ws_folder(name)
        path = cls.get_ws_json_file_path(name)
        if not os.path.exists(folder):
            os.makedirs(folder)
        ws_data = ws.to_primitive()
        with open(path, 'w') as f:
            json.dump(ws_data, f, ensure_ascii=False)

    @classmethod
    def delete_workspace(cls, name):
        folder = cls.get_ws_folder(name)
        path = cls.get_ws_json_file_path(name)
        if os.path.exists(path):
            # make sure ws.json exist in folder
            if not os.path.isfile(path):
                raise exceptions.ResourceConflict(f"Workspace conflict: Is not file path: {path}")
            shutil.rmtree(folder)   # remove the whole folder
            return True
        return False

    @classmethod
    def create_workspace(cls, name, plane):
        path = cls.get_ws_json_file_path(name)
        if os.path.exists(path):
            raise exceptions.ResourceConflict(f"Workspace conflict: Workspace json file path exists: {path}")
        ws = CMDEditorWorkspace({
            "name": name,
            "plane": plane,
            "version": datetime.utcnow(),
            "commandTree": {
                "name": cls.COMMAND_TREE_ROOT_NAME,
            }
        })
        cls.save_workspace(name, ws)
        return ws

    @classmethod
    def update_workspace(cls, name, ws):
        pre_ws = cls.load_workspace(name)
        if pre_ws.version != ws.version:
            raise exceptions.ResourceConflict(
                f"Workspace conflict: Version control timestamp not match: expect {pre_ws.version} get {ws.version}")
        ws.version = datetime.utcnow()
        cls.save_workspace(name, ws)
        return ws

    @classmethod
    def get_ws_resource_cfg_json_file_path(cls, name, resource_id, version):
        return os.path.join(cls.get_ws_folder(name), "Resources", b64encode_str(resource_id), f"{version}.json")

    @classmethod
    def load_ws_resource_cfg(cls, name, resource_id, version):
        path = cls.get_ws_resource_cfg_json_file_path(name, resource_id, version)
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            if '$ref' in data:
                path = cls.get_ws_resource_cfg_json_file_path(name, data['$ref'], version)
                with open(path, 'r') as f:
                    data = json.load(f)
            return CMDConfiguration(data)
        except Exception as e:
            logger.error(f"load workspace resource cfg failed: {e}: {name} {resource_id} {version}")
            return None


class WorkspaceEditor:

    def __init__(self, name):
        self.ws = ConfigEditorWorkspaceManager.load_workspace(name)

        self.swagger_specs = SwaggerSpecsManager()
        self.swagger_command_generator = CommandGenerator()
        self.aaz_specs = AAZSpecsManager()
        self.modified_cfgs = {}

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
            nodes = [root]   # add root node
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
                    "name": name,
                    "stage": node.stage,
                })
            node = node.command_groups[name]
            idx += 1
        return node

    def check_resource_exist(self, resource_id, *root_node_names):
        for leaf in self.ws.command_tree_leaves(*root_node_names):
            for resource in leaf.resources:
                if resource.id == resource_id:
                    return True
        return False

    def add_resources_by_swagger(self, mod_names, version, resource_ids, *root_node_names):
        root_node = self.find_command_tree_node(*root_node_names)
        if not root_node:
            raise exceptions.InvalidAPIUsage(f"Command Group not exist: '{' '.join(root_node_names)}'")

        swagger_resources = []
        for resource_id in set(resource_ids):
            if self.check_resource_exist(resource_id):
                raise exceptions.InvalidAPIUsage(f"Resource already added in Workspace: {resource_id}")
            swagger_resources.append(self.swagger_specs.get_resource_in_version(self.ws.plane, mod_names, resource_id, version))

        self.swagger_command_generator.load_resources(swagger_resources)

        # generate cfg command group from swagger command generator
        cfgs = []
        for resource in swagger_resources:
            cfg = CMDConfiguration()
            cfg.plane = self.ws.plane
            cfg.resources = [resource.to_cmd()]
            cfg.command_group = self.swagger_command_generator.create_draft_command_group(resource)
            assert not cfg.command_group.command_groups, "The logic to support sub command groups is not supported"
            cfgs.append(cfg)

        if len(root_node_names) > 0:
            # rename cfg command group by applying root_node_names prefix

            # calculate common cg name prefix
            common_cg_name_prefix = None
            cg_names = []
            for cfg in cfgs:
                cg_name = cfg.command_group.name.split(" ")
                if common_cg_name_prefix is None:
                    common_cg_name_prefix = cg_name
                    continue
                cg_names.append(cg_name)

            # should also include the existing commands
            for leaf in (root_node.commands or []):
                for cmd_r in leaf.resources:
                    # get the cg_name of existing resource from generator
                    try:
                        resource = self.swagger_specs.get_resource_in_version(
                            plane=self.ws.plane, mod_names=mod_names, resource_id=cmd_r.id, version=version)
                        cg_name = self.swagger_command_generator.generate_command_group_name_by_resource(
                            resource_path=resource.path, rp_name=resource.resource_provider.name)
                    except Exception:
                        # cannot find match resource of resource_id with current mod_names and version
                        cg_name = self.swagger_command_generator.generate_command_group_name_by_resource(
                            resource_path=cmd_r.swagger_path, rp_name=cmd_r.rp_name)
                    cg_name = cg_name.split(" ")
                    cg_names.append(cg_name)

            for cg_name in cg_names:
                if len(cg_name) < len(common_cg_name_prefix):
                    common_cg_name_prefix = common_cg_name_prefix[:len(cg_name)]
                for i, k in enumerate(cg_name):
                    if i >= len(common_cg_name_prefix):
                        break
                    if common_cg_name_prefix[i] != k:
                        common_cg_name_prefix = common_cg_name_prefix[:i]
                        break

            # replace common_cg_name_prefix by root_node_names
            for cfg in cfgs:
                cg_name = cfg.command_group.name.split(" ")
                cg_name = [*root_node_names, *cg_name[len(common_cg_name_prefix):]]
                cfg.command_group.name = " ".join(cg_name)

        for cfg in cfgs:
            node_names = cfg.command_group.name.split(" ")
            node = self.find_command_tree_node(*node_names)
            if not node:
                self.add_resource_cfg(cfg)
                continue

            # some cfg maybe merged into existing cfg
            merged = False
            for command in cfg.command_group.commands:
                if command.name in node.commands:
                    ws_command = node.commands[command.name]
                    if ws_command.version == command.version and self.can_merge_commands(ws_command, command):
                        # TODO: self.merge_resources(ws_command.resources, command.resources)
                        merged = True
                        break
                    # resource cannot merge, so generation a unique command name
                    command.name = self.generate_unique_command_name(*node_names, command_name=command.name)

            if not merged:
                self.add_resource_cfg(cfg)

    def add_resource_cfg(self, cfg):
        # add cfg into modified_cfgs
        main_resource = cfg.resources[0]
        for resource in cfg.resources[1:]:
            self.modified_cfgs[resource.id] = {
                "$ref": main_resource.id
            }
        self.modified_cfgs[main_resource.id] = cfg

        # update command tree
        node_names = cfg.command_group.name.split(" ")
        node = self.create_command_tree_nodes(*node_names)
        for command in cfg.command_group.commands:
            assert command.name not in node.commands
            node.commands[command.name] = CMDCommandTreeLeaf({
                "name": command.name,
                "stage": node.stage,
                "help": command.help.to_primitive(),
                "version": command.version.to_primitive(),
                "resources": [r.to_primitive() for r in command.resources]
            })

    def can_merge_commands(self, cmd_1, cmd_2):
        # TODO:
        return False

    def merge_resources(self):
        # TODO:
        pass

    def generate_unique_command_name(self, *node_names, command_name):
        tree_node = self.find_command_tree_node(*node_names)
        if not tree_node or command_name not in tree_node.commands:
            return command_name
        idx = 1
        name = f"{command_name}_Untitled_{idx}"
        while name in tree_node.commands:
            idx += 1
            name = f"{command_name}_Untitled_{idx}"
        return name

    def add_resources_by_aaz(self, version, resource_ids):
        for resource_id in set(resource_ids):
            if self.check_resource_exist(resource_id):
                raise exceptions.InvalidAPIUsage(f"Resource already added in Workspace: {resource_id}")
        pass

    # def _load_cmd_config(self, config_path):
    #     # load command configuration from persistence layer
    #     return None
    #
    # def _fetch_config_path_by_resource_id(self, resource_id, v):
    #     # TODO: read from repo index
    #     return None
    #
    # def _fetch_config_path_by_cmd_name(self, cmd_name, v):
    #     # TODO: read from repo index
    #     return None
    #
    # def add_resource_by_cmd(self, cmd_name, v):
    #     config_path = self._fetch_config_path_by_cmd_name(cmd_name, v)
    #     cmd_config = self._load_cmd_config(config_path)
    #     # TODO:
    #
    # def add_resource_by_swagger(self, module, resource_id, v, inherent_v=None):
    #     # config_path = self._fetch_config_path_by_resource_id(resource_id, v)
    #     resources = [
    #         CMDResource({
    #             "id": resource_id,
    #             "version": v
    #         })
    #     ]
    #     if inherent_v:
    #         config_path = self._fetch_config_path_by_resource_id(resource_id, inherent_v)
    #         assert config_path is not None, "config not exist error"
    #         inherent_config = self._load_cmd_config(config_path)    # type: CMDConfiguration
    #         resources = inherent_config.resources   # use inherent configuration resources
    #




