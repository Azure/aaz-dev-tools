import json
from abc import abstractmethod

from command.controller.cfg_reader import CfgReader
from command.model.configuration import CMDArgGroup
from swagger.model.schema.parameter import PathParameter, QueryParameter, HeaderParameter, BodyParameter
from command.model.configuration._utils import CMDArgBuildPrefix


class ExampleItem:
    def __init__(self, command=None, arg_var=None, key=None, val=None):
        self.arg_var = arg_var
        self.key = key
        self.val = val

        self.arg_parent, self.arg, self.arg_option = CfgReader.find_arg_in_command_with_parent_by_var(command, arg_var)

        if self.arg_option is not None:
            self.arg_option = self.arg_option.split(".")[-1]

    @property
    def is_flatten(self):
        return self.arg_parent and not self.arg

    @property
    def is_top_level(self):
        return isinstance(self.arg_parent, CMDArgGroup) and self.arg


class ExampleBuilder:
    def __init__(self, command=None):
        self.command = command
        self.example_items = []

    @abstractmethod
    def mapping(self, example_dict):
        pass


class SwaggerExampleBuilder(ExampleBuilder):
    def __init__(self, command=None, operation=None):
        super().__init__(command=command)
        self.operation = operation

    def mapping(self, example_dict):
        for param in self.operation.parameters:
            if param.name not in example_dict:
                continue

            arg_var = None
            value = example_dict[param.name]
            param_name = param.name.replace("$", "")  # schema name may contain $

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

            item = ExampleItem(command=self.command, arg_var=arg_var, key=param_name, val=value)
            if item.is_top_level:
                self.example_items.append((item.arg_option, json.dumps(value)))

        return self.example_items

    def build(self, var_prefix, example_dict):
        example_items = []
        if isinstance(example_dict, list):
            arg_var = f"{var_prefix}[]"
            for item in example_dict:
                example_items += self.build(arg_var, item)
        elif isinstance(example_dict, dict):
            for name, value in example_dict.copy().items():
                item = ExampleItem(command=self.command, arg_var=f"{var_prefix}{{}}.{name}", key=name, val=value)
                if item.arg is None:
                    item = ExampleItem(command=self.command, arg_var=f"{var_prefix}.{name}", key=name, val=value)

                example_items += self.build(item.arg_var, value)

                if item.is_top_level:
                    example_items.append((item.arg_option, json.dumps(value)))
                elif item.is_flatten:
                    example_dict.pop(item.key)
                    for k, v in item.val.items():
                        example_dict[k] = v
                elif item.arg_option:
                    example_dict.pop(item.key)
                    example_dict[item.arg_option] = item.val

        return example_items
