import os
from swagger.model.specs import SwaggerSpecs
from aazdev.tests.common import ApiTestCase
from utils.plane import PlaneEnum


class SwaggerSpecsTestCase(ApiTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # register data plane for test only
        PlaneEnum.Data = "data-plane"
        PlaneEnum._config[PlaneEnum.Data] = {}

        folder_path = os.environ.get("AAZ_SWAGGER_PATH", None)
        if not folder_path or not os.path.isdir(folder_path):
            raise ValueError("Invalid swagger folder path, Please setup it in environment value 'AAZ_SWAGGER_PATH'.")
        self.specs = SwaggerSpecs(folder_path=folder_path)

    def get_data_plane_modules(self, module_filter=None):
        for module in self.specs.get_data_plane_modules(PlaneEnum.Data):
            if module_filter is None or module_filter(module):
                yield module

    def get_mgmt_plane_modules(self, module_filter=None):
        for module in self.specs.get_mgmt_plane_modules(PlaneEnum.Mgmt):
            if module_filter is None or module_filter(module):
                yield module

    def get_data_plane_resource_providers(self, resource_provider_filter=None, **kwargs):
        for module in self.get_data_plane_modules(**kwargs):
            for rp in module.get_resource_providers():
                if resource_provider_filter is None or resource_provider_filter(rp):
                    yield rp

    def get_mgmt_plane_resource_providers(self, resource_provider_filter=None, **kwargs):
        for module in self.get_mgmt_plane_modules(**kwargs):
            for rp in module.get_resource_providers():
                if resource_provider_filter is None or resource_provider_filter(rp):
                    yield rp

    def get_resource_providers(self, **kwargs):
        for rp in self.get_data_plane_resource_providers(**kwargs):
            yield rp
        for rp in self.get_mgmt_plane_resource_providers(**kwargs):
            yield rp

    def get_swagger_file_paths(self, file_path_filter=None, **kwargs):
        for rp in self.get_resource_providers(**kwargs):
            for root, dirs, files in os.walk(rp.folder_path):
                for file in files:
                    if not file.endswith('.json'):
                        continue
                    file_path = os.path.join(root, file)
                    if file_path_filter is None or file_path_filter(file_path):
                        yield file_path
