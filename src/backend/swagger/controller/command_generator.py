import logging

from command.model.configuration import CMDCommandGroup, CMDCommand, CMDHttpOperation, CMDHttpRequest, \
    CMDSchemaDefault, CMDHttpJsonBody, CMDObjectOutput, CMDArrayOutput, CMDGenericInstanceUpdateAction, \
    CMDGenericInstanceUpdateMethod, CMDJsonInstanceUpdateAction, CMDInstanceUpdateOperation, CMDJson, CMDHelp, \
    CMDArgGroup, CMDDiffLevelEnum, \
    CMDObjectSchema, CMDArraySchema, CMDStringSchema, CMDObjectSchemaBase, CMDArraySchemaBase, CMDStringSchemaBase
from swagger.model.schema.fields import MutabilityEnum
from swagger.model.schema.path_item import PathItem
from swagger.model.schema.x_ms_pageable import XmsPageable
from swagger.model.specs import SwaggerLoader, SwaggerSpecs, DataPlaneModule, MgmtPlaneModule
from swagger.model.specs._utils import operation_id_separate, camel_case_to_snake_case
from utils import config

logger = logging.getLogger('backend')


class BuildInVariants:
    Query = "$Query"
    Header = "$Header"
    Path = "$Path"

    Instance = "$Instance"


class CommandGenerator:

    def __init__(self, module_name):
        self.loader = SwaggerLoader()
        self.specs = SwaggerSpecs(
            folder_path=config.SWAGGER_PATH
        )
        self.module, self.rps = self._setup_module(module_name)

    def _setup_module(self, module_name):
        if module_name.startswith(MgmtPlaneModule.PREFIX):
            for module in self.specs.get_mgmt_plane_modules():
                if str(module) == module_name:
                    return module, module.get_resource_providers()
                elif module_name.startswith(f"{module}/"):
                    rps = module.get_resource_providers()
                    for rp in rps:
                        if str(rp).startswith(f"{module_name}/"):
                            return rp.swagger_module, rps
        elif module_name.startswith(DataPlaneModule.PREFIX):
            for module in self.specs.get_data_plane_modules():
                if str(module) == module_name:
                    return module, module.get_resource_providers()
                elif module_name.startswith(f"{module}/"):
                    rps = module.get_resource_providers()
                    for rp in rps:
                        if str(rp).startswith(f"{module_name}/"):
                            return rp.swagger_module, rps
        else:
            raise ValueError(f"Invalid module name {module_name}")
        if self.module is None:
            raise ValueError(f"Cannot find module {module_name}")

    def load_resources(self, cmd_resources):
        # find resource by cmd_resource
        resources = {}
        for rp in self.rps:
            resource_map = rp.get_resource_map(read_only=True)
            for cmd_r in cmd_resources:
                if cmd_r.id in resources:
                    if cmd_r.version != resources[cmd_r.id].version:
                        raise ValueError(
                            f"Multi versions {cmd_r.version} and {resources[cmd_r.id].version} "
                            f"for resource {cmd_r.id}")
                    continue
                if cmd_r.id in resource_map and cmd_r.version in resource_map[cmd_r.id]:
                    resources[cmd_r.id] = resource_map[cmd_r.id][cmd_r.version]

        for cmd_r in cmd_resources:
            if cmd_r.id not in resources:
                raise ValueError(f"Resource {cmd_r.id} for version {cmd_r.version} is not exist")
            self.loader.load_file(resources[cmd_r.id].file_path)
        self.loader.link_swaggers()

        return resources

    def create_draft_command_group(self, resource):
        swagger = self.loader.get_loaded(resource.file_path)
        assert swagger is not None
        path_item = swagger.paths.get(resource.path, None)
        if path_item is None:
            path_item = swagger.x_ms_paths.get(resource.path, None)

        command_group = CMDCommandGroup()
        command_group.commands = []

        assert isinstance(path_item, PathItem)
        if path_item.get is not None:
            show_or_list_command = self.generate_command(path_item, resource, 'get', MutabilityEnum.Read)
            command_group.commands.append(show_or_list_command)

        if path_item.delete is not None:
            delete_command = self.generate_command(path_item, resource, 'delete', MutabilityEnum.Create)
            command_group.commands.append(delete_command)

        if path_item.put is not None:
            create_command = self.generate_command(path_item, resource, 'put', MutabilityEnum.Create)
            command_group.commands.append(create_command)

        if path_item.post is not None:
            action_command = self.generate_command(path_item, resource, 'post', MutabilityEnum.Create)
            command_group.commands.append(action_command)

        if path_item.head is not None:
            head_command = self.generate_command(path_item, resource, 'head', MutabilityEnum.Read)
            command_group.commands.append(head_command)

        # update command
        update_by_patch_command = None
        update_by_generic_command = None
        if path_item.patch is not None:
            update_by_patch_command = self.generate_command(path_item, resource, 'patch', MutabilityEnum.Update)
        if path_item.get is not None and path_item.put is not None:
            update_by_generic_command = self.generate_generic_update_command(path_item, resource)
        if update_by_patch_command and update_by_generic_command:
            # TODO: merge patch command and generic command
            update_command = self._merge_update_commands(
                patch_command=update_by_patch_command, generic_command=update_by_generic_command
            )
            command_group.commands.append(update_command)
        elif update_by_generic_command:
            command_group.commands.append(update_by_generic_command)
        elif update_by_patch_command:
            command_group.commands.append(update_by_patch_command)

        # TODO: generate command group name

        return command_group

    def generation_command_group_name(self, resource):
        # TODO:
        return ["COMMAND", "GROUP"]

    def generate_command(self, path_item, resource, method, mutability):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]

        op = path_item.to_cmd_operation(resource.path, method=method, mutability=mutability)

        assert isinstance(op, CMDHttpOperation)
        if not self._set_api_version_parameter(op.http.request, api_version=resource.version.version):
            logger.warning(f"Cannot Find api version parameter: {resource.path}, '{method}' : {path_item.traces}")

        output = self._generate_output(
            op,
            pageable=path_item.get.x_ms_pageable if method == 'get' else None,
        )
        if output is not None:
            command.outputs = []
            command.outputs.append(output)

        command.name = self._generate_command_name(path_item, resource, method, output)

        command.help = self._generate_command_help(op.description)
        command.operations = [op]

        arguments = self._generate_command_arguments(command)
        command.arg_groups = self._group_arguments(arguments)

        return command

    def generate_generic_update_command(self, path_item, resource):
        command = CMDCommand()
        command.resources = [
            resource.to_cmd_resource()
        ]
        assert path_item.get is not None
        assert path_item.put is not None
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

        self._filter_generic_update_parameters(get_op, put_op)

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

        arguments = self._generate_command_arguments(command)
        command.arg_groups = self._group_arguments(arguments)

        command.name = "update"
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
                    if query.consts is None:
                        query.consts = []
                    query.consts.append(param)
                    query.params.pop(idx)
                    find_api_version = True
                    break
        return find_api_version

    def _generate_output(self, op, pageable: XmsPageable = None):
        assert isinstance(op, CMDHttpOperation)
        if pageable is None and op.http.request.method == "get":
            # some list operation may miss pageable
            for resp in op.http.responses:
                if resp.is_error:
                    continue
                if not isinstance(resp.body, CMDHttpJsonBody):
                    continue
                if not isinstance(resp.body.json.schema, CMDObjectSchema):
                    continue
                body_schema = resp.body.json.schema
                if not body_schema.props:
                    continue

                has_value = False
                has_next_link = False
                for prop in body_schema.props:
                    if prop.name == "value" and isinstance(prop, CMDArraySchema):
                        has_value = True
                    if prop.name == "nextLink" and isinstance(prop, CMDStringSchema):
                        has_next_link = True
                if has_value and has_next_link:
                    pageable = XmsPageable()
                    pageable.next_link_name = "nextLink"

        output = None
        for resp in op.http.responses:
            if resp.is_error:
                continue
            if resp.body is None:
                continue
            if isinstance(resp.body, CMDHttpJsonBody):
                body_json = resp.body.json
                body_json.var = BuildInVariants.Instance
                if pageable and pageable.item_name:
                    output = CMDArrayOutput()
                    output.ref = f"{body_json.var}.{pageable.item_name}"
                    if pageable.next_link_name:
                        output.next_link = f"{body_json.var}.{pageable.next_link_name}"
                elif isinstance(resp.body.json.schema, CMDArraySchemaBase):
                    output = CMDArrayOutput()
                    output.ref = body_json.var
                elif isinstance(resp.body.json.schema, CMDStringSchemaBase):
                    output = CMDStringSchema()
                    output.ref = body_json.var
                else:
                    if not isinstance(resp.body.json.schema, CMDObjectSchemaBase):
                        print(f"Output Special Schema: {type(resp.body.json.schema)}")
                    output = CMDObjectOutput()
                    output.ref = body_json.var
                output.client_flatten = True
            else:
                raise NotImplementedError()
        return output

    @staticmethod
    def _generate_command_name(path_item, resource, method, output):
        url_path = resource.id.split("?")[0]
        if method == "get":
            if url_path.endswith("/{}"):
                command_name = "show"
            else:
                sub_url_path = url_path + "/{}"
                if path_item.get.x_ms_pageable:
                    command_name = "list"
                elif isinstance(output, CMDArrayOutput) and output.next_link is not None:
                    command_name = "list"
                    # logger.debug(
                    #     f"Command Name For Get set to 'list' by nexLink: {resource.path} :"
                    #     f" {path_item.get.operation_id} : {path_item.traces}"
                    # )
                elif sub_url_path in resource.resource_provider.get_resource_map(read_only=True):
                    command_name = "list"
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
                        command_name = "list"
                        # logger.debug(
                        #     f"Command Name For Get set to 'list' by operation_id: {resource.path} :"
                        #     f" {path_item.get.operation_id} : {path_item.traces}"
                        # )
                    elif contain_get and not contain_list:
                        command_name = "show"
                        # logger.debug(
                        #     f"Command Name For Get set to 'show' by operation_id: {resource.path} :"
                        #     f" {path_item.get.operation_id} : {path_item.traces}"
                        # )
                    else:
                        command_name = '-'.join(op_parts[-1])
                        logger.warning(
                            f"Command Name For Get set by operation_id: {command_name} : {resource.path} :"
                            f" {path_item.get.operation_id} : {path_item.traces}"
                        )
        elif method == "delete":
            command_name = "delete"
        elif method == "put":
            command_name = "create"
        elif method == "patch":
            command_name = "update"
        elif method == "head":
            command_name = "head"
        elif method == "post":
            if not url_path.endswith("/{}") and not path_item.get and not path_item.put and not path_item.patch and \
                    not path_item.delete and not path_item.head:
                command_name = camel_case_to_snake_case(
                    url_path.split('/')[-1],
                    separator='-'
                )
            else:
                op_parts = operation_id_separate(path_item.post.operation_id)
                command_name = '-'.join(op_parts[-1])
                logger.warning(f"Command Name For Post set by operation_id: {command_name} : {resource.path} :"
                               f" {path_item.post.operation_id} : {path_item.traces}")
        else:
            raise NotImplementedError()
        return command_name

    @staticmethod
    def _generate_command_help(op_description):
        # TODO:
        h = CMDHelp()
        h.short = op_description
        return h

    def _generate_command_arguments(self, command):
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
                if self._can_replace_argument(r_arg, arg):
                    arg.ref_schema.arg = r_arg.var
                    dropped_args.add(arg.var)
                elif self._can_replace_argument(arg, r_arg):
                    r_arg.ref_schema.arg = arg.var
                    dropped_args.add(r_arg.var)
                else:
                    # let developer handle duplicated options
                    logger.warning(
                        f"Duplicated Option Value: {set(arg.options).intersection(r_arg.options)} : "
                        f"{arg.var} with {r_arg.var} : {command.operations[-1].operation_id}"
                    )

        return [arg for var, arg in arguments.items() if var not in dropped_args]

    @staticmethod
    def _can_replace_argument(arg, old_arg):
        arg_prefix = arg.var.split('.')[0]
        old_prefix = old_arg.var.split('.')[0]
        if old_prefix in (BuildInVariants.Query, BuildInVariants.Header, BuildInVariants.Path):
            # replace argument should only be in body
            return False
        if arg_prefix in (BuildInVariants.Query, BuildInVariants.Header):
            # only support path argument to replace
            return False

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
                    return False
                return True
            finally:
                arg.ref_schema.name = arg_schema_name
                arg.ref_schema.required = arg_schema_required
        else:
            # body argument
            diff = arg.ref_schema.diff(old_arg.ref_schema, level=CMDDiffLevelEnum.Structure)
            if diff:
                return False
            return True

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

    # For update
    @staticmethod
    def _generate_instance_update_operations(put_op):

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
    def _filter_generic_update_parameters(get_op, put_op):
        """Get operation may contains useless query or header parameters for update, ignore them"""
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
