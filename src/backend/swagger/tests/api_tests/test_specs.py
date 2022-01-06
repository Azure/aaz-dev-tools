from swagger.tests.common import SwaggerSpecsTestCase
import os
import time
from utils.constants import PlaneEnum


class SwaggerSpecsApiTestCase(SwaggerSpecsTestCase):

    def test_mgmt_plane_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f'/swagger/specs/{PlaneEnum.Mgmt}')
            json_data = rv.get_json()
            assert rv.status_code == 200
            assert len(json_data) > 0
            for module in json_data:
                assert os.path.isdir(module['folder'])

    def test_data_plane_modules(self):
        with self.app.test_client() as c:
            rv = c.get(f'/swagger/specs/{PlaneEnum.Data}')
            json_data = rv.get_json()
            assert rv.status_code == 200
            assert len(json_data) > 0
            for module in json_data:
                assert os.path.isdir(module['folder'])

    def test_mgmt_plane_rp(self):
        with self.app.test_client() as c:
            rv = c.get(f'/swagger/specs/{PlaneEnum.Mgmt}')
            json_data = rv.get_json()
            assert rv.status_code == 200
            for module in json_data:
                rv = c.get(f"{module['id']}/providers")
                assert rv.status_code == 200
                data = rv.get_json()
                print(f"{len(data)} {data}")
        time.sleep(1)

    def test_data_plane_rp(self):
        with self.app.test_client() as c:
            rv = c.get(f'/swagger/specs/{PlaneEnum.Data}')
            json_data = rv.get_json()
            assert rv.status_code == 200
            for module in json_data:
                rv = c.get(f"{module['id']}/providers")
                assert rv.status_code == 200
                data = rv.get_json()
                print(f"{len(data)} {data}")
        time.sleep(1)

    def test_mgmt_plane_resources(self):
        with self.app.test_client() as c:
            rv = c.get(f'/swagger/specs/{PlaneEnum.Mgmt}')
            modules = rv.get_json()
            assert rv.status_code == 200
            for module in modules:
                rv = c.get(f"{module['id']}/providers")
                assert rv.status_code == 200
                rps = rv.get_json()
                for rp in rps:
                    start = time.time()
                    rv = c.get(f"{rp['id']}/resources")
                    assert rv.status_code == 200
                    resources = rv.get_json()
                    end = time.time()
                    print(rp['id'], len(resources), f"{end-start}s")
        time.sleep(1)

    def test_data_plane_resources(self):
        with self.app.test_client() as c:
            rv = c.get(f'/swagger/specs/{PlaneEnum.Data}')
            modules = rv.get_json()
            assert rv.status_code == 200
            for module in modules:
                rv = c.get(f"{module['id']}/providers")
                assert rv.status_code == 200
                rps = rv.get_json()
                for rp in rps:
                    start = time.time()
                    rv = c.get(f"{rp['id']}/resources")
                    assert rv.status_code == 200
                    resources = rv.get_json()
                    end = time.time()
                    print(rp['id'], len(resources), f"{end-start}s")
        time.sleep(1)
