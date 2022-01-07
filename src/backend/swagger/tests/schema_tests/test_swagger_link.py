import os
from swagger.tests.common import SwaggerSpecsTestCase
from swagger.model.specs import SwaggerLoader
from swagger.model.specs._utils import map_path_2_repo
from swagger.utils import exceptions


class SwaggerLinkTest(SwaggerSpecsTestCase):

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
        for file_path in self.get_swagger_file_paths(lambda x: 'example' not in x.lower()):
            loader = SwaggerLoader()
            try:
                loader.load_file(file_path)
            except Exception:
                print(map_path_2_repo(file_path), file_path)
                raise
            idx = 0
            while idx < len(loader.loaded_swaggers):
                file_path, swagger = [*loader.loaded_swaggers.items()][idx]
                try:
                    swagger.link(loader, file_path)
                except exceptions.InvalidSwaggerValueError as err:
                    print(err)
                except Exception:
                    print(map_path_2_repo(file_path), file_path)
                    raise
                idx += 1
