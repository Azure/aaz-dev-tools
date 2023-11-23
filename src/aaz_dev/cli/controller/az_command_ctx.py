import logging

from command.model.configuration import CMDResourceGroupNameArg
from utils import exceptions
from utils.case import to_snake_case
from .az_arg_group_generator import AzArgClsGenerator
from .az_operation_generator import AzRequestClsGenerator, AzResponseClsGenerator

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
