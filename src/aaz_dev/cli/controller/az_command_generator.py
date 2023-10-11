from cli.model.atomic import CLIAtomicCommand
from command.model.configuration import CMDCommand, CMDHttpOperation, CMDCondition, CMDConditionAndOperator, \
    CMDConditionOrOperator, CMDConditionNotOperator, CMDConditionHasValueOperator, CMDInstanceUpdateOperation, \
    CMDJsonInstanceUpdateAction, CMDResourceGroupNameArg, CMDJsonSubresourceSelector, CMDInstanceCreateOperation, \
    CMDInstanceDeleteOperation, CMDJsonInstanceCreateAction, CMDJsonInstanceDeleteAction
from utils.case import to_camel_case, to_snake_case
from utils.plane import PlaneEnum
from .az_operation_generator import AzHttpOperationGenerator, AzJsonUpdateOperationGenerator, \
    AzGenericUpdateOperationGenerator, AzRequestClsGenerator, AzResponseClsGenerator, \
    AzInstanceUpdateOperationGenerator, AzLifeCycleInstanceUpdateCallbackGenerator, AzJsonCreateOperationGenerator, \
    AzJsonDeleteOperationGenerator, AzLifeCycleCallbackGenerator
from .az_arg_group_generator import AzArgGroupGenerator, AzArgClsGenerator
from .az_output_generator import AzOutputGenerator
from .az_selector_generator import AzJsonSelectorGenerator
from utils import exceptions
import logging


logger = logging.getLogger('backend')


class AzCommandCtx:

    def __init__(self):
        self._cls_arg_maps = {}
        self._ctx_arg_map = {}
        self._selectors = {}
        self.rg_arg_var = None

        self.arg_clses = {}
        self.update_clses = {}
        self.response_clses = {}
        self.support_id_part = True

    def set_argument_cls(self, arg):
        cls_name = arg.cls
        self._cls_arg_maps[f"@{cls_name}"] = {}
        assert cls_name not in self.arg_clses, f"Argument class {cls_name} is defined more than one place"
        self.arg_clses[cls_name] = AzArgClsGenerator(cls_name, self, arg)

    def set_argument(self, keys, arg, ctx_namespace='self.ctx.args'):
        var_name = arg.var
        hide = arg.hide
        if var_name.startswith('@'):
            map_name = var_name.replace('[', '.[').replace('{', '.{').split('.', maxsplit=1)[0]
            if map_name != keys[0]:
                raise exceptions.VerificationError(
                    "Invalid argument var",
                    details=f"argument var '{var_name}' does not start with '{keys[0]}'"
                )
            if map_name not in self._cls_arg_maps:
                self._cls_arg_maps[map_name] = {}
            self._cls_arg_maps[map_name][var_name] = (
                '.'.join(keys).replace('.[', '[').replace('.{', '{'),
                hide
            )
        else:
            self._ctx_arg_map[var_name] = (
                '.'.join([ctx_namespace, *keys]).replace('.[', '[').replace('.{', '{'),
                hide
            )

        if isinstance(arg, CMDResourceGroupNameArg):
            assert self.rg_arg_var is None, "Resource Group Argument defined twice"
            self.rg_arg_var = arg.var

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
        variant = to_snake_case(variant)
        if name_only:
            return variant

        is_selector = variant in self._selectors

        if is_selector:
            return f'self.ctx.selectors.{variant}', is_selector
        else:
            return f'self.ctx.vars.{variant}', is_selector

    def set_update_cls(self, schema):
        cls_name = schema.cls
        assert cls_name not in self.update_clses, f"Schema cls '{cls_name}', is defined more than once"
        self.update_clses[cls_name] = AzRequestClsGenerator(self, cls_name, schema)

    def set_response_cls(self, schema):
        cls_name = schema.cls
        assert cls_name not in self.response_clses, f"Schema cls '{cls_name}', is defined more than once"
        self.response_clses[cls_name] = AzResponseClsGenerator(self, cls_name, schema)

    def set_selector(self, selector):
        self._selectors[self.get_variant(selector.var, name_only=True)] = selector

    def render_arg_resource_id_template(self, template):
        # TODO: fill blank placeholders as much as possible

        return template


class AzCommandGenerator:

    ARGS_SCHEMA_NAME = "_args_schema"

    def __init__(self, cmd: CLIAtomicCommand, is_wait=False):
        self.cmd = cmd
        self.is_wait = is_wait
        self.cmd_ctx = AzCommandCtx()

        if cmd.names[-1] in ("create", "list"):
            # disable id part for create and list command
            self.cmd_ctx.support_id_part = False

        assert isinstance(self.cmd.cfg, CMDCommand)
        self.conditions = []
        if self.cmd.cfg.conditions:
            for idx, condition in enumerate(self.cmd.cfg.conditions):
                self.conditions.append((condition.var, f"condition_{idx}", condition))

        # prepare arguments
        self.arg_groups = []
        if self.cmd.cfg.arg_groups:
            for arg_group in self.cmd.cfg.arg_groups:
                if arg_group.args:
                    self.arg_groups.append(AzArgGroupGenerator(self.ARGS_SCHEMA_NAME, self.cmd_ctx, arg_group))

        self.selectors = []
        if self.cmd.cfg.subresource_selector:
            # disable id part for subresource command
            self.cmd_ctx.support_id_part = False

            if isinstance(self.cmd.cfg.subresource_selector, CMDJsonSubresourceSelector):
                selector = AzJsonSelectorGenerator(self.cmd_ctx, self.cmd.cfg.subresource_selector)
                self.selectors.append(selector)
            else:
                raise NotImplementedError()

        # prepare operations
        self.lro_counts = 0
        self.operations = []
        self.http_operations = []
        self.json_instance_operations = []
        self.support_generic_update = False

        json_instance_counts = 0
        for operation in self.cmd.cfg.operations:
            lr = False
            if isinstance(operation, CMDHttpOperation):
                op_cls_name = to_camel_case(operation.operation_id)
                if operation.long_running:
                    lr = True
                op = AzHttpOperationGenerator(op_cls_name, self.cmd_ctx, operation)
                self.http_operations.append(op)
            elif isinstance(operation, CMDInstanceUpdateOperation):
                if isinstance(operation.instance_update, CMDJsonInstanceUpdateAction):
                    op_cls_name = f'InstanceUpdateByJson'
                    if json_instance_counts > 0:
                        op_cls_name += f'_{json_instance_counts}'
                    op = AzJsonUpdateOperationGenerator(op_cls_name, self.cmd_ctx, operation)
                    self.json_instance_operations.append(op)
                    json_instance_counts += 1
                else:
                    raise NotImplementedError()
            elif isinstance(operation, CMDInstanceCreateOperation):
                if isinstance(operation.instance_create, CMDJsonInstanceCreateAction):
                    op_cls_name = f"InstanceCreateByJson"
                    if json_instance_counts > 0:
                        op_cls_name += f"_{json_instance_counts}"
                    op = AzJsonCreateOperationGenerator(op_cls_name, self.cmd_ctx, operation)
                    self.json_instance_operations.append(op)
                    json_instance_counts += 1
                else:
                    raise NotImplementedError()
            elif isinstance(operation, CMDInstanceDeleteOperation):
                if isinstance(operation.instance_delete, CMDJsonInstanceDeleteAction):
                    op_cls_name = f'InstanceDeleteByJson'
                    if json_instance_counts > 0:
                        op_cls_name += f'_{json_instance_counts}'
                    op = AzJsonDeleteOperationGenerator(op_cls_name, self.cmd_ctx, operation)
                    self.json_instance_operations.append(op)
                    json_instance_counts += 1
            else:
                raise NotImplementedError()

            if lr:
                self.lro_counts += 1
            self.operations.append(op)

        # generic_update_op
        if self.json_instance_operations:
            self.support_generic_update = self.cmd.names[-1] == "update"
            if self.support_generic_update:
                # make sure all json update operations has the same variant key
                variant_key = self.json_instance_operations[0].variant_key
                is_selector_variant = self.json_instance_operations[0].is_selector_variant
                for op in self.json_instance_operations[1:]:
                    if not isinstance(op, AzJsonUpdateOperationGenerator) or op.variant_key != variant_key:
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
                if max_idx + 1 - min_idx != len(self.json_instance_operations):
                    # has other operations between
                    self.support_generic_update = False
                else:
                    op = AzGenericUpdateOperationGenerator(self.cmd_ctx, variant_key, is_selector_variant)
                    self.json_instance_operations.append(op)
                    self.operations = [*self.operations[:max_idx+1], op, *self.operations[max_idx+1:]]

        # Add instance update callbacks
        first_instance_op_idx = None
        last_instance_op_idx = None
        for idx, op in enumerate(self.operations):
            if isinstance(op, AzInstanceUpdateOperationGenerator):
                if first_instance_op_idx is None:
                    first_instance_op_idx = idx
                last_instance_op_idx = idx
        if last_instance_op_idx is not None and len(self.operations) > last_instance_op_idx + 1:
            post_op_generator = AzLifeCycleInstanceUpdateCallbackGenerator('post_instance_update', self.operations[last_instance_op_idx].variant_key, self.operations[last_instance_op_idx].is_selector_variant)
            self.operations = [*self.operations[:last_instance_op_idx+1], post_op_generator, *self.operations[last_instance_op_idx+1:]]
        if first_instance_op_idx is not None and first_instance_op_idx > 0:
            pre_op_generator = AzLifeCycleInstanceUpdateCallbackGenerator('pre_instance_update', self.operations[first_instance_op_idx].variant_key, self.operations[last_instance_op_idx].is_selector_variant)
            self.operations = [*self.operations[:first_instance_op_idx], pre_op_generator, *self.operations[first_instance_op_idx:]]

        # Add instance create callbacks
        first_instance_op_idx = None
        last_instance_op_idx = None
        for idx, op in enumerate(self.operations):
            if isinstance(op, AzJsonCreateOperationGenerator):
                if first_instance_op_idx is None:
                    first_instance_op_idx = idx
                last_instance_op_idx = idx
        if last_instance_op_idx is not None and len(self.operations) > last_instance_op_idx + 1:
            post_op_generator = AzLifeCycleInstanceUpdateCallbackGenerator('post_instance_create', self.operations[last_instance_op_idx].variant_key, self.operations[last_instance_op_idx].is_selector_variant)
            self.operations = [*self.operations[:last_instance_op_idx+1], post_op_generator, *self.operations[last_instance_op_idx+1:]]
        if first_instance_op_idx is not None and first_instance_op_idx > 0:
            pre_op_generator = AzLifeCycleCallbackGenerator('pre_instance_create')
            self.operations = [*self.operations[:first_instance_op_idx], pre_op_generator, *self.operations[first_instance_op_idx:]]

        # Add instance delete callbacks
        first_instance_op_idx = None
        last_instance_op_idx = None
        for idx, op in enumerate(self.operations):
            if isinstance(op, AzJsonDeleteOperationGenerator):
                if first_instance_op_idx is None:
                    first_instance_op_idx = idx
                last_instance_op_idx = idx
        if last_instance_op_idx is not None and len(self.operations) > last_instance_op_idx + 1:
            post_op_generator = AzLifeCycleCallbackGenerator('post_instance_delete')
            self.operations = [*self.operations[:last_instance_op_idx + 1], post_op_generator,
                               *self.operations[last_instance_op_idx + 1:]]
        if first_instance_op_idx is not None and first_instance_op_idx > 0:
            pre_op_generator = AzLifeCycleCallbackGenerator('pre_instance_delete')
            self.operations = [*self.operations[:first_instance_op_idx], pre_op_generator,
                               *self.operations[first_instance_op_idx:]]

        self.plane = None
        for resource in self.cmd.resources:
            if not self.plane:
                self.plane = resource.plane
            elif resource.plane != self.plane:
                raise ValueError(f"Find multiple planes in a command: {resource.plane}, {self.plane}")

        self.client_type = PlaneEnum.http_client(self.plane)
        # TODO: add support for DataPlaneClient client_type

        # prepare outputs
        self.outputs = []
        self.paging = False
        if self.cmd.cfg.outputs:
            for output in self.cmd.cfg.outputs:
                output_generator = AzOutputGenerator(output, self.cmd_ctx)
                self.outputs.append(output_generator)
                if output_generator.next_link:
                    self.paging = True
        if self.lro_counts > 0 and self.paging:
            self.paging = False
            # TODO: support paging for long running command later
            logger.warning(f"Disable paging for long running command: '{self.name}'")

        if len(self.outputs) > 1:
            # TODO: add support for output larger than 1
            raise NotImplementedError()

        if self.paging:
            # disable id part for paging commands
            self.cmd_ctx.support_id_part = False

    @property
    def name(self):
        return ' '.join(self.cmd.names)

    @property
    def cls_name(self):
        return to_camel_case(self.cmd.names[-1])

    @property
    def helper_cls_name(self):
        return f'_{to_camel_case(self.cmd.names[-1])}Helper'

    @property
    def help(self):
        return self.cmd.help

    @property
    def register_info(self):
        return self.cmd.register_info

    @property
    def support_no_wait(self):
        return self.cmd.support_no_wait or False

    @property
    def version(self):
        return self.cmd.version

    @property
    def resources(self):
        return self.cmd.resources

    def get_arg_clses(self):
        return sorted(self.cmd_ctx.arg_clses.values(), key=lambda a: a.name)

    def get_update_clses(self):
        return sorted(self.cmd_ctx.update_clses.values(), key=lambda s: s.name)

    def get_response_clses(self):
        return sorted(self.cmd_ctx.response_clses.values(), key=lambda s: s.name)

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
