from swagger.tests.common import SwaggerSpecsTestCase
import json


class SchemaTest(SwaggerSpecsTestCase):

    def _swagger_bodies(self):
        for file_path in self.get_swagger_file_paths(lambda x: 'example' not in x.lower()):
            with open(file_path, 'r', encoding='utf-8') as f:
                body = json.load(f)
            if 'swagger' not in body:
                continue
            yield file_path, body

    def test_Swagger(self):
        from swagger.model.schema.swagger import Swagger
        parsed = 0
        for file_path, body in self._swagger_bodies():
            try:
                Swagger(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _infoes(self):
        for file_path, body in self._swagger_bodies():
            if 'info' in body:
                yield file_path, body['info']

    def test_Info(self):
        from swagger.model.schema.info import Info
        parsed = 0
        for file_path, body in self._infoes():
            try:
                Info(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _pathItems(self):
        for file_path, body in self._swagger_bodies():
            for v in body['paths'].values():
                yield file_path, v

    def test_PathItem(self):
        from swagger.model.schema.path_item import PathItem
        parsed = 0
        for file_path, body in self._pathItems():
            try:
                PathItem(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _definitions(self):
        for file_path, body in self._swagger_bodies():
            for v in body.get('definitions', {}).values():
                yield file_path, v

    def test_Schema_by_definitions(self):
        from swagger.model.schema.schema import Schema
        parsed = 0
        for file_path, body in self._definitions():
            try:
                Schema(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _parameters(self):
        for file_path, body in self._swagger_bodies():
            for v in body.get('parameters', {}).values():
                yield file_path, v

    def test_ParameterType(self):
        from swagger.model.schema.parameter import ParameterField
        parsed = 0
        for file_path, body in self._parameters():
            try:
                ParameterField(support_reference=True)(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _responses(self):
        for file_path, body in self._swagger_bodies():
            for v in body.get('responses', {}).values():
                yield file_path, v

    def test_Response(self):
        from swagger.model.schema.response import Response
        parsed = 0
        for file_path, body in self._responses():
            try:
                Response(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _response_headers(self):
        for file_path, body in self._responses():
            for v in body.get('headers', {}).values():
                yield file_path, v

    def test_Header(self):
        from swagger.model.schema.header import Header
        parsed = 0
        for file_path, body in self._response_headers():
            try:
                Header(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _response_schema(self):
        for file_path, body in self._responses():
            if 'schema' in body:
                yield file_path, body['schema']

    def test_Schema_by_response(self):
        from swagger.model.schema.schema import Schema
        parsed = 0
        for file_path, body in self._response_schema():
            try:
                Schema(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _securityDefinitions(self):
        for file_path, body in self._swagger_bodies():
            for v in body.get('securityDefinitions', {}).values():
                yield file_path, v

    def test_SecuritySchemeType(self):
        from swagger.model.schema.security_scheme import SecuritySchemeField
        parsed = 0
        for file_path, body in self._securityDefinitions():
            try:
                SecuritySchemeField()(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _tags(self):
        for file_path, body in self._swagger_bodies():
            for v in body.get('tags', []):
                yield file_path, v

    def test_Tag(self):
        from swagger.model.schema.tag import Tag
        parsed = 0
        for file_path, body in self._tags():
            try:
                Tag(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _externalDocs(self):
        for file_path, body in self._swagger_bodies():
            if 'externalDocs' in body:
                yield file_path, body['externalDocs']

    def test_ExternalDocumentation(self):
        from swagger.model.schema.external_documentation import ExternalDocumentation
        parsed = 0
        for file_path, body in self._externalDocs():
            try:
                ExternalDocumentation(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _x_ms_paths(self):
        for file_path, body in self._swagger_bodies():
            for v in body.get('x-ms-paths', {}).values():
                yield file_path, v

    def test_PathItem_by_xmsPaths(self):
        from swagger.model.schema.path_item import PathItem
        parsed = 0
        for file_path, body in self._x_ms_paths():
            try:
                PathItem(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")

    def _x_ms_parameterized_host(self):
        for file_path, body in self._swagger_bodies():
            if 'x-ms-parameterized-host' in body:
                yield file_path, body['x-ms-parameterized-host']

    def test_XmsParameterizedHost(self):
        from swagger.model.schema.x_ms_parameterized_host import XmsParameterizedHost
        parsed = 0
        for file_path, body in self._x_ms_parameterized_host():
            try:
                XmsParameterizedHost(body)
            except Exception as err:
                print(file_path)
                raise err
            parsed += 1
        print(f"Parsed: {parsed}")
