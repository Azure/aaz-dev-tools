import logging

from command.model.configuration import CMDConfiguration, CMDHttpOperation, CMDDiffLevelEnum, \
    CMDInstanceUpdateOperation, CMDHttpRequest, CMDArgGroup, CMDObjectArg, CMDArrayArg, \
    CMDObjectArgBase, CMDArrayArgBase, CMDCondition, CMDConditionNotOperator, CMDConditionHasValueOperator, \
    CMDConditionAndOperator
from swagger.controller.command_generator import CommandGenerator
from swagger.controller.specs_manager import SwaggerSpecsManager
from utils import exceptions
from .specs_manager import AAZSpecsManager

logger = logging.getLogger('backend')


class WorkspaceEditor:

    def __init__(self, manager):
        self.manager = manager

        self.swagger_specs = SwaggerSpecsManager()
        self.swagger_command_generator = CommandGenerator()
        self.aaz_specs = AAZSpecsManager()

    def add_resources_by_aaz(self, version, resource_ids):
        used_resource_ids = set()
        for resource_id in resource_ids:
            if resource_id in used_resource_ids:
                continue
            if self.manager.check_resource_exist(resource_id):
                raise exceptions.InvalidAPIUsage(f"Resource already added in Workspace: {resource_id}")
            used_resource_ids.update(resource_id)

        raise NotImplementedError()

    def add_resources_by_swagger(self, mod_names, version, resource_ids, *root_node_names):
        root_node = self.manager.find_command_tree_node(*root_node_names)
        if not root_node:
            raise exceptions.InvalidAPIUsage(f"Command Group not exist: '{' '.join(root_node_names)}'")

        swagger_resources = []
        used_resource_ids = set()
        for resource_id in resource_ids:
            if resource_id in used_resource_ids:
                continue
            if self.manager.check_resource_exist(resource_id):
                raise exceptions.InvalidAPIUsage(f"Resource already added in Workspace: {resource_id}")
            swagger_resources.append(self.swagger_specs.get_resource_in_version(
                self.manager.ws.plane, mod_names, resource_id, version))
            used_resource_ids.update(resource_id)

        self.swagger_command_generator.load_resources(swagger_resources)

        # generate cfg command group from swagger command generator
        cfgs = []
        for resource in swagger_resources:
            cfg = CMDConfiguration()
            cfg.plane = self.manager.ws.plane
            cfg.resources = [resource.to_cmd()]
            cfg.command_group = self.swagger_command_generator.create_draft_command_group(resource)
            assert not cfg.command_group.command_groups, "The logic to support sub command groups is not supported"
            cfgs.append(cfg)

        if len(root_node_names) > 0:
            # rename cfg command group by applying root_node_names prefix

            # calculate common cg name prefix
            common_cg_name_prefix = None
            cg_names = []
            for cfg in cfgs:
                cg_name = cfg.command_group.name.split(" ")
                if common_cg_name_prefix is None:
                    common_cg_name_prefix = cg_name
                    continue
                cg_names.append(cg_name)

            # should also include the existing commands
            for leaf in (root_node.commands or []):
                for cmd_r in leaf.resources:
                    # get the cg_name of existing resource from generator
                    try:
                        resource = self.swagger_specs.get_resource_in_version(
                            plane=self.manager.ws.plane, mod_names=mod_names, resource_id=cmd_r.id, version=version)
                        cg_name = self.swagger_command_generator.generate_command_group_name_by_resource(
                            resource_path=resource.path, rp_name=resource.resource_provider.name)
                    except Exception:
                        # cannot find match resource of resource_id with current mod_names and version
                        cg_name = self.swagger_command_generator.generate_command_group_name_by_resource(
                            resource_path=cmd_r.swagger_path, rp_name=cmd_r.rp_name)
                    cg_name = cg_name.split(" ")
                    cg_names.append(cg_name)

            for cg_name in cg_names:
                if len(cg_name) < len(common_cg_name_prefix):
                    common_cg_name_prefix = common_cg_name_prefix[:len(cg_name)]
                for i, k in enumerate(cg_name):
                    if i >= len(common_cg_name_prefix):
                        break
                    if common_cg_name_prefix[i] != k:
                        common_cg_name_prefix = common_cg_name_prefix[:i]
                        break

            # replace common_cg_name_prefix by root_node_names
            for cfg in cfgs:
                cg_name = cfg.command_group.name.split(" ")
                cg_name = [*root_node_names, *cg_name[len(common_cg_name_prefix):]]
                cfg.command_group.name = " ".join(cg_name)

        for cfg in cfgs:
            node_names = cfg.command_group.name.split(" ")
            node = self.manager.find_command_tree_node(*node_names)
            if not node:
                self.manager.add_resource_cfg(cfg)
                continue

            # some cfg maybe merged into existing cfg
            merged = False
            for command in cfg.command_group.commands:
                if command.name in node.commands:
                    cur_command = node.commands[command.name]
                    if cur_command.version == command.version:
                        cur_cfg = self.manager.load_command_cfg(cur_command)
                        if self.merge_cfgs(cur_cfg, cfg):
                            merged = True
                            break
                    # resource cannot merge, so generation a unique command name
                    command.name = self.generate_unique_command_name(*node_names, command_name=command.name)

            if not merged:
                self.manager.add_resource_cfg(cfg)

    def can_merge_cfgs(self, main_cfg, plus_cfg):
        # only support to merge plus_cfg contains get operation
        if len([*plus_cfg.iter_commands()]) != 1:
            return False
        plus_commands = [*self._iter_commands_by_operations(plus_cfg, 'get')]
        if len(plus_commands) != 1:
            return False
        plus_command = plus_commands[0]
        if len(plus_command.resources) != len(plus_cfg.resources):
            return False

        main_get_commands = [*self._iter_commands_by_operations(main_cfg, 'get')]
        if len(main_get_commands) == 0:
            return False
        for command in main_get_commands:
            if len(command.resources) != len(main_cfg.resources):
                return False

        plus_200_response = None
        for http_op in plus_command.operations:
            if not isinstance(http_op, CMDHttpOperation):
                continue
            assert http_op.http.request.method == 'get'
            for response in http_op.http.responses:
                if response.is_error:
                    continue
                if 200 in response.status_codes:
                    plus_200_response = response
                    break
            if plus_200_response:
                break
        if not plus_200_response:
            return False

        main_200_response = None
        for command in main_get_commands:
            for http_op in command.operations:
                if not isinstance(http_op, CMDHttpOperation):
                    continue
                assert http_op.http.request.method == 'get'
                for response in http_op.http.responses:
                    if response.is_error:
                        continue
                    if 200 in response.status_codes:
                        if plus_200_response.diff(response, CMDDiffLevelEnum.Structure):
                            return False
                        main_200_response = response
        if not main_200_response:
            return False

        plus_op_required_args, plus_op_optional_args = self._parse_operation_url_args(plus_command)
        for main_command in main_get_commands:
            main_op_required_args, main_op_optional_args = self._parse_operation_url_args(main_command)
            for main_op_id, main_required_args in main_op_required_args.items():
                if main_op_id in plus_op_required_args:
                    # the operation id should be different with plus's
                    return False
                for plus_required_args in plus_op_required_args.values():
                    if plus_required_args == main_required_args:
                        # the required arguments should be different
                        return False
        return True

    def _parse_operation_url_args(self, command):
        operation_required_args = {}
        operation_optional_args = {}
        for http_op in command.operations:
            if not isinstance(http_op, CMDHttpOperation):
                continue
            required_args = set()
            optional_args = set()
            request = http_op.http.request
            assert isinstance(request, CMDHttpRequest)
            if request.path and request.path.params:
                for param in request.path.params:
                    if param.arg:
                        if param.required:
                            required_args.add(param.arg)
                        else:
                            optional_args.add(param.arg)
            if request.query and request.query.params:
                for param in request.query.params:
                    if param.arg:
                        if param.required:
                            required_args.add(param.arg)
                        else:
                            optional_args.add(param.arg)
            operation_required_args[http_op.operation_id] = required_args
            operation_optional_args[http_op.operation_id] = optional_args
        return operation_required_args, operation_optional_args

    def _filter_args_in_item(self, item, arg_vars, copy=True):
        if isinstance(item, CMDObjectArgBase):
            return self._filter_args_in_object_arg(item, arg_vars, copy)
        elif isinstance(item, CMDArrayArgBase):
            return self._filter_args_in_array_arg(item, arg_vars, copy)
        return None

    def _filter_args_in_object_arg(self, object_arg, arg_vars, copy=True):
        assert isinstance(object_arg, CMDObjectArgBase)
        if copy:
            object_arg = object_arg.__class__(object_arg.to_primitive())
        contains = False
        if object_arg.args:
            args = []
            for arg in object_arg.args:
                if arg.var in arg_vars:
                    args.append(arg)
                elif isinstance(arg, CMDObjectArg):
                    arg = self._filter_args_in_object_arg(arg, arg_vars, copy=False)
                    if arg:
                        args.append(arg)
                elif isinstance(arg, CMDArrayArg):
                    arg = self._filter_args_in_array_arg(arg, arg_vars, copy=False)
                    if arg:
                        args.append(arg)
            if args:
                object_arg.args = args
                contains = True

        if object_arg.additional_props:
            additional_props = None
            if object_arg.additional_props.item:
                item = self._filter_args_in_item(object_arg.additional_props.item, arg_vars, copy=False)
                if item:
                    additional_props = object_arg.additional_props
                    additional_props.item = item
            if additional_props:
                object_arg.additional_props = additional_props
                contains = True

        if contains:
            return object_arg
        return None

    def _filter_args_in_array_arg(self, array_arg, arg_vars, copy=True):
        assert isinstance(array_arg, CMDArrayArgBase)
        if copy:
            array_arg = array_arg.__class__(array_arg.to_primitive())
        item = self._filter_args_in_item(array_arg.item, arg_vars, copy=False)
        if item:
            array_arg.item = item
            return array_arg
        return None

    def _filter_args_in_arg_group(self, arg_group, arg_vars, copy=True):
        assert isinstance(arg_group, CMDArgGroup)
        if copy:
            arg_group = arg_group.__class__(arg_group.to_primitive())
        args = []
        for arg in arg_group.args:
            if arg.var in arg_vars:
                args.append(arg)
            elif isinstance(arg, CMDObjectArg):
                arg = self._filter_args_in_object_arg(arg, arg_vars, copy=False)
                if arg:
                    args.append(arg)
            elif isinstance(arg, CMDArrayArg):
                arg = self._filter_args_in_array_arg(arg, arg_vars, copy=False)
                if arg:
                    args.append(arg)
        if args:
            arg_group.args = args
            return arg_group
        return None

    def _arg_group_merge_arg(self, arg_group, arg):
        for cmd_arg in arg_group.args:
            if cmd_arg.var == arg.var and not isinstance(arg, type(cmd_arg)):
                raise exceptions.InvalidAPIUsage(
                    f"Same Arg var but different arg types: {arg.var} : {type(cmd_arg)} != {type(arg)}")
            if cmd_arg.var == arg.var:
                return None
            # TODO: handle merge complex args
        return arg

    def _command_merge_arg_group(self, command, arg_group):
        assert isinstance(arg_group, CMDArgGroup)
        remain_args = []
        for arg in arg_group.args:
            for cmd_ag in command.arg_groups:
                arg = self._arg_group_merge_arg(cmd_ag, arg)
                if not arg:
                    break
            if arg:
                remain_args.append(arg)
        if remain_args:
            arg_group.args = remain_args
            command.arg_groups.append(arg_group)

    def _command_merge_operations(self, op_required_args, *operations):
        arg_ops_map = {}
        for op_id, required_args in op_required_args.items():
            for arg in required_args:
                if arg not in arg_ops_map:
                    arg_ops_map[arg] = set()
                arg_ops_map[arg].add(op_id)
        conditions = []
        new_operations = []
        for operation in operations:
            assert operation.operation_id in op_required_args
            op_id = operation.operation_id

            has_args = [*op_required_args[operation.operation_id]]
            if has_args:
                conflict_ops_set = set(arg_ops_map[has_args[0]])
                for arg in has_args[1:]:
                    conflict_ops_set.intersection_update(arg_ops_map[arg])
                assert op_id in conflict_ops_set
                conflict_ops_set.remove(op_id)
                not_has_args = set()
                for c_op_id in conflict_ops_set:
                    not_has_args.update(op_required_args[c_op_id])
                not_has_args.difference_update(has_args)
            else:
                not_has_args = set(arg_ops_map.keys())

            # generate condition
            assert len(has_args) + len(not_has_args) > 0
            condition = CMDCondition()
            condition.var = f"$Condition_{op_id}"
            condition.operator = CMDConditionAndOperator()
            condition.operator.operators = []
            for has_arg in sorted(has_args):
                has_operator = CMDConditionHasValueOperator()
                has_operator.arg = has_arg
                condition.operator.operators.append(has_operator)
            for not_has_arg in sorted(not_has_args):
                not_operator = CMDConditionNotOperator()
                not_operator.operator = CMDConditionHasValueOperator()
                not_operator.operator.arg = not_has_arg
                condition.operator.operators.append(not_operator)
            conditions.append(condition)

            operation.when = [condition.var]
            new_operations.append(operation)

        return conditions, new_operations

    def merge_cfgs(self, main_cfg, plus_cfg):
        # only support to merge plus_cfg with 'get' operation
        if not self.can_merge_cfgs(main_cfg, plus_cfg):
            return False

        plus_command = [*self._iter_commands_by_operations(plus_cfg, 'get')][0]
        plus_op_required_args, plus_op_optional_args = self._parse_operation_url_args(plus_command)

        main_cfg_cpy = main_cfg.__class__(main_cfg.to_primitive())  # generate a copy of main cfg
        main_commands = [*self._iter_commands_by_operations(main_cfg_cpy, 'get')]
        for main_command in main_commands:

            # merge args
            new_args = set()
            for args in plus_op_required_args.values():
                new_args.update(args)
            for args in plus_op_optional_args.values():
                new_args.update(args)
            for arg_group in plus_command.arg_groups:
                arg_group = self._filter_args_in_arg_group(arg_group, new_args, copy=True)
                if arg_group:
                    try:
                        self._command_merge_arg_group(main_command, arg_group)
                    except exceptions.InvalidAPIUsage as ex:
                        logger.error(ex)
                        return False

            # create conditions
            main_op_required_args, _ = self._parse_operation_url_args(main_command)
            plus_operations = []
            for operation in plus_command.operations:
                plus_operations.append(operation.__class__(operation.to_primitive()))
            op_required_args = {**plus_op_required_args, **main_op_required_args}
            main_command.conditions, main_command.operations = self._command_merge_operations(
                op_required_args,
                *plus_operations, *main_command.operations
            )
            for resource in plus_command.resources:
                main_command.resources.append(
                    resource.__class__(resource.to_primitive())
                )
        for resource in plus_cfg.resources:
            main_cfg_cpy.resources.append(
                resource.__class__(resource.to_primitive())
            )
        self.manager.remove_resource_cfg(main_cfg)
        self.manager.add_resource_cfg(main_cfg_cpy)
        return True

    @staticmethod
    def _iter_commands_by_resource(cfg, resource):
        for command in cfg.iter_commands():
            for r in command.resources:
                if r.id == resource.id:
                    yield command
                    break

    @staticmethod
    def _iter_commands_by_operations(cfg, *methods):
        # use 'update' to file instance update operation
        methods = {m.lower() for m in methods}
        for command in cfg.iter_commands():
            ops_methods = set()
            has_extra_methods = False
            for operation in command.operations:
                if isinstance(operation, CMDInstanceUpdateOperation):
                    if 'update' not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add('update')
                elif isinstance(operation, CMDHttpOperation):
                    http = operation.http
                    if http.request.method.lower() not in methods:
                        has_extra_methods = True
                        break
                    ops_methods.add(http.request.method.lower())
            if not has_extra_methods and ops_methods == methods:
                yield command

    def generate_unique_command_name(self, *node_names, command_name):
        tree_node = self.manager.find_command_tree_node(*node_names)
        if not tree_node or command_name not in tree_node.commands:
            return command_name
        idx = 1
        name = f"{command_name}_Untitled_{idx}"
        while name in tree_node.commands:
            idx += 1
            name = f"{command_name}_Untitled_{idx}"
        return name
