import copy
import re
from abc import abstractmethod

from command.controller.cfg_reader import CfgReader
from command.model.configuration import CMDArgGroup
from command.model.configuration._utils import CMDArgBuildPrefix
from swagger.model.schema.parameter import PathParameter, QueryParameter, HeaderParameter, BodyParameter


class ExampleItem:
    def __init__(
            self,
            cmd_operation=None,
            arg_var=None,
            key=None,
            val=None,
            arg_parent=None,
            arg=None,
            arg_option=None
    ):
        self.cmd_operation = cmd_operation
        self.arg_var = arg_var
        self.key = key
        self.val = val

        self.arg_parent, self.arg, self.arg_option = arg_parent, arg, arg_option

        if self.arg_option is not None:
            self.arg_option = self.arg_option.split(".")[-1]

    @classmethod
    def new_instance(cls, command=None, cmd_operation=None, arg_var=None, key=None, val=None):
        arg_parent, arg, arg_option = CfgReader.find_arg_in_command_with_parent_by_var(command, arg_var)

        if arg_parent or arg or arg_option:
            return cls(
                cmd_operation=cmd_operation,
                arg_var=arg_var,
                key=key,
                val=val,
                arg_parent=arg_parent,
                arg=arg,
                arg_option=arg_option
            )

    @property
    def is_flatten(self):
        return self.arg_parent and not self.arg

    @property
    def is_top_level(self):
        return isinstance(self.arg_parent, CMDArgGroup) and self.arg

    @property
    def discriminators(self):
        for _, schema, _ in CfgReader.iter_schema_in_operation_by_arg_var(self.cmd_operation, self.arg_var):
            if hasattr(schema, "discriminators") and schema.discriminators:
                return schema.discriminators

        return []


class ExampleBuilder:
    def __init__(self, command=None):
        self.command = command
        self.example_items = []

    @abstractmethod
    def mapping(self, example_dict):
        pass


class SwaggerExampleBuilder(ExampleBuilder):
    def __init__(self, command=None, operation=None, cmd_operation=None):
        super().__init__(command=command)
        self.operation = operation
        self.cmd_operation = cmd_operation

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

            item = ExampleItem.new_instance(
                command=self.command,
                cmd_operation=self.cmd_operation,
                arg_var=arg_var,
                key=param_name,
                val=value
            )
            if item and item.is_top_level:
                self.example_items.append((item.arg_option, value))

        return self.example_items

    def build(self, var_prefix, example_obj, disc=None):
        example_items = []
        if isinstance(example_obj, list):
            arg_var = f"{var_prefix}[]"
            item = ExampleItem.new_instance(
                command=self.command,
                cmd_operation=self.cmd_operation,
                arg_var=arg_var
            )
            if item:
                discs = item.discriminators
                for obj in example_obj:
                    for disc in discs:
                        if disc.property not in obj or obj[disc.property] != disc.value:
                            continue

                        example_items += self.build(arg_var, obj, disc)
                        break
                    else:
                        example_items += self.build(arg_var, obj)

        elif isinstance(example_obj, dict):
            disc_name = None
            if disc is not None:  # handle discriminator
                example_obj.pop(disc.property)  # ignore discriminator prop

                safe_value = self.get_safe_value(disc.value)
                disc_item = ExampleItem.new_instance(
                    command=self.command,
                    cmd_operation=self.cmd_operation,
                    arg_var=f"{var_prefix}.{safe_value}"
                )

                if disc_item and (disc_name := disc_item.arg_option):
                    example_obj[disc_name] = copy.deepcopy(example_obj)  # further trim (polymorphic or not)
                    example_items += self.build(disc_item.arg_var, example_obj[disc_name])

            for name, value in example_obj.copy().items():
                if name == disc_name:
                    continue

                item = ExampleItem.new_instance(
                    command=self.command,
                    cmd_operation=self.cmd_operation,
                    arg_var=f"{var_prefix}{{}}.{name}",
                    key=name,
                    val=value
                )
                if not item:
                    item = ExampleItem.new_instance(
                        command=self.command,
                        cmd_operation=self.cmd_operation,
                        arg_var=f"{var_prefix}.{name}",
                        key=name,
                        val=value
                    )

                if item:
                    example_obj.pop(name)  # will push back if arg_var valid

                    for disc in item.discriminators:
                        if disc.property not in value or value[disc.property] != disc.value:
                            continue

                        example_items += self.build(item.arg_var, value, disc)
                        break
                    else:
                        example_items += self.build(item.arg_var, value)

                    if item.is_top_level:
                        example_items.append((item.arg_option, value))

                    elif item.is_flatten:
                        for k, v in item.val.items():
                            example_obj[k] = v

                    elif item.arg_option:
                        example_obj[item.arg_option] = item.val

        return example_items

    @staticmethod
    def get_safe_value(value):
        """Some value may contain special characters such as Microsoft.db/mysql, it will cause issues.
           This function will replace them by `_`
        """
        safe_value = re.sub(r'[^A-Za-z0-9_-]', '_', value)

        return safe_value
