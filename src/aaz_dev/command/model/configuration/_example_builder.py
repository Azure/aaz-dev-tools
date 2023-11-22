import json
from abc import abstractmethod

from command.controller.cfg_reader import CfgReader
from command.model.configuration import CMDArgGroup
from swagger.model.schema.parameter import PathParameter, QueryParameter, HeaderParameter, BodyParameter
from ._utils import CMDArgBuildPrefix


class ExampleBuilder:
    def __init__(self, command=None, operation=None):
        self.command = command
        self.operation = operation
        self.example_items = []

    def get_option_name(self, arg_var):
        if not arg_var:
            return

        arg_parent, arg, arg_option = CfgReader.find_arg_in_command_with_parent_by_var(self.command, arg_var)
        if isinstance(arg_parent, CMDArgGroup) and arg:
            return arg_option  # top-level parameter

    @abstractmethod
    def mapping(self, example_dict):
        pass


class SwaggerExampleBuilder(ExampleBuilder):
    def mapping(self, example_dict):
        for param in self.operation.parameters:
            if param.name not in example_dict:
                continue

            arg_var = None
            value = example_dict[param.name]
            param_name = param.name.replace("$", "")

            if param.IN_VALUE == BodyParameter.IN_VALUE:
                arg_var = f"${param_name}"
                self.example_items += self.build(arg_var, value)
            else:
                if param.IN_VALUE == PathParameter.IN_VALUE:
                    arg_var = f"{CMDArgBuildPrefix.Path}.{param_name}"
                if param.IN_VALUE == QueryParameter.IN_VALUE:
                    arg_var = f"{CMDArgBuildPrefix.Query}.{param_name}"
                if param.IN_VALUE == HeaderParameter.IN_VALUE:
                    arg_var = f"{CMDArgBuildPrefix.Header}.{param_name}"

            option = self.get_option_name(arg_var)
            if option:
                self.example_items.append((option, json.dumps(value)))

        return self.example_items

    def build(self, var_prefix, example_dict):
        if not isinstance(example_dict, dict):
            return []

        example_items = []
        for name, value in example_dict.items():
            arg_var = f"{var_prefix}.{name}"

            option = self.get_option_name(arg_var)
            if option:
                example_items.append((option, json.dumps(value)))

            example_items += self.build(arg_var, value)

        return example_items
