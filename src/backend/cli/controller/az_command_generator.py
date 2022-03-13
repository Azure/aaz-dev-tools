from cli.model.atomic import CLIAtomicCommand
from command.model.configuration import CMDCommand, CMDHttpOperation, CMDCondition, CMDConditionAndOperator, \
    CMDConditionOrOperator, CMDConditionNotOperator, CMDConditionHasValueOperator, CMDInstanceUpdateOperation, \
    CMDJsonInstanceUpdateAction
from utils.case import to_camel_case, to_snack_case
from utils.plane import PlaneEnum
from .az_operation_generator import AzHttpOperationGenerator, AzJsonUpdateOperationGenerator, \
    AzGenericUpdateOperationGenerator
from .az_arg_group_generator import AzArgGroupGenerator
from .az_output_generator import AzOutputGenerator
from utils import exceptions


class AzCommandCtx:

    def __init__(self):
        self._cls_arg_maps = {}
        self._ctx_arg_map = {}

    def set_argument_cls(self, cls_name):
        self._cls_arg_maps[f"@{cls_name}"] = {}

    def set_argument(self, keys, var_name, hide, ctx_namespace='self.ctx.args'):
        if var_name.startswith('@'):
            map_name = var_name.replace('[', '.[').replace('{', '.{').split('.', maxsplit=1)[0]
            if map_name != keys[0]:
                raise exceptions.VerificationError(
                    "Invalid argument var",
                    details=f"argument var '{var_name}' does not start with '{keys[0]}'"
                )
            if map_name not in self._cls_arg_maps:
                self._cls_arg_maps[map_name] = {}
            self._cls_arg_maps[map_name][var_name] = ('.'.join(keys), hide)
        else:
            self._ctx_arg_map[var_name] = (
                '.'.join([ctx_namespace, *keys]).replace('.[', '[').replace('.{', '{'),
                hide
            )

    def get_argument(self, var_name):
        if var_name.startswith('@'):
            map_name = var_name.replace('[', '.[').replace('{', '.{').split('.', maxsplit=1)[0]
            if map_name not in self._cls_arg_maps:
                raise exceptions.VerificationError(
                    "Invalid argument var",
                    details=f"argument var '{var_name}' has unregistered class '{map_name}'."
                )
            if var_name not in self._cls_arg_maps[map_name]:
                raise exceptions.VerificationError(
                    "Invalid argument var",
                    details=f"argument var '{var_name}' does not find."
                )
            return self._cls_arg_maps[map_name][var_name]
        else:
            if var_name not in self._ctx_arg_map:
                raise exceptions.VerificationError(
                    "Invalid argument var",
                    details=f"argument var '{var_name}' does not find."
                )
            return self._ctx_arg_map[var_name]

    def get_variant(self, variant, name_only=False):
        if variant.startswith('$'):
            variant = variant[1:]
        variant = to_snack_case(variant)
        if name_only:
            return variant
        return f'self.ctx.vars.{variant}'


class AzCommandGenerator:

    ARGS_SCHEMA_NAME = "_args_schema"

    def __init__(self, cmd: CLIAtomicCommand):
        self.cmd = cmd
        self.name = ' '.join(self.cmd.names)
        self.cls_name = to_camel_case(self.cmd.names[-1])

        self.cmd_ctx = AzCommandCtx()

        assert isinstance(self.cmd.cfg, CMDCommand)
        self.conditions = []
        if self.cmd.cfg.conditions:
            for idx, condition in enumerate(self.cmd.cfg.conditions):
                self.conditions.append((condition.var, f"condition_{idx}", condition))

        # prepare arguments
        self.arg_groups = []
        self._arg_cls_map = {}    # shared between arg_groups
        if self.cmd.cfg.arg_groups:
            for arg_group in self.cmd.cfg.arg_groups:
                if arg_group.args:
                    self.arg_groups.append(AzArgGroupGenerator(
                        self.ARGS_SCHEMA_NAME, self.cmd_ctx, self._arg_cls_map, arg_group))

        # prepare operations
        self.lro_counts = 0
        self._op_update_cls_map = {}    # shared between operation request and instance update
        self._op_response_cls_map = {}   # shared between operation response
        self.operations = []
        self.http_operations = []
        self.json_update_operations = []
        self.generic_update_op = None
        self.support_generic_update = False

        json_update_counts = 0
        for operation in self.cmd.cfg.operations:
            lr = False
            if isinstance(operation, CMDHttpOperation):
                op_cls_name = to_camel_case(operation.operation_id)
                if operation.long_running:
                    lr = True
                op = AzHttpOperationGenerator(op_cls_name, self.cmd_ctx, operation, self._op_update_cls_map, self._op_response_cls_map)
                self.http_operations.append(op)
            elif isinstance(operation, CMDInstanceUpdateOperation):
                if isinstance(operation.instance_update, CMDJsonInstanceUpdateAction):
                    op_cls_name = f'InstanceUpdateByJson'
                    if json_update_counts > 0:
                        op_cls_name += f'_{json_update_counts}'
                    op = AzJsonUpdateOperationGenerator(op_cls_name, self.cmd_ctx, operation, self._op_update_cls_map)
                    self.json_update_operations.append(op)
                    json_update_counts += 1
                else:
                    raise NotImplementedError()
            else:
                raise NotImplementedError()
            if lr:
                self.lro_counts += 1
            self.operations.append(op)

        self.support_no_wait = self.lro_counts == 1  # not support no wait if there are multiple long running operations

        # generic_update_op
        if self.json_update_operations:
            self.support_generic_update = self.cmd.names[-1] == "update"
            if self.support_generic_update:
                # make sure all json update operations has the same variant key
                variant_key = self.json_update_operations[0].variant_key
                for op in self.json_update_operations[1:]:
                    if op.variant_key != variant_key:
                        self.support_generic_update = False
                        break
            if self.support_generic_update:
                min_idx = None
                max_idx = None
                for idx, op in enumerate(self.operations):
                    if isinstance(op, AzJsonUpdateOperationGenerator):
                        if min_idx is None:
                            min_idx = idx
                        if max_idx is None or max_idx < idx:
                            max_idx = idx
                if max_idx + 1 - min_idx != len(self.json_update_operations):
                    # has other operations between
                    self.support_generic_update = False
                else:
                    self.generic_update_op = AzGenericUpdateOperationGenerator(self.cmd_ctx, variant_key)
                    self.operations = [*self.operations[:max_idx+1], self.generic_update_op, *self.operations[max_idx+1:]]

        self.version = cmd.version
        self.resources = cmd.resources
        self.plane = None
        for resource in self.cmd.resources:
            if not self.plane:
                self.plane = resource.plane
            elif resource.plane != self.plane:
                raise ValueError(f"Find multiple planes in a command: {resource.plane}, {self.plane}")

        self.client_type = PlaneEnum.http_client(self.plane)

        # prepare outputs
        self.outputs = []
        if self.cmd.cfg.outputs:
            for output in self.cmd.cfg.outputs:
                self.outputs.append(AzOutputGenerator(output, self.cmd_ctx))
        if len(self.outputs) > 1:
            # TODO: add support for output larger than 1
            raise NotImplementedError()

    @property
    def help(self):
        return self.cmd.help

    @property
    def register_info(self):
        return self.cmd.register_info

    def get_arg_clses(self):
        return sorted(self._arg_cls_map.values(), key=lambda a: a.name)

    def get_update_clses(self):
        return sorted(self._op_update_cls_map.values(), key=lambda s: s.name)

    def get_response_clses(self):
        return sorted(self._op_response_cls_map.values(), key=lambda s: s.name)

    def has_outputs(self):
        return len(self.outputs) > 0

    def render_condition(self, condition):
        assert isinstance(condition, CMDCondition)
        return self._render_operator(condition.operator, parent_priority=0)

    def _render_operator(self, operator, parent_priority):
        if isinstance(operator, CMDConditionOrOperator):
            results = []
            for op in operator.operators:
                results.append(
                    self._render_operator(op, parent_priority=2 if len(operator.operators) > 1 else parent_priority)
                )
            if len(results) < 1:
                raise ValueError()
            elif len(results) == 1:
                result = results[0]
            else:
                result = ' or '.join(results)
                if parent_priority > 2:
                    result = f"({result})"
        elif isinstance(operator, CMDConditionAndOperator):
            results = []
            for op in operator.operators:
                results.append(
                    self._render_operator(op, parent_priority=3 if len(operator.operators) > 1 else parent_priority)
                )
            if len(results) < 1:
                raise ValueError()
            elif len(results) == 1:
                result = results[0]
            else:
                result = ' and '.join(results)
                if parent_priority > 3:
                    result = f"({result})"
        elif isinstance(operator, CMDConditionNotOperator):
            result = f'{self._render_operator(operator.operator, parent_priority=6)} is not True'
            if parent_priority > 6:
                result = f"({result})"
        elif isinstance(operator, CMDConditionHasValueOperator):
            arg_keys, hide = self.cmd_ctx.get_argument(operator.arg)
            assert not hide
            result = f'has_value({arg_keys})'
        else:
            raise NotImplementedError()
        return result

    def render_operation_when(self, when):
        results = []
        for condition_var in when:
            condition_name = None
            for c_v, c_name, _ in self.conditions:
                if c_v == condition_var:
                    condition_name = c_name
                    break
            if not condition_name:
                raise KeyError(f"Condition variant not exist: {condition_var}")
            results.append(condition_name)
        return ' or '.join(results)
