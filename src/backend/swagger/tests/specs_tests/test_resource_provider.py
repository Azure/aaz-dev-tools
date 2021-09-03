from swagger.tests.common import SwaggerSpecsTestCase


class ResourceProviderLoaderTest(SwaggerSpecsTestCase):

    def test_mgmt_plan_resource_providers(self):
        for rp in self.get_mgmt_plane_resource_providers():
            print(rp)

    def test_data_plan_resource_providers(self):
        for rp in self.get_data_plane_resource_providers():
            print(rp)

    def test_resource_map(self):
        for rp in self.get_resource_providers():
            print(rp)
            resource_map = rp.get_resource_map()

    def test_resource_map_similar_path(self):
        for rp in self.get_resource_providers():
            print(rp)
            resource_map = rp.get_resource_map()
            for resource_version_map in resource_map.values():
                path = None
                for resource in resource_version_map.values():
                    if path is None:
                        path = resource.path
                    if path != resource.path:
                        print(f"\n\t\t{path}\n\t\t{resource.path}\n")
