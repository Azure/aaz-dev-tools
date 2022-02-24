from cli.model.atomic import CLIAtomicCommand
from command.model.configuration import CMDCommand, CMDHttpOperation, CMDCondition, CMDConditionAndOperator, \
    CMDConditionOrOperator, CMDConditionNotOperator, CMDConditionHasValueOperator, CMDInstanceUpdateOperation, \
    CMDJsonInstanceUpdateAction, CMDGenericInstanceUpdateAction, CMDOperation
from utils.case import to_camel_case
from utils import exceptions
from utils.plane import PlaneEnum
from .az_operation_generator import AzHttpOperationGenerator, AzJsonUpdateOperationGenerator, \
    AzGenericUpdateOperationGenerator
from .az_arg_group_generator import AzArgGroupGenerator, AzArgClsGenerator


class AzCommandGenerator:

    ARGS_SCHEMA_NAME = "_args_schema"

    def __init__(self, cmd: CLIAtomicCommand):
        self.cmd = cmd
        self.name = ' '.join(self.cmd.names)
        self.cls_name = to_camel_case(self.cmd.names[-1])

        assert isinstance(self.cmd.cfg, CMDCommand)
        self.conditions = []
        if self.cmd.cfg.conditions:
            for idx, condition in self.cmd.cfg.conditions:
                self.conditions.append((condition.var, f"condition_{idx}", condition))

        self._variants = {}

        # prepare arguments
        self._arguments = {}

        self.arg_groups = []
        self._arg_cls_map = {}    # shared between arg_groups
        if self.cmd.cfg.arg_groups:
            for arg_group in self.cmd.cfg.arg_groups:
                if arg_group.args:
                    self.arg_groups.append(AzArgGroupGenerator(
                        self.ARGS_SCHEMA_NAME, self._arguments, self._arg_cls_map, arg_group))

        # prepare operations
        self.lro_counts = 0

        self.operations = []
        self.http_operations = []
        self.json_update_operations = []
        self.generic_update_operations = []

        json_update_counts = 0
        generic_update_counts = 0
        for operation in self.cmd.cfg.operations:
            lr = False
            if isinstance(operation, CMDHttpOperation):
                op_cls_name = to_camel_case(operation.operation_id)
                if operation.long_running:
                    lr = True
                op = AzHttpOperationGenerator(op_cls_name, self._arguments, self._variants, operation)
                self.http_operations.append(op)
            elif isinstance(operation, CMDInstanceUpdateOperation):
                if isinstance(operation.instance_update, CMDJsonInstanceUpdateAction):
                    op_cls_name = f'InstanceUpdateByJson'
                    if json_update_counts > 0:
                        op_cls_name += f'_{json_update_counts}'
                    op = AzJsonUpdateOperationGenerator(op_cls_name, self._arguments, self._variants, operation)
                    self.json_update_operations.append(op)
                    json_update_counts += 1
                elif isinstance(operation.instance_update, CMDGenericInstanceUpdateAction):
                    op_cls_name = f'InstanceUpdateByGeneric'
                    if generic_update_counts > 0:
                        op_cls_name += f'_{generic_update_counts}'
                    op = AzGenericUpdateOperationGenerator(op_cls_name, self._arguments, self._variants, operation)
                    self.generic_update_operations.append(op)
                    generic_update_counts += 1
                else:
                    raise NotImplementedError()
            else:
                raise NotImplementedError()
            if lr:
                self.lro_counts += 1
            self.operations.append(op)

        self.support_no_wait = self.lro_counts == 1  # not support no wait if there are multiple long running operations

        self.plane = None
        for resource in self.cmd.resources:
            if not self.plane:
                self.plane = resource.plane
            elif resource.plane != self.plane:
                raise ValueError(f"Find multiple planes in a command: {resource.plane}, {self.plane}")

        self.client_type = PlaneEnum.http_client(self.plane)

    @property
    def help(self):
        return self.cmd.help

    @property
    def register_info(self):
        return self.cmd.register_info

    def get_arg_clses(self):
        return sorted(self._arg_cls_map.values(), key=lambda a: a.name)

    def has_outputs(self):
        if self.cmd.cfg.outputs:
            return True
        return False

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
            result = f'has_value({self._variants[operator.arg]})'
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
