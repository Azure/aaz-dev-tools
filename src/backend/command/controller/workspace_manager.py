import json
import logging
import os
import shutil
from datetime import datetime

from command.model.configuration import CMDHelp, CMDResource, CMDCommandExample
from command.model.editor import CMDEditorWorkspace, CMDCommandTreeNode, CMDCommandTreeLeaf
from swagger.controller.command_generator import CommandGenerator
from swagger.controller.specs_manager import SwaggerSpecsManager
from utils import exceptions
from utils.config import Config
from .specs_manager import AAZSpecsManager
from .workspace_cfg_editor import WorkspaceCfgEditor
from command.model.configuration import CMDStageField, CMDHelp, CMDResource, CMDCommandExample

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
                "names": [cls.COMMAND_TREE_ROOT_NAME],
            }
        })
        return manager

    def __init__(self, name):
        self.name = name
        if not Config.AAZ_DEV_WORKSPACE_FOLDER or os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER) and not os.path.isdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
            raise ValueError(
                f"Invalid AAZ_DEV_WORKSPACE_FOLDER: Expect a folder path: {Config.AAZ_DEV_WORKSPACE_FOLDER}")
        self.folder = os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)
        if os.path.exists(self.folder) and not os.path.isdir(self.folder):
            raise ValueError(f"Invalid workspace folder: Expect a folder path: {self.folder}")
        self.path = os.path.join(self.folder, 'ws.json')

        self.ws = None
        self._cfg_editors = {}
        self._reusable_leaves = {}

        self.aaz_specs = AAZSpecsManager()
        self.swagger_specs = SwaggerSpecsManager()
        self.swagger_command_generator = CommandGenerator()

    def load(self):
        # TODO: handle exception
        if not os.path.exists(self.path) or not os.path.isfile(self.path):
            raise exceptions.ResourceNotFind(f"Workspace json file not exist: {self.path}")
        with open(self.path, 'r') as f:
            data = json.load(f)
            self.ws = CMDEditorWorkspace(raw_data=data)

        self._cfg_editors = {}

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

        remove_folders = []
        update_files = []
        used_resources = set()
        for resource_id, cfg_editor in self._cfg_editors.items():
            if resource_id in used_resources:
                continue
            for r_id, data in cfg_editor.iter_cfg_files_data():
                assert r_id not in used_resources
                if data is None:
                    remove_folders.append(WorkspaceCfgEditor.get_cfg_folder(self.folder, r_id))
                else:
                    update_files.append((WorkspaceCfgEditor.get_cfg_path(self.folder, r_id), data))
                used_resources.add(r_id)
        assert set(self._cfg_editors.keys()) == used_resources

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

        self._cfg_editors = {}

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
        if not node.commands or name not in node.commands:
            return None
        leaf = node.commands[name]
        return leaf

    def iter_command_tree_nodes(self, *root_node_names):
        """ Including the root node
        """
        root = self.find_command_tree_node(*root_node_names)
        if root:
            nodes = [root]  # add root node
            i = 0
            while i < len(nodes):
                yield nodes[i]
                for node in (nodes[i].command_groups or {}).values():
                    nodes.append(node)
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
                aaz_node = self.aaz_specs.find_command_group(*node_names[:idx + 1])
                if aaz_node is not None:
                    new_node = CMDCommandTreeNode({
                        "names": node_names[:idx + 1],
                        "help": aaz_node.help.to_primitive()
                    })
                else:
                    new_node = CMDCommandTreeNode({
                        "names": node_names[:idx + 1],
                    })
                node.command_groups[name] = new_node
            node = node.command_groups[name]
            idx += 1
        return node

    def delete_command_tree_node(self, *node_names):
        for _ in self.iter_command_tree_leaves(*node_names):
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

    def add_cfg(self, cfg_editor):
        cfg_editor.deleted = False
        for resource in cfg_editor.resources:
            self._cfg_editors[resource.id] = cfg_editor

        # update command tree
        for cmd_names, command in cfg_editor.iter_commands():
            node = self.create_command_tree_nodes(*cmd_names[:-1])
            name = cmd_names[-1]
            if node.commands is None:
                node.commands = {}
            assert name not in node.commands
            if node.command_groups:
                assert name not in node.command_groups
            reusable_leaf = self._reusable_leaves.pop(tuple(cmd_names), None)
            if reusable_leaf:
                new_cmd = reusable_leaf

            else:
                aaz_leaf = self.aaz_specs.find_command(*cmd_names)
                if aaz_leaf:
                    new_cmd = CMDCommandTreeLeaf({
                        "names": [*cmd_names],
                        "stage": node.stage,
                        "help": aaz_leaf.help.to_primitive(),
                    })
                    for v in (aaz_leaf.versions or []):
                        if v.name == command.version:
                            new_cmd.stage = v.stage
                            if v.examples:
                                new_cmd.examples = [CMDCommandExample(example.to_primitive()) for example in v.examples]
                            break
                else:
                    new_cmd = CMDCommandTreeLeaf({
                        "names": [*cmd_names],
                        "stage": node.stage,
                        "help": {
                            "short": command.description or ""
                        },
                    })
            new_cmd.version = command.version
            new_cmd.resources = [CMDResource(r.to_primitive()) for r in command.resources]
            node.commands[name] = new_cmd

    def remove_cfg(self, cfg_editor):
        cfg_editor.deleted = True
        for resource in cfg_editor.resources:
            self._cfg_editors[resource.id] = cfg_editor

        # update command tree
        for cmd_names, _ in cfg_editor.iter_commands():
            node = self.find_command_tree_node(*cmd_names[:-1])
            name = cmd_names[-1]
            if node and node.commands and name in node.commands:
                # add into reusable leaves in case it's added in add_cfg again.
                self._reusable_leaves[tuple(cmd_names)] = node.commands.pop(name)

    def load_cfg_editor_by_resource(self, resource_id, version):
        if resource_id in self._cfg_editors:
            # load from modified dict
            return self._cfg_editors[resource_id]
        try:
            cfg_editor = WorkspaceCfgEditor.load_resource(self.folder, resource_id, version)
            for resource in cfg_editor.resources:
                self._cfg_editors[resource.id] = cfg_editor
            return cfg_editor
        except Exception as e:
            logger.error(f"load workspace resource cfg failed: {e}: {self.name} {resource_id} {version}")
            return None

    def load_cfg_editor_by_command(self, cmd):
        return self.load_cfg_editor_by_resource(cmd.resources[0].id, cmd.resources[0].version)

    def update_command_tree_node_help(self, *node_names, help):
        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceNotFind(f"Command Tree Node not found: '{' '.join(node_names)}'")

        if isinstance(help, CMDHelp):
            help = help.to_primitive()
        else:
            assert isinstance(help, dict)
        node.help = CMDHelp(help)
        return node

    def update_command_tree_leaf_help(self, *leaf_names, help):
        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(f"Command Tree leaf not found: '{' '.join(leaf_names)}'")

        if isinstance(help, CMDHelp):
            help = help.to_primitive()
        else:
            assert isinstance(help, dict)
        leaf.help = CMDHelp(help)
        return leaf

    def update_command_tree_node_stage(self, *node_names, stage):
        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceNotFind(f"Command Tree Node not found: '{' '.join(node_names)}'")

        if node.stage == stage:
            return
        node.stage = stage

        if node.command_groups:
            for sub_node_name in node.command_groups:
                self.update_command_tree_node_stage(*node_names, sub_node_name, stage=stage)

        if node.commands:
            for leaf_name in node.commands:
                self.update_command_tree_leaf_stage(*node_names, leaf_name, stage=stage)
        return node

    def update_command_tree_leaf_stage(self, *leaf_names, stage):
        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(f"Command Tree leaf not found: '{' '.join(leaf_names)}'")

        if leaf.stage == stage:
            return
        leaf.stage = stage
        return leaf

    def update_command_tree_leaf_examples(self, *leaf_names, examples):
        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(f"Command Tree leaf not found: '{' '.join(leaf_names)}'")
        if not examples:
            leaf.examples = None
        else:
            leaf.examples = []
            for example in examples:
                example = CMDCommandExample(example)
                try:
                    example.validate()
                except Exception as err:
                # if not example.get('name', None) or not isinstance(example['name'], str):
                    raise exceptions.InvalidAPIUsage(f"Invalid example data: {err}")
                leaf.examples.append(example)
        return leaf

    def rename_command_tree_node(self, *node_names, new_node_names):
        new_name = ' '.join(new_node_names)
        if not new_name:
            raise exceptions.InvalidAPIUsage(f"Invalid new command name: {new_name}")

        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceNotFind(f"Command Tree Node not found: '{' '.join(node_names)}'")

        if node.names == new_node_names:
            return

        parent = self.find_command_tree_node(*node.names[:-1])
        name = node.names[-1]
        if not parent or not parent.command_groups or name not in parent.command_groups or \
                node != parent.command_groups[name]:
            raise exceptions.ResourceConflict(f"Command Tree node not exist: '{' '.join(node.names)}'")

        self._pop_command_tree_node(parent, name)

        parent = self.create_command_tree_nodes(*new_node_names[:-1])
        return self._add_command_tree_node(parent, node, new_node_names[-1])

    def rename_command_tree_leaf(self, *leaf_names, new_leaf_names):
        new_name = ' '.join(new_leaf_names)
        if not new_name:
            raise exceptions.InvalidAPIUsage(f"Invalid new command name: {new_name}")

        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(f"Command Tree leaf not found: '{' '.join(leaf_names)}'")

        if leaf.names == new_leaf_names:
            return

        parent = self.find_command_tree_node(*leaf.names[:-1])
        name = leaf.names[-1]
        if not parent or not parent.commands or name not in parent.commands or leaf != parent.commands[name]:
            raise exceptions.ResourceConflict(f"Command Tree leaf not exist: '{' '.join(leaf.names)}")

        self._pop_command_tree_leaf(parent, name)

        parent = self.create_command_tree_nodes(*new_leaf_names[:-1])
        return self._add_command_tree_leaf(parent, leaf, new_leaf_names[-1])

    def generate_unique_name(self, *node_names, name):
        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceConflict(f"Command Tree node not exist: '{' '.join(node_names)}'")
        if (not node.commands or name not in node.commands) and (
                not node.command_groups or name not in node.command_groups):
            return name
        idx = 1
        new_name = f"{name}-untitled{idx}"
        while node.commands and new_name in node.commands or node.command_groups and new_name in node.command_groups:
            idx += 1
            new_name = f"{name}-untitled{idx}"
        return new_name

    def add_new_resources_by_swagger(self, mod_names, version, resources, *root_node_names):
        root_node = self.find_command_tree_node(*root_node_names)
        if not root_node:
            raise exceptions.InvalidAPIUsage(f"Command Group not exist: '{' '.join(root_node_names)}'")

        swagger_resources = []
        resource_options = []
        used_resource_ids = set()
        for r in resources:
            if r['id'] in used_resource_ids:
                continue
            if self.check_resource_exist(r['id']):
                raise exceptions.InvalidAPIUsage(f"Resource already added in Workspace: {r['id']}")
            swagger_resource = self.swagger_specs.get_resource_in_version(
                self.ws.plane, mod_names, r['id'], version)
            swagger_resources.append(swagger_resource)
            resource_options.append(r.get("options", {}))
            used_resource_ids.update(r['id'])

        self.swagger_command_generator.load_resources(swagger_resources)

        cfg_editors = []
        for resource, options in zip(swagger_resources, resource_options):
            command_group = self.swagger_command_generator.create_draft_command_group(resource, **options)
            assert not command_group.command_groups, "The logic to support sub command groups is not supported"
            cfg_editors.append(WorkspaceCfgEditor.new_cfg(
                plane=self.ws.plane,
                resources=[resource.to_cmd()],
                command_groups=[command_group]
            ))

        # TODO: apply the command name used in aaz specs

        if len(root_node_names) > 0:
            cg_names = self._calculate_cfgs_common_command_group(cfg_editors, *root_node_names)
            for cfg_editor in cfg_editors:
                cfg_editor.rename_command_group(*cg_names, new_cg_names=root_node_names)

        for cfg_editor in cfg_editors:
            merged = False
            for cmd_names, command in cfg_editor.iter_commands():
                cur_cmd = self.find_command_tree_leaf(*cmd_names)
                if cur_cmd is None:
                    continue
                if cur_cmd.version == command.version:
                    main_cfg_editor = self.load_cfg_editor_by_command(cur_cmd)
                    merged_cfg_editor = main_cfg_editor.merge(cfg_editor)
                    if merged_cfg_editor:
                        self.remove_cfg(main_cfg_editor)
                        self.add_cfg(merged_cfg_editor)
                        merged = True
                        break
                new_name = self.generate_unique_name(*cmd_names[:-1], name=cmd_names[-1])
                cfg_editor.rename_command(*cmd_names, new_cmd_names=[*cmd_names[:-1], new_name])
            if not merged:
                self.add_cfg(cfg_editor)

    def add_new_command_by_aaz(self, *cmd_names, version):
        # TODO: add support to load from aaz
        raise NotImplementedError()

    def _calculate_cfgs_common_command_group(self, cfg_editors, *node_names):
        # calculate common cg name prefix
        groups_names = []
        for cfg_editor in cfg_editors:
            for group in cfg_editor.cfg.command_groups:
                cg_names = group.name.split(" ")
                groups_names.append(cg_names)

        root_node = self.find_command_tree_node(*node_names)
        if len(node_names):
            # should also include the existing commands
            for leaf in (root_node.commands or {}).values():
                for leaf_resource in leaf.resources:
                    # cannot find match resource of resource_id with current mod_names and version
                    cg_names = self.swagger_command_generator.generate_command_group_name_by_resource(
                        resource_path=leaf_resource.swagger_path, rp_name=leaf_resource.rp_name)
                    cg_names = cg_names.split(" ")
                    groups_names.append(cg_names)

        common_prefix = groups_names[0]
        for names in groups_names[1:]:
            if len(names) < len(common_prefix):
                common_prefix = common_prefix[:len(names)]
            for i, k in enumerate(names):
                if i >= len(common_prefix):
                    break
                if common_prefix[i] != k:
                    common_prefix = common_prefix[:i]
                    break
        return common_prefix

    def get_resources(self, *root_node_names):
        resources = []
        used_resources = set()
        for leaf in self.iter_command_tree_leaves(*root_node_names):
            for resource in leaf.resources:
                if resource.id not in used_resources:
                    used_resources.add(resource.id)
                    resources.append(resource)
        resources = sorted(resources, key=lambda r: r.id)
        return resources

    def remove_resource(self, resource_id, version):
        cfg_editor = self.load_cfg_editor_by_resource(resource_id, version)
        if not cfg_editor:
            return False
        self.remove_cfg(cfg_editor)
        return True

    def list_commands_by_resource(self, resource_id, version):
        commands = []
        cfg_editor = self.load_cfg_editor_by_resource(resource_id, version)
        if cfg_editor:
            for cmd_names, _ in cfg_editor.iter_commands():
                leaf = self.find_command_tree_leaf(*cmd_names)
                if leaf:
                    commands.append(leaf)
        return commands

    def merge_resources(self, main_resource_id, main_resource_version, plus_resource_id, plus_resource_version):
        main_cfg_editor = self.load_cfg_editor_by_resource(main_resource_id, main_resource_version)
        plus_cfg_editor = self.load_cfg_editor_by_resource(plus_resource_id, plus_resource_version)
        merged_cfg_editor = main_cfg_editor.merge(plus_cfg_editor)
        if merged_cfg_editor:
            self.remove_cfg(plus_cfg_editor)
            self.remove_cfg(main_cfg_editor)
            self.add_cfg(merged_cfg_editor)
            return True
        return False

    @staticmethod
    def _pop_command_tree_node(parent, name):
        if not parent.command_groups or name not in parent.command_groups:
            raise IndexError(f"Command Tree node '{' '.join(parent.names)}' don't contain '{name}' sub node")
        return parent.command_groups.pop(name)

    @staticmethod
    def _pop_command_tree_leaf(parent, name):
        if not parent.commands or name not in parent.commands:
            raise IndexError(f"Command Tree node '{' '.join(parent.names)}' don't contain '{name}' leaf")
        return parent.commands.pop(name)

    def _add_command_tree_node(self, parent, node, name):
        command_groups = node.command_groups
        commands = node.commands

        node.command_groups = None
        node.commands = None

        # when it's conflict with command name, generate a unique name
        if parent.commands and name in parent.commands:
            new_name = self.generate_unique_name(*parent.names, name=name)
            logger.warning(f"Command Group name conflict with Command name: '{' '.join([*parent.names, name])}' : "
                           f"Use '{' '.join([*parent.names, new_name])}' instead")
            name = new_name

        if not parent.command_groups or name not in parent.command_groups:
            if not parent.command_groups:
                parent.command_groups = {}
            parent.command_groups[name] = node
            if parent == self.ws.command_tree:
                node.names = [name]
            else:
                node.names = [*parent.names, name]
        else:
            # merge with existing command group
            node = parent.command_groups[name]

        # add sub node and sub leaf
        if command_groups:
            for sub_name, sub_node in command_groups.items():
                self._add_command_tree_node(node, sub_node, sub_name)
        if commands:
            for sub_name, sub_leaf in commands.items():
                self._add_command_tree_leaf(node, sub_leaf, sub_name)
        return node

    def _add_command_tree_leaf(self, parent, leaf, name):
        cfg_editor = self.load_cfg_editor_by_command(leaf)

        # when it's conflict with command group name, generate a unique name
        if parent.command_groups and name in parent.command_groups:
            new_name = self.generate_unique_name(*parent.names, name=name)
            logger.warning(f"Command name conflict with Command Group name: '{' '.join([*parent.names, name])}' : "
                           f"Use '{' '.join([*parent.names, new_name])}' instead")
            name = new_name

        if parent.commands and name in parent.commands:
            assert leaf != parent.commands[name]
            new_name = self.generate_unique_name(*parent.names, name=name)
            logger.warning(f"Command name conflict with another Command's: '{' '.join([*parent.names, name])}' : "
                           f"Use '{' '.join([*parent.names, new_name])}' instead")
            name = new_name

        if not parent.commands:
            parent.commands = {}
        assert name not in parent.commands
        parent.commands[name] = leaf
        old_names = leaf.names
        if parent != self.ws.command_tree:
            new_cmd_names = [*parent.names, name]
        else:
            new_cmd_names = [name]
        leaf.names = [*new_cmd_names]
        cfg_editor.rename_command(*old_names, new_cmd_names=new_cmd_names)
        return leaf

    def generate_to_aaz(self):
        # update configurations
        for ws_leaf in self.iter_command_tree_leaves():
            editor = self.load_cfg_editor_by_command(ws_leaf)
            cfg = editor.cfg
            self.aaz_specs.update_resource_cfg(cfg)
        # update commands
        for ws_leaf in self.iter_command_tree_leaves():
            self.aaz_specs.update_command_by_ws(ws_leaf)
        # update command groups
        for ws_node in self.iter_command_tree_nodes():
            if ws_node == self.ws.command_tree:
                # ignore root node
                continue
            self.aaz_specs.update_command_group_by_ws(ws_node)
        self.aaz_specs.save()
