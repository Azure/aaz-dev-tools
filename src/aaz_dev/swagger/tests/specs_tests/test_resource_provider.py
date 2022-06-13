from swagger.tests.common import SwaggerSpecsTestCase
from datetime import datetime
import time


class ResourceProviderLoaderTest(SwaggerSpecsTestCase):

    def test_mgmt_plan_resource_providers(self):
        total = 0
        for rp in self.get_mgmt_plane_resource_providers():
            print(rp)
            total += 1
        print(total)
        time.sleep(1)

    def test_data_plan_resource_providers(self):
        total = 0
        for rp in self.get_data_plane_resource_providers():
            print(rp)
            total += 1
        print(total)
        time.sleep(1)

    def test_resource_map(self):
        total = 0
        for rp in self.get_resource_providers():
            print(rp)
            resource_map = rp.get_resource_map()
            total += len(resource_map)
        print(total)
        time.sleep(1)

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
        time.sleep(1)

    def test_resource_map_of_network(self):
        start = datetime.now()
        rp = next(self.get_mgmt_plane_resource_providers(
            module_filter=lambda m: m.name == "network",
            resource_provider_filter=lambda r: r.name == "Microsoft.Network"
        ))
        _ = rp.get_resource_map()
        delta = datetime.now() - start
        print(delta.total_seconds())
        time.sleep(1)
