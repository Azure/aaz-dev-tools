from command.model.configuration import CMDStringArgBase, CMDByteArgBase, CMDBinaryArgBase, CMDDurationArgBase, \
    CMDDateArgBase, CMDDateTimeArgBase, CMDUuidArgBase, CMDPasswordArgBase, \
    CMDSubscriptionIdArgBase, CMDResourceGroupNameArgBase, CMDResourceIdArgBase, CMDResourceLocationArgBase, \
    CMDIntegerArgBase, CMDInteger32ArgBase, CMDInteger64ArgBase, CMDBooleanArgBase, CMDFloatArgBase, \
    CMDFloat32ArgBase, CMDFloat64ArgBase, CMDObjectArgBase, CMDArrayArgBase, CMDClsArgBase, CMDSubscriptionIdArg, CMDArg
from command.model.configuration import CMDArgGroup, CMDArgumentHelp
from utils.case import to_camel_case, to_snack_case
from utils import exceptions
from utils.stage import AAZStageEnum


class AzArgGroupGenerator:

    def __init__(self, args_schema_name, cmd_ctx, cls_map, arg_group):
        assert isinstance(arg_group, CMDArgGroup)
        assert arg_group.name is not None   # empty string is valid
        self.name = arg_group.name
        self._cls_map = cls_map
        self._arg_group = arg_group
        self._args_schema_name = args_schema_name
        self._cmd_ctx = cmd_ctx

        # update args
        for arg in self._arg_group.args:
            self._update_over_arg(arg, parse_arg_name(arg))

    def _update_over_arg(self, arg, *arg_keys):
        if isinstance(arg, CMDArg):
            if isinstance(arg, CMDSubscriptionIdArg) \
                    and arg_keys == ('subscription', ) and arg.options == ['subscription']:
                # use self.ctx.subscription_id
                self._cmd_ctx.set_argument(('subscription_id', ), arg.var, arg.hide, ctx_namespace='self.ctx')
            else:
                self._cmd_ctx.set_argument(arg_keys, arg.var, arg.hide)

        if getattr(arg, 'cls', None):
            assert arg.cls not in self._cls_map
            self._cls_map[arg.cls] = AzArgClsGenerator(arg.cls, self._cls_map, arg)
            self._cmd_ctx.set_argument_cls(arg.cls)
            arg_keys = (f"@{arg.cls}", )  # prepare for cls sub property use

        if isinstance(arg, CMDObjectArgBase):
            if arg.args:
                for sub_arg in arg.args:
                    self._update_over_arg(sub_arg, *arg_keys, parse_arg_name(sub_arg))
            if arg.additional_props and arg.additional_props.item:
                self._update_over_arg(arg.additional_props.item, *arg_keys, '{}')
        elif isinstance(arg, CMDArrayArgBase):
            if arg.item:
                self._update_over_arg(arg.item, *arg_keys, '[]')

    def iter_scopes(self):
        scope = self._args_schema_name
        scope_define = f"cls.{self._args_schema_name}"
        rendered_args = []
        search_args = {}
        for a in self._arg_group.args:
            if a.hide:
                # escape hide argument
                continue

            if isinstance(a, CMDSubscriptionIdArg) and a.options == ['subscription']:
                # ignore subscription id, because cli core registered global _subscription argument
                continue

            a_name = parse_arg_name(a)
            a_type, a_kwargs, cls_builder_name = render_arg(a, self._cls_map, arg_group=self.name)

            rendered_args.append((a_name, a_type, a_kwargs, cls_builder_name))
            if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
                search_args[a_name] = a
        if rendered_args:
            yield scope, scope_define, rendered_args

        for a_name, a in search_args.items():
            for scopes in _iter_scopes_by_arg_base(a, a_name, f"{scope_define}.{a_name}", self._cls_map):
                yield scopes


class AzArgClsGenerator:

    def __init__(self, name, cls_map, arg):
        self.arg = arg
        self.name = name
        self.args_schema_name = f"_args_{to_snack_case(name)}"
        self.builder_name = parse_cls_builder_name(name)
        self._cls_map = cls_map
        self.arg_type, self.arg_kwargs, _ = render_arg_base(self.arg, self._cls_map)

        self.props = []
        if isinstance(arg, CMDObjectArgBase):
            if arg.args and arg.additional_props:
                # not support to translate argument with both args and additional_props
                raise NotImplementedError()
            if arg.args:
                for a in arg.args:
                    if a.hide:
                        # escape hide argument
                        continue
                    self.props.append(parse_arg_name(a))
            elif arg.additional_props:
                self.props.append("Element")
        elif isinstance(arg, CMDArrayArgBase):
            self.props.append("Element")

        self.props = sorted(self.props)

    def iter_scopes(self):
        for scopes in _iter_scopes_by_arg_base(self.arg, to_snack_case(self.name), f"cls.{self.args_schema_name}", self._cls_map):
            yield scopes


def _iter_scopes_by_arg_base(arg, name, scope_define, cls_map):
    rendered_args = []
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
                a_name = parse_arg_name(a)
                a_type, a_kwargs, cls_builder_name = render_arg(a, cls_map)
                rendered_args.append((a_name, a_type, a_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
                    search_args[a_name] = a
        elif arg.additional_props:
            # AAZDictArg
            assert arg.additional_props.item is not None
            a = arg.additional_props.item
            a_name = "Element"
            a_type, a_kwargs, cls_builder_name = render_arg_base(a, cls_map)
            rendered_args.append((a_name, a_type, a_kwargs, cls_builder_name))
            if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
                search_args[a_name] = a
    elif isinstance(arg, CMDArrayArgBase):
        # AAZListArg
        assert arg.item is not None
        a = arg.item
        a_name = "Element"
        a_type, a_kwargs, cls_builder_name = render_arg_base(a, cls_map)
        rendered_args.append((a_name, a_type, a_kwargs, cls_builder_name))
        if not cls_builder_name and isinstance(a, (CMDObjectArgBase, CMDArrayArgBase)):
            search_args[a_name] = a
    else:
        raise NotImplementedError()

    if rendered_args:
        yield name, scope_define, rendered_args

    for a_name, a in search_args.items():
        a_scope_define = f"{scope_define}.{a_name}"
        if a_name == "Element":
            a_name = '_element'
        for scopes in _iter_scopes_by_arg_base(a, a_name, a_scope_define, cls_map):
            yield scopes


def parse_cls_builder_name(cls_name):
    return f"_build_args_{to_snack_case(cls_name)}"


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


def parse_arg_enum(enum):
    if not enum or not enum.items:
        return None
    e = {}
    for item in enum.items:
        if item.hide:
            continue
        e[item.name] = item.value
    return e


def parse_arg_name(arg):
    arg_name_length = 0
    arg_name = None
    for option in arg.options:
        if len(option) > arg_name_length:
            arg_name = to_snack_case(option)
            arg_name_length = len(option)
    return arg_name


def render_arg(arg, cls_map, arg_group=None):
    arg_kwargs = {
        "options": []
    }
    for option in arg.options:
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
        arg_kwargs["help"] = parse_arg_help(arg.help)
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

    arg_type, arg_kwargs, cls_builder_name = render_arg_base(arg, cls_map, arg_kwargs)

    return arg_type, arg_kwargs, cls_builder_name


def render_arg_base(arg, cls_map, arg_kwargs=None):
    # TODO: add format in argument
    if isinstance(arg, CMDClsArgBase):
        cls_name = arg.type[1:]
        arg = cls_map[cls_name].arg
    else:
        cls_name = getattr(arg, 'cls', None)
    cls_builder_name = parse_cls_builder_name(cls_name) if cls_name else None

    if arg_kwargs is None:
        arg_kwargs = {}

    if isinstance(arg, CMDStringArgBase):
        arg_type = "AAZStrArg"
        enum = parse_arg_enum(arg.enum)
        if enum:
            arg_kwargs['enum'] = enum

        if isinstance(arg, CMDSubscriptionIdArgBase):
            arg_type = "AAZSubscriptionIdArg"
        elif isinstance(arg, CMDResourceGroupNameArgBase):
            arg_type = "AAZResourceGroupNameArg"
            if 'options' in arg_kwargs and set(arg_kwargs['options']) == {'--resource-group', '-g'}:
                # it's default value
                del arg_kwargs['options']
            if 'id_part' in arg_kwargs and arg_kwargs['id_part'] == 'resource_group':
                # it's default value
                del arg_kwargs['id_part']
        elif isinstance(arg, CMDResourceIdArgBase):
            arg_type = "AAZResourceIdArg"
            # TODO: add format for it
        elif isinstance(arg, CMDResourceLocationArgBase):
            arg_type = "AAZResourceLocationArg"
            if 'options' in arg_kwargs and set(arg_kwargs['options']) == {'--location', '-l'}:
                # it's default value
                del arg_kwargs['options']
        elif isinstance(arg, CMDByteArgBase):
            raise NotImplementedError()
        elif isinstance(arg, CMDBinaryArgBase):
            raise NotImplementedError()
        elif isinstance(arg, CMDDurationArgBase):
            raise NotImplementedError()
        elif isinstance(arg, CMDDateArgBase):
            raise NotImplementedError()
        elif isinstance(arg, CMDDateTimeArgBase):
            raise NotImplementedError()
        elif isinstance(arg, CMDUuidArgBase):
            arg_type = "AAZStrArg"
            # TODO: add format for it
        elif isinstance(arg, CMDPasswordArgBase):
            raise NotImplementedError()

    elif isinstance(arg, CMDIntegerArgBase):
        arg_type = "AAZIntArg"
        enum = parse_arg_enum(arg.enum)
        if enum:
            arg_kwargs['enum'] = enum

        if isinstance(arg, CMDInteger32ArgBase):
            raise NotImplementedError()
        elif isinstance(arg, CMDInteger64ArgBase):
            raise NotImplementedError()

    elif isinstance(arg, CMDBooleanArgBase):
        arg_type = "AAZBoolArg"

    elif isinstance(arg, CMDFloatArgBase):
        arg_type = "AAZFloatArg"
        enum = parse_arg_enum(arg.enum)
        if enum:
            arg_kwargs['enum'] = enum

        if isinstance(arg, CMDFloat32ArgBase):
            raise NotImplementedError()
        elif isinstance(arg, CMDFloat64ArgBase):
            raise NotImplementedError()

    elif isinstance(arg, CMDObjectArgBase):
        if arg.args:
            arg_type = "AAZObjectArg"
            if arg.additional_props:
                raise NotImplementedError()
        elif arg.additional_props:
            arg_type = "AAZDictArg"
        else:
            raise NotImplementedError()

    elif isinstance(arg, CMDArrayArgBase):
        arg_type = "AAZListArg"

    else:
        raise NotImplementedError()

    return arg_type, arg_kwargs, cls_builder_name
