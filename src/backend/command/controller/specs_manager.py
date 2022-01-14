from utils.config import Config
import os
from utils.base64 import b64decode_str, b64encode_str


class AAZSpecsManager:

    def __init__(self):
        pass

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
    def get_resource_config_file_name(cls, plane, resource_id, version):
        file_name = os.path.join(cls.get_resource_configs_folder(plane, resource_id), version)

    def find_related_resource_ids(self, plane, resource_id, version):
        pass
