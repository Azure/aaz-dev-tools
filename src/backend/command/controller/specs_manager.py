import json
import os
import re

from command.model.configuration import CMDConfiguration
from utils.base64 import b64encode_str
from utils.config import Config
from command.model.specs import CMDSpecsCommandTreeNode, CMDSpecsCommandTreeLeaf


class AAZSpecsUpdater:

    def __init__(self, manager):
        self.manager = manager
        self.updated_nodes = {}
        self.updated_leaves = {}
        self.updated_resources = {}

    def add_command_tree_node(self, node):
        self.manager.get_command_tree_node(*node.names)
        pass

    def add_command_tree_leaf(self, leaf, cfg_editor):
        pass

    def save(self):
        pass


class AAZSpecsManager:
    REFERENCE_HEADER = "# Reference"
    REFERENCE_LINE = re.compile(r"^\s*\[(.*) (.*)\]\((.*)\)\s*$")

    def __init__(self):
        self.folder = Config.AAZ_PATH
        self.resources_folder = os.path.join(self.folder, "Resources")
        self.commands_folder = os.path.join(self.folder, "Commands")

    def get_resource_plane_folder(self, plane):
        return os.path.join(self.resources_folder, plane)

    def get_resource_configs_folder(self, plane, resource_id):
        return os.path.join(self.get_resource_plane_folder(plane), b64encode_str(resource_id))

    def get_resource_config_file_path(self, plane, resource_id, version):
        file_name = os.path.join(self.get_resource_configs_folder(plane, resource_id), version)
        return file_name + ".xml"

    def get_resource_config_reference_file_path(self, plane, resource_id, version):
        file_name = os.path.join(self.get_resource_configs_folder(plane, resource_id), version)
        return file_name + ".md"

    def get_command_tree_node_folder(self, *node_names):
        return os.path.join(self.commands_folder, *node_names)

    def get_command_tree_node_file(self, *node_names):
        return os.path.join(self.get_command_tree_node_folder(*node_names), "readme.md")

    def get_command_tree_leaf_file(self, *leaf_names):
        assert len(leaf_names) > 0
        return os.path.join(self.get_command_tree_node_folder(*leaf_names[:-1]), f"{leaf_names[-1]}.md")

    def new_updater(self):
        return AAZSpecsUpdater(manager=self)

    def get_command_tree_node(self, *node_names):
        node_file = self.get_command_tree_node_file(*node_names)
        if not os.path.exists(node_file):
            return None

        with open(node_file, 'r') as f:
            data = f.read()
            node = CMDSpecsCommandTreeNode


    # def verify_command_tree_node(self, node):
    #     pass
    #
    # def verify_command_tree_leaf(self, leaf, cfg_editor):
    #     pass

    # @classmethod
    # def find_cmd_resources(cls, plane, resource_id, version):
    #     """ the related resource ids are those used in the same command configuration file """
    #     path = cls.get_resource_config_file_path(plane, resource_id, version)
    #     if not os.path.exists(path):
    #         path = cls.get_resource_config_file_path(plane, resource_id, version, link=True)
    #         if not os.path.exists(path):
    #             return None
    #         content = cls.parse_link_file(path)
    #         if not content:
    #             return None
    #         path = content[2]  # the link file path
    #     config = cls.load_cmd_config_file(path)
    #     return config.resources
    #
    # @classmethod
    # def load_cmd_config_file(cls, path):
    #     with open(path, 'r') as f:
    #         config_data = json.load(f)
    #         config = CMDConfiguration(config_data)
    #     return config
    #
    # @classmethod
    # def parse_link_file(cls, link_file):
    #     with open(link_file, 'r') as f:
    #         lines = f.readlines()
    #         for idx, line in enumerate(lines):
    #             if line == cls.REFERENCE_HEADER:
    #                 if idx + 1 < len(lines):
    #                     link_line = lines[idx + 1]
    #                     match = cls.REFERENCE_LINE.fullmatch(link_line)
    #                     if match:
    #                         return match[1], match[2], match[3]  # resource_id, version, file_path
    #     return None
