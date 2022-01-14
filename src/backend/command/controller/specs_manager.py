from utils.config import Config
import os
import re
from utils.base64 import b64decode_str, b64encode_str
from command.model.configuration import CMDConfiguration
import json


class AAZSpecsManager:

    REFERENCE_HEADER = "# Reference"
    REFERENCE_LINE = re.compile(r"^\s*\[(.*) (.*)\]\((.*)\)\s*$")

    def __init__(self):
        pass

    @classmethod
    def find_cmd_resources(cls, plane, resource_id, version):
        """ the related resource ids are those used in the same command configuration file """
        path = cls.get_resource_config_file_path(plane, resource_id, version)
        if not os.path.exists(path):
            path = cls.get_resource_config_file_path(plane, resource_id, version, link=True)
            if not os.path.exists(path):
                return None
            content = cls.parse_link_file(path)
            if not content:
                return None
            path = content[2]   # the link file path
        config = cls.load_cmd_config_file(path)
        return config.resources

    @classmethod
    def load_cmd_config_file(cls, path):
        with open(path, 'r') as f:
            config_data = json.load(f)
            config = CMDConfiguration(config_data)
        return config

    @classmethod
    def parse_link_file(cls, link_file):
        with open(link_file, 'r') as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                if line == cls.REFERENCE_HEADER:
                    if idx + 1 < len(lines):
                        link_line = lines[idx + 1]
                        match = cls.REFERENCE_LINE.fullmatch(link_line)
                        if match:
                            return match[1], match[2], match[3]  # resource_id, version, file_path
        return None

    @classmethod
    def get_resources_folder(cls):
        return os.path.join(Config.AAZ_PATH, "resources")

    @classmethod
    def get_resource_plane_folder(cls, plane):
        return os.path.join(cls.get_resources_folder(), plane)

    @classmethod
    def get_resource_configs_folder(cls, plane, resource_id):
        return os.path.join(cls.get_resource_plane_folder(plane), b64encode_str(resource_id))

    @classmethod
    def get_resource_config_file_path(cls, plane, resource_id, version, link=False):
        file_name = os.path.join(cls.get_resource_configs_folder(plane, resource_id), version)
        if link:
            return file_name + ".md"    # using md format
        else:
            return file_name + ".json"   # using json format, TODO: switch to xml later
