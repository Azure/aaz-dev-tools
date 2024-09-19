import logging
import re

from pluralizer import Pluralizer
from abc import abstractmethod, ABC

from command.model.configuration import CMDCommandGroup, CMDCommand, CMDHttpOperation, CMDHttpRequest, \
    CMDSchemaDefault, CMDHttpResponseJsonBody, CMDArrayOutput, CMDJsonInstanceUpdateAction, \
    CMDInstanceUpdateOperation, CMDRequestJson, DEFAULT_CONFIRMATION_PROMPT, CMDClsSchemaBase, CMDHttpResponse, \
    CMDResponseJson, CMDResource
from swagger.model.schema.cmd_builder import CMDBuilder
from swagger.model.schema.fields import MutabilityEnum
from swagger.model.schema.path_item import PathItem
from swagger.model.schema.x_ms_parameterized_host import XmsParameterizedHost
from swagger.model.specs import SwaggerLoader
from swagger.model.specs._utils import operation_id_separate, camel_case_to_snake_case, get_url_path_valid_parts
from swagger.model.schema.typespec.path_item import TypeSpecPathItem
from utils import exceptions
from utils.config import Config
from utils.plane import PlaneEnum
from utils.error_format import AAZErrorFormatEnum

logger = logging.getLogger('backend')


class _CommandGenerator(ABC):

    _pluralizer = Pluralizer()

    @staticmethod
    def generate_command_version(resource):
        return resource.version

    @classmethod
    def generate_command(cls, path_item, resource, instance_var, cmd_builder, op):
        command = CMDCommand()
        command.version = cls.generate_command_version(resource)
        command.resources = [
            resource.to_cmd() if not isinstance(resource, CMDResource) else resource
        ]

        cmd_builder.apply_cls_definitions(op)

        assert isinstance(op, CMDHttpOperation)
        if not cls._set_api_version_parameter(op.http.request, api_version=resource.version):
            logger.warning(
                f"Cannot Find api version parameter: {cmd_builder.path}, '{cmd_builder.method}' : {path_item.traces}")

        command.description = op.description
        command.operations = [op]

        command.generate_args()
        command.generate_outputs(pageable=cmd_builder.get_pageable(path_item, op))

        output = command.outputs[0] if command.outputs else None
        command.name = cls._generate_command_name(path_item, resource, cmd_builder.method, output)

        return command

    @classmethod
    def generate_generic_update_command(cls, path_item, resource, instance_var, cmd_builder, get_op, put_op):
        command = CMDCommand()
        command.version = cls.generate_command_version(resource)
        command.resources = [
            resource.to_cmd() if not isinstance(resource, CMDResource) else resource
        ]
        assert path_item.get is not None
        assert path_item.put is not None

        cmd_builder.apply_cls_definitions(get_op, put_op)

        if put_op.http.request.body is None:
            return None

        if not cls._set_api_version_parameter(get_op.http.request, api_version=resource.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'get' : {path_item.traces}")
        if not cls._set_api_version_parameter(put_op.http.request, api_version=resource.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'put' : {path_item.traces}")

        if not command.build_output_by_operation(get_op):
            return None

        if not command.build_output_by_operation(put_op):
            return None

        cls._filter_generic_update_parameters(get_op, put_op)

        command.description = put_op.description
        json_update_op = cls._generate_instance_update_operation(put_op, instance_var)
        command.operations = [
            get_op,
            json_update_op,
            put_op
        ]

        command.generate_args()
        command.generate_outputs()

        assert command.outputs

        group_name = cls.generate_command_group_name_by_resource(
            resource_path=resource.path, rp_name=resource.rp_name)
        command.name = f"{group_name} update"
        return command

    @staticmethod
    def _set_api_version_parameter(request, api_version):
        assert isinstance(request, CMDHttpRequest)
        assert isinstance(api_version, str)
        find_api_version = False
        query = request.query
        if query is not None:
            for idx in range(len(query.params)):
                param = query.params[idx]
                if param.name == "api-version":
                    param.default = CMDSchemaDefault()
                    param.default.value = api_version
                    param.read_only = True
                    param.const = True
                    if query.consts is None:
                        query.consts = []
                    query.consts.append(param)
                    query.params.pop(idx)
                    find_api_version = True
                    break
        path = request.path
        if not find_api_version and path is not None and path.params:
            # some data plane module contains apiversion in their host template
            for idx in range(len(path.params)):
                param = path.params[idx]
                if param.name.lower() == "apiversion":
                    param.default = CMDSchemaDefault()
                    param.default.value = api_version
                    param.read_only = True
                    param.const = True
                    if path.consts is None:
                        path.consts = []
                    path.consts.append(param)
                    path.params.pop(idx)
                    find_api_version = True
                    break
        return find_api_version

    @classmethod
    def generate_command_group_name_by_resource(cls, resource_path, rp_name):
        valid_parts = get_url_path_valid_parts(resource_path, rp_name)

        names = []

        # add resource provider name as command group name
        for rp_part in rp_name.split('.'):
            if rp_part.lower() in ("microsoft", "azure"):
                # ignore microsoft and azure keywards
                continue
            names.append(camel_case_to_snake_case(rp_part, '-'))

        for part in valid_parts[1:]:  # ignore first part to avoid include resource provider
            if re.match(r'^\{[^{}]*}$', part):
                continue
            # handle part such as `docs('{key}')`
            part = re.sub(r"\{[^{}]*}", '', part)
            part = re.sub(r"[^a-zA-Z0-9\-._]", '', part)
            name = camel_case_to_snake_case(part, '-')
            singular_name = cls._pluralizer.singular(name) or name
            names.append(singular_name)
        return " ".join([name for name in names if name])

    @classmethod
    def _generate_command_name(cls, path_item, resource, method, output):
        group_name = cls.generate_command_group_name_by_resource(
            resource_path=resource.path, rp_name=resource.rp_name)
        url_path = resource.id.split("?")[0]
        if method == "get":
            if url_path.endswith("/{}"):
                command_name = f"{group_name} show"
            else:
                sub_url_path = url_path + "/{}"
                if path_item.get.x_ms_pageable:
                    command_name = f"{group_name} list"
                elif isinstance(output, CMDArrayOutput) and output.next_link is not None:
                    command_name = f"{group_name} list"
                    # logger.debug(
                    #     f"Command Name For Get set to 'list' by nexLink: {resource.path} :"
                    #     f" {path_item.get.operation_id} : {path_item.traces}"
                    # )
                elif sub_url_path in resource.resource_provider.get_resource_map():
                    command_name = f"{group_name} list"
                    # logger.debug(
                    #     f"Command Name For Get set to 'list' by sub_url_path: {resource.path} :"
                    #     f" {path_item.get.operation_id} : {path_item.traces}"
                    # )
                else:
                    # by operation id
                    op_parts = operation_id_separate(path_item.get.operation_id)
                    contain_list = False
                    contain_get = False
                    for part in op_parts:
                        if "list" in part:
                            contain_list = True
                        elif "get" in part:
                            contain_get = True
                    if contain_list and not contain_get:
                        command_name = f"{group_name} list"
                        # logger.debug(
                        #     f"Command Name For Get set to 'list' by operation_id: {resource.path} :"
                        #     f" {path_item.get.operation_id} : {path_item.traces}"
                        # )
                    elif contain_get and not contain_list:
                        command_name = f"{group_name} show"
                        # logger.debug(
                        #     f"Command Name For Get set to 'show' by operation_id: {resource.path} :"
                        #     f" {path_item.get.operation_id} : {path_item.traces}"
                        # )
                    else:
                        command_name = f"{group_name} " + '-'.join(op_parts[-1])
                        logger.warning(
                            f"Command Name For Get set by operation_id: {command_name} : {resource.path} :"
                            f" {path_item.get.operation_id} : {path_item.traces}"
                        )

        elif method == "delete":
            command_name = f"{group_name} delete"
        elif method == "put":
            command_name = f"{group_name} create"
        elif method == "patch":
            command_name = f"{group_name} update"
        elif method == "head":
            command_name = f"{group_name} head"
        elif method == "post":
            if not url_path.endswith("/{}") and not path_item.get and not path_item.put and not path_item.patch and \
                    not path_item.delete and not path_item.head:
                # directly use group name as command name
                command_name = group_name
            else:
                op_parts = operation_id_separate(path_item.post.operation_id)
                command_name = f"{group_name} " + '-'.join(op_parts[-1])
                logger.warning(f"Command Name For Post set by operation_id: {command_name} : {resource.path} :"
                               f" {path_item.post.operation_id} : {path_item.traces}")
        else:
            raise NotImplementedError()
        return command_name

    # For update
    @staticmethod
    def _generate_instance_update_operation(put_op, instance_var):
        json_update_op = CMDInstanceUpdateOperation()
        json_update_op.instance_update = CMDJsonInstanceUpdateAction()
        json_update_op.instance_update.ref = instance_var
        json_update_op.instance_update.json = CMDRequestJson()
        json_update_op.instance_update.json.schema = put_op.http.request.body.json.schema

        put_op.http.request.body.json.ref = instance_var
        put_op.http.request.body.json.schema = None
        return json_update_op

    @staticmethod
    def _filter_generic_update_parameters(get_op, put_op):
        """Get operation may contain useless query or header parameters for update, ignore them"""
        get_request = get_op.http.request
        put_request = put_op.http.request

        query_name_set = set()
        if put_request.query:
            for param in put_request.query.params:
                query_name_set.add(param.name)
        if get_request.query:
            get_query_params = []
            for param in get_request.query.params:
                if param.name in query_name_set:
                    get_query_params.append(param)
                elif param.required:
                    print(f"Query param {param.name} in Get ({get_op.operation_id}) not in Put ({put_op.operation_id})")
                    get_query_params.append(param)
            get_request.query.params = get_query_params

        header_name_set = set()
        if put_request.header:
            for param in put_request.header.params:
                header_name_set.add(param.name)
        if get_request.header:
            get_header_params = []
            for param in get_request.header.params:
                if param.name in header_name_set:
                    get_header_params.append(param)
                elif param.required:
                    print(
                        f"Header param {param.name} in Get ({get_op.operation_id}) not in Put ({put_op.operation_id})")
                    get_header_params.append(param)
            get_request.header.params = get_header_params

    @staticmethod
    def _merge_update_commands(patch_command, generic_command):
        # TODO: merge patch command and generic command into one
        return generic_command

    @staticmethod
    def optimize_command_description(command):
        if command.description:
            keywords = command.description.split(' ')
            if command.name.lower() == "show":
                keywords[0] = "Get"
            elif command.name.lower() == "list":
                keywords[0] = "List"
            elif command.name.lower() == "delete":
                keywords[0] = "Delete"
            elif command.name.lower() == "create":
                if len(keywords) > 1 and keywords[1].lower() == "or":
                    keywords = ["Create", *keywords[3:]]
                else:
                    keywords[0] = "Create"
            elif command.name.lower() == "update":
                if len(keywords) > 1 and keywords[1].lower() == "or":
                    keywords = ["Update", *keywords[3:]]
                else:
                    keywords[0] = "Update"
            command.description = " ".join(keywords)
    
    @staticmethod
    def format_http_operation(op, instance_var):
        assert isinstance(op, CMDHttpOperation)
        error_format = None
        for resp in op.http.responses:
            if resp.is_error:
                if not isinstance(resp.body, CMDHttpResponseJsonBody):
                    if not resp.body:
                        raise exceptions.InvalidAPIUsage(
                            f"Invalid `Error` response schema in operation `{op.operation_id}`: "
                            f"Missing `schema` property in response "
                            f"`{resp.status_codes or 'default'}`."
                        )
                    else:
                        raise exceptions.InvalidAPIUsage(
                            f"Invalid `Error` response schema in operation `{op.operation_id}`: "
                            f"Only support json schema, current is '{type(resp.body)}' in response "
                            f"`{resp.status_codes or 'default'}`"
                        )
                schema = resp.body.json.schema
                if not isinstance(schema, CMDClsSchemaBase):
                    raise NotImplementedError()
                name = schema.type[1:]
                if not error_format:
                    error_format = name
                if error_format != name:
                    raise exceptions.InvalidAPIUsage(
                        f"Invalid `Error` response schema in operation `{op.operation_id}`: "
                        f"Multiple schema formats are founded: {name}, {error_format}"
                    )
            else:
                if resp.body is None:
                    continue
                if isinstance(resp.body, CMDHttpResponseJsonBody):
                    resp.body.json.var = instance_var

        if not error_format:
            # TODO: refactor the following line to support data plane command generation.
            if Config.DEFAULT_PLANE != PlaneEnum.Mgmt:
                raise exceptions.InvalidAPIUsage(
                    f"Missing `Error` response schema in operation `{op.operation_id}`: "
                    f"Please define the `default` response in swagger for error."
                )
            # use MgmtErrorFormat for default error response schema
            error_format = AAZErrorFormatEnum.MgmtErrorFormat
            err_response = CMDHttpResponse()
            err_response.is_error = True
            err_response.status_codes = []
            err_response.body = CMDHttpResponseJsonBody()
            err_response.body.json = CMDResponseJson()
            err_schema = CMDClsSchemaBase()
            err_schema._type = f"@{error_format}"
            err_response.body.json.schema = err_schema
            op.http.responses.append(err_response)
        elif not AAZErrorFormatEnum.validate(error_format):
            raise exceptions.InvalidAPIUsage(
                f"Invalid `Error` response schema in operation `{op.operation_id}`: "
                f"Invalid error format `{error_format}`. Support `ODataV4Format` and `MgmtErrorFormat` only"
            )

        return op

    def create_draft_command_group(self, resource,
                                   instance_var,
                                   update_by=None,
                                   methods=('get', 'delete', 'put', 'post', 'head', 'patch'),
                                   **kwargs):

        command_group = CMDCommandGroup()
        command_group.commands = []
        path_item = self.get_path_item(resource)
        parameterized_host = self.get_parameterized_host(resource)

        if path_item.get is not None and 'get' in methods:
            cmd_builder = CMDBuilder(path=resource.path, method='get', mutability=MutabilityEnum.Read,
                                     parameterized_host=parameterized_host)
            op = self.generate_operation(cmd_builder, path_item, instance_var)
            show_or_list_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
            command_group.commands.append(show_or_list_command)

        if path_item.delete is not None and 'delete' in methods:
            cmd_builder = CMDBuilder(path=resource.path, method='delete', mutability=MutabilityEnum.Create,
                                     parameterized_host=parameterized_host)
            op = self.generate_operation(cmd_builder, path_item, instance_var)
            delete_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
            delete_command.confirmation = DEFAULT_CONFIRMATION_PROMPT   # add confirmation for delete command by default
            command_group.commands.append(delete_command)

        if path_item.put is not None and 'put' in methods:
            cmd_builder = CMDBuilder(path=resource.path, method='put', mutability=MutabilityEnum.Create,
                                     parameterized_host=parameterized_host)
            op = self.generate_operation(cmd_builder, path_item, instance_var)
            create_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
            command_group.commands.append(create_command)

        if path_item.post is not None and 'post' in methods:
            cmd_builder = CMDBuilder(path=resource.path, method='post', mutability=MutabilityEnum.Create,
                                     parameterized_host=parameterized_host)
            op = self.generate_operation(cmd_builder, path_item, instance_var)
            action_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
            command_group.commands.append(action_command)

        if path_item.head is not None and 'head' in methods:
            cmd_builder = CMDBuilder(path=resource.path, method='head', mutability=MutabilityEnum.Read,
                                     parameterized_host=parameterized_host)
            op = self.generate_operation(cmd_builder, path_item, instance_var)
            head_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
            command_group.commands.append(head_command)

        # update command
        if update_by is None:
            update_by_patch_command = None
            update_by_generic_command = None
            if path_item.patch is not None and 'patch' in methods:
                cmd_builder = CMDBuilder(path=resource.path, method='patch', mutability=MutabilityEnum.Update,
                                         parameterized_host=parameterized_host)
                op = self.generate_operation(cmd_builder, path_item, instance_var)
                update_by_patch_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
            if path_item.get is not None and path_item.put is not None and 'get' in methods and 'put' in methods:
                cmd_builder = CMDBuilder(path=resource.path,
                                         parameterized_host=parameterized_host)
                get_op = self.generate_operation(
                    cmd_builder, path_item, instance_var, method='get', mutability=MutabilityEnum.Read)
                put_op = self.generate_operation(
                    cmd_builder, path_item, instance_var, method='put', mutability=MutabilityEnum.Update)
                update_by_generic_command = self.generate_generic_update_command(path_item, resource, instance_var, cmd_builder, get_op, put_op)
            # generic update command first, patch update command after that
            if update_by_generic_command:
                command_group.commands.append(update_by_generic_command)
            elif update_by_patch_command:
                command_group.commands.append(update_by_patch_command)
        else:
            if update_by == 'GenericOnly':
                if path_item.get is None or path_item.put is None:
                    raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: resource needs to have 'get' and 'put' operations: '{resource}'")
                if 'get' not in methods or 'put' not in methods:
                    raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: '{resource}': 'get' or 'put' not in methods: '{methods}'")
                cmd_builder = CMDBuilder(path=resource.path,
                                         parameterized_host=parameterized_host)
                get_op = self.generate_operation(
                    cmd_builder, path_item, instance_var, method='get', mutability=MutabilityEnum.Read)
                put_op = self.generate_operation(
                    cmd_builder, path_item, instance_var, method='put', mutability=MutabilityEnum.Update)
                generic_update_command = self.generate_generic_update_command(path_item, resource, instance_var, cmd_builder, get_op, put_op)
                if generic_update_command is None:
                    raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: failed to generate generic update: '{resource}'")
                command_group.commands.append(generic_update_command)
                # elif 'update_by' in kwargs:
                #     logger.error(f'Failed to generate generic update for resource: {resource}')
            elif update_by == 'PatchOnly':
                if path_item.patch is None:
                    raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: resource needs to have 'patch' operation: '{resource}'")
                if 'patch' not in methods:
                    raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: '{resource}': 'patch' not in methods: '{methods}'")
                cmd_builder = CMDBuilder(path=resource.path, method='patch', mutability=MutabilityEnum.Update,
                                         parameterized_host=parameterized_host)
                op = self.generate_operation(cmd_builder, path_item, instance_var)
                patch_update_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
                command_group.commands.append(patch_update_command)
            # elif update_by == 'GenericAndPatch':
            #     # TODO: add support for generic and patch merge
            #     if path_item.get is None or path_item.put is None or path_item.patch is None:
            #         raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: resource needs to have 'get' and 'put' and 'patch' operation: '{resource}'")
            #     if 'get' not in methods or 'put' not in methods or 'patch' not in methods:
            #         raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: '{resource}': 'get' or 'put' or 'patch' not in methods: '{methods}'")
            #     cmd_builder = CMDBuilder(path=resource.path,
            #                              parameterized_host=parameterized_host)
            #     get_op = self.generate_operation(
            #         cmd_builder, path_item, instance_var, method='get', mutability=MutabilityEnum.Read)
            #     put_op = self.generate_operation(
            #         cmd_builder, path_item, instance_var, method='put', mutability=MutabilityEnum.Update)
            #     generic_update_command = self.generate_generic_update_command(path_item, resource, instance_var, cmd_builder, get_op, put_op)
            #     if generic_update_command is None:
            #         raise exceptions.InvalidAPIUsage(f"Invalid update_by resource: failed to generate generic update: '{resource}'")
            #     cmd_builder = CMDBuilder(path=resource.path, method='patch', mutability=MutabilityEnum.Update,
            #                              parameterized_host=parameterized_host)
            #     op = self.generate_operation(cmd_builder, path_item, instance_var)
            #     patch_update_command = self.generate_command(path_item, resource, instance_var, cmd_builder, op)
            #     generic_and_patch_update_command = self._merge_update_commands(
            #         patch_command=patch_update_command, generic_command=generic_update_command
            #     )
            #     command_group.commands.append(generic_and_patch_update_command)
            elif update_by != 'None':
                raise exceptions.InvalidAPIUsage(f"Invalid update_by value: {update_by} : only support ['GenericOnly', 'PatchOnly', 'None'] values")

        for command in command_group.commands:
            parts = command.name.split(' ')
            group_name = ' '.join(parts[:-1])
            if command_group.name:
                assert group_name == command_group.name
            else:
                command_group.name = group_name
            command.name = parts[-1]  # remove the command group name parts
            self.optimize_command_description(command)

        return command_group

    @abstractmethod
    def load_resources(self, resources):
        raise NotImplementedError()
    
    @abstractmethod
    def generate_operation(self, cmd_builder, path_item, instance_var, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_path_item(self, resource):
        raise NotImplementedError()
    
    @abstractmethod
    def get_parameterized_host(self, resource):
        raise NotImplementedError()


class SwaggerCommandGenerator(_CommandGenerator):

    def __init__(self):
        super().__init__()
        self.loader = SwaggerLoader()

    def load_resources(self, resources):
        for resource in resources:
            self.loader.load_file(resource.file_path)
        self.loader.link_swaggers()
    
    def get_path_item(self, resource):
        swagger = self.loader.get_loaded(resource.file_path)
        assert swagger is not None
        path_item = swagger.paths.get(resource.path, None)
        if path_item is None:
            path_item = swagger.x_ms_paths.get(resource.path, None)
        return path_item
    
    def get_parameterized_host(self, resource):
        swagger = self.loader.get_loaded(resource.file_path)
        if swagger.x_ms_parameterized_host:
            return swagger.x_ms_parameterized_host
        elif swagger.base_path:
            return XmsParameterizedHost({"hostTemplate": swagger.base_path})

    def generate_operation(self, cmd_builder, path_item, instance_var, **kwargs):
        assert isinstance(path_item, PathItem)
        op = cmd_builder(path_item, **kwargs)
        return self.format_http_operation(op, instance_var)


class TypespecCommandGenerator(_CommandGenerator):

    def __init__(self):
        super().__init__()
        self._path_items = {}

    def load_resources(self, resources):
        for resource in resources:
            self._path_items[resource['path']] = TypeSpecPathItem(resource['pathItem'])
    
    def get_path_item(self, resource):
        return self._path_items.get(resource.path, None)

    def generate_operation(self, cmd_builder, path_item, instance_var, **kwargs):
        assert isinstance(path_item, TypeSpecPathItem)
        method = kwargs.get('method', cmd_builder.method)
        op = getattr(path_item, method, None)
        if op is None:
            return None
        mutability = kwargs.get('mutability', cmd_builder.mutability)
        op = getattr(op, mutability, None)
        if op is None:
            return None
        return self.format_http_operation(op, instance_var)
    
    def get_parameterized_host(self, resource):
        return None
