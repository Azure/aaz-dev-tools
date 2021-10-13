from swagger.model.specs import SwaggerLoader
from swagger.model.schema.path_item import PathItem
from swagger.model.schema.fields import MutabilityEnum
from swagger.model.schema.x_ms_pageable import XmsPageable
from command.model.configuration import CMDCommandGroup, CMDCommand, CMDHttpOperation, CMDHttpRequest, \
    CMDSchemaDefault, CMDHttpJsonBody, CMDObjectOutput, CMDArrayOutput, CMDResource, CMDGenericInstanceUpdateAction, \
    CMDGenericInstanceUpdateMethod, CMDJsonInstanceUpdateAction, CMDInstanceUpdateOperation, CMDJson, CMDHelp
import logging

logger = logging.getLogger('backend')


class BuildInVariants:

    Instance = "$instance"


class CommandConfigurationGenerator:

    def __init__(self):
        self.loader = SwaggerLoader()

    def load_resources(self, resources):
        for resource in resources:
            self.create_commands_for_resource(resource)

    def create_commands_for_resource(self, resource):
        swagger = self.loader.load_file(resource.file_path)
        self.loader.link_swaggers()

        path_item = swagger.paths.get(resource.path, None)
        if path_item is None:
            path_item = swagger.x_ms_paths.get(resource.path, None)

        assert isinstance(path_item, PathItem)
        if path_item.get is not None:
            self.generate_show_or_list_command(path_item, resource)
        if path_item.delete is not None:
            self.generate_delete_command(path_item, resource)
        if path_item.put is not None:
            self.generate_create_command(path_item, resource)
        if (path_item.get is not None and path_item.put is not None) or path_item.patch is not None:
            self.generate_update_command(path_item, resource)
        if path_item.post is not None:
            self.generate_post_command(path_item, resource)
        if path_item.head is not None:
            self.generate_head_command(path_item, resource)

    @staticmethod
    def _set_api_version_parameter(request, api_version):
        assert isinstance(request, CMDHttpRequest)
        assert isinstance(api_version, str)
        find_api_version = False
        request_params = request.query
        if request_params is not None:
            for idx in range(len(request_params.params)):
                param = request_params.params[idx]
                if param.name == "api-version":
                    param.default = CMDSchemaDefault()
                    param.default.value = api_version
                    param.read_only = True
                    if request_params.consts is None:
                        request_params.consts = []
                    request_params.consts.append(param)
                    request_params.params = request_params.params[:idx] + request_params.params[idx+1:]
                    find_api_version = True
                    break
        return find_api_version

    @staticmethod
    def _generate_command_help(op_description):
        # TODO:
        h = CMDHelp()
        h.short = op_description
        return h

    @staticmethod
    def _generate_command_arguments(command):
        args = []
        for op in command.operations:
            args.extend(op.generate_args())
        return args

    @staticmethod
    def _merge_commands(prim_command, second_command):
        # TODO:
        pass

    def generate_output(self, op, pageable: XmsPageable = None):
        assert isinstance(op, CMDHttpOperation)
        output = None
        for resp in op.http.responses:
            if resp.is_error:
                continue
            if resp.body is None:
                continue
            if isinstance(resp.body, CMDHttpJsonBody):
                resp.body.json.var = BuildInVariants.Instance
                if pageable:
                    output = CMDArrayOutput()
                    output.next_link = f"{resp.body.json.var}.{pageable.next_link_name}"
                    output.ref = f"{resp.body.json.var}.{pageable.item_name}"
                else:
                    output = CMDObjectOutput()
                    output.ref = resp.body.json.var
                output.client_flatten = True
            else:
                raise NotImplementedError()
        return output

    def generate_show_or_list_command(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]

        op = path_item.to_cmd_operation(resource.path, method='get', mutability=MutabilityEnum.Read)

        assert isinstance(op, CMDHttpOperation)
        if not self._set_api_version_parameter(op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'get' : {path_item.traces}")

        output = self.generate_output(op, pageable=path_item.get.x_ms_pageable)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        self._generate_command_arguments(command)

        return command

    def generate_delete_command(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]

        op = path_item.to_cmd_operation(resource.path, method='delete', mutability=MutabilityEnum.Create)

        assert isinstance(op, CMDHttpOperation)
        if not self._set_api_version_parameter(op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'delete' : {path_item.traces}")

        output = self.generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        self._generate_command_arguments(command)

        return command

    def generate_create_command(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]

        op = path_item.to_cmd_operation(resource.path, method='put', mutability=MutabilityEnum.Create)

        assert isinstance(op, CMDHttpOperation)
        if not self._set_api_version_parameter(op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'put' : {path_item.traces}")

        output = self.generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        self._generate_command_arguments(command)

        return command

    def generate_post_command(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]

        op = path_item.to_cmd_operation(resource.path, method='post', mutability=MutabilityEnum.Create)

        assert isinstance(op, CMDHttpOperation)
        if not self._set_api_version_parameter(op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'post' : {path_item.traces}")

        output = self.generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        self._generate_command_arguments(command)

        return command

    def generate_head_command(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]

        op = path_item.to_cmd_operation(resource.path, method='head', mutability=MutabilityEnum.Read)

        assert isinstance(op, CMDHttpOperation)
        if not self._set_api_version_parameter(op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'head' : {path_item.traces}")

        output = self.generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        self._generate_command_arguments(command)
        return command

    def _generate_instance_update_operations(self, put_op):

        json_update_op = CMDInstanceUpdateOperation()
        json_update_op.instance_update = CMDJsonInstanceUpdateAction()
        json_update_op.instance_update.instance = BuildInVariants.Instance
        json_update_op.instance_update.json = CMDJson()
        json_update_op.instance_update.json.schema = put_op.http.request.body.json.schema

        generic_update_op = CMDInstanceUpdateOperation()
        generic_update_op.instance_update = CMDGenericInstanceUpdateAction()
        generic_update_op.instance_update.instance = BuildInVariants.Instance
        generic_update_op.instance_update.client_flatten = True
        generic_update_op.instance_update.generic = CMDGenericInstanceUpdateMethod()

        put_op.http.request.body.json.ref = BuildInVariants.Instance
        put_op.http.request.body.json.schema = None
        return json_update_op, generic_update_op

    def _generate_update_command_for_put(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]
        if path_item.get is None:
            return None
        get_op = path_item.to_cmd_operation(resource.path, method='get', mutability=MutabilityEnum.Read)
        put_op = path_item.to_cmd_operation(resource.path, method='put', mutability=MutabilityEnum.Update)
        if put_op.http.request.body is None:
            return None

        if not self._set_api_version_parameter(get_op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'get' : {path_item.traces}")
        if not self._set_api_version_parameter(put_op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'put' : {path_item.traces}")
        output = self.generate_output(put_op)
        if output is None:
            return None

        # assert output is not None
        command.outputs = []
        command.outputs.append(output)
        command.help = self._generate_command_help(put_op.description)

        json_update_op, generic_update_op = self._generate_instance_update_operations(put_op)
        command.operations = [
            get_op,
            json_update_op,
            generic_update_op,
            put_op
        ]
        self._generate_command_arguments(command)
        return command

    def _generate_update_command_for_patch(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]
        patch_op = path_item.to_cmd_operation(resource.path, method='patch', mutability=MutabilityEnum.Update)
        if not self._set_api_version_parameter(patch_op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'patch' : {path_item.traces}")
        output = self.generate_output(patch_op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)
        command.help = self._generate_command_help(patch_op.description)
        command.operations = [
            patch_op
        ]
        self._generate_command_arguments(command)
        return command

    def generate_update_command(self, path_item, resource):
        put_command = None
        patch_command = None
        if path_item.put is not None:
            put_command = self._generate_update_command_for_put(path_item, resource)

        if path_item.patch is not None:
            patch_command = self._generate_update_command_for_patch(path_item, resource)

        if put_command and patch_command:
            return self._merge_commands(put_command, patch_command)
        else:
            return put_command or patch_command
