from swagger.model.specs import SwaggerLoader
from swagger.model.schema.path_item import PathItem
from swagger.model.schema.operation import Operation
from swagger.model.schema.parameter import PathParameter, QueryParameter, HeaderParameter, FormDataParameter, BodyParameter
from swagger.model.schema.reference import Reference
from swagger.utils import exceptions
from command.model.configuration import CMDHttpOperation, CMDHttpAction, CMDHttpRequest, CMDHttpResponse, CMDHttpRequestPath, CMDHttpRequestQuery, CMDHttpRequestHeader, CMDHttpBody


class CommandConfigurationGenerator:

    def __init__(self):
        self.loader = SwaggerLoader()

    def load_resources(self, resources):
        for resource in resources:
            swagger = self.loader.load_file(resource.file_path)
            swagger.link(self.loader, resource.file_path)
            self._flatten_resource_path(swagger, resource.path)

    def _flatten_resource_path(self, swagger, path):
        path_item = swagger.paths.get(path, None)
        if path_item is None:
            path_item = swagger.x_ms_paths.get(path, None)
        assert isinstance(path_item, PathItem)

        if path_item.get is not None:
            self._build_http_operation(path, 'get', path_item.get)
        if path_item.put is not None:
            self._build_http_operation(path, 'put', path_item.put, mutability_mode='create')
            self._build_http_operation(path, 'put', path_item.put, mutability_mode='update')
        if path_item.patch is not None:
            self._build_http_operation(path, 'patch', path_item.patch, mutability_mode='update')
        if path_item.delete is not None:
            self._build_http_operation(path, 'delete', path_item.delete)

        if path_item.post is not None:
            self._build_http_operation(path, 'post', path_item.post)  # TODO: determine which mutability mode should be used

        if path_item.head is not None:
            self._build_http_operation(path, 'head', path_item.head)

    def _build_http_operation(self, path, method, op: Operation, mutability_mode=None):
        cmd_op = CMDHttpOperation()
        cmd_op.http = CMDHttpAction()
        cmd_op.http.path = path

        if op.x_ms_long_running_operation:
            cmd_op.long_running = True

        request = CMDHttpRequest()
        request.method = method
        if op.parameters:
            for parameter in op.parameters:
                p = parameter
                while isinstance(p, Reference):
                    if p.ref_instance is None:
                        raise exceptions.InvalidSwaggerValueError("Reference not exist", key=p.ref)
                    p = p.ref_instance

                if isinstance(p, PathParameter):
                    if request.path is None:
                        request.path = CMDHttpRequestPath()

                    param = p.to_cmd_model()

                    if request.path.params is None:
                        request.path.params = []
                    request.path.params.append(param)

                elif isinstance(p, QueryParameter):
                    if request.query is None:
                        request.query = CMDHttpRequestQuery()

                    param = p.to_cmd_model()

                    if request.query.params is None:
                        request.query.params = []
                    request.query.params.append(param)

                elif isinstance(p, HeaderParameter):
                    if request.header is None:
                        request.header = CMDHttpRequestHeader()

                    param = p.to_cmd_model()

                    if request.header.params is None:
                        request.header.params = []
                    request.header.params.append(param)

                    if p.x_ms_client_request_id:
                        request.header.client_request_id = param.name
                    elif param.name == "x-ms-client-request-id":
                        request.header.client_request_id = param.name

                elif isinstance(p, BodyParameter):
                    assert request.body is None
                    request.body = CMDHttpBody()

                elif isinstance(p, FormDataParameter):
                    # TODO: For DataPlan
                    pass
                else:
                    raise NotImplementedError()

    # def _build_http_operation_for_get(self, path, op: Operation):
    #     self._build_http_operation(path, op)
    #
    # def _build_http_operation_for_put(self, path, op: Operation, update_mode=False):
    #     self._build_http_operation(path, op)
    #
    # def _build_http_operation_for_patch(self, path, op: Operation):
    #     self._build_http_operation(path, op)
    #
    # def _build_http_operation_for_delete(self, path, op: Operation):
    #     self._build_http_operation(path, op)
    #
    # def _build_http_operation_for_post(self, path, op: Operation):
    #     self._build_http_operation(path, op)
    #
    # def _build_http_operation_for_head(self, path, op: Operation):
    #     # check for existence or get header in response such as EntityTags
    #     self._build_http_operation(path, op)

