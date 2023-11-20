import json

from collections import defaultdict
from command.controller.cfg_reader import CfgReader
from command.model.configuration import CMDRequestJson, CMDResponseJson
from swagger.model.schema.parameter import PathParameter, QueryParameter, HeaderParameter, BodyParameter, \
    FormDataParameter
from ._schema import CMDSchema, CMDObjectSchemaBase, CMDObjectSchemaDiscriminator, CMDArraySchemaBase, \
    CMDObjectSchemaAdditionalProperties
from ._utils import CMDArgBuildPrefix


class ExampleBuilder:
    def __init__(self, operation=None):
        self.operation = operation

    def param_mapping(self, params):
        raise NotImplementedError()


class SwaggerExampleBuilder(ExampleBuilder):
    def __init__(self, operation=None, command=None, cmd_operation=None, cmd_builder=None):
        super().__init__(operation)

        param_models = defaultdict(dict)
        for param in self.operation.parameters:
            param_models[param.IN_VALUE][param.name] = param.to_cmd(cmd_builder)

        self.op_param_models = param_models
        self.command = command
        self.cmd_operation = cmd_operation

    def build_arg_var(self, params):
        param_models = self._build_model(params)
        self._build_arg_var_by_model(param_models)

        return param_models

    def param_mapping(self, params):
        def _mapping(arg):
            if hasattr(arg, 'schema'):
                arg = arg.schema

            if hasattr(arg, 'arg_var'):
                param, arg_idx = CfgReader.find_arg_in_command_by_var(self.command, arg.arg_var)
                if arg_idx:
                    arg.arg_idx = arg_idx
                    matched_param_models.append(arg)

            if hasattr(arg, 'props') and arg.props:
                for prop in arg.props:
                    _mapping(prop)

        matched_param_models = []
        for params_models in params.values():
            for model in params_models.values():
                _mapping(model)

        return matched_param_models

    def _build_arg_var_by_model(self, param_models):
        def _build_arg_var(schema, parent_schema=None, var_prefix=None):
            if var_prefix is None:
                if parent_schema is None or parent_schema.arg_var is None:
                    arg_var = "$"
                else:
                    arg_var = parent_schema.arg_var
            else:
                arg_var = var_prefix

            if parent_schema is None or parent_schema.arg_var is None:
                if isinstance(schema, CMDSchema):
                    if not arg_var.endswith("$") and not schema.name.startswith('[') and not schema.name.startswith(
                            '{'):
                        arg_var += '.'
                    arg_var += f'{schema.name}'.replace('$', '')  # some schema name may contain $
                else:
                    raise NotImplementedError()
            else:
                if isinstance(parent_schema, CMDArraySchemaBase):
                    arg_var += '[]'
                elif isinstance(parent_schema, CMDObjectSchemaAdditionalProperties):
                    arg_var += '{}'
                elif isinstance(parent_schema, (CMDObjectSchemaBase, CMDObjectSchemaDiscriminator)):
                    if not isinstance(schema, CMDObjectSchemaAdditionalProperties):
                        if not arg_var.endswith("$"):
                            arg_var += '.'
                        if isinstance(schema, CMDObjectSchemaDiscriminator):
                            arg_var += schema.get_safe_value()
                        elif isinstance(schema, CMDSchema):
                            arg_var += f'{schema.name}'.replace('$', '')  # some schema name may contain $
                        else:
                            raise NotImplementedError()
                else:
                    raise NotImplementedError()
                cls_name = getattr(parent_schema, 'cls', None)
                if cls_name is not None:
                    arg_var = arg_var.replace(parent_schema.arg_var, f"@{cls_name}")

            return arg_var

        def _build_schema_arg_var(schema, parent_schema=None, var_prefix=None):
            arg_var = _build_arg_var(schema, parent_schema, var_prefix)
            schema.arg_var = arg_var

            if hasattr(schema, 'props') and schema.props:
                for prop in schema.props:
                    _build_schema_arg_var(prop, schema, var_prefix)

        if PathParameter.IN_VALUE in param_models:
            for _, model in param_models[PathParameter.IN_VALUE].items():
                _build_schema_arg_var(schema=model, parent_schema=None, var_prefix=CMDArgBuildPrefix.Path)

        if QueryParameter.IN_VALUE in param_models:
            for _, model in param_models[QueryParameter.IN_VALUE].items():
                _build_schema_arg_var(schema=model, parent_schema=None, var_prefix=CMDArgBuildPrefix.Query)

        if HeaderParameter.IN_VALUE in param_models:
            for _, model in param_models[HeaderParameter.IN_VALUE].items():
                _build_schema_arg_var(schema=model, parent_schema=None, var_prefix=CMDArgBuildPrefix.Header)

        if BodyParameter.IN_VALUE in param_models:
            for _, model in param_models[BodyParameter.IN_VALUE].items():
                _build_schema_arg_var(schema=model.schema, parent_schema=None, var_prefix=None)

        if FormDataParameter.IN_VALUE in param_models:
            raise NotImplementedError()

    def _build_model(self, params):
        def build_sub_param_model(new_model, old_model, example_params):
            new_model.value = json.dumps(example_params)
            if not hasattr(old_model, 'props') or not old_model.props:
                return

            new_model_props = []
            for prop in old_model.props:
                if prop.name in example_params:
                    new_prop_model = type(prop)()
                    new_prop_model.name = prop.name
                    new_model_props.append(new_prop_model)
                    build_sub_param_model(new_prop_model, prop, example_params[prop.name])

            new_model.props = new_model_props

        param_models = defaultdict(dict)
        for in_value, op_params in self.op_param_models.items():
            for param_name, param_model in op_params.items():

                if param_name in params:
                    new_model = type(param_model)()
                    new_model.name = param_name
                    param_models[in_value][param_name] = new_model

                    if isinstance(param_model, (CMDRequestJson, CMDResponseJson)):
                        new_model.schema = type(param_model.schema)()
                        new_model = new_model.schema
                        new_model.name = param_model.schema.name
                        param_model = param_model.schema

                    build_sub_param_model(new_model, param_model, params[param_name])

        return param_models

    # def _find_param_in_operation(self, example_param):
    #     for param in self.operation.parameters:
    #         if param.name == example_param:
    #             return param
    #
    #     return None
