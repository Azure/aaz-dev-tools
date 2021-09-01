import os
from unittest import TestCase
from swagger.model.specs import SwaggerSpecs, SwaggerLoader
from swagger.utils import exceptions


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

    def test_swagger_link_data_collection_rules(self):
        file_path = os.path.join(self.specs._folder_path, 'specification', 'monitor', 'resource-manager',
                                 'Microsoft.Insights', 'stable', '2021-04-01', 'dataCollectionRules_API.json')
        loader = SwaggerLoader()
        loader.load_file(file_path)
        idx = 0
        while idx < len(loader.loaded_swaggers):
            file_path = [*loader.loaded_swaggers.keys()][idx]
            swagger = loader.loaded_swaggers[file_path]
            try:
                swagger.link(loader, file_path)
            except exceptions.InvalidSwaggerValueError as err:
                print(err)
            except Exception:
                raise
            idx += 1
        assert idx == 2

    def test_swagger_link_data_factory(self):
        file_path = os.path.join(self.specs._folder_path, 'specification', 'datafactory', 'resource-manager',
                                 'Microsoft.DataFactory', 'stable', '2018-06-01', 'datafactory.json')
        loader = SwaggerLoader()
        loader.load_file(file_path)
        idx = 0
        while idx < len(loader.loaded_swaggers):
            file_path = [*loader.loaded_swaggers.keys()][idx]
            swagger = loader.loaded_swaggers[file_path]
            try:
                swagger.link(loader, file_path)
            except exceptions.InvalidSwaggerValueError as err:
                print(err)
            except Exception:
                raise
            idx += 1

    def test_swagger_link(self):
        for file_path in self._swagger_file_paths(lambda x: 'example' not in x.lower()):
            loader = SwaggerLoader()
            loader.load_file(file_path)
            idx = 0
            while idx < len(loader.loaded_swaggers):
                file_path = [*loader.loaded_swaggers.keys()][idx]
                swagger = loader.loaded_swaggers[file_path]
                try:
                    swagger.link(loader, file_path)
                except exceptions.InvalidSwaggerValueError as err:
                    print(err)
                except Exception:
                    raise
                idx += 1
