from swagger.model.specs import SwaggerLoader
from swagger.model.schema.path_item import PathItem
from swagger.model.schema.operation import Operation
from swagger.model.schema.parameter import PathParameter, QueryParameter, HeaderParameter, FormDataParameter, BodyParameter
from swagger.model.schema.reference import Reference
from swagger.utils import exceptions
from command.model.configuration import CMDHttpOperation, CMDHttpAction, CMDHttpRequest, CMDHttpResponse, CMDHttpRequestPath, CMDHttpRequestQuery, CMDHttpRequestHeader, CMDHttpJsonBody, CMDJson
from swagger.model.schema.fields import MutabilityEnum


class CommandConfigurationGenerator:

    def __init__(self):
        self.loader = SwaggerLoader()

    def load_resources(self, resources):
        for resource in resources:
            swagger = self.loader.load_file(resource.file_path)
            self.loader.link_swaggers()
            self._flatten_resource_path(swagger, resource.path)

    def _flatten_resource_path(self, swagger, path):
        path_item = swagger.paths.get(path, None)
        if path_item is None:
            path_item = swagger.x_ms_paths.get(path, None)
        assert isinstance(path_item, PathItem)

        path_item.to_cmd_operation(path, method='head', mutability=MutabilityEnum.Read)
        path_item.to_cmd_operation(path, method='get', mutability=MutabilityEnum.Read)
        path_item.to_cmd_operation(path, method='put', mutability=MutabilityEnum.Create)
        path_item.to_cmd_operation(path, method='put', mutability=MutabilityEnum.Update)
        path_item.to_cmd_operation(path, method='patch', mutability=MutabilityEnum.Update)
        path_item.to_cmd_operation(path, method='delete', mutability=MutabilityEnum.Create)
        path_item.to_cmd_operation(path, method='post', mutability=MutabilityEnum.Create)
