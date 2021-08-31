import os
from unittest import TestCase
from swagger.model.specs import SwaggerSpecs, SwaggerLoader
import json


class SwaggerLinkTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(SwaggerLinkTest, self).__init__(*args, **kwargs)
        folder_path = os.environ.get("AAZ_SWAGGER_PATH", None)
        if not folder_path or not os.path.isdir(folder_path):
            raise ValueError("Invalid swagger folder path, Please setup it in environment value 'AAZ_SWAGGER_PATH'.")
        self.specs = SwaggerSpecs(folder_path=folder_path)

    def _swagger_file_paths(self, file_path_filter=None):
        modules = self.specs.get_data_plane_modules() + self.specs.get_mgmt_plane_modules()
        for module in modules:
            for rp in module.get_resource_providers():
                for root, dirs, files in os.walk(rp._file_path):
                    for file in files:
                        if not file.endswith('.json'):
                            continue
                        file_path = os.path.join(root, file)
                        if file_path_filter is None or file_path_filter(file_path):
                            yield file_path

    def test_swagger_link(self):
        for file_path in self._swagger_file_paths(lambda x: 'example' not in x.lower()):
            loader = SwaggerLoader()
            swagger = loader.load_swagger(file_path)
            swagger.link(loader, file_path)
            print(file_path)
