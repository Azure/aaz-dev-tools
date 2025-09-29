import json
import logging
import os
import re
import shutil

from command.model.configuration import CMDConfiguration, CMDHelp, CMDCommandExample, XMLSerializer, CMDClientConfig
from utils.base64 import b64encode_str
from utils.config import Config
from utils.plane import PlaneEnum
from command.model.specs import CMDSpecsCommandTree, CMDSpecsCommandGroup, CMDSpecsCommand, CMDSpecsCommandVersion, CMDSpecsResource
from command.templates import get_templates
from utils import exceptions
from .cfg_reader import CfgReader
from .client_cfg_reader import ClientCfgReader
from .cfg_validator import CfgValidator
from .command_tree import CMDSpecsPartialCommandTree

logger = logging.getLogger('aaz')


class AAZSpecsManager:
    COMMAND_TREE_ROOT_NAME = "aaz"

    REFERENCE_LINE = re.compile(r"^Reference\s*\[(.*) (.*)]\((.*)\)\s*$")

    def __init__(self):
        if not Config.AAZ_PATH or not os.path.exists(Config.AAZ_PATH) or not os.path.isdir(Config.AAZ_PATH):
            raise ValueError(f"aaz repo path is invalid: '{Config.AAZ_PATH}'")

        self.folder = Config.AAZ_PATH
        self.resources_folder = os.path.join(self.folder, "Resources")
        self.commands_folder = os.path.join(self.folder, "Commands")
        self._tree = None
        self._modified_resource_cfgs = {}
        self._modified_resource_client_cfgs = {}

        self._tree = CMDSpecsPartialCommandTree(self.folder)

    @property
    def tree(self):
        return self._tree

    @property
    def simple_tree(self):
        return self.tree.simple_tree

    # Commands folder
    def get_tree_file_path(self):
        return os.path.join(self.commands_folder, "tree.json")

    def get_command_group_folder(self, *cg_names):
        # support len(cg_names) == 0
        return os.path.join(self.commands_folder, *cg_names)

    def get_command_group_readme_path(self, *cg_names):
        # when len(cg_names) == 0, the path will be the CommandGroup/readme.md
        return os.path.join(self.get_command_group_folder(*cg_names), "readme.md")

    def get_command_readme_path(self, *cmd_names):
        if len(cmd_names) <= 1:
            raise ValueError(f"Invalid command names: '{' '.join(cmd_names)}'")
        return os.path.join(self.get_command_group_folder(*cmd_names[:-1]), f"_{cmd_names[-1]}.md")

    # resources
    def get_resource_plane_folder(self, plane):
        if plane == PlaneEnum.Mgmt:
            return os.path.join(self.resources_folder, plane)
        elif PlaneEnum.is_data_plane(plane):
            scope = PlaneEnum.get_data_plane_scope(plane)
            if not scope:
                raise ValueError(f"Invalid plane: Missing scope in data plane '{plane}'")
            return os.path.join(self.resources_folder, PlaneEnum._Data, scope)
        else:
            raise ValueError(f"Invalid plane: '{plane}'")
    
    def get_resource_client_cfg_paths(self, plane):
        path = self.get_resource_plane_folder(plane)
        return os.path.join(path, "client.json"), os.path.join(path, "client.xml")

    def get_resource_cfg_folder(self, plane, resource_id):
        path = self.get_resource_plane_folder(plane)
        name = b64encode_str(resource_id)
        while len(name):
            if len(name) > 255:
                path = os.path.join(path, name[:254] + '+')
                name = name[254:]
            else:
                path = os.path.join(path, name)
                name = ""
        return path

    def get_resource_cfg_file_paths(self, plane, resource_id, version):
        """Return Json and XML path"""
        path = os.path.join(self.get_resource_cfg_folder(plane, resource_id), f"{version}")
        return f"{path}.json", f"{path}.xml"

    def get_resource_cfg_ref_file_path(self, plane, resource_id, version):
        return os.path.join(self.get_resource_cfg_folder(plane, resource_id), f"{version}.md")

    def get_resource_versions(self, plane, resource_id):
        path = self.get_resource_cfg_folder(plane, resource_id)
        if not os.path.exists(path) or not os.path.isdir(path):
            return None
        versions = set()
        for file_name in os.listdir(path):
            if file_name.endswith('.xml'):
                versions.add(file_name[:-4])
            elif file_name.endswith('.json'):
                versions.add(file_name[:-5])
            elif file_name.endswith('.md'):
                versions.add(file_name[:-3])
        return sorted(versions, reverse=True)

    def find_command_group(self, *cg_names):
        return self.tree.find_command_group(*cg_names)

    def find_command(self, *cmd_names):
        return self.tree.find_command(*cmd_names)

    def iter_command_groups(self, *root_cg_names):
        yield from self.tree.iter_command_groups(*root_cg_names)

    def iter_commands(self, *root_node_names):
        yield from self.tree.iter_commands(*root_node_names)

    def load_resource_cfg_reader(self, plane, resource_id, version):
        key = (plane, resource_id, version)
        if key in self._modified_resource_cfgs:
            # cfg already modified
            cfg = self._modified_resource_cfgs[key]
            return CfgReader(cfg) if cfg else None

        json_path, xml_path = self.get_resource_cfg_file_paths(plane, resource_id, version)
        if not os.path.exists(json_path) and not os.path.exists(xml_path):
            ref_path = self.get_resource_cfg_ref_file_path(plane, resource_id, version)
            if not os.path.exists(ref_path):
                return None
            json_path = None
            with open(ref_path, 'r', encoding="utf-8") as f:
                for line in f.readlines():
                    match = self.REFERENCE_LINE.fullmatch(line)
                    if match:
                        resource_id, version = match[1], match[2]
                        json_path, xml_path = self.get_resource_cfg_file_paths(plane, resource_id, version)
                        break
            if not json_path or not os.path.exists(json_path):
                raise ValueError(f"Invalid reference file: {ref_path}")

        if not os.path.exists(json_path) and os.path.exists(xml_path):
            if not os.path.isfile(xml_path):
                raise ValueError(f"Invalid file path: {xml_path}")
            # Convert existing xml to json.
            # Not recommend to use xml, because there are some issues in XMLSerializer
            if not os.path.isfile(xml_path):
                raise ValueError(f"Invalid file path: {xml_path}")
            with open(xml_path, 'r', encoding="utf-8") as f:
                cfg = XMLSerializer.from_xml(CMDConfiguration, f.read())
            data = self.render_resource_cfg_to_json(cfg)
            with open(json_path, 'w', encoding="utf-8") as f:
                f.write(data)
            data = self.render_resource_cfg_to_xml(cfg)
            with open(xml_path, 'w', encoding="utf-8") as f:
                f.write(data)

        if not os.path.isfile(json_path):
            raise ValueError(f"Invalid file path: {json_path}")

        with open(json_path, 'r', encoding="utf-8") as f:
            #print(json_path)
            data = json.load(f)
        cfg = CMDConfiguration(data)

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
        return self.tree.create_command_group(*cg_names)

    def update_command_group_by_ws(self, ws_node):
        return self.tree.update_command_group_by_ws(ws_node)

    def delete_command_group(self, *cg_names):
        return self.tree.delete_command_group(*cg_names)
    
    def create_command(self, *cmd_names):
        return self.tree.create_command(*cmd_names)
    
    def delete_command(self, *cmd_names):
        return self.tree.delete_command(*cmd_names)
    
    def delete_command_version(self, *cmd_names, version):
        return self.tree.delete_command_version(*cmd_names, version=version)
    
    def update_command_version(self, *cmd_names, plane, cfg_cmd):
        return self.tree.update_command_version(*cmd_names, plane=plane, cfg_cmd=cfg_cmd)
    
    def update_command_by_ws(self, ws_leaf):
        return self.tree.update_command_by_ws(ws_leaf)
    
    def verify_command_tree(self):
        return self.tree.verify_command_tree()

    def verify_updated_command_tree(self):
        return self.tree.verify_updated_command_tree()

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
            if pre_cfg_reader and pre_cfg_reader.cfg != cfg:
                self._remove_cfg(pre_cfg_reader.cfg)

        # add new command version
        for cmd_names, cmd in cfg_reader.iter_commands():
            self.update_command_version(*cmd_names, plane=cfg.plane, cfg_cmd=cmd)

        for resource in cfg_reader.resources:
            key = (cfg.plane, resource.id, resource.version)
            self._modified_resource_cfgs[key] = cfg

    # client configuration
    def load_client_cfg_reader(self, plane):
        key = (plane, )
        if key in self._modified_resource_client_cfgs:
            # cfg already modified
            cfg = self._modified_resource_client_cfgs[key]
            return ClientCfgReader(cfg) if cfg else None

        json_path, xml_path = self.get_resource_client_cfg_paths(plane)
        if not os.path.exists(json_path) and not os.path.exists(xml_path):
            return None
        
        if not os.path.exists(json_path) and os.path.exists(xml_path):
            if not os.path.isfile(xml_path):
                raise ValueError(f"Invalid file path: {xml_path}")
            # Convert existing xml to json.
            # Not recommend to use xml, because there are some issues in XMLSerializer
            if not os.path.isfile(xml_path):
                raise ValueError(f"Invalid file path: {xml_path}")
            with open(xml_path, 'r') as f:
                cfg = XMLSerializer.from_xml(CMDClientConfig, f.read())
            data = self.render_resource_cfg_to_json(cfg)
            with open(json_path, 'w') as f:
                f.write(data)
            data = self.render_resource_cfg_to_xml(cfg)
            with open(xml_path, 'w') as f:
                f.write(data)
        
        if not os.path.isfile(json_path):
            raise ValueError(f"Invalid file path: {json_path}")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        cfg = CMDClientConfig(data)
        return ClientCfgReader(cfg)

    def update_client_cfg(self, cfg):
        """This function guarantee the client config version is always increasing."""
        assert isinstance(cfg, CMDClientConfig)
        if old_cfg_reader := self.load_client_cfg_reader(cfg.plane):
            if old_cfg_reader.cfg.version > cfg.version:
                raise exceptions.InvalidAPIUsage("Failed to update: a new version of client config exists.")
            if cfg.version == old_cfg_reader.cfg.version:
                # didn't change when version is same
                return
        key = (cfg.plane, )
        self._modified_resource_client_cfgs[key] = cfg

    def save(self):
        self.verify_updated_command_tree()

        remove_files = []
        remove_folders = []
        update_files = {}
        command_groups = set()

        # command
        for cmd_names in sorted(self.tree._modified_commands):
            cmd = self.find_command(*cmd_names)
            file_path = self.get_command_readme_path(*cmd_names)
            if not cmd:
                # remove command file
                remove_files.append(file_path)
            else:
                update_files[file_path] = self.render_command_readme(cmd)

            command_groups.add(tuple(cmd_names[:-1]))

        for cg_names in sorted(self.tree._modified_command_groups):
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
            json_file_path, xml_file_path = self.get_resource_cfg_file_paths(plane, resource_id, version)
            ref_file_path = self.get_resource_cfg_ref_file_path(plane, resource_id, version)
            if not cfg:
                remove_files.append(json_file_path)
                remove_files.append(xml_file_path)
                remove_files.append(ref_file_path)
            else:
                main_resource = cfg.resources[0]
                if main_resource.id != resource_id or main_resource.version != version:
                    update_files[ref_file_path] = self.render_resource_ref_readme(
                        plane=cfg.plane, ref_resource_id=main_resource.id, ref_resource_version=main_resource.version)
                else:
                    update_files[json_file_path] = self.render_resource_cfg_to_json(cfg)
                    update_files[xml_file_path] = self.render_resource_cfg_to_xml(cfg)
        
        # client cfg files
        for (plane, ), cfg in self._modified_resource_client_cfgs.items():
            json_file_path, xml_file_path = self.get_resource_client_cfg_paths(plane)
            assert isinstance(cfg, CMDClientConfig)
            update_files[json_file_path] = self.render_resource_cfg_to_json(cfg)
            update_files[xml_file_path] = self.render_resource_cfg_to_xml(cfg)

        for remove_file in remove_files:
            if os.path.exists(remove_file):
                os.remove(remove_file)

        for remove_folder in remove_folders:
            shutil.rmtree(remove_folder, ignore_errors=True)

        for file_path, data in update_files.items():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding="utf-8") as f:
                f.write(data)

        self._modified_resource_cfgs = {}
        self._modified_resource_client_cfgs = {}

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
        assert isinstance(tree, (CMDSpecsCommandTree, CMDSpecsPartialCommandTree))
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
    def render_resource_cfg_to_json(cfg):
        data = cfg.to_primitive()
        return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def render_resource_cfg_to_xml(cfg):
        return XMLSerializer.to_xml(cfg)
