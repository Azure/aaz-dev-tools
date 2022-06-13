from swagger.tests.common import SwaggerSpecsTestCase
import os
import time
from utils.plane import PlaneEnum
from utils.base64 import b64encode_str


class SwaggerSpecsApiTestCase(SwaggerSpecsTestCase):

    def test_mgmt_plane_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Mgmt}')
            json_data = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            assert len(json_data) > 0
            for module in json_data:
                assert os.path.isdir(module['folder'])
                rv = c.get(module['url'])
                assert rv.status_code == 200, rv.get_json()['message']
                assert rv.get_json()['url'] == module['url']

    def test_data_plane_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Data}')
            json_data = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            assert len(json_data) > 0
            for module in json_data:
                assert os.path.isdir(module['folder'])
                rv = c.get(module['url'])
                assert rv.status_code == 200, rv.get_json()['message']
                assert rv.get_json()['url'] == module['url']

    def test_mgmt_plane_rp(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Mgmt}')
            json_data = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in json_data:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                print(f"{len(rps)} {rps}")
                for rp in rps:
                    rv = c.get(rp['url'])
                    assert rv.status_code == 200, rv.get_json()['message']
                    assert rv.get_json()['url'] == rp['url']
        time.sleep(1)

    def test_data_plane_rp(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Data}')
            json_data = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in json_data:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                print(f"{len(rps)} {rps}")
                for rp in rps:
                    rv = c.get(rp['url'])
                    assert rv.status_code == 200, rv.get_json()['message']
                    assert rv.get_json()['url'] == rp['url']
        time.sleep(1)

    def test_mgmt_plane_resources(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Mgmt}')
            modules = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in modules:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                for rp in rps:
                    start = time.time()
                    rv = c.get(f"{rp['url']}/Resources")
                    assert rv.status_code == 200, rv.get_json()['message']
                    resources = rv.get_json()
                    end = time.time()
                    print(rp['url'], len(resources), f"{end-start}s")
                    for resource in resources:
                        rv = c.get(resource['url'])
                        assert rv.status_code == 200, rv.get_json()['message']
        time.sleep(1)

    def test_data_plane_resources(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Data}')
            modules = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in modules:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                for rp in rps:
                    start = time.time()
                    rv = c.get(f"{rp['url']}/Resources")
                    assert rv.status_code == 200, rv.get_json()['message']
                    resources = rv.get_json()
                    end = time.time()
                    print(rp['url'], len(resources), f"{end-start}s")
                    for resource in resources:
                        rv = c.get(resource['url'])
                        assert rv.status_code == 200, rv.get_json()['message']
        time.sleep(1)

    def test_mgmt_plane_resource_version(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Mgmt}')
            modules = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in modules:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                for rp in rps:
                    rv = c.get(f"{rp['url']}/Resources")
                    assert rv.status_code == 200, rv.get_json()['message']
                    resources = rv.get_json()
                    for resource in resources:
                        for version in resource['versions']:
                            rv = c.get(version['url'])
                            assert rv.status_code == 200, rv.get_json()['message']

    def test_data_plane_resource_version(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Data}')
            modules = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in modules:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                for rp in rps:
                    rv = c.get(f"{rp['url']}/Resources")
                    assert rv.status_code == 200, rv.get_json()['message']
                    resources = rv.get_json()
                    for resource in resources:
                        for version in resource['versions']:
                            rv = c.get(version['url'])
                            assert rv.status_code == 200, rv.get_json()['message']

    def test_mgmt_plane_resource_and_version_in_module(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Mgmt}')
            modules = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in modules:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                for rp in rps:
                    rv = c.get(f"{rp['url']}/Resources")
                    assert rv.status_code == 200, rv.get_json()['message']
                    resources = rv.get_json()
                    for resource in resources:
                        url = f"{module['url']}/Resources/{b64encode_str(resource['id'])}"
                        rv = c.get(url)
                        if rv.status_code == 400:
                            err_message = rv.get_json()['message']
                            print(f"{module['name']}\t{resource['id']}\t{err_message}")
                            continue
                        assert rv.status_code == 200, rv.get_json()['message']
                        assert rv.get_json() == resource
                        for version in resource['versions']:
                            url = f"{module['url']}/Resources/{b64encode_str(resource['id'])}/V/{b64encode_str(version['version'])}"
                            rv = c.get(url)
                            assert rv.status_code == 200, rv.get_json()['message']
                            assert rv.get_json() == version

    def test_data_plane_resource_and_version_in_module(self):
        with self.app.test_client() as c:
            rv = c.get(f'/Swagger/Specs/{PlaneEnum.Data}')
            modules = rv.get_json()
            assert rv.status_code == 200, rv.get_json()['message']
            for module in modules:
                rv = c.get(f"{module['url']}/ResourceProviders")
                assert rv.status_code == 200, rv.get_json()['message']
                rps = rv.get_json()
                for rp in rps:
                    rv = c.get(f"{rp['url']}/Resources")
                    assert rv.status_code == 200, rv.get_json()['message']
                    resources = rv.get_json()
                    for resource in resources:
                        url = f"{module['url']}/Resources/{b64encode_str(resource['id'])}"
                        rv = c.get(url)
                        if rv.status_code == 400:
                            err_message = rv.get_json()['message']
                            print(f"{module['name']}\t{resource['id']}\t{err_message}")
                            continue
                        assert rv.status_code == 200, rv.get_json()['message']
                        assert rv.get_json() == resource
                        for version in resource['versions']:
                            url = f"{module['url']}/Resources/{b64encode_str(resource['id'])}/V/{b64encode_str(version['version'])}"
                            rv = c.get(url)
                            assert rv.status_code == 200, rv.get_json()['message']
                            assert rv.get_json() == version
