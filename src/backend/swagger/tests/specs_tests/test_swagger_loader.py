from swagger.tests.common import SwaggerSpecsTestCase
from swagger.model.specs import SwaggerLoader
from swagger.utils import exceptions
import json


class SwaggerLoaderTest(SwaggerSpecsTestCase):

    def test_load_swagger(self):
        loader = SwaggerLoader()
        for file_path in self.get_swagger_file_paths(lambda x: 'example' not in x.lower()):
            s = loader.load_file(file_path)
            assert s is not None

    def _fetch_ref_values(self, body):
        if isinstance(body, list):
            for k in body:
                for p in self._fetch_ref_values(k):
                    if p is not None:
                        yield p
        elif isinstance(body, dict):
            for k in body:
                if k == '$ref' or k == 'x-ms-odata':
                    if isinstance(body[k], str):
                        yield body[k]
                else:
                    for p in self._fetch_ref_values(body[k]):
                        if p is not None:
                            yield p
        else:
            return None

    def test_ref_loader(self):
        for file_path in self.get_swagger_file_paths(lambda x: 'example' not in x.lower()):
            loader = SwaggerLoader()
            loader.load_file(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                body = json.load(f)
            for ref_link in self._fetch_ref_values(body):
                if 'example' in ref_link:
                    continue
                if ref_link is not None:
                    try:
                        ref, traces = loader.load_ref(ref_link, file_path)
                    except exceptions.InvalidSwaggerValueError as err:
                        print(err)
                    except Exception:
                        print(file_path)
                        raise
