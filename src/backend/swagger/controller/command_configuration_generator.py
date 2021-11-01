from swagger.model.specs import SwaggerLoader
from swagger.model.schema.path_item import PathItem
from swagger.model.schema.fields import MutabilityEnum
from swagger.model.schema.x_ms_pageable import XmsPageable
from command.model.configuration import CMDCommandGroup, CMDCommand, CMDHttpOperation, CMDHttpRequest, \
    CMDSchemaDefault, CMDHttpJsonBody, CMDObjectOutput, CMDArrayOutput, CMDResource, CMDGenericInstanceUpdateAction, \
    CMDGenericInstanceUpdateMethod, CMDJsonInstanceUpdateAction, CMDInstanceUpdateOperation, CMDJson, CMDHelp, CMDArgGroup, CMDDiffLevelEnum
import logging
from swagger.model.specs._utils import map_path_2_repo

logger = logging.getLogger('backend')


class BuildInVariants:

    Query = "$Query"
    Header = "$Header"
    Path = "$Path"

    Instance = "$Instance"


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
    def _group_arguments(arguments):
        arg_groups = {}
        for arg in arguments:
            group_name = arg.group or ""
            if group_name not in arg_groups:
                arg_groups[group_name] = {}
            if arg.var not in arg_groups[group_name]:
                arg_groups[group_name][arg.var] = arg

        groups = []
        for group_name, args in arg_groups.items():
            group = CMDArgGroup()
            group.name = group_name
            group.args = [arg for arg in args.items()]
            groups.append(group)
        return groups or None

    # def _generate_command_arguments(self, command, file_path):
    #     arguments = {}
    #     for op in command.operations:
    #         for arg in op.generate_args():
    #             if arg.var not in arguments:
    #                 arguments[arg.var] = arg
    #     used_options = {}
    #     for arg in arguments.values():
    #         if arg.options:
    #             for option in arg.options:
    #                 if option in used_options:
    #                     print(f"Duplicated Option Value: {option} : {arg.var} with {used_options[option]} : {command.operations[-1].operation_id} : {map_path_2_repo(file_path)}")
    #                 used_options[option] = arg.var
    #     return [*arguments.values()]

    def _generate_command_arguments(self, command, file_path):
        arguments = {}
        for op in command.operations:
            for arg in op.generate_args():
                if arg.var not in arguments:
                    arguments[arg.var] = arg

        dropped_args = set()
        used_args = set()
        for arg in arguments.values():
            used_args.add(arg.var)
            if arg.var in dropped_args or not arg.options:
                continue
            r_arg = None
            for v in arguments.values():
                if v.var in used_args or v.var in dropped_args or arg.var == v.var or not v.options:
                    continue
                if not set(arg.options).isdisjoint(v.options):
                    r_arg = v
                    break
            if r_arg:
                replace, diff_a = self._can_replace_argument(r_arg, arg)
                if replace:
                    arg.ref_schema.arg = r_arg.var
                    dropped_args.add(arg.var)
                else:
                    replace, diff_b = self._can_replace_argument(arg, r_arg)
                    if replace:
                        r_arg.ref_schema.arg = arg.var
                        dropped_args.add(r_arg.var)
                    else:
                        print(f"Duplicated Option Value: {set(arg.options).intersection(r_arg.options)} : {arg.var} with {r_arg.var} : {command.operations[-1].operation_id}: {diff_a} : {diff_b} : {map_path_2_repo(file_path)}")

        return [arg for var, arg in arguments.items() if var not in dropped_args]

    @staticmethod
    def _can_replace_argument(arg, old_arg):
        arg_prefix = arg.var.split('.')[0]
        old_prefix = old_arg.var.split('.')[0]
        if old_prefix in (BuildInVariants.Query, BuildInVariants.Header, BuildInVariants.Path):
            # replace argument should only be in body
            return False, "Replace argument should only be in body"
        if arg_prefix in (BuildInVariants.Query, BuildInVariants.Header):
            return False, "Only support path or body argument to replace"
        elif arg_prefix == BuildInVariants.Path:
            # path argument
            arg_schema_required = arg.ref_schema.required
            arg_schema_name = arg.ref_schema.name
            try:
                arg.ref_schema.required = old_arg.ref_schema.required
                if old_arg.ref_schema.name == "name" and "name" in arg.options:
                    arg.ref_schema.name = "name"
                diff = arg.ref_schema.diff(old_arg.ref_schema, level=CMDDiffLevelEnum.Structure)
                if diff:
                    return False, diff
                return True, None
            finally:
                arg.ref_schema.name = arg_schema_name
                arg.ref_schema.required = arg_schema_required
        else:
            # body argument
            diff = arg.ref_schema.diff(old_arg.ref_schema, level=CMDDiffLevelEnum.Structure)
            if diff:
                return False, diff
            return True, None

    @staticmethod
    def _merge_commands(prim_command, second_command):
        # TODO:
        pass

    def _generate_output(self, op, pageable: XmsPageable = None):
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

        output = self._generate_output(op, pageable=path_item.get.x_ms_pageable)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        arguments = self._generate_command_arguments(command, file_path=resource.file_path)
        command.arg_groups = self._group_arguments(arguments)

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

        output = self._generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        arguments = self._generate_command_arguments(command, file_path=resource.file_path)
        command.arg_groups = self._group_arguments(arguments)

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

        output = self._generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        arguments = self._generate_command_arguments(command, file_path=resource.file_path)
        command.arg_groups = self._group_arguments(arguments)

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

        output = self._generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        arguments = self._generate_command_arguments(command, file_path=resource.file_path)
        command.arg_groups = self._group_arguments(arguments)

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

        output = self._generate_output(op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        arguments = self._generate_command_arguments(command, file_path=resource.file_path)
        command.arg_groups = self._group_arguments(arguments)

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

    @staticmethod
    def _sync_generic_update(get_op, put_op):
        """get operation may contains useless query or header parameters for update, ignore them"""
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
                    print(f"Header param {param.name} in Get ({get_op.operation_id}) not in Put ({put_op.operation_id})")
                    get_header_params.append(param)
            get_request.header.params = get_header_params

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
        output = self._generate_output(put_op)
        if output is None:
            return None

        self._sync_generic_update(get_op, put_op)

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

        arguments = self._generate_command_arguments(command, file_path=resource.file_path)
        command.arg_groups = self._group_arguments(arguments)

        return command

    def _generate_update_command_for_patch(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]
        patch_op = path_item.to_cmd_operation(resource.path, method='patch', mutability=MutabilityEnum.Update)
        if not self._set_api_version_parameter(patch_op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, 'patch' : {path_item.traces}")
        output = self._generate_output(patch_op)
        if output is not None:
            command.outputs = []
            command.outputs.append(output)
        command.help = self._generate_command_help(patch_op.description)
        command.operations = [
            patch_op
        ]

        arguments = self._generate_command_arguments(command, file_path=resource.file_path)
        command.arg_groups = self._group_arguments(arguments)

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
