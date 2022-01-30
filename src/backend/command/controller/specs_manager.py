import json
import os
import re

from command.model.configuration import CMDConfiguration
from utils.base64 import b64encode_str
from utils.config import Config
from command.model.specs import CMDSpecsCommandTree, CMDSpecsCommandGroup, CMDSpecsCommand
from command.templates import get_templates


# class AAZSpecsUpdater:
#
#     def __init__(self, manager):
#         self.manager = manager
#         self.updated_nodes = {}
#         self.updated_leaves = {}
#         self.updated_resources = {}
#         self.templates = get_templates()
#
#     def add_command_tree_node(self, node):
#         self.manager.get_command_tree_node(*node.names)
#         pass
#
#     def add_command_tree_leaf(self, leaf, cfg_editor):
#         pass
#
#     def save(self):
#         pass


class AAZSpecsManager:
    REFERENCE_HEADER = "# Reference"
    REFERENCE_LINE = re.compile(r"^\s*\[(.*) (.*)\]\((.*)\)\s*$")

    def __init__(self):
        if not Config.AAZ_PATH or not os.path.exists(Config.AAZ_PATH) or not os.path.isdir(Config.AAZ_PATH):
            raise ValueError(f"aaz repo path is invalid: '{Config.AAZ_PATH}'")

        self.folder = Config.AAZ_PATH
        self.resources_folder = os.path.join(self.folder, "Resources")
        self.commands_folder = os.path.join(self.folder, "Commands")
        self.tree = None

    def load(self):
        tree_path = self.get_tree_file_path()
        if not os.path.exists(tree_path):
            self.tree = CMDSpecsCommandTree()
            self.tree.command_groups = {}
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

    def get_command_group(self, *cg_names):
        node = self.tree
        idx = 0
        while idx < len(cg_names):
            name = cg_names[idx]
            if not node.command_groups or name not in node.command_groups:
                return None
            node = node.command_groups[name]
            idx += 1
        return node

    def get_command(self, *cmd_names):
        if len(cmd_names) < 1:
            raise exceptions.InvalidAPIUsage(f"Invalid command name: '{' '.join(cmd_names)}'")

        node = self.get_command_group(*cmd_names[:-1])
        if not node:
            return None
        name = cmd_names[-1]
        if not node.commands or name not in node.commands:
            return None
        leaf = node.commands[name]
        return leaf

    def get_resource_cfg(self, plane, resource_id, version):
        path = self.get_resource_cfg_file_path(plane, resource_id, version)
        if not os.path.exists(path):
            ref_path = self.get_resource_cfg_ref_file_path(plane, resource_id, version)
            if not os.path.exists(ref_path):
                return None

        with open(path, 'r') as f:
            data = json.load(f)



    # def new_updater(self):
    #     return AAZSpecsUpdater(manager=self)


    # def get_command_tree_node(self, *node_names):
    #     node_file = self.get_command_tree_node_file(*node_names)
    #     if not os.path.exists(node_file):
    #         return None
    #
    #     with open(node_file, 'r') as f:
    #         data = f.read()
    #         node = CMDSpecsCommandGroup


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
