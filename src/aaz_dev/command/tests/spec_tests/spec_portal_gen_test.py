
import os, json
from utils.config import Config
from command.controller.specs_manager import AAZSpecsManager
from cli.controller.portal_cli_generator import PortalCliGenerator
from utils import exceptions
from unittest import TestCase

class AAZSpecPortalGenTest(TestCase):

    def test_aaz_cmd_portal_generate(self):
        node_names = ['aaz', 'change-analysis']
        leaf_name = "list"
        if node_names[0] != AAZSpecsManager.COMMAND_TREE_ROOT_NAME:
            raise exceptions.ResourceNotFind("Command group not exist")
        node_names = node_names[1:]

        manager = AAZSpecsManager()
        leaf = manager.find_command(*node_names, leaf_name)
        if not leaf:
            raise exceptions.ResourceNotFind("Command group not exist")

        target_version = "2021-04-01"
        version = None
        for v in (leaf.versions or []):
            if v.name == target_version:
                version = v
                break

        if not version:
            raise exceptions.ResourceNotFind("Command of version not exist")
        portal_cli_generator = PortalCliGenerator()
        cfg_reader = manager.load_resource_cfg_reader_by_command_with_version(leaf, version=version)
        cmd_cfg = cfg_reader.find_command(*leaf.names)
        cmd_portal_info = portal_cli_generator.generator_command_portal(cmd_cfg, leaf, version)
        file_path = "-".join(leaf.names) + ".json"
        with open(file_path, "w") as f_out:
            f_out.write(json.dumps(cmd_portal_info, indent=4))
