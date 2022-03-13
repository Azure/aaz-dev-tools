import json
import logging
import os

from command.model.configuration import CMDConfiguration, CMDHttpOperation, CMDDiffLevelEnum, \
    CMDHttpRequest, CMDArgGroup, CMDObjectArg, CMDArrayArg, \
    CMDObjectArgBase, CMDArrayArgBase, CMDCondition, CMDConditionNotOperator, CMDConditionHasValueOperator, \
    CMDConditionAndOperator, CMDCommandGroup
from utils import exceptions
from utils.base64 import b64encode_str
from .cfg_reader import CfgReader

logger = logging.getLogger('backend')


class WorkspaceCfgEditor(CfgReader):

    @staticmethod
    def get_cfg_folder(ws_folder, resource_id):
        return os.path.join(ws_folder, "Resources", b64encode_str(resource_id))

    @classmethod
    def get_cfg_path(cls, ws_folder, resource_id):
        return os.path.join(cls.get_cfg_folder(ws_folder, resource_id), f"cfg.json")

    @classmethod
    def load_resource(cls, ws_folder, resource_id, version):
        path = cls.get_cfg_path(ws_folder, resource_id)
        with open(path, 'r') as f:
            data = json.load(f)
        if '$ref' in data:
            ref_resource_id = data['$ref']
            path = cls.get_cfg_path(ws_folder, ref_resource_id)
            with open(path, 'r') as f:
                data = json.load(f)
        cfg = CMDConfiguration(data)
        for resource in cfg.resources:
            if resource.version != version:
                raise ValueError(f"Resource version not match: {version} != {resource.version}")
        cfg_editor = cls(cfg)
        cfg_editor.reformat()
        return cfg_editor

    @classmethod
    def new_cfg(cls, plane, resources, command_groups):
        assert len(resources) and len(command_groups)
        cfg = CMDConfiguration()
        cfg.plane = plane
        cfg.resources = resources
        cfg.command_groups = command_groups
        cfg_editor = cls(cfg)
        cfg_editor.reformat()
        return cfg_editor

    def __init__(self, cfg, deleted=False):
        super().__init__(cfg)
        self.deleted = deleted

    def iter_cfg_files_data(self):
        if self.deleted:
            for resource in self.resources:
                yield resource.id, None
        else:
            for resource_id, data in super().iter_cfg_files_data():
                yield resource_id, data

    def rename_command_group(self, *cg_names, new_cg_names):
        if len(cg_names) < 1:
            raise exceptions.InvalidAPIUsage(f"Invalid command group name, it's empty")
        if len(new_cg_names) < 1:
            raise exceptions.InvalidAPIUsage(f"Invalid new command group name, it's empty")

        cg_names = [*cg_names]
        new_cg_names = [*new_cg_names]

        group, tail_names, parent, remain_names = self.find_command_group(*cg_names)

        if not group:
            raise exceptions.InvalidAPIUsage(f"Cannot find command group name '{' '.join(cg_names)}'")

        # remove command group from parent command group
        idx = parent.command_groups.index(group)
        parent.command_groups.pop(idx)

        new_group_names = [*new_cg_names, *tail_names]

        conflict_group, conflict_tail_names, parent, remain_names = self.find_command_group(*new_group_names)
        if not conflict_group:
            if parent.command_groups is None:
                parent.command_groups = []
            group.name = ' '.join(remain_names)
            parent.command_groups.append(group)
        elif conflict_tail_names:
            idx = parent.command_groups.index(conflict_group)
            parent.command_groups.pop(idx)
            group.name = ' '.join(remain_names)
            conflict_group.name = ' '.join(conflict_tail_names)
            if group.command_groups is None:
                group.command_groups = []
            group.command_groups.append(conflict_group)
            parent.command_groups.append(group)
        else:
            assert group.commands or group.command_groups
            raise exceptions.InvalidAPIUsage(f"Command Group '{' '.join(new_group_names)}' already exist")

        self.reformat()

    def rename_command(self, *cmd_names, new_cmd_names):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid command name, it's empty")
        if len(new_cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid new command name, it's empty")

        cmd_names = [*cmd_names]
        new_cmd_names = [*new_cmd_names]

        command = self.find_command(*cmd_names)
        if command is None:
            raise exceptions.ResourceNotFind(f"Cannot find definition for command '{' '.join(cmd_names)}'")

        command_group, tail_names, _, _ = self.find_command_group(*cmd_names[:-1])
        assert command_group is not None and not tail_names

        idx = command_group.commands.index(command)
        command_group.commands.pop(idx)

        if self.find_command(*new_cmd_names):
            raise exceptions.InvalidAPIUsage(f"Command '{' '.join(new_cmd_names)}' already exist")

        command_group, tail_names, parent, remain_names = self.find_command_group(*new_cmd_names[:-1])
        if not command_group:
            cg_names = remain_names
            while not command_group and len(cg_names) > 1:
                cg_names = cg_names[:-1]
                command_group, tail_names, _, _ = self.find_command_group(*cg_names, parent=parent)
            if command_group:
                assert tail_names
                idx = parent.command_groups.index(command_group)
                parent.command_groups.pop(idx)
                new_command_group = CMDCommandGroup()
                new_command_group.name = ' '.join(cg_names)
                command_group.name = ' '.join(tail_names)
                new_command_group.command_groups = [command_group]
                parent.command_groups.append(new_command_group)
                parent = new_command_group
                remain_names = remain_names[len(cg_names):]

            new_command_group = CMDCommandGroup()
            new_command_group.name = ' '.join(remain_names)
            if parent.command_groups is None:
                parent.command_groups = []
            parent.command_groups.append(new_command_group)
            command_group = new_command_group

        elif tail_names:
            idx = parent.command_groups.index(command_group)
            parent.command_groups.pop(idx)
            new_command_group = CMDCommandGroup()
            new_command_group.name = ' '.join(remain_names)
            command_group.name = ' '.join(tail_names)
            new_command_group.command_groups = [command_group]
            parent.command_groups.append(new_command_group)
            command_group = new_command_group

        if command_group.commands is None:
            command_group.commands = []

        command.name = new_cmd_names[-1]
        command_group.commands.append(command)

        self.reformat()

    def merge(self, plus_cfg_editor):
        if not self._can_merge(plus_cfg_editor):
            return None

        _, plus_command = [*plus_cfg_editor.iter_commands_by_operations('get')][0]
        plus_op_required_args, plus_op_optional_args = plus_cfg_editor._parse_command_http_op_url_args(plus_command)

        main_editor = WorkspaceCfgEditor(self.cfg.__class__(self.cfg.to_primitive()))  # generate a copy of main cfg
        main_commands = [command for _, command in main_editor.iter_commands_by_operations('get')]
        for main_command in main_commands:
            # merge args
            new_args = set()
            for args in plus_op_required_args.values():
                new_args.update(args)
            for args in plus_op_optional_args.values():
                new_args.update(args)

            for arg_group in plus_command.arg_groups:
                arg_group = plus_cfg_editor.filter_args_in_arg_group(arg_group, new_args, copy=True)
                if arg_group:
                    try:
                        main_editor._command_merge_arg_group(main_command, arg_group)
                    except exceptions.InvalidAPIUsage as ex:
                        logger.error(ex)
                        return None

            # create conditions
            main_op_required_args, _ = main_editor._parse_command_http_op_url_args(main_command)
            plus_operations = []
            for operation in plus_command.operations:
                plus_operations.append(operation.__class__(operation.to_primitive()))
            op_required_args = {**plus_op_required_args, **main_op_required_args}
            common_required_args, main_command.conditions, main_command.operations = main_editor._merge_command_operations(
                op_required_args,
                *plus_operations, *main_command.operations
            )

            # update arg required of command
            for arg_group in main_command.arg_groups:
                for arg in arg_group.args:
                    arg.required = arg.var in common_required_args

            for resource in plus_command.resources:
                main_command.resources.append(
                    resource.__class__(resource.to_primitive())
                )

        for resource in plus_cfg_editor.resources:
            main_editor.cfg.resources.append(
                resource.__class__(resource.to_primitive())
            )

        main_editor.reformat()
        return main_editor

    def _parse_command_http_op_url_args(self, command):
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

    def _can_merge(self, plus_cfg_editor):
        if len([*plus_cfg_editor.iter_commands()]) != 1:
            return False
        plus_commands = [command for _, command in plus_cfg_editor.iter_commands_by_operations('get')]
        if len(plus_commands) != 1:
            return False
        plus_command = plus_commands[0]
        if len(plus_command.resources) != len(plus_cfg_editor.resources):
            return False

        main_get_commands = [command for _, command in self.iter_commands_by_operations('get')]
        if len(main_get_commands) == 0:
            return False
        for command in main_get_commands:
            if len(command.resources) != len(self.resources):
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

        plus_op_required_args, plus_op_optional_args = self._parse_command_http_op_url_args(plus_command)
        for main_command in main_get_commands:
            main_op_required_args, main_op_optional_args = self._parse_command_http_op_url_args(main_command)
            for main_op_id, main_required_args in main_op_required_args.items():
                if main_op_id in plus_op_required_args:
                    # the operation id should be different with plus's
                    return False
                for plus_required_args in plus_op_required_args.values():
                    if plus_required_args == main_required_args:
                        # the required arguments should be different
                        return False
        return True

    def filter_args_in_arg_group(self, arg_group, arg_vars, copy=True):
        assert isinstance(arg_group, CMDArgGroup)
        if copy:
            arg_group = arg_group.__class__(arg_group.to_primitive())
        args = []
        for arg in arg_group.args:
            if arg.var in arg_vars:
                args.append(arg)
            elif isinstance(arg, CMDObjectArg):
                arg = self.filter_args_in_object_arg(arg, arg_vars, copy=False)
                if arg:
                    args.append(arg)
            elif isinstance(arg, CMDArrayArg):
                arg = self.filter_args_in_array_arg(arg, arg_vars, copy=False)
                if arg:
                    args.append(arg)
        if args:
            arg_group.args = args
            return arg_group
        return None

    def filter_args_in_array_arg(self, array_arg, arg_vars, copy=True):
        assert isinstance(array_arg, CMDArrayArgBase)
        if copy:
            array_arg = array_arg.__class__(array_arg.to_primitive())
        item = self.filter_args_in_item(array_arg.item, arg_vars, copy=False)
        if item:
            array_arg.item = item
            return array_arg
        return None

    def filter_args_in_item(self, item, arg_vars, copy=True):
        if isinstance(item, CMDObjectArgBase):
            return self.filter_args_in_object_arg(item, arg_vars, copy)
        elif isinstance(item, CMDArrayArgBase):
            return self.filter_args_in_array_arg(item, arg_vars, copy)
        return None

    def filter_args_in_object_arg(self, object_arg, arg_vars, copy=True):
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
                    arg = self.filter_args_in_object_arg(arg, arg_vars, copy=False)
                    if arg:
                        args.append(arg)
                elif isinstance(arg, CMDArrayArg):
                    arg = self.filter_args_in_array_arg(arg, arg_vars, copy=False)
                    if arg:
                        args.append(arg)
            if args:
                object_arg.args = args
                contains = True

        if object_arg.additional_props:
            additional_props = None
            if object_arg.additional_props.item:
                item = self.filter_args_in_item(object_arg.additional_props.item, arg_vars, copy=False)
                if item:
                    additional_props = object_arg.additional_props
                    additional_props.item = item
            if additional_props:
                object_arg.additional_props = additional_props
                contains = True

        if contains:
            return object_arg
        return None

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
            match_ag = None
            for ag in command.arg_groups:
                if ag.name == arg_group.name:
                    match_ag = ag
                    break
            if match_ag:
                match_ag.args.extend(arg_group.args)
            else:
                command.arg_groups.append(arg_group)

    def _arg_group_merge_arg(self, arg_group, arg):
        for cmd_arg in arg_group.args:
            if cmd_arg.var == arg.var and not isinstance(arg, type(cmd_arg)):
                raise exceptions.InvalidAPIUsage(
                    f"Same Arg var but different arg types: {arg.var} : {type(cmd_arg)} != {type(arg)}")
            if cmd_arg.var == arg.var:
                return None
            # TODO: handle merge complex args
        return arg

    def _merge_command_operations(self, op_required_args, *operations):
        common_required_args = None
        for required_args in op_required_args.values():
            if common_required_args is None:
                common_required_args = {*required_args}
            else:
                common_required_args.intersection_update(required_args)

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

        return common_required_args, conditions, new_operations

    def reformat(self):
        self.cfg.reformat()
