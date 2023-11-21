import json

from command.controller.cfg_reader import CfgReader
from command.model.configuration._arg_group import CMDArgGroup
from swagger.model.schema.parameter import PathParameter, QueryParameter, HeaderParameter, BodyParameter
from ._utils import CMDArgBuildPrefix


class ExampleBuilder:
    def __init__(self, operation=None):
        self.operation = operation

    def param_mapping(self, params):
        raise NotImplementedError()


class SwaggerExampleBuilder(ExampleBuilder):
    def __init__(self, operation=None, command=None):
        super().__init__(operation)

        self.command = command

    def param_mapping(self, example_dict):
        def build_example_param(arg_var, value):
            parent, arg, arg_idx = CfgReader.find_arg_in_command_with_parent_by_var(self.command, arg_var)

            # ignore parameter flattened or not found
            if arg and isinstance(parent, CMDArgGroup):
                example_params.append((arg_idx, json.dumps(value)))

        def build_body_example_param(parent_arg_var, example):
            if not isinstance(example, dict):
                return

            for example_param, example_value in example.items():
                arg_var = parent_arg_var + '.' + example_param
                build_example_param(arg_var, example_value)
                build_body_example_param(arg_var, example_value)

        example_params = []

        for op_param in self.operation.parameters:
            if op_param.name in example_dict:
                if PathParameter.IN_VALUE == op_param.IN_VALUE:
                    path_arg_var = CMDArgBuildPrefix.Path + '.' + op_param.name.replace('$', '')
                    build_example_param(path_arg_var, example_dict[op_param.name])

                elif QueryParameter.IN_VALUE == op_param.IN_VALUE:
                    query_arg_var = CMDArgBuildPrefix.Query + '.' + op_param.name.replace('$', '')
                    build_example_param(query_arg_var, example_dict[op_param.name])

                elif HeaderParameter.IN_VALUE == op_param.IN_VALUE:
                    header_arg_var = CMDArgBuildPrefix.Header + '.' + op_param.name.replace('$', '')
                    build_example_param(header_arg_var, example_dict[op_param.name])

                elif BodyParameter.IN_VALUE == op_param.IN_VALUE:
                    body_arg_var = '$' + op_param.name.replace('$', '')
                    build_example_param(body_arg_var, example_dict[op_param.name])
                    build_body_example_param(body_arg_var, example_dict[op_param.name])

        return example_params
