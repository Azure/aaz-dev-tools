import copy
import json
import logging
import os

from command.model.configuration import *
from utils import exceptions
from utils.base64 import b64encode_str
from utils.case import to_camel_case
from .cfg_reader import CfgReader
from .workspace_helper import ArgumentUpdateMixin

logger = logging.getLogger('backend')


class WorkspaceCfgEditor(CfgReader, ArgumentUpdateMixin):

    @staticmethod
    def get_cfg_folder(ws_folder, resource_id):
        path = os.path.join(ws_folder, "Resources")
        name = b64encode_str(resource_id)
        while len(name):
            if len(name) > 255:
                path = os.path.join(path, name[:254]+'+')
                name = name[254:]
            else:
                path = os.path.join(path, name)
                name = ""
        return path

    @classmethod
    def get_cfg_path(cls, ws_folder, resource_id):
        return os.path.join(cls.get_cfg_folder(ws_folder, resource_id), f"cfg.json")

    @classmethod
    def load_resource(cls, ws_folder, resource_id, version):
        path = cls.get_cfg_path(ws_folder, resource_id)
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
        if '$ref' in data:
            ref_resource_id = data['$ref']
            path = cls.get_cfg_path(ws_folder, ref_resource_id)
            with open(path, 'r', encoding="utf-8") as f:
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
        command = self._remove_command(*cmd_names)
        command.name = new_cmd_names[-1]
        self._add_command(*new_cmd_names, command=command)
        self.reformat()

    def _remove_command(self, *cmd_names):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid command name, it's empty")

        cmd_names = [*cmd_names]
        command = self.find_command(*cmd_names)
        if command is None:
            raise exceptions.ResourceNotFind(f"Cannot find definition for command '{' '.join(cmd_names)}'")

        command_group, tail_names, _, _ = self.find_command_group(*cmd_names[:-1])
        assert command_group is not None and not tail_names

        idx = command_group.commands.index(command)
        command_group.commands.pop(idx)

        return command

    def _add_command(self, *cmd_names, command):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid new command name, it's empty")
        cmd_names = [*cmd_names]

        if self.find_command(*cmd_names):
            raise exceptions.InvalidAPIUsage(f"Command '{' '.join(cmd_names)}' already exist")

        command_group, tail_names, parent, remain_names = self.find_command_group(*cmd_names[:-1])
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

        command_group.commands.append(command)

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
                arg_group = plus_cfg_editor._filter_args_in_arg_group(arg_group, new_args, copy=True)
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

            # relink main_command
            main_command.link()

        for resource in plus_cfg_editor.resources:
            main_editor.cfg.resources.append(
                resource.__class__(resource.to_primitive())
            )

        main_editor.reformat()
        return main_editor

    def update_command_confirmation(self, *cmd_names, confirmation):
        if len(cmd_names) < 2:
            raise exceptions.InvalidAPIUsage(f"Invalid command name, it's empty")

        command = self.find_command(*cmd_names)
        if command is None:
            raise exceptions.ResourceNotFind(f"Cannot find definition for command '{' '.join(cmd_names)}'")
        if confirmation != command.confirmation:
            command.confirmation = confirmation
        self.reformat()

    def update_arg_by_var(self, *cmd_names, arg_var, **kwargs):
        arg, _ = self.find_arg_by_var(*cmd_names, arg_var=arg_var)
        if not arg:
            return None
        self._update_arg(arg, **kwargs)
        self.reformat()

    def unwrap_cls_arg(self, *cmd_names, arg_var):
        command = self.find_command(*cmd_names)
        self._unwrap_cls_arg_in_command(command, arg_var)
        self.reformat()

    @classmethod
    def _unwrap_cls_arg_in_command(cls, command, arg_var):
        parent_arg, arg, _ = cls.find_arg_in_command_with_parent_by_var(command, arg_var=arg_var)
        if not arg:
            raise exceptions.InvalidAPIUsage(
                f"Argument not exist: {arg.var}")
        assert parent_arg is not None

        if isinstance(arg, CMDObjectArgBase):
            if not arg.cls:
                raise exceptions.InvalidAPIUsage(
                    f"{arg.var} is not a class argument"
                )
        elif not isinstance(arg, CMDClsArgBase):
            raise exceptions.InvalidAPIUsage(
                f"{arg.var} is not a class argument"
            )

        linked_schema_parent = None
        linked_schema = None

        # find linked schema
        for parent_schema, schema, _ in cls.iter_schema_in_command_by_arg_var(command, arg_var=arg_var):
            if linked_schema is not None:
                raise exceptions.InvalidAPIUsage(
                    f"Cannot unwrap argument: {arg.var} is used by mutiple schemas."
                )
            linked_schema_parent = parent_schema
            linked_schema = schema

        if linked_schema is None:
            raise exceptions.InvalidAPIUsage(
                f"Cannot unwrap argument: {arg.var} is not used by any schema."
            )

        if isinstance(linked_schema, CMDClsSchemaBase):
            new_schema = linked_schema.get_unwrapped()
            assert new_schema.cls == linked_schema.type[1:]
            new_schema.cls = None  # set the cls to None
            cls.replace_schema(linked_schema_parent, linked_schema, new_schema)
        elif isinstance(linked_schema, (CMDObjectSchemaBase, CMDArraySchemaBase)):
            assert linked_schema.cls is not None
            # unwrap one clsSchema to instance
            for ref_parent, ref_schema, _ in cls.iter_schema_cls_reference(command, linked_schema.cls):
                assert isinstance(ref_schema, CMDClsSchemaBase)
                new_ref_schema = ref_schema.get_unwrapped()
                assert new_ref_schema.cls == linked_schema.cls
                cls.replace_schema(ref_parent, ref_schema, new_ref_schema)
                break
            # unregister current linked schema cls
            linked_schema.cls = None
        else:
            raise exceptions.InvalidAPIUsage(
                f"Not supported schema type: {type(linked_schema)}"
            )

        # regenerate args and its relationship with schema
        command._reformat_operations()  # handle duplicated schema cls definition
        command.generate_args()
        command.link()

    @staticmethod
    def replace_schema(parent, schema, new_schema):
        if isinstance(parent, (CMDObjectSchemaBase, CMDObjectSchemaDiscriminator)):
            if isinstance(schema, CMDSchema):
                assert isinstance(new_schema, CMDSchema)
                schema_idx = None
                for idx in range(len(parent.props)):
                    if parent.props[idx].name == schema.name:
                        schema_idx = idx
                        break
                assert schema_idx is not None
                parent.props[schema_idx] = new_schema
            else:
                assert isinstance(parent, CMDObjectSchemaBase) and isinstance(schema, CMDSchemaBase)
                assert not isinstance(new_schema, CMDSchema) and isinstance(new_schema, CMDSchemaBase)
                assert parent.additional_props.item == schema
                parent.additional_props.item = new_schema
        elif isinstance(parent, CMDArraySchemaBase):
            assert isinstance(schema, CMDSchemaBase)
            assert not isinstance(new_schema, CMDSchema) and isinstance(new_schema, CMDSchemaBase)
            assert parent.item == schema
            parent.item = new_schema
        else:
            raise NotImplementedError()

    def flatten_arg(self, *cmd_names, arg_var, sub_args_options=None):
        command = self.find_command(*cmd_names)
        parent, arg, _ = self.find_arg_with_parent_by_var(*cmd_names, arg_var=arg_var)
        if not arg:
            raise exceptions.InvalidAPIUsage(
                f"Argument not exist: {arg.var}")
        assert parent is not None

        need_unwrap = False
        if isinstance(arg, CMDClsArg) and isinstance(arg.implement, CMDObjectArg):
            if arg.implement.additional_props:
                raise exceptions.InvalidAPIUsage(f"Cannot flatten argument with additional properties")
            need_unwrap = True
        elif isinstance(arg, CMDObjectArg):
            if arg.additional_props:
                raise exceptions.InvalidAPIUsage(f"Cannot flatten argument with additional properties")
            if arg.cls:
                need_unwrap = True
        else:
            raise exceptions.InvalidAPIUsage(f"Cannot flatten argument in type: '{type(arg)}'")

        if need_unwrap:
            # unwrap cls argument first
            self.unwrap_cls_arg(*cmd_names, arg_var=arg_var)
            command = self.find_command(*cmd_names)
            parent, arg, _ = self.find_arg_with_parent_by_var(*cmd_names, arg_var=arg_var)
            assert arg and parent

        parent.args.remove(arg)

        used_options = set()
        if isinstance(parent, CMDArgGroup):
            for group in command.arg_groups:
                for a in group.args:
                    used_options.update(a.options)
        else:
            for a in parent.args:
                used_options.update(a.options)

        for sub_arg in arg.args:
            if sub_args_options and sub_arg.var in sub_args_options:
                sub_arg.options = sub_args_options[sub_arg.var]
            # verify duplicated option
            for option in sub_arg.options:
                if option in used_options:
                    raise exceptions.VerificationError(
                        message=f"Argument option '{option}' duplicated.",
                        details={
                            "type": "Argument",
                            "options": sub_arg.options,
                            "var": sub_arg.var,
                        }
                    )
                used_options.add(option)

            sub_arg.group = to_camel_case(arg.options[0])
            sub_arg.hide = sub_arg.hide or arg.hide  # inherient the hide property from the parent arguments
            parent.args.append(sub_arg)

        # regenerate args and its relationship with schema
        command.generate_args()
        self.reformat()

    def unflatten_arg(self, *cmd_names, arg_var, options, help, sub_args_options=None):
        command = self.find_command(*cmd_names)
        parent, arg, _ = self.find_arg_with_parent_by_var(*cmd_names, arg_var=arg_var)
        if arg:
            raise exceptions.InvalidAPIUsage(
                f"Argument already exist: {arg_var}")
        if not parent:
            assert not arg
            raise exceptions.InvalidAPIUsage(
                f"Sub arguments not exist: {arg_var}")

        sub_args = []
        args = []
        for a in parent.args:
            if a.var.startswith(f'{arg_var}.'):
                a.group = None
                if sub_args_options and a.var in sub_args_options:
                    a.options = sub_args_options[a.var]
                sub_args.append(a)
            else:
                args.append(a)
        assert sub_args

        new_arg = CMDObjectArg()
        new_arg.var = arg_var
        new_arg.options = options
        new_arg.help = CMDArgumentHelp(raw_data=help)
        new_arg.args = sub_args

        args.append(new_arg)
        parent.args = args

        # regenerate args and its relation ship with schema
        command.generate_args()
        self.reformat()

    def reformat(self):
        self.cfg.reformat()

    def _parse_command_http_op_url_args(self, command):
        operation_required_args = {}
        operation_optional_args = {}
        for http_op in command.operations:
            if not isinstance(http_op, CMDHttpOperation):
                continue
            required_args, optional_args = self.parse_http_operation_url_args(http_op)
            operation_required_args[http_op.operation_id] = required_args
            operation_optional_args[http_op.operation_id] = optional_args
        return operation_required_args, operation_optional_args

    @staticmethod
    def parse_http_operation_url_args(op):
        required_args = set()
        optional_args = set()
        request = op.http.request
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
        return required_args, optional_args

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

    def _filter_args_in_arg_group(self, arg_group, arg_vars, copy=True):
        assert isinstance(arg_group, CMDArgGroup)
        if copy:
            arg_group = arg_group.__class__(arg_group.to_primitive())
        args = []
        for arg in arg_group.args:
            if arg.var in arg_vars:
                args.append(arg)
            elif isinstance(arg, CMDObjectArg):
                obj_arg = self._filter_args_in_object_arg(arg, arg_vars, copy=False)
                if obj_arg:
                    args.append(obj_arg)
            elif isinstance(arg, CMDArrayArg):
                arr_arg = self._filter_args_in_array_arg(arg, arg_vars, copy=False)
                if arr_arg:
                    args.append(arr_arg)
        if args:
            arg_group.args = args
            return arg_group
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
                    obj_arg = self._filter_args_in_object_arg(arg, arg_vars, copy=False)
                    if obj_arg:
                        args.append(obj_arg)
                elif isinstance(arg, CMDArrayArg):
                    arr_arg = self._filter_args_in_array_arg(arg, arg_vars, copy=False)
                    if arr_arg:
                        args.append(arr_arg)
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

    def inherit_modification(self, ref_cfg: CfgReader):
        command_rename_list = []
        existing_resources = set()
        existing_sub_resources = set()
        for cmd_names, command in self.iter_commands():
            counterpart = self._find_ref_command_counterpart(cmd_names, command, ref_cfg)
            if not counterpart:
                continue
            ref_cmd_names, ref_command = counterpart
            self._inherit_modification_in_command(command, ref_command)
            command_rename_list.append((cmd_names, ref_cmd_names))
            for r in ref_command.resources:
                existing_resources.add(r.id)
                if r.subresource:
                    existing_sub_resources.add((r.id, r.subresource))

        # rename commands
        for cmd_names, ref_cmd_names in command_rename_list:
            self.rename_command(*cmd_names, new_cmd_names=ref_cmd_names)

        # inherit sub command
        sub_resources = set()
        array_sub_resources = set()
        dict_sub_resources = set()
        for ref_cmd_names, ref_command in ref_cfg.iter_commands():
            for r in ref_command.resources:
                if r.id not in existing_resources:
                    # ignore unrelated resources
                    continue
                if not r.subresource:
                    continue
                subresource_id = r.subresource
                if subresource_id.endswith('[]'):
                    subresource_id = subresource_id[:-2]
                    array_sub_resources.add((r.id, subresource_id))
                elif subresource_id.endswith('{}'):
                    subresource_id = subresource_id[:-2]
                    dict_sub_resources.add((r.id, subresource_id))
                sub_resources.add((r.id, subresource_id))
        sub_resources.difference_update(existing_sub_resources)
        if not sub_resources:
            return

        command_rename_list = []
        for resource_id, subresource_id in sub_resources:
            update_cmd_info = self.get_update_cmd(resource_id)
            if not update_cmd_info:
                continue
            update_cmd_names, update_cmd, update_by = update_cmd_info
            if update_by != "GenericOnly":
                continue

            update_cmd.link()
            update_op = None
            for operation in update_cmd.operations:
                if isinstance(operation, CMDInstanceUpdateOperation):
                    update_op = operation
            assert update_op is not None
            update_json = update_op.instance_update.json
            subresource_idx = self.idx_to_list(subresource_id)
            schema = self.find_schema_in_json(update_json, subresource_idx)
            if not schema:
                # schema not exist
                continue
            assert isinstance(schema, CMDSchema)

            # build ref_args_options
            cg_names = None
            ref_args_options = {}
            for ref_cmd_names, ref_command in ref_cfg.iter_commands_by_resource(resource_id, subresource_id):
                cg_names = ref_cmd_names[:-1]
                for ref_arg_group in ref_command.arg_groups:
                    for ref_arg in ref_arg_group.args:
                        ref_args_options[ref_arg.var] = [*ref_arg.options]
            if (resource_id, subresource_id) in array_sub_resources:
                for ref_cmd_names, ref_command in ref_cfg.iter_commands_by_resource(resource_id, subresource_id + '[]'):
                    cg_names = ref_cmd_names[:-1]
                    for ref_arg_group in ref_command.arg_groups:
                        for ref_arg in ref_arg_group.args:
                            ref_args_options[ref_arg.var] = [*ref_arg.options]
            if (resource_id, subresource_id) in dict_sub_resources:
                for ref_cmd_names, ref_command in ref_cfg.iter_commands_by_resource(resource_id, subresource_id + '{}'):
                    cg_names = ref_cmd_names[:-1]
                    for ref_arg_group in ref_command.arg_groups:
                        for ref_arg in ref_arg_group.args:
                            ref_args_options[ref_arg.var] = [*ref_arg.options]
            assert cg_names is not None

            # generate sub commands
            sub_commands = self._generate_sub_commands(schema, subresource_idx, update_cmd, ref_args_options)
            for sub_command in sub_commands:
                cmd_names = [*cg_names, sub_command.name]
                self._add_command(*cmd_names, command=sub_command)
                counterpart = self._find_ref_command_counterpart(cmd_names, sub_command, ref_cfg)
                if not counterpart:
                    continue
                ref_cmd_names, ref_command = counterpart
                self._inherit_modification_in_command(sub_command, ref_command)
                command_rename_list.append((cmd_names, ref_cmd_names))

        # rename sub commands
        for cmd_names, ref_cmd_names in command_rename_list:
            self.rename_command(*cmd_names, new_cmd_names=ref_cmd_names)

        self.reformat()

    @staticmethod
    def _find_ref_command_counterpart(cmd_names, command, ref_cfg):
        counterpart = None

        # find counterpart
        ops_methods = set()
        for operation in command.operations:
            if isinstance(operation, CMDInstanceUpdateOperation):
                ops_methods.add('instance-update')
            elif isinstance(operation, CMDInstanceCreateOperation):
                ops_methods.add('instance-create')
            elif isinstance(operation, CMDInstanceDeleteOperation):
                ops_methods.add('instance-delete')
            elif isinstance(operation, CMDHttpOperation):
                ops_methods.add(operation.http.request.method.lower())
        for ref_cmd_names, ref_command in ref_cfg.iter_commands_by_operations(*ops_methods):
            command_resources = {(r.id, r.subresource) for r in command.resources}
            ref_command_resources = {(r.id, r.subresource) for r in ref_command.resources}
            if not command_resources.issubset(ref_command_resources):
                # resources not match
                continue
            if counterpart:
                raise exceptions.ResourceConflict(
                    message=f"Failed to inherit modification for command: '{' '.join(cmd_names)}', multiple reference commands find: '{' '.join(counterpart[0])}' & '{' '.join(ref_cmd_names)}'"
                )
            counterpart = (ref_cmd_names, ref_command)
        return counterpart

    @classmethod
    def _inherit_modification_in_command(cls, command, ref_command):
        # confirmation
        if ref_command.confirmation is not None:
            command.confirmation = ref_command.confirmation

        # unwrap modification
        arg_cls_names = set()
        for _, arg, _, arg_var in cls._iter_arg_cls_definition(command):
            arg_cls_names.add(arg.cls)

        for cls_name in arg_cls_names:
            unwrap_detect = True
            while unwrap_detect:
                _, _, _, arg_var = cls._find_arg_cls_definition(command, cls_name=cls_name)
                if not arg_var:
                    break

                arg_vars = [arg_var]
                for _, _, _, arg_var in cls._iter_arg_cls_reference(command, cls_name=cls_name):
                    arg_vars.append(arg_var)

                unwrap_arg_vars = set()
                for arg_var in arg_vars:
                    schema_idx = None
                    for _, _, s_idx in cls.iter_schema_in_command_by_arg_var(command, arg_var):
                        assert schema_idx is None
                        schema_idx = s_idx
                    assert schema_idx is not None
                    # find the schema in ref_command
                    ref_s = cls.find_schema_in_command(ref_command, schema_idx)
                    if not ref_s:
                        continue
                    if not isinstance(ref_s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                        continue
                    if ref_s.cls:
                        continue
                    unwrap_arg_vars.add(arg_var)

                for arg_var in unwrap_arg_vars:
                    cls._unwrap_cls_arg_in_command(command, arg_var)

                # When unwrapped, the schema changed, so it's required to continue to verify the cls_name
                unwrap_detect = len(unwrap_arg_vars) > 0

        # inherit arguments modification
        ref_args = []
        if ref_command.arg_groups:
            for group in ref_command.arg_groups:
                ref_args.extend(group.args)
        command.generate_args(ref_args=ref_args)

        # inherit outputs
        command.generate_outputs(ref_outputs=ref_command.outputs)

    def remove_subresource_commands(self, resource_id, version, subresource):
        commands = []

        cmd_names_list = [cmd_names for cmd_names, _ in self.iter_commands_by_resource(resource_id, subresource, version)]
        if not cmd_names_list:
            return commands

        for cmd_names in cmd_names_list:
            commands.append(self._remove_command(*cmd_names))

        self.reformat()
        return commands

    def build_subresource_commands_by_arg_var(self, resource_id, arg_var, cg_names, ref_args_options=None):
        """

        :param resource_id:
        :param arg_var:
        :param cg_names: command group name for subresource commands
        :param ref_args_options: reference argument options
        :return:
        """
        if isinstance(cg_names, str):
            cg_names = [w for w in cg_names.split(' ') if w]

        assert isinstance(cg_names, list)

        update_cmd_info = self.get_update_cmd(resource_id)
        if not update_cmd_info:
            raise exceptions.InvalidAPIUsage(f"Resource does not exist generic update command: resource_id={resource_id}")

        update_cmd_names, update_cmd, update_by = update_cmd_info
        if update_by != "GenericOnly":
            raise exceptions.InvalidAPIUsage(f"Resource does not exist generic update command: resource_id={resource_id}")

        if arg_var.startswith('@'):
            raise exceptions.InvalidAPIUsage(f"Not support class arg={arg_var}, please unwrap it first.")

        update_op = None
        for operation in update_cmd.operations:
            if isinstance(operation, CMDInstanceUpdateOperation):
                update_op = operation
        assert update_op is not None

        # find schema_idx
        schema = None
        schema_idx = None
        for _, s, s_idx in self.iter_schema_in_operation_by_arg_var(update_op, arg_var):
            assert schema is None
            schema, schema_idx = s, s_idx
        if not schema:
            raise exceptions.InvalidAPIUsage(f"Cannot find schema for arg_var={arg_var}")

        subresource_idx = self.schema_idx_to_subresource_idx(schema_idx)
        assert subresource_idx

        sub_commands = self._generate_sub_commands(schema, subresource_idx, update_cmd, ref_args_options)

        for sub_command in sub_commands:
            self._add_command(*cg_names, sub_command.name, command=sub_command)

        self.reformat()

    @classmethod
    def _generate_sub_commands(cls, schema, subresource_idx, update_cmd, ref_args_options=None):
        update_op = None
        for operation in update_cmd.operations:
            if isinstance(operation, CMDInstanceUpdateOperation):
                update_op = operation
        assert update_op is not None

        # find arg
        if schema.arg:
            arg_var = schema.arg
            arg, arg_idx = cls.find_arg_in_command_by_var(update_cmd, arg_var)
            if not arg or not arg_idx:
                raise exceptions.InvalidAPIUsage(f"Argument '{arg_var}' not exist in command")
        else:
            # schema is flatten
            arg = None

        # build ref_args
        ref_args = []
        update_json = update_op.instance_update.json
        update_arg_prefix = f"${update_json.schema.name}"
        if update_cmd.arg_groups:
            for g in update_cmd.arg_groups:
                for a in g.args:
                    if a.var.startswith(update_arg_prefix):
                        # ignore arguments linked with body
                        continue
                    if 'name' in a.options and isinstance(a, CMDStringArgBase):
                        # remove auto add 'name', 'n' options
                        a = a.__class__(raw_data=a.to_native())
                        a.options = sorted(a.options, key=lambda o: (len(o), o))[-1:]  # use the longest argument
                    ref_args.append(a)

        if isinstance(schema, CMDArraySchema):
            assert isinstance(arg, CMDArrayArg)
            # list command
            list_command = cls._build_subresource_list_or_show_command(
                update_cmd=update_cmd,
                subresource_idx=subresource_idx,
                ref_args=ref_args,
                ref_options=ref_args_options
            )

            # generate item command
            item_subresource_idx = [*subresource_idx, '[]']

            item_arg = arg.item
            if isinstance(item_arg, CMDClsArgBase):
                raise exceptions.InvalidAPIUsage(f"Not support array<class> arg={arg_var}, please unwrap it first.")

            if not isinstance(item_arg, CMDObjectArgBase):
                raise NotImplementedError()

            if item_arg.additional_props:
                raise NotImplementedError()

            ref_args.extend(item_arg.args)

            # create command
            create_command = cls._build_subresource_create_command(
                update_cmd=update_cmd,
                subresource_idx=item_subresource_idx,
                ref_args=ref_args,
                ref_options=ref_args_options,
            )
            # update command
            update_command = cls._build_subresource_update_command(
                update_cmd=update_cmd,
                subresource_idx=item_subresource_idx,
                ref_args=ref_args,
                ref_options=ref_args_options,
            )
            # delete command
            delete_command = cls._build_subresource_delete_command(
                update_cmd=update_cmd,
                subresource_idx=item_subresource_idx,
                ref_args=ref_args,
                ref_options=ref_args_options,
            )
            # show command
            show_command = cls._build_subresource_list_or_show_command(
                update_cmd=update_cmd,
                subresource_idx=item_subresource_idx,
                ref_args=ref_args,
                ref_options=ref_args_options,
            )

            list_command.name = 'list'
            create_command.name = 'create'
            update_command.name = 'update'
            delete_command.name = 'delete'
            show_command.name = 'show'

            return [list_command, create_command, update_command, delete_command, show_command]

        elif isinstance(schema, CMDObjectSchema):
            if schema.props and schema.additional_props:
                raise NotImplementedError()

            if schema.props:
                if arg:
                    assert isinstance(arg, CMDObjectArg)
                    ref_args.extend(arg.args)

                # create command
                create_command = cls._build_subresource_create_command(
                    update_cmd=update_cmd,
                    subresource_idx=subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )
                # update command
                update_command = cls._build_subresource_update_command(
                    update_cmd=update_cmd,
                    subresource_idx=subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )
                # delete command
                delete_command = cls._build_subresource_delete_command(
                    update_cmd=update_cmd,
                    subresource_idx=subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )
                # show command
                show_command = cls._build_subresource_list_or_show_command(
                    update_cmd=update_cmd,
                    subresource_idx=subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )

            elif schema.additional_props and schema.additional_props.item:
                assert isinstance(arg, CMDObjectArg)
                item_subresource_idx = [*subresource_idx, '{}']

                item_arg = arg.additional_props.item
                if isinstance(item_arg, CMDClsArgBase):
                    raise exceptions.InvalidAPIUsage(f"Not support dict<class> arg={arg_var}, please unwrap it first.")

                if not isinstance(item_arg, CMDObjectSchemaBase):
                    raise NotImplementedError()

                if item_arg.additional_props:
                    raise NotImplementedError()

                ref_args.extend(item_arg.args)

                # create command
                create_command = cls._build_subresource_create_command(
                    update_cmd=update_cmd,
                    subresource_idx=item_subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )
                # update command
                update_command = cls._build_subresource_update_command(
                    update_cmd=update_cmd,
                    subresource_idx=item_subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )
                # delete command
                delete_command = cls._build_subresource_delete_command(
                    update_cmd=update_cmd,
                    subresource_idx=item_subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )
                # show command
                show_command = cls._build_subresource_list_or_show_command(
                    update_cmd=update_cmd,
                    subresource_idx=item_subresource_idx,
                    ref_args=ref_args,
                    ref_options=ref_args_options
                )
            else:
                raise NotImplementedError()

            create_command.name = 'create'
            update_command.name = 'update'
            delete_command.name = 'delete'
            show_command.name = 'show'

            return [create_command, update_command, delete_command, show_command]
        else:
            raise NotImplementedError()

    @classmethod
    def _build_sub_command_base(cls, update_cmd, subresource_idx, **kwargs):
        get_op = None
        put_op = None
        update_op = None
        for operation in update_cmd.operations:
            if isinstance(operation, CMDInstanceUpdateOperation):
                update_op = operation
            if isinstance(operation, CMDHttpOperation) and operation.http.request and operation.http.responses:
                if operation.http.request.method == "get":
                    get_op = operation
                if operation.http.request.method == "put":
                    put_op = operation
        assert get_op is not None
        assert put_op is not None
        assert update_op is not None

        # find response body
        response_json = None
        for response in get_op.http.responses:
            if response.is_error:
                continue
            if not isinstance(response.body, CMDHttpResponseJsonBody):
                continue
            if response.body.json.var == update_op.instance_update.ref:
                response_json = response.body.json
                break
        assert response_json is not None

        update_json = update_op.instance_update.json

        _sub_command = CMDCommand()
        _sub_command.version = update_cmd.version
        assert len(update_cmd.resources) == 1
        _resource = CMDResource(raw_data=update_cmd.resources[0].to_native())
        _resource.subresource = cls.idx_to_str(subresource_idx)
        _sub_command.resources = [_resource]
        _sub_command.subresource_selector = cls._build_subresource_selector(
            response_json, update_json, subresource_idx, **kwargs)
        return _sub_command, get_op, put_op, update_json

    @classmethod
    def _build_subresource_list_or_show_command(cls, update_cmd, subresource_idx, ref_args, ref_options):
        _sub_command, get_op, _, update_json = cls._build_sub_command_base(update_cmd, subresource_idx)

        _sub_command.operations = [get_op.__class__(raw_data=get_op.to_native())]
        _sub_command.generate_args(ref_args=ref_args, ref_options=ref_options)
        _sub_command.generate_outputs(ref_outputs=update_cmd.outputs)
        _sub_command.link()
        return _sub_command

    @classmethod
    def _build_subresource_create_command(cls, update_cmd, subresource_idx, ref_args, ref_options):
        _sub_command, get_op, put_op, update_json = cls._build_sub_command_base(update_cmd, subresource_idx, optional_end_index_indentifier=True)

        _instance_op = CMDInstanceCreateOperation()
        _instance_op.instance_create = CMDJsonInstanceCreateAction()
        _instance_op.instance_create.ref = _sub_command.subresource_selector.var
        _instance_op.instance_create.json = CMDRequestJson()

        # fork json schema
        assert update_cmd.schema_cls_register_map is not None
        _instance_op_schema = cls.fork_schema_in_json(
            update_json, subresource_idx, update_cmd.schema_cls_register_map)
        assert not isinstance(_instance_op_schema, CMDClsSchemaBase)
        if not isinstance(_instance_op_schema, CMDSchema):
            # convert schema base to schema
            if isinstance(_instance_op_schema, CMDObjectSchemaBase):
                _instance_op_schema = CMDObjectSchema(raw_data=_instance_op_schema.to_native())
            elif isinstance(_instance_op_schema, CMDArraySchemaBase):
                _instance_op_schema = CMDArraySchema(raw_data=_instance_op_schema.to_native())
            else:
                raise NotImplementedError()
        # _subresource_idx does not contains update_json.schema.name
        _instance_op_schema.name = cls.idx_to_str([update_json.schema.name, *subresource_idx])
        _instance_op_schema.required = True
        _instance_op.instance_create.json.schema = _instance_op_schema

        _sub_command.operations = [
            get_op.__class__(raw_data=get_op.to_native()),
            _instance_op,
            put_op.__class__(raw_data=put_op.to_native()),
        ]
        _sub_command.generate_args(ref_args=ref_args, ref_options=ref_options)
        _sub_command.generate_outputs(ref_outputs=update_cmd.outputs)
        _sub_command.link()
        return _sub_command

    @classmethod
    def _build_subresource_update_command(cls, update_cmd, subresource_idx, ref_args, ref_options):
        _sub_command, get_op, put_op, update_json = cls._build_sub_command_base(update_cmd, subresource_idx)

        _instance_op = CMDInstanceUpdateOperation()
        _instance_op.instance_update = CMDJsonInstanceUpdateAction()
        _instance_op.instance_update.ref = _sub_command.subresource_selector.var
        _instance_op.instance_update.json = CMDRequestJson()

        # fork json schema
        assert update_cmd.schema_cls_register_map is not None
        _instance_op_schema = cls.fork_schema_in_json(
            update_json, subresource_idx, update_cmd.schema_cls_register_map)
        if not isinstance(_instance_op_schema, CMDSchema):
            # convert schema base to schema
            if isinstance(_instance_op_schema, CMDObjectSchemaBase):
                _instance_op_schema = CMDObjectSchema(raw_data=_instance_op_schema.to_native())
            elif isinstance(_instance_op_schema, CMDArraySchemaBase):
                _instance_op_schema = CMDArraySchema(raw_data=_instance_op_schema.to_native())
            else:
                raise NotImplementedError()
        # _subresource_idx does not contains update_json.schema.name
        _instance_op_schema.name = cls.idx_to_str([update_json.schema.name, *subresource_idx])
        _instance_op_schema.required = True
        _instance_op.instance_update.json.schema = _instance_op_schema

        _sub_command.operations = [
            get_op.__class__(raw_data=get_op.to_native()),
            _instance_op,
            put_op.__class__(raw_data=put_op.to_native()),
        ]
        _sub_command.generate_args(ref_args=ref_args, ref_options=ref_options)
        _sub_command.generate_outputs(ref_outputs=update_cmd.outputs)
        _sub_command.link()
        return _sub_command

    @classmethod
    def _build_subresource_delete_command(cls, update_cmd, subresource_idx, ref_args, ref_options):
        _sub_command, get_op, put_op, _ = cls._build_sub_command_base(update_cmd, subresource_idx)

        _instance_op = CMDInstanceDeleteOperation()
        _instance_op.instance_delete = CMDJsonInstanceDeleteAction()
        _instance_op.instance_delete.ref = _sub_command.subresource_selector.var
        _instance_op.instance_delete.json = CMDRequestJson()
        _sub_command.operations = [
            get_op.__class__(raw_data=get_op.to_native()),
            _instance_op,
            put_op.__class__(raw_data=put_op.to_native()),
        ]
        _sub_command.confirmation = DEFAULT_CONFIRMATION_PROMPT
        _sub_command.generate_args(ref_args=ref_args, ref_options=ref_options)
        _sub_command.generate_outputs(ref_outputs=update_cmd.outputs)
        _sub_command.link()
        return _sub_command

    @classmethod
    def _build_subresource_selector(cls, response_json, update_json, subresource_idx, **kwargs):
        assert isinstance(response_json, CMDResponseJson)
        assert isinstance(update_json, CMDRequestJson)

        idx = cls.idx_to_list(subresource_idx)
        selector = CMDJsonSubresourceSelector()
        selector.ref = response_json.var

        if isinstance(update_json.schema, CMDObjectSchema):
            assert isinstance(response_json.schema, CMDObjectSchemaBase)
            index = CMDObjectIndex()
            index.name = update_json.schema.name
            # disable prune for the outer layer index
            selector.json = cls._build_object_index_base(update_json.schema, idx, index=index, prune=False, **kwargs)
        elif isinstance(update_json.schema, CMDArraySchema):
            assert isinstance(response_json.schema, CMDArraySchemaBase)
            index = CMDArrayIndex()
            index.name = update_json.schema.name
            selector.json = cls._build_array_index_base(update_json.schema, idx, index=index, **kwargs)
        else:
            raise NotImplementedError(f"Not support schema {type(update_json.schema)}")

        return selector

    @classmethod
    def _build_simple_index_base(cls, schema, idx, index=None, **kwargs):
        if index is None:
            if not isinstance(schema, CMDSimpleIndexBase.supported_schema_types):
                raise NotImplementedError(f"Not support schema '{type(schema)}'")
            index = CMDSimpleIndexBase()
        if idx:
            raise exceptions.InvalidAPIUsage(f"Not support remain index {idx}")
        return index

    @classmethod
    def _build_object_index_base(cls, schema, idx, index=None, prune=False, **kwargs):
        assert isinstance(schema, CMDObjectSchemaBase)

        if not index:
            index = CMDObjectIndexBase()

        if not idx:
            return index

        current_idx = idx[0]
        remain_idx = idx[1:]
        find_idx = False

        if schema.props:
            for prop in schema.props:
                if prop.name != current_idx:
                    continue
                find_idx = True
                if prune:
                    assert isinstance(index, CMDSelectorIndex)
                    name = f"{index.name}.{prop.name}"
                    if isinstance(prop, CMDClsSchema):
                        prop = prop.implement
                    # ignore the current index, return the sub index with index.name prefix
                    if isinstance(prop, CMDObjectSchema):
                        return cls._build_object_index(prop, remain_idx, name=name, **kwargs)
                    elif isinstance(prop, CMDArraySchema):
                        return cls._build_array_index(prop, remain_idx, name=name, **kwargs)
                    else:
                        return cls._build_simple_index(prop, remain_idx, name=name, **kwargs)
                else:
                    name = prop.name
                    if isinstance(prop, CMDClsSchema):
                        prop = prop.implement
                    if isinstance(prop, CMDObjectSchema):
                        index.prop = cls._build_object_index(prop, remain_idx, name=name, **kwargs)
                        break
                    elif isinstance(prop, CMDArraySchema):
                        index.prop = cls._build_array_index(prop, remain_idx, name=name, **kwargs)
                        break
                    else:
                        index.prop = cls._build_simple_index(prop, remain_idx, name=name, **kwargs)
                        break

        if schema.discriminators:
            for disc in schema.discriminators:
                if disc.get_safe_value() == current_idx:
                    find_idx = True
                    index.discriminator = cls._build_object_index_discriminator(disc, remain_idx, **kwargs)
                    break

        if schema.additional_props and current_idx == "{}":
            find_idx = True
            index.additional_props = cls._build_object_index_additional_prop(schema.additional_props, remain_idx, **kwargs)

        if not find_idx:
            raise exceptions.InvalidAPIUsage(f"Cannot find remain index {idx}")

        return index

    @classmethod
    def _build_array_index_base(cls, schema, idx, index=None, **kwargs):
        assert isinstance(schema, CMDArraySchemaBase)

        if not index:
            index = CMDArrayIndexBase()

        if not idx:
            return index

        current_idx = idx[0]
        remain_idx = idx[1:]
        if current_idx != '[]':
            raise exceptions.InvalidAPIUsage(f"Cannot find index '{idx}'")

        item = schema.item
        if isinstance(item, CMDClsSchemaBase):
            item = item.implement

        identifiers = []
        identifier_names = schema.identifiers
        if not identifier_names and isinstance(item, CMDObjectSchemaBase):
            prop_names = {prop.name for prop in item.props}
            if 'id' in prop_names and 'name' in prop_names:
                # use name as default identifier when schema contains 'id' property
                identifier_names = ['name']

        if identifier_names:
            assert isinstance(item, CMDObjectSchemaBase)
            for prop in item.props:
                if prop.name in identifier_names:
                    identifier = prop.__class__(raw_data=prop.to_native())
                    identifier.name = '[].' + prop.name
                    identifier.required = True
                    identifier.read_only = False
                    identifier.frozen = False
                    identifiers.append(identifier)

        if not identifiers:
            # use index as identifier
            identifier = CMDIntegerSchema()
            identifier.name = '[Index]'
            identifiers.append(identifier)
            identifier.required = len(remain_idx) > 0 or not kwargs.get('optional_end_index_indentifier', False)
        index.identifiers = identifiers

        if isinstance(item, CMDObjectSchemaBase):
            index.item = cls._build_object_index_base(item, remain_idx, **kwargs)
        elif isinstance(item, CMDArraySchemaBase):
            index.item = cls._build_array_index_base(item, remain_idx, **kwargs)
        else:
            index.item = cls._build_simple_index_base(item, remain_idx, **kwargs)

        return index

    @classmethod
    def _build_simple_index(cls, schema, idx, name, **kwargs):
        if not isinstance(schema, CMDSimpleIndex.supported_schema_types):
            raise NotImplementedError(f"Not support schema '{type(schema)}'")
        index = CMDSimpleIndex()
        index.name = name
        return cls._build_simple_index_base(schema, idx, index=index, **kwargs)

    @classmethod
    def _build_object_index(cls, schema, idx, name, **kwargs):
        index = CMDObjectIndex()
        index.name = name
        return cls._build_object_index_base(schema, idx, index, prune=True, **kwargs)

    @classmethod
    def _build_array_index(cls, schema, idx, name, **kwargs):
        index = CMDArrayIndex()
        index.name = name
        return cls._build_array_index_base(schema, idx, index, **kwargs)

    @classmethod
    def _build_object_index_discriminator(cls, schema, idx, **kwargs):
        assert isinstance(schema, CMDObjectSchemaDiscriminator)

        index = CMDObjectIndexDiscriminator()
        index.property = schema.property
        index.value = schema.value

        if not idx:
            return index

        current_idx = idx[0]
        remain_idx = idx[1:]

        find_idx = False

        if schema.props:
            for prop in schema.props:
                if prop.name != current_idx:
                    continue
                find_idx = True
                name = prop.name
                if isinstance(prop, CMDClsSchema):
                    prop = prop.implement

                if isinstance(prop, CMDObjectSchema):
                    index.prop = cls._build_object_index(prop, remain_idx, name, **kwargs)
                    break
                elif isinstance(prop, CMDArraySchema):
                    index.prop = cls._build_array_index(prop, remain_idx, name, **kwargs)
                    break
                else:
                    index.prop = cls._build_simple_index(prop, remain_idx, name, **kwargs)
                    break

        if schema.discriminators:
            for disc in schema.discriminators:
                if disc.get_safe_value() == current_idx:
                    find_idx = True
                    index.discriminator = cls._build_object_index_discriminator(disc, remain_idx, **kwargs)
                    break

        if not find_idx:
            raise exceptions.InvalidAPIUsage(f"Cannot find remain index {idx}")

        return index

    @classmethod
    def _build_object_index_additional_prop(cls, schema, idx, **kwargs):
        assert isinstance(schema, CMDObjectSchemaAdditionalProperties)
        index = CMDObjectIndexAdditionalProperties()

        identifier = CMDStringSchema()
        identifier.name = "{Key}"
        identifier.required = True
        index.identifiers = [identifier]

        item = schema.item
        if isinstance(item, CMDClsSchemaBase):
            item = item.implement
        if isinstance(item, CMDObjectSchemaBase):
            index.item = cls._build_object_index_base(item, idx, **kwargs)
        elif isinstance(item, CMDArraySchemaBase):
            index.item = cls._build_array_index_base(item, idx, **kwargs)
        else:
            index.item = cls._build_simple_index_base(item, idx, **kwargs)

        return index

    @classmethod
    def fork_schema_in_json(cls, js, idx, reference_cls_map):
        from command.model.configuration._content import _iter_over_schema_for_cls_register
        schema = cls.find_schema_in_json(js, idx)
        if not schema:
            return None

        if isinstance(schema, CMDClsSchemaBase):
            assert schema.implement is not None
            schema = schema.get_unwrapped()
        else:
            schema = schema.__class__(raw_data=schema.to_native())
        assert not isinstance(schema, CMDClsSchemaBase)

        # make sure cls implement contained in schema
        cls_register_map = {}
        _iter_over_schema_for_cls_register(schema, cls_register_map)
        miss_implement_cls_names = set()
        for k, v in cls_register_map.items():
            if not v['implement']:
                miss_implement_cls_names.add(k)

        pre_miss_implement_cls_names = set()
        while len(miss_implement_cls_names) > 0 and pre_miss_implement_cls_names != miss_implement_cls_names:
            for cls_name in miss_implement_cls_names:
                # unwrap the miss implement clsSchema to instance
                for ref_parent, ref_schema, _ in cls.iter_schema_cls_reference_in_schema(schema, cls_name):
                    assert isinstance(ref_schema, CMDClsSchemaBase)
                    assert cls_register_map[cls_name]['implement'] is None
                    ref_schema.implement = reference_cls_map[cls_name]['implement']
                    assert ref_schema.implement is not None
                    new_ref_schema = ref_schema.get_unwrapped()
                    assert new_ref_schema.cls == cls_name
                    cls.replace_schema(ref_parent, ref_schema, new_ref_schema)
                    break

            # recalculate miss implement cls
            pre_miss_implement_cls_names = miss_implement_cls_names
            cls_register_map = {}
            _iter_over_schema_for_cls_register(schema, cls_register_map)
            miss_implement_cls_names = set()
            for k, v in cls_register_map.items():
                if not v['implement']:
                    miss_implement_cls_names.add(k)

        if len(miss_implement_cls_names) > 0:
            raise exceptions.InvalidAPIUsage(f"Always miss class implements for {miss_implement_cls_names}")

        return schema


def build_endpoint_selector_for_client_config(get_op, subresource_idx, **kwargs):
    # find response body
    response_json = None
    for response in get_op.http.responses:
        if response.is_error:
            continue
        if not isinstance(response.body, CMDHttpResponseJsonBody):
            continue
        if response.body.json.var == CMDBuildInVariants.EndpointInstance:
            response_json = response.body.json
            break

    assert isinstance(response_json, CMDResponseJson)
    idx = WorkspaceCfgEditor.idx_to_list(subresource_idx)
    selector = CMDJsonSubresourceSelector()
    selector.ref = response_json.var
    selector.var = CMDBuildInVariants.Endpoint
    if isinstance(response_json.schema, CMDObjectSchemaBase):
        index = CMDObjectIndex()
        index.name = 'response'
        selector.json = WorkspaceCfgEditor._build_object_index_base(
            response_json.schema, idx, index=index, **kwargs)
    elif isinstance(response_json.schema, CMDArraySchemaBase):
        index = CMDArrayIndex()
        index.name = 'response'
        selector.json = WorkspaceCfgEditor._build_array_index_base(
            response_json.schema, idx, index=index, **kwargs)
    else:
        raise NotImplementedError(f"Not support schema {type(response_json.schema)}")

    return selector
