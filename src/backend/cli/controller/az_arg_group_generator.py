from command.model.configuration import CMDStringArgBase, CMDByteArgBase, CMDBinaryArgBase, CMDDurationArgBase, \
    CMDDateArgBase, CMDDateTimeArgBase, CMDUuidArgBase, CMDPasswordArgBase, \
    CMDSubscriptionIdArgBase, CMDResourceGroupNameArgBase, CMDResourceIdArgBase, CMDResourceLocationArgBase, \
    CMDIntegerArgBase, CMDInteger32ArgBase, CMDInteger64ArgBase, CMDBooleanArgBase, CMDFloatArgBase, \
    CMDFloat32ArgBase, CMDFloat64ArgBase, CMDObjectArgBase, CMDArrayArgBase, CMDClsArgBase, CMDObjectArg, CMDArrayArg
from command.model.configuration import CMDArgGroup, CMDArgumentHelp
from utils.case import to_camel_case, to_snack_case
from utils import exceptions
from utils.stage import AAZStageEnum


class AzArgGroupGenerator:

    @staticmethod
    def cls_builder_name(cls_name):
        return f"_build_args_{to_camel_case(cls_name)}"

    @staticmethod
    def parse_arg_help(help):
        assert isinstance(help, CMDArgumentHelp)
        if not help.lines and not help.ref_commands:
            if not help.short:
                raise exceptions.InvalidAPIUsage("Invalid argument help, short summery is miss.")
            return help.short
        h = {
            "short-summery": help.short
        }
        if help.lines:
            h["long-summery"] = '\n'.join(help.lines)
        if help.ref_commands:
            h["populator-commands"] = [*help.ref_commands]

    @staticmethod
    def parse_arg_enum(enum):
        if not enum or not enum.items:
            return None
        e = {}
        for item in enum.items:
            if item.hide:
                continue
            e[item.name] = item.value
        return e

    def __init__(self, args_schema_name, arguments, cls_reference, arg_group):
        assert isinstance(arguments, dict)
        assert isinstance(arg_group, CMDArgGroup)
        assert arg_group.name is not None   # empty string is valid
        self.name = arg_group.name
        self._cls_reference = cls_reference
        self._arg_group = arg_group
        self._args_schema_name = args_schema_name
        # update the cls_reference
        for arg in self._iter_args():
            if getattr(arg, 'cls', None):
                assert arg.cls not in self._cls_reference
                self._cls_reference[arg.cls] = arg

    def _iter_args(self):
        idx = 0
        args = [*self._arg_group.args]
        while idx < len(args):
            arg = args[idx]
            yield arg
            if isinstance(arg, CMDObjectArgBase):
                if arg.args:
                    args.extend(*arg.args)
                if arg.additional_props and arg.additional_props.item:
                    args.append(arg.additional_props.item)
            elif isinstance(arg, CMDArrayArgBase):
                if arg.item:
                    args.append(arg.item)
            idx += 1

    def iter_scopes(self):
        scope = self._args_schema_name
        scope_define = f"cls.{self._args_schema_name}"
        arguments = []
        search_args = {}
        for a in self._arg_group.args:
            if a.hide:
                # escape hide argument
                continue
            a_name, a_type, a_kwargs, cls_builder_name = self.render_arg(a, arg_group=self.name)
            arguments.append((a_name, a_type, a_kwargs, cls_builder_name))
            if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
                search_args[a_name] = a
        if arguments:
            yield scope, scope_define, arguments

        for a_name, a in search_args.items():
            for scopes in self._iter_scopes_by_arg_base(a, a_name, f"{scope_define}.{a_name}"):
                yield scopes

    def _iter_scopes_by_arg_base(self, arg, name, scope_define):
        arguments = []
        search_args = {}

        if isinstance(arg, CMDObjectArgBase):
            if arg.args and arg.additional_props:
                # not support to translate argument with both args and additional_props
                raise NotImplementedError()
            if arg.args:
                for a in arg.args:
                    if a.hide:
                        # escape hide argument
                        continue
                    a_name, a_type, a_kwargs, cls_builder_name = self.render_arg(a)
                    arguments.append((a_name, a_type, a_kwargs, cls_builder_name))
                    if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
                        search_args[a_name] = a
            elif arg.additional_props:
                # AAZDictArg
                assert arg.additional_props.item is not None
                a = arg.additional_props.item
                a_name = "Element"
                a_type, a_kwargs, cls_builder_name = self.render_arg_base(a)
                arguments.append((a_name, a_type, a_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
                    search_args[a_name] = a
        elif isinstance(arg, CMDArrayArgBase):
            # AAZListArg
            assert arg.item is not None
            a = arg.item
            a_name = "Element"
            a_type, a_kwargs, cls_builder_name = self.render_arg_base(a)
            arguments.append((a_name, a_type, a_kwargs, cls_builder_name))
            if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
                search_args[a_name] = a
        else:
            raise NotImplementedError()

        if arguments:
            yield name, scope_define, arguments

        for a_name, a in search_args.items():
            for scopes in self._iter_scopes_by_arg_base(a, a_name, f"{scope_define}.{a_name}"):
                yield scopes

    def render_arg(self, arg, arg_group=None):
        arg_kwargs = {
            "options": []
        }
        arg_name_length = 0
        arg_name = None
        for option in arg.options:
            if len(option) > arg_name_length:
                arg_name = to_snack_case(option)
                arg_name_length = len(option)
            if arg_group is not None:
                if len(option) == 1:
                    option = f"-{option}"
                else:
                    option = f"--{option}"
            arg_kwargs["options"].append(option)
        if getattr(arg, 'singular_options', None):
            arg_kwargs["singular_options"] = []
            for option in arg.singular_options:
                if arg_group is not None:
                    if len(option) == 1:
                        option = f"-{option}"
                    else:
                        option = f"--{option}"
                arg_kwargs["singular_options"].append(option)

        if arg_group:  # not empty string or None
            arg_kwargs["arg_group"] = arg_group
        if arg.help:
            arg_kwargs["help"] = self.parse_arg_help(arg.help)
        if arg.required:
            arg_kwargs["required"] = True
        if arg.stage == AAZStageEnum.Preview:
            arg_kwargs["is_preview"] = True
        elif arg.stage == AAZStageEnum.Experimental:
            arg_kwargs["is_experimental"] = True

        if arg.id_part:
            arg_kwargs["id_part"] = arg.id_part

        if arg.default:
            arg_kwargs["default"] = arg.default.value

        if arg.blank:
            arg_kwargs["blank"] = arg.blank.value

        arg_type, arg_kwargs, cls_builder_name = self.render_arg_base(arg, arg_kwargs)

        return arg_name, arg_type, arg_kwargs, cls_builder_name

    def render_arg_base(self, argument, arg_kwargs=None):
        if isinstance(argument, CMDClsArgBase):
            cls_name = argument.type[1:]
            argument = self._cls_reference[cls_name]
        else:
            cls_name = getattr(argument, 'cls', None)
        cls_builder_name = self.cls_builder_name(cls_name) if cls_name else None

        if arg_kwargs is None:
            arg_kwargs = {}

        if isinstance(argument, CMDStringArgBase):
            arg_type = "AAZStrType"
            enum = self.parse_arg_enum(argument.enum)
            if enum:
                arg_kwargs['enum'] = enum

            if isinstance(argument, CMDSubscriptionIdArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDResourceGroupNameArgBase):
                arg_type = "AAZResourceGroupNameArg"
                if 'options' in arg_kwargs and set(arg_kwargs['options']) == {'--resource-group', '-g'}:
                    # it's default value
                    del arg_kwargs['options']
                if 'id_part' in arg_kwargs and arg_kwargs['id_part'] == 'resource_group':
                    # it's default value
                    del arg_kwargs['id_part']
            elif isinstance(argument, CMDResourceIdArgBase):
                # TODO:
                raise NotImplementedError()
            elif isinstance(argument, CMDResourceLocationArgBase):
                # TODO:
                raise NotImplementedError()
            elif isinstance(argument, CMDByteArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDBinaryArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDDurationArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDDateArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDDateTimeArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDUuidArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDPasswordArgBase):
                raise NotImplementedError()

        elif isinstance(argument, CMDIntegerArgBase):
            arg_type = "AAZIntArg"
            enum = self.parse_arg_enum(argument.enum)
            if enum:
                arg_kwargs['enum'] = enum

            if isinstance(argument, CMDInteger32ArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDInteger64ArgBase):
                raise NotImplementedError()

        elif isinstance(argument, CMDBooleanArgBase):
            arg_type = "AAZBoolArg"

        elif isinstance(argument, CMDFloatArgBase):
            arg_type = "AAZFloatArg"
            enum = self.parse_arg_enum(argument.enum)
            if enum:
                arg_kwargs['enum'] = enum

            if isinstance(argument, CMDFloat32ArgBase):
                raise NotImplementedError()
            elif isinstance(argument, CMDFloat64ArgBase):
                raise NotImplementedError()

        elif isinstance(argument, CMDObjectArgBase):
            if argument.args:
                arg_type = "AAZObjectArg"
                if argument.additional_props:
                    raise NotImplementedError()
            elif argument.additional_props:
                arg_type = "AAZDictArg"
            else:
                raise NotImplementedError()

        elif isinstance(argument, CMDArrayArgBase):
            arg_type = "AAZListArg"

        else:
            raise NotImplementedError()

        return arg_type, arg_kwargs, cls_builder_name
