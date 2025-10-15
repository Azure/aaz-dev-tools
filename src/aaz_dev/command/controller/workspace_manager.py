import json
import logging
import os
import shutil
from datetime import datetime

from command.model.configuration import CMDHelp, CMDResource, CMDCommandExample, CMDArg, CMDCommand, \
    CMDBuildInVariants, CMDHttpOperation, CMDInstanceUpdateOperation
from command.model.editor import CMDEditorWorkspace, CMDCommandTreeNode, CMDCommandTreeLeaf
from swagger.controller.example_generator import ExampleGenerator
from swagger.controller.command_generator import SwaggerCommandGenerator, TypespecCommandGenerator
from swagger.controller.specs_manager import SwaggerSpecsManager
from swagger.utils.exceptions import InvalidSwaggerValueError
from utils import exceptions
from utils.config import Config
from utils.plane import PlaneEnum
from utils.base64 import b64encode_str
from utils.case import to_camel_case
from .specs_manager import AAZSpecsManager
from .workspace_cfg_editor import WorkspaceCfgEditor, build_endpoint_selector_for_client_config
from .workspace_client_cfg_editor import WorkspaceClientCfgEditor

logger = logging.getLogger('aaz')


class WorkspaceManager:
    COMMAND_TREE_ROOT_NAME = "aaz"

    IN_MEMORY = "__IN_MEMORY_WORKSPACE__"

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
    def new(cls, name, plane, mod_names, resource_provider, source, **kwargs):
        manager = cls(name, **kwargs)
        if not manager.is_in_memory and os.path.exists(manager.path):
            raise exceptions.ResourceConflict(
                f"Workspace conflict: Workspace json file path exists: {manager.path}")
        if plane == PlaneEnum._Data:
            # add resource provider as the scope for data plane
            plane = PlaneEnum.Data(resource_provider)
        manager.ws = CMDEditorWorkspace({
            "name": name,
            "plane": plane,
            "modNames": mod_names,
            "resourceProvider": resource_provider,
            "source": source,
            "version": datetime.utcnow(),
            "commandTree": {
                "names": [cls.COMMAND_TREE_ROOT_NAME],
            }
        })
        manager.inherit_client_cfg_from_spec()
        return manager

    def __init__(self, name, folder=None, aaz_manager=None, swagger_manager=None):
        self.name = name
        if not folder:
            if not Config.AAZ_DEV_WORKSPACE_FOLDER or os.path.exists(Config.AAZ_DEV_WORKSPACE_FOLDER) and not os.path.isdir(Config.AAZ_DEV_WORKSPACE_FOLDER):
                raise ValueError(
                    f"Invalid AAZ_DEV_WORKSPACE_FOLDER: Expect a folder path: {Config.AAZ_DEV_WORKSPACE_FOLDER}")
            self.folder = os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, name)
        else:
            self.folder = os.path.expanduser(
                folder) if folder != self.IN_MEMORY else self.IN_MEMORY
        if not self.is_in_memory and os.path.exists(self.folder) and not os.path.isdir(self.folder):
            raise ValueError(
                f"Invalid workspace folder: Expect a folder path: {self.folder}")
        self.path = os.path.join(self.folder, 'ws.json')

        self.ws = None
        self._cfg_editors = {}
        self._client_cfg_editor = None
        self._reusable_leaves = {}

        self._aaz_specs = aaz_manager
        self._swagger_specs = swagger_manager
        self._swagger_command_generator = None
        
        self._typespec_command_generator = None
        self._swagger_example_generator = None

    @property
    def is_in_memory(self):
        return self.folder == self.IN_MEMORY

    @property
    def aaz_specs(self):
        if not self._aaz_specs:
            self._aaz_specs = AAZSpecsManager()
        return self._aaz_specs

    @property
    def swagger_specs(self):
        if not self._swagger_specs:
            self._swagger_specs = SwaggerSpecsManager()
        return self._swagger_specs

    @property
    def swagger_command_generator(self):
        if not self._swagger_command_generator:
            self._swagger_command_generator = SwaggerCommandGenerator()
        return self._swagger_command_generator
    
    @property
    def typespec_command_generator(self):
        if not self._typespec_command_generator:
            self._typespec_command_generator = TypespecCommandGenerator()
        return self._typespec_command_generator

    @property
    def swagger_example_generator(self):
        if not self._swagger_example_generator:
            self._swagger_example_generator = ExampleGenerator()

        return self._swagger_example_generator

    def load(self):
        assert not self.is_in_memory
        # TODO: handle exception
        if not os.path.exists(self.path) or not os.path.isfile(self.path):
            raise exceptions.ResourceNotFind(
                f"Workspace json file not exist: {self.path}")
        with open(self.path, 'r', encoding="utf-8") as f:
            data = json.load(f)
            self.ws = CMDEditorWorkspace(raw_data=data)

        if not self.ws.mod_names or not self.ws.resource_provider:
            # calculate mod_names and resource_provider for old workspaces
            self.__update_mod_names_and_resource_provider()

        self._cfg_editors = {}
        self._client_cfg_editor = None

    def rename(self, new_name):
        assert not self.is_in_memory
        new_folder = os.path.join(Config.AAZ_DEV_WORKSPACE_FOLDER, new_name)
        if os.path.exists(new_folder):
            raise ValueError(
                f"Invalid new workspace folder: folder path exists: {new_folder}")
        os.rename(self.folder, new_folder)
        self.name = new_name
        self.folder = new_folder
        self.path = os.path.join(self.folder, 'ws.json')
        self.load()
        self.ws.name = new_name
        self.save()

    def delete(self):
        if not self.is_in_memory and os.path.exists(self.path):
            # make sure ws.json exist in folder
            if not os.path.isfile(self.path):
                raise exceptions.ResourceConflict(
                    f"Workspace conflict: Is not file path: {self.path}")
            shutil.rmtree(self.folder)  # remove the whole folder
            return True
        return False

    def save(self):
        assert not self.is_in_memory

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
                    remove_folders.append(
                        WorkspaceCfgEditor.get_cfg_folder(self.folder, r_id))
                else:
                    update_files.append(
                        (WorkspaceCfgEditor.get_cfg_path(self.folder, r_id), data))
                used_resources.add(r_id)
        assert set(self._cfg_editors.keys()) == used_resources

        if not self.ws.mod_names or not self.ws.resource_provider:
            # calculate mod_names and resource_provider for old workspaces
            self.__update_mod_names_and_resource_provider()

        if self._client_cfg_editor:
            data = self._client_cfg_editor.get_cfg_file_data()
            update_files.append(
                (WorkspaceClientCfgEditor.get_cfg_path(self.folder), data))

        # verify ws timestamps
        # TODO: add write lock for path file
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding="utf-8") as f:
                data = json.load(f)
                pre_ws = CMDEditorWorkspace(data)
            if pre_ws.version != self.ws.version:
                raise exceptions.InvalidAPIUsage(
                    f"Workspace Changed after: {self.ws.version}")

        self.ws.version = datetime.utcnow()
        with open(self.path, 'w', encoding="utf-8") as f:
            data = json.dumps(self.ws.to_primitive(), ensure_ascii=False)
            f.write(data)

        for folder in remove_folders:
            shutil.rmtree(folder)

        for file_name, data in update_files:
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, 'w', encoding="utf-8") as f:
                f.write(data)

        self._cfg_editors = {}
        self._client_cfg_editor = None

    def __update_mod_names_and_resource_provider(self):
        resource_mod_set = set()
        resource_rp_set = set()
        for leaf in self.iter_command_tree_leaves():
            for r in leaf.resources:
                resource_mod_set.add('/'.join(r.mod_names))
                resource_rp_set.add(r.rp_name)
        if not self.ws.mod_names and len(resource_mod_set) == 1:
            self.ws.mod_names = resource_mod_set.pop()
        if not self.ws.resource_provider and len(resource_rp_set) == 1:
            self.ws.resource_provider = resource_rp_set.pop()

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
            raise exceptions.InvalidAPIUsage(
                f"Invalid command name: '{' '.join(leaf_names)}'")

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
            if node.commands and name in node.commands:
                raise exceptions.InvalidAPIUsage(
                    f"Failed to create command group, '{' '.join(node_names[:idx+1])}' is command")
            if not node.command_groups or name not in node.command_groups:
                if not node.command_groups:
                    node.command_groups = {}
                aaz_node = self.aaz_specs.find_command_group(
                    *node_names[:idx + 1])
                if aaz_node is not None:
                    new_node = CMDCommandTreeNode({
                        "names": node_names[:idx + 1],
                        "help": aaz_node.help.to_primitive()
                    })
                else:
                    new_node = CMDCommandTreeNode({
                        "names": node_names[:idx + 1]
                    })
                    self.generate_command_group_help(new_node, node_names[:idx + 1])
                node.command_groups[name] = new_node
            node = node.command_groups[name]
            idx += 1
        return node

    def delete_command_tree_node(self, *node_names):
        for _ in self.iter_command_tree_leaves(*node_names):
            raise exceptions.ResourceConflict(
                "Cannot delete command group with commands")
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

    def _set_cfg_editor(self, cfg_editor, aaz_ref=None):
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
            reusable_leaf = self._reusable_leaves.pop(tuple(cmd_names), None) \
                            or self._build_command_tree_leaf_from_aaz_ref(node, name, aaz_ref)
            self._unchecked_add_command_tree_leaf(node, name, command, existed_leaf=reusable_leaf)

    def _unset_cfg_editor(self, cfg_editor):
        cfg_editor.deleted = True
        for resource in cfg_editor.resources:
            self._cfg_editors[resource.id] = cfg_editor

        # update command tree
        for cmd_names, _ in cfg_editor.iter_commands():
            node = self.find_command_tree_node(*cmd_names[:-1])
            name = cmd_names[-1]
            if node and node.commands and name in node.commands:
                # add into reusable leaves in case it's added in add_cfg again.
                self._reusable_leaves[tuple(
                    cmd_names)] = node.commands.pop(name)

    def load_cfg_editor_by_resource(self, resource_id, version, reload=False):
        if not reload and resource_id in self._cfg_editors:
            # load from modified dict
            cfg_editor = self._cfg_editors[resource_id]
            return None if cfg_editor.deleted else cfg_editor
        assert not self.is_in_memory
        try:
            cfg_editor = WorkspaceCfgEditor.load_resource(
                self.folder, resource_id, version)
            for resource in cfg_editor.resources:
                self._cfg_editors[resource.id] = cfg_editor
            return cfg_editor
        except Exception as e:
            logger.error(
                f"load workspace resource cfg failed: {e}: {self.name} {resource_id} {version}")
            return None

    def load_cfg_editor_by_command(self, cmd, reload=False):
        return self.load_cfg_editor_by_resource(cmd.resources[0].id, cmd.resources[0].version, reload=reload)

    def update_command_tree_node_help(self, *node_names, help):
        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceNotFind(
                f"Command Tree Node not found: '{' '.join(node_names)}'")

        if isinstance(help, CMDHelp):
            help = help.to_primitive()
        else:
            assert isinstance(help, dict)
        node.help = CMDHelp(help)
        return node

    def update_command_tree_leaf_help(self, *leaf_names, help):
        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(
                f"Command Tree leaf not found: '{' '.join(leaf_names)}'")

        if isinstance(help, CMDHelp):
            help = help.to_primitive()
        else:
            assert isinstance(help, dict)
        leaf.help = CMDHelp(help)
        return leaf

    def update_command_tree_node_stage(self, *node_names, stage):
        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceNotFind(
                f"Command Tree Node not found: '{' '.join(node_names)}'")

        if node.stage == stage:
            return
        node.stage = stage

        if node.command_groups:
            for sub_node_name in node.command_groups:
                self.update_command_tree_node_stage(
                    *node_names, sub_node_name, stage=stage)

        if node.commands:
            for leaf_name in node.commands:
                self.update_command_tree_leaf_stage(
                    *node_names, leaf_name, stage=stage)
        return node

    def update_command_tree_leaf_stage(self, *leaf_names, stage):
        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(
                f"Command Tree leaf not found: '{' '.join(leaf_names)}'")

        if leaf.stage == stage:
            return
        leaf.stage = stage
        return leaf

    def update_command_tree_leaf_examples(self, *leaf_names, examples):
        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(
                f"Command Tree leaf not found: '{' '.join(leaf_names)}'")
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
                    raise exceptions.InvalidAPIUsage(
                        f"Invalid example data: {err}")
                leaf.examples.append(example)
        return leaf

    def generate_examples_by_swagger(self, leaf, command):
        def is_ready_to_skip(operations):
            if not operations:
                return True

            if len(operations) == 1 and isinstance(operations[0], CMDHttpOperation):
                return False

            # skip when there is no http operation
            return all(not isinstance(op, CMDHttpOperation) for op in operations)

        if is_ready_to_skip(command.operations):
            return []

        return self.generate_operations_examples_by_swagger(
            command,
            " ".join(leaf.names)
        )

    def generate_operations_examples_by_swagger(self, command, cmd_name):
        root = self.find_command_tree_node()
        assert root

        # convert cmd resource to swagger resource
        swagger_resources = []
        for resource in command.resources:
            swagger_resources.append(self.swagger_specs.get_module_manager(
                plane=self.ws.plane,
                mod_names=self.ws.mod_names
            ).get_resource_in_version(resource["id"], resource["version"], resource.rp_name))

        # load swagger resource
        is_generic_update = {op.http.request.method for op in command.operations if isinstance(op, CMDHttpOperation)} == {'get', 'put'}
        if is_generic_update:
            cmd_operation_ids = {op.operation_id: op for op in command.operations if isinstance(op, CMDHttpOperation) and op.http.request.method == 'put'}
        else:
            cmd_operation_ids = {op.operation_id: op for op in command.operations if isinstance(op, CMDHttpOperation)}

        self.swagger_example_generator.load_examples(swagger_resources)

        examples = self.swagger_example_generator.create_draft_examples_by_swagger(
            swagger_resources,
            command,
            cmd_operation_ids,
            cmd_name
        )

        return examples
    
    def generate_command_group_help(self, command_group_node, command_group_names):
        default_help = {
            "short": "Manage " + to_camel_case(command_group_names[-1], delimeters=" ")
        }
        command_group_node.help = CMDHelp(default_help)

    def generate_command_help(self, command_node, cmd_description, cmd_names):
        if cmd_description:
            default_help = {"short": cmd_description}
        else:
            default_help = {
                "short": to_camel_case(cmd_names[-1] +  " " + cmd_names[-2], delimeters=" ")
            }
        command_node.help = CMDHelp(default_help)

    def rename_command_tree_node(self, *node_names, new_node_names):
        new_name = ' '.join(new_node_names)
        if not new_name:
            raise exceptions.InvalidAPIUsage(
                f"Invalid new command name: {new_name}")

        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceNotFind(
                f"Command Tree Node not found: '{' '.join(node_names)}'")

        if node.names == new_node_names:
            return

        parent = self.find_command_tree_node(*node.names[:-1])
        name = node.names[-1]
        if not parent or not parent.command_groups or name not in parent.command_groups or \
                node != parent.command_groups[name]:
            raise exceptions.ResourceConflict(
                f"Command Tree node not exist: '{' '.join(node.names)}'")

        self._pop_command_tree_node(parent, name)

        parent = self.create_command_tree_nodes(*new_node_names[:-1])
        return self._add_command_tree_node(parent, node, new_node_names[-1])

    def rename_command_tree_leaf(self, *leaf_names, new_leaf_names):
        new_name = ' '.join(new_leaf_names)
        if not new_name:
            raise exceptions.InvalidAPIUsage(
                f"Invalid new command name: {new_name}")

        leaf = self.find_command_tree_leaf(*leaf_names)
        if not leaf:
            raise exceptions.ResourceNotFind(
                f"Command Tree leaf not found: '{' '.join(leaf_names)}'")

        if leaf.names == new_leaf_names:
            return

        parent = self.create_command_tree_nodes(*new_leaf_names[:-1])
        new_leaf_name = new_leaf_names[-1]

        leaf = self._checked_pop_command_tree_leaf(*leaf_names)
        cfg_editor = self.load_cfg_editor_by_command(leaf)
        cfg_editor.rename_command(*leaf_names, new_cmd_names=new_leaf_names)
        return self._add_command_tree_leaf(parent, new_leaf_name, cfg_editor, existed_leaf=leaf)

    def generate_unique_name(self, *node_names, name):
        node = self.find_command_tree_node(*node_names)
        if not node:
            raise exceptions.ResourceConflict(
                f"Command Tree node not exist: '{' '.join(node_names)}'")
        if (not node.commands or name not in node.commands) and (
                not node.command_groups or name not in node.command_groups):
            return name
        idx = 1
        new_name = f"{name}-untitled{idx}"
        while node.commands and new_name in node.commands or node.command_groups and new_name in node.command_groups:
            idx += 1
            new_name = f"{name}-untitled{idx}"
        return new_name

    def add_new_resources_by_swagger(self, mod_names, version, resources):
        root_node = self.find_command_tree_node()
        assert root_node

        swagger_resources = []
        resource_options = []
        used_resource_ids = set()
        for r in resources:
            if r['id'] in used_resource_ids:
                continue
            if self.check_resource_exist(r['id']):
                raise exceptions.InvalidAPIUsage(
                    f"Resource already added in Workspace: {r['id']}")
            # convert resource to swagger resource
            swagger_resource = self.swagger_specs.get_swagger_resource(
                plane=self.ws.plane, mod_names=mod_names, resource_id=r['id'], version=version)
            swagger_resources.append(swagger_resource)
            resource_options.append(r.get("options", {}))
            used_resource_ids.update(r['id'])

        # load swagger resources
        self.swagger_command_generator.load_resources(swagger_resources)

        self._add_new_resources(self.swagger_command_generator, swagger_resources, resource_options)

    def add_new_resources_by_typespec(self, version, resources):
        root_node = self.find_command_tree_node()
        assert root_node

        cmd_resources = []
        resource_options = []
        used_resource_ids = set()
        for r in resources:
            if r['id'] in used_resource_ids:
                continue
            if self.check_resource_exist(r['id']):
                raise exceptions.InvalidAPIUsage(
                    f"Resource already added in Workspace: {r['id']}")
            used_resource_ids.update(r['id'])
            cmd_resources.append(CMDResource({
                "id": r['id'],
                "version": version,
                "swagger": f"{self.ws.plane}/{self.ws.mod_names}/ResourceProviders/{self.ws.resource_provider}/Paths/{b64encode_str(r['path'])}/V/{b64encode_str(version)}" 
            }))
            resource_options.append(r.get("options", {}))
        
        # load typespec resources
        self.typespec_command_generator.load_resources(resources)

        self._add_new_resources(self.typespec_command_generator, cmd_resources, resource_options)
    
    def _add_new_resources(self, command_generator, resources, resource_options):
        # generate cfg editors by resource
        cfg_editors = []
        aaz_ref = {}
        for resource, options in zip(resources, resource_options):
            # inherit modification from cfg in aaz
            aaz_cfg_reader = None
            aaz_version = options.get('aaz_version', None)
            if aaz_version:
                try:
                    aaz_cfg_reader = self.aaz_specs.load_resource_cfg_reader(
                        self.ws.plane, resource.id, aaz_version)
                except ValueError as err:
                    raise exceptions.InvalidAPIUsage(message=str(err)) from err
                # inherit update_by from existing cfg in aaz
                if "update_by" not in options:
                    aaz_update_cmd_info = aaz_cfg_reader.get_update_cmd(resource.id)
                    if aaz_update_cmd_info:
                        options["update_by"] = aaz_update_cmd_info[2]
            cfg_editor = self._build_draft_cfg_editor(command_generator, resource, options)
            if aaz_cfg_reader:
                cfg_editor.inherit_modification(aaz_cfg_reader)
                for cmd_names, _ in cfg_editor.iter_commands():
                    aaz_ref[' '.join(cmd_names)] = aaz_version

            update_cmd_info = cfg_editor.get_update_cmd(resource.id)
            temp_update_cmd = None
            if update_cmd_info and options.get('update_by', None) == "PatchOnly" and cfg_editor.find_identity_schema_in_command(update_cmd_info[1]):
                temp_cfg_editor = self._build_draft_cfg_editor(command_generator, resource, {"update_by": "PatchOnly", "methods": ('get', 'patch'), "is_identity": True})
                temp_update_cmd_info = temp_cfg_editor.get_update_cmd(resource.id)
                if temp_update_cmd_info:
                    _, temp_update_cmd, _ = temp_update_cmd_info
            cfg_editor.build_identity_subresource(resource.id, temp_update_cmd)
            cfg_editors.append(cfg_editor)

        # add cfg_editors
        self._add_cfg_editors(cfg_editors, aaz_ref=aaz_ref)

    def _add_cfg_editors(self, cfg_editors, aaz_ref=None):
        for cfg_editor in cfg_editors:
            self._add_cfg_editor(cfg_editor, aaz_ref=aaz_ref)

    def _add_cfg_editor(self, cfg_editor, aaz_ref=None):
        # command group rename
        rename_cg_list = []
        for cg_names in cfg_editor.iter_command_group_names():
            if self.find_command_tree_leaf(*cg_names):
                # command group name conflicted with existing command name
                new_name = self.generate_unique_name(*cg_names[:-1], name=cg_names[-1])
                rename_cg_list.append((cg_names, [*cg_names[:-1], new_name]))
        for cg_names, new_cg_names in rename_cg_list:
            cfg_editor.rename_command_group(*cg_names, new_cg_names=new_cg_names)
        # command rename
        for cmd_names, command in cfg_editor.iter_commands():
            cmd_names, merged_cfg_editor = self._check_and_handle_leaf_name_conflict(*cmd_names, cfg_editor=cfg_editor)
            if merged_cfg_editor:
                self._set_cfg_editor(merged_cfg_editor, aaz_ref=aaz_ref)
                return merged_cfg_editor
        self._set_cfg_editor(cfg_editor, aaz_ref=aaz_ref)
        return cfg_editor

    def reload_resources_by_swagger(self, resources):
        reload_resource_map = {
            r['id']: {"version": r['version']} for r in resources}
        for leaf in self.iter_command_tree_leaves():
            ignore_resources = set()
            reload_versions = set()
            for r in leaf.resources:
                if r.id not in reload_resource_map:
                    ignore_resources.add(r.id)
                    continue
                reload_resource = reload_resource_map[r.id]
                version = reload_resource['version']
                reload_versions.add(version)
                if 'resource' not in reload_resource:
                    reload_resource['resource'] = self.swagger_specs.get_module_manager(
                        self.ws.plane, r.mod_names
                    ).get_resource_in_version(r.id, version)

                if 'cfg_editor' not in reload_resource:
                    reload_resource['cfg_editor'] = self.load_cfg_editor_by_command(
                        leaf)
            if ignore_resources and len(ignore_resources) != len(leaf.resources):
                # not support partial resources reload
                raise exceptions.InvalidAPIUsage(
                    f"Not support partial resources reload in one command: please select the following resources as well: {list(ignore_resources)}")
            if len(reload_versions) > 1:
                # not support multiple resource version for the same command
                raise exceptions.InvalidAPIUsage(
                    f"Please select the same resource version for command: '{' '.join(leaf.names)}'")

        swagger_resources = []
        for resource_id, reload_resource in reload_resource_map.items():
            resource = reload_resource.get('resource', None)
            if not resource:
                raise exceptions.ResourceNotFind(
                    f"Command not exist for '{resource_id}'")
            swagger_resources.append(resource)

        self.swagger_command_generator.load_resources(swagger_resources)
        
        self._reload_resources(self.swagger_command_generator, reload_resource_map)

    def reload_resources_by_typespec(self, resources):
        reload_resource_map = {
            r['id']: {"version": r['version']} for r in resources}
        for leaf in self.iter_command_tree_leaves():
            ignore_resources = set()
            reload_versions = set()
            for r in leaf.resources:
                if r.id not in reload_resource_map:
                    ignore_resources.add(r.id)
                    continue
                reload_resource = reload_resource_map[r.id]
                version = reload_resource['version']
                reload_versions.add(version)
                if 'resource' not in reload_resource:
                    # Ignore subresource property
                    reload_resource['resource'] = CMDResource({
                        "id": r.id,
                        "version": r.version,
                        "swagger": r.swagger, 
                    })
                if 'cfg_editor' not in reload_resource:
                    reload_resource['cfg_editor'] = self.load_cfg_editor_by_command(
                        leaf)
            if ignore_resources and len(ignore_resources) != len(leaf.resources):
                # not support partial resources reload
                raise exceptions.InvalidAPIUsage(
                    f"Not support partial resources reload in one command: please select the following resources as well: {list(ignore_resources)}")
            if len(reload_versions) > 1:
                # not support multiple resource version for the same command
                raise exceptions.InvalidAPIUsage(
                    f"Please select the same resource version for command: '{' '.join(leaf.names)}'")

        self.typespec_command_generator.load_resources(resources)
        self._reload_resources(self.typespec_command_generator, reload_resource_map)

    def _reload_resources(self, command_generator, reload_resource_map):
        new_cfg_editors = []
        for resource_id, reload_resource in reload_resource_map.items():
            options = {}
            cfg_editor = reload_resource['cfg_editor']
            resource = reload_resource['resource']
            methods = cfg_editor.get_used_http_methods(resource_id)
            if methods:
                options['methods'] = methods
            update_cmd_info = cfg_editor.get_update_cmd(resource_id)
            if update_cmd_info:
                _, command, update_by = update_cmd_info
                options['update_by'] = update_by
            new_cfg_editor = self._build_draft_cfg_editor(command_generator, resource, options)
            new_cfg_editor.inherit_modification(cfg_editor)
            temp_update_cmd = None
            if update_cmd_info and update_by == "PatchOnly" and cfg_editor.find_identity_schema_in_command(command):
                temp_cfg_editor = self._build_draft_cfg_editor(command_generator, resource, {"update_by": "PatchOnly", "methods": ('get', 'patch'), "is_identity": True})
                temp_update_cmd_info = temp_cfg_editor.get_update_cmd(resource_id)
                if temp_update_cmd_info:
                    _, temp_update_cmd, _ = temp_update_cmd_info

            new_cfg_editor.build_identity_subresource(resource_id, temp_update_cmd)
            new_cfg_editors.append(new_cfg_editor)

        # remove old cfg editor
        for resource_id, reload_resource in reload_resource_map.items():
            cfg_editor = reload_resource['cfg_editor']
            self._unset_cfg_editor(cfg_editor)

        # add cfg_editors
        self._add_cfg_editors(new_cfg_editors)
    
    def _build_draft_cfg_editor(self, command_generator, resource, options):
        try:
            command_group = command_generator.create_draft_command_group(
                resource, instance_var=CMDBuildInVariants.Instance, **options)
        except InvalidSwaggerValueError as err:
            raise exceptions.InvalidAPIUsage(
                message=str(err)
            ) from err
        assert not command_group.command_groups, "The logic to support sub command groups is not supported"
        if not isinstance(resource, CMDResource):
            # Typespec use CMDResource directly, but swagger use swagger Resource
            resource = resource.to_cmd()
        return WorkspaceCfgEditor.new_cfg(
            plane=self.ws.plane,
            resources=[resource],
            command_groups=[command_group]
        )

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
                        resource_path=leaf_resource.path, rp_name=leaf_resource.rp_name)
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
        self._unset_cfg_editor(cfg_editor)
        return True

    def list_commands_by_resource(self, resource_id, version):
        # will include all commands
        commands = []
        cfg_editor = self.load_cfg_editor_by_resource(resource_id, version)
        if cfg_editor:
            for cmd_names, _ in cfg_editor.iter_commands():
                leaf = self.find_command_tree_leaf(*cmd_names)
                if leaf:
                    commands.append(leaf)
        return commands

    def merge_resources(self, main_resource_id, main_resource_version, plus_resource_id, plus_resource_version):
        main_cfg_editor = self.load_cfg_editor_by_resource(
            main_resource_id, main_resource_version)
        plus_cfg_editor = self.load_cfg_editor_by_resource(
            plus_resource_id, plus_resource_version)
        merged_cfg_editor = main_cfg_editor.merge(plus_cfg_editor)
        if merged_cfg_editor:
            self._unset_cfg_editor(plus_cfg_editor)
            self._unset_cfg_editor(main_cfg_editor)
            self._set_cfg_editor(merged_cfg_editor)
            return True
        return False

    def add_subresource_by_arg_var(self, resource_id, version, arg_var, cg_names, ref_args_options):

        cfg_editor = self.load_cfg_editor_by_resource(resource_id, version)
        if not cfg_editor:
            raise exceptions.InvalidAPIUsage(
                f"Resource not exist: resource_id={resource_id} version={version}")

        self._unset_cfg_editor(cfg_editor)
        cfg_editor.build_subresource_commands_by_arg_var(
            resource_id, arg_var, cg_names, ref_args_options)
        self._set_cfg_editor(cfg_editor)

    def remove_subresource(self, resource_id, version, subresource):
        cfg_editor = self.load_cfg_editor_by_resource(resource_id, version)
        if not cfg_editor:
            return False
        if not subresource:
            raise exceptions.InvalidAPIUsage(
                f"Invalid subresource: '{subresource}'")

        self._unset_cfg_editor(cfg_editor)
        removed_commands = cfg_editor.remove_subresource_commands(
            resource_id, version, subresource)
        self._set_cfg_editor(cfg_editor)
        return len(removed_commands) > 0

    def list_commands_by_subresource(self, resource_id, version, subresource):
        commands = []
        cfg_editor = self.load_cfg_editor_by_resource(resource_id, version)
        if cfg_editor:
            for cmd_names, _ in cfg_editor.iter_commands_by_resource(resource_id, subresource, version):
                leaf = self.find_command_tree_leaf(*cmd_names)
                if leaf:
                    commands.append(leaf)
        return commands

    def _build_command_tree_leaf_from_aaz_ref(self, parent, name, aaz_ref):
        cmd_names = [*parent.names, name]
        if (ref_v_name := aaz_ref.get(' '.join(cmd_names), None)) \
                and (aaz_leaf := self.aaz_specs.find_command(*cmd_names)):
            # reference from aaz specs
            ref_v = None
            for v in aaz_leaf.versions:
                if v.name == ref_v_name:
                    ref_v = v
                    break
            leaf = CMDCommandTreeLeaf({
                "names": [*cmd_names],
                "stage": ref_v.stage if ref_v else parent.stage,
                "help": aaz_leaf.help.to_primitive(),
            })
            if ref_v and ref_v.examples:
                leaf.examples = []
                for example in ref_v.examples:
                    leaf.examples.append(
                        CMDCommandExample(example.to_primitive()))
            return leaf
        return None

    def _checked_pop_command_tree_leaf(self, *leaf_names):
        parent = self.find_command_tree_node(*leaf_names[:-1])
        name = leaf_names[-1]
        if not parent or not parent.commands or name not in parent.commands:
            raise exceptions.ResourceConflict(
                f"Command Tree leaf not exist: '{' '.join(leaf_names)}")
        return parent.commands.pop(name)

    @staticmethod
    def _pop_command_tree_node(parent, name):
        if not parent.command_groups or name not in parent.command_groups:
            raise IndexError(
                f"Command Tree node '{' '.join(parent.names)}' don't contain '{name}' sub node")
        return parent.command_groups.pop(name)

    @staticmethod
    def _pop_command_tree_leaf(parent, name):
        if not parent.commands or name not in parent.commands:
            raise IndexError(
                f"Command Tree node '{' '.join(parent.names)}' don't contain '{name}' leaf")
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
                cfg_editor = self.load_cfg_editor_by_command(sub_leaf)
                cfg_editor.rename_command(*sub_leaf.names, new_cmd_names=[*node.names, sub_name])
                self._add_command_tree_leaf(node, sub_name, cfg_editor, existed_leaf=sub_leaf)
        return node

    def _add_command_tree_leaf(self, parent, name, cfg_editor, existed_leaf=None):
        names, new_cfg_editor = self._check_and_handle_leaf_name_conflict(*parent.names, name, cfg_editor=cfg_editor)
        if new_cfg_editor:
            # Merge Successfully
            self._unset_cfg_editor(cfg_editor)
            self._set_cfg_editor(new_cfg_editor)
            return self.find_command_tree_leaf(*parent.names, name)
        command = cfg_editor.find_command(*names)
        assert command is not None

        return self._unchecked_add_command_tree_leaf(parent, names[-1], command, existed_leaf=existed_leaf)

    def _check_and_handle_leaf_name_conflict(self, *names, cfg_editor):
        if self.find_command_tree_node(*names):
            # command name conflicted with existing command group name
            new_name = self.generate_unique_name(*names[:-1], name=names[-1])
            new_names = [*names[:-1], new_name]
            cfg_editor.rename_command(*names, new_cmd_names=new_names)
            return new_names, None
        elif cur_cmd := self.find_command_tree_leaf(*names):
            command = cfg_editor.find_command(*names)
            assert command is not None
            # command name conflict with existing one's
            if cur_cmd.version == command.version:
                main_cfg_editor = self.load_cfg_editor_by_command(cur_cmd)
                merged_cfg_editor = main_cfg_editor.merge(cfg_editor)
                if merged_cfg_editor:
                    self._unset_cfg_editor(main_cfg_editor)
                    return names, merged_cfg_editor
            new_name = self.generate_unique_name(*names[:-1], name=names[-1])
            new_names = [*names[:-1], new_name]
            cfg_editor.rename_command(*names, new_cmd_names=new_names)
            return new_names, None
        return names, None

    def _unchecked_add_command_tree_leaf(self, parent, name, command, *, existed_leaf=None):
        cmd_names = [*parent.names, name]
        if existed_leaf:
            existed_leaf.names = cmd_names
            leaf = existed_leaf
        else:
            leaf = CMDCommandTreeLeaf({
                "names": [*cmd_names],
                "stage": parent.stage
            })
            self.generate_command_help(leaf, command.description, cmd_names)

        leaf.version = command.version
        leaf.resources = [CMDResource(
            r.to_primitive()) for r in command.resources]

        if not parent.commands:
            parent.commands = {}
        assert name not in parent.commands
        if parent.command_groups:
            assert name not in parent.command_groups
        parent.commands[name] = leaf
        return leaf

    def generate_to_aaz(self):
        # Merge the commands of subresources which exported in aaz but not exist in current workspace
        self._merge_sub_resources_in_aaz()

        # in memory workspace folder does not support client cfg
        if not self.is_in_memory:
            # update client config
            editor = self.load_client_cfg_editor()
            if editor:
                self.aaz_specs.update_client_cfg(editor.cfg)

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

    def _merge_sub_resources_in_aaz(self):
        """Merge the commands of subresources which exported in aaz but not exist in current workspace"""
        updated_cfgs = []
        inserted_commands = set()
        for ws_leaf in self.iter_command_tree_leaves():
            editor = self.load_cfg_editor_by_command(ws_leaf)
            existing_sub_resources = {}
            for cmd_names, command in editor.iter_commands():
                for r in command.resources:
                    if not r.subresource:
                        continue
                    key = (r.id, r.version)
                    if key not in existing_sub_resources:
                        existing_sub_resources[key] = set()
                    existing_sub_resources[key].add(r.subresource)
                    if r.subresource.endswith("[]") or r.subresource.endswith("{}"):
                        existing_sub_resources[key].add(r.subresource[:-2])

            aaz_ref = {}
            for (r_id, r_version), r_sub_resources in existing_sub_resources.items():
                pre_cfg_reader = self.aaz_specs.load_resource_cfg_reader(
                    editor.cfg.plane, resource_id=r_id, version=r_version
                )
                if not pre_cfg_reader:
                    continue

                for cmd_names, command in pre_cfg_reader.iter_commands():
                    insert_command = True
                    for r in command.resources:
                        if (r.id, r.version) not in existing_sub_resources:
                            insert_command = False
                            break
                        if not r.subresource or r.subresource in r_sub_resources:
                            insert_command = False
                            break
                    if not insert_command:
                        continue
                    cmd_names_str = ' '.join(cmd_names)
                    if cmd_names_str in inserted_commands:
                        continue
                    if self.find_command_tree_leaf(*cmd_names) is not None:
                        logger.error(
                            f"Command '{' '.join(cmd_names)}' in workspace conflict the name of Subresource Command in `aaz`")
                        continue
                    if self.find_command_tree_node(*cmd_names) is not None:
                        logger.error(
                            f"Command Group '{' '.join(cmd_names)}' in workspace conflict the name of Subresource Command in `aaz`")
                        continue
                    command = CMDCommand(command.to_native())
                    command.link()
                    editor._add_command(*cmd_names, command=command)
                    inserted_commands.add(cmd_names_str)
                    aaz_ref[cmd_names_str] = r_version
            if aaz_ref:
                editor.reformat()
                updated_cfgs = [(editor, aaz_ref)]

        for editor, aaz_ref in updated_cfgs:
            self._unset_cfg_editor(editor)
            self._set_cfg_editor(editor, aaz_ref)

    def find_similar_args(self, *cmd_names, arg):
        assert isinstance(arg, CMDArg)
        results = {}
        if arg.var.startswith("@"):
            # specify idx_suffix
            cls_name = arg.var[1:].replace(
                '[', '.[').replace('{', '.{').split('.')[0]
            leaf = self.find_command_tree_leaf(*cmd_names)
            assert leaf is not None
            cfg_editor = self.load_cfg_editor_by_command(leaf)
            _, cls_arg, cls_arg_idx, _ = cfg_editor.find_arg_cls_definition(
                *cmd_names, cls_name=cls_name)
            _, arg_idx = cfg_editor.find_arg_by_var(
                *cmd_names, arg_var=arg.var)
            assert arg_idx.startswith(cls_arg_idx)
            idx_suffix = arg_idx[len(cls_arg_idx):]
            assert len(idx_suffix) > 0

            # remove the subfix such as `_create` `_update`
            cls_name_prefix = cls_name.split('_')[0]
            for leaf in self.iter_command_tree_leaves():
                cfg_editor = self.load_cfg_editor_by_command(leaf)
                for _, similar_cls_arg, similar_cls_arg_idx, _ in cfg_editor.iter_arg_cls_definition(
                        *leaf.names, cls_name_prefix=cls_name_prefix):
                    # search cls definition in command
                    # find sub arg by idx_suffix
                    similar_arg = cfg_editor.find_sub_arg(
                        similar_cls_arg, idx=idx_suffix)
                    if similar_arg is None or not cfg_editor.is_similar_args(arg, similar_arg):
                        continue
                    similar_arg_idx = similar_cls_arg_idx + idx_suffix

                    key = tuple(leaf.names)
                    assert key not in results
                    results[key] = {
                        similar_arg.var: [similar_arg_idx]
                    }

                    # search cls reference in command
                    for _, _, ref_arg_idx, _ in cfg_editor.iter_arg_cls_reference(*leaf.names, cls_name=similar_cls_arg.cls):
                        results[key][similar_arg.var].append(
                            ref_arg_idx + idx_suffix)

        else:
            for leaf in self.iter_command_tree_leaves():
                cfg_editor = self.load_cfg_editor_by_command(leaf)
                similar_arg, similar_arg_idx = cfg_editor.find_arg_by_var(
                    *leaf.names, arg_var=arg.var)
                if similar_arg is None or not cfg_editor.is_similar_args(arg, similar_arg):
                    continue
                key = tuple(leaf.names)
                assert key not in results
                results[key] = {
                    similar_arg.var: [similar_arg_idx]
                }
        return results

    # client config
    # TODO: support typespec
    def create_cfg_editor(self, auth, templates=None, cloud_medadata=None, arm_resource=None):
        ref_cfg = self.load_client_cfg_editor()
        if templates:
            endpoints = WorkspaceClientCfgEditor.new_client_endpoints_by_template(templates, cloud_medadata)
        elif arm_resource:
            # arm_resrouce should have these keys: "module", "version", "id", "subresource"
            mod_names = arm_resource['module']
            version = arm_resource['version']
            resource_id = arm_resource['id']
            subresource = arm_resource['subresource']
            swagger_resource = self.swagger_specs.get_swagger_resource(
                plane=PlaneEnum.Mgmt, mod_names=mod_names, resource_id=resource_id, version=version)
            if 'get' not in set(swagger_resource.operations.values()):
                raise exceptions.InvalidAPIUsage(f"The resource doesn't has 'get' method: {resource_id}")
            self.swagger_command_generator.load_resources([swagger_resource])

            resource = swagger_resource.to_cmd()
            resource.subresource = subresource

            # build get operation by draft command
            get_op = self.swagger_command_generator.create_draft_command_group(
                swagger_resource, instance_var=CMDBuildInVariants.EndpointInstance, methods=('get',)
            ).commands[0].operations[0]

            selector = build_endpoint_selector_for_client_config(get_op, subresource_idx=resource.subresource)

            endpoints = WorkspaceClientCfgEditor.new_client_endpoints_by_http_operation(
                resource=resource,
                selector=selector,
                operation=get_op,
            )
        else:
            raise NotImplementedError()

        self._client_cfg_editor = WorkspaceClientCfgEditor.new_client_cfg(
            plane=self.ws.plane,
            auth=auth,
            endpoints=endpoints,
            ref_cfg=ref_cfg,
        )
        return self._client_cfg_editor

    def load_client_cfg_editor(self, reload=False):
        if not reload and self._client_cfg_editor:
            return self._client_cfg_editor
        assert not self.is_in_memory
        try:
            self._client_cfg_editor = WorkspaceClientCfgEditor.load_client_cfg(self.folder)
            return self._client_cfg_editor
        except Exception as e:
            logger.error(
                f"load workspace client cfg failed: {e}: {self.name}")
            return None

    def compare_client_cfg_with_spec(self):
        """ Check whether the client configuration version in workspace is later than the aaz specs one. """
        # compare client configuration from aaz specs
        aaz_client_cfg_reader = self.aaz_specs.load_client_cfg_reader(self.ws.plane)
        client_cfg_reader = self.load_client_cfg_editor()
        if client_cfg_reader and not aaz_client_cfg_reader:
            return True
        if aaz_client_cfg_reader and not client_cfg_reader:
            return False
        if aaz_client_cfg_reader.cfg.version > client_cfg_reader.cfg.version:
            return False
        return True

    def inherit_client_cfg_from_spec(self):
        # inherit client configuration from aaz specs
        client_cfg_reader = self.aaz_specs.load_client_cfg_reader(self.ws.plane)
        if client_cfg_reader:
            self._client_cfg_editor = WorkspaceClientCfgEditor(client_cfg_reader.cfg)
