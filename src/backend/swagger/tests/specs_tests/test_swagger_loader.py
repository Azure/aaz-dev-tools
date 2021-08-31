import os
from unittest import TestCase
from swagger.model.specs import SwaggerSpecs, SwaggerLoader
import json


class SwaggerLoaderTest(TestCase):

    def __init__(self, *args, **kwargs):
        super(SwaggerLoaderTest, self).__init__(*args, **kwargs)
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

    def test_load_swagger(self):
        loader = SwaggerLoader()
        for file_path in self._swagger_file_paths(lambda x: 'example' not in x.lower()):
            s = loader.load_swagger(file_path)
            assert s is not None

    def _fetch_ref_values(self, body):
        if isinstance(body, list):
            for k in body:
                for p in self._fetch_ref_values(k):
                    if p is not None:
                        yield p
        elif isinstance(body, dict):
            for k in body:
                if k == '$ref':
                    if isinstance(body[k], str):
                        yield body[k]
                else:
                    for p in self._fetch_ref_values(body[k]):
                        if p is not None:
                            yield p
        else:
            return None

    def test_ref_loader(self):
        for file_path in self._swagger_file_paths(lambda x: 'example' not in x.lower()):
            loader = SwaggerLoader()
            loader.load_swagger(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                body = json.load(f)
            for ref_link in self._fetch_ref_values(body):
                if 'example' in ref_link:
                    continue
                if ref_link is not None:
                    try:
                        ref, path = loader.load_ref(file_path, ref_link)
                    except Exception:
                        print(file_path)
                        raise
