from swagger.tests.common import SwaggerSpecsTestCase


class ResourceProviderLoaderTest(SwaggerSpecsTestCase):

    def test_mgmt_plan_resource_providers(self):
        for rp in self._get_mgmt_plane_resource_provides():
            print(rp)

    def test_data_plan_resource_providers(self):
        for rp in self._get_data_plane_resource_provides():
            print(rp)
