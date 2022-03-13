import re

import inflect
from utils.case import to_camel_case

from ._arg import CMDArg, CMDArgBase, CMDArgumentHelp, CMDArgEnum, CMDArgEnumItem, CMDArgDefault, CMDBooleanArgBase, \
    CMDArgBlank, CMDObjectArgAdditionalProperties
from ._format import CMDFormat
from ._schema import CMDObjectSchema, CMDSchema, CMDSchemaBase, CMDObjectSchemaBase, CMDObjectSchemaDiscriminator, \
    CMDArraySchema, CMDArraySchemaBase, CMDSchemaEnumItem, CMDObjectSchemaAdditionalProperties, CMDResourceIdSchema


class CMDArgBuilder:
    _inflect_engine = inflect.engine()

    @classmethod
    def new_builder(cls, schema, parent=None, var_prefix=None, is_update_action=False):
        if var_prefix is None:
            if parent is None or parent._arg_var is None:
                arg_var = "$"
            else:
                arg_var = parent._arg_var
        else:
            arg_var = var_prefix

        if parent is None or parent._arg_var is None:
            if isinstance(schema, CMDSchema):
                if not arg_var.endswith("$"):
                    arg_var += '.'
                arg_var += f'{schema.name}'.replace('$', '')  # some schema name may contain $
            else:
                raise NotImplementedError()
        else:
            assert isinstance(parent, CMDArgBuilder)
            if isinstance(parent.schema, CMDArraySchemaBase):
                arg_var += '[]'
            elif isinstance(parent.schema, CMDObjectSchemaAdditionalProperties):
                arg_var += '{}'
            elif isinstance(parent.schema, (CMDObjectSchemaBase, CMDObjectSchemaDiscriminator)):
                if not isinstance(schema, CMDObjectSchemaAdditionalProperties):
                    if not arg_var.endswith("$"):
                        arg_var += '.'
                    if isinstance(schema, CMDObjectSchemaDiscriminator):
                        arg_var += f'{schema.value}'
                    elif isinstance(schema, CMDSchema):
                        arg_var += f'{schema.name}'.replace('$', '')  # some schema name may contain $
                    else:
                        raise NotImplementedError()
            else:
                raise NotImplementedError()
            cls_name = getattr(parent.schema, 'cls', None)
            if cls_name is not None:
                arg_var = arg_var.replace(parent._arg_var, f"@{cls_name}")

        return cls(schema=schema, arg_var=arg_var, parent=parent, is_update_action=is_update_action)

    def __init__(self, schema, arg_var, parent=None, is_update_action=False):
        self.schema = schema
        self._parent = parent
        self._arg_var = arg_var
        self._flatten_discriminators = False
        self._is_update_action = is_update_action

    def get_sub_builder(self, schema):
        return self.new_builder(schema=schema, parent=self, is_update_action=self._is_update_action)

    def _ignore(self):
        if self.schema.frozen:
            return True
        if isinstance(self.schema, CMDSchemaBase):
            assert not self.schema.read_only
            if self.schema.const:
                return True
        return False

    def _build_arg_base(self):
        if self._ignore():
            return None
        arg_cls = self.schema.ARG_TYPE
        assert issubclass(arg_cls, (CMDArgBase, CMDObjectArgAdditionalProperties))
        return arg_cls.build_arg_base(self)

    def _build_arg(self):
        if self._ignore():
            return None

        arg_cls = self.schema.ARG_TYPE
        assert issubclass(arg_cls, CMDArg)
        return arg_cls.build_arg(self)

    def _need_flatten(self):
        if isinstance(self.schema, CMDObjectSchema):
            if self.schema.client_flatten:
                return True
            if self.schema.name == "properties":
                return True
        if isinstance(self.schema, CMDObjectSchemaDiscriminator):
            return self._parent._flatten_discriminators
        return False

    def get_args(self):
        if self._ignore():
            return []

        arg = self._build_arg()
        assert arg is not None
        if self._need_flatten():
            if isinstance(self.schema, CMDSchema):
                self.schema.arg = None
                if arg.args:
                    for sub_arg in arg.args:
                        sub_arg.group = to_camel_case(self.schema.name)
            return arg.args or []
        elif isinstance(self.schema, CMDSchema):
            self.schema.arg = arg.var
            arg.ref_schema = self.schema
        return [arg, ]

    def get_sub_args(self):
        assert isinstance(self.schema, (CMDObjectSchemaBase, CMDObjectSchemaDiscriminator))
        sub_args = []
        discriminator_mapping = {}
        if self.schema.discriminators:
            # update self._flatten_discriminators, if any discriminator need flatten, then all discriminator needs tp flatten
            for disc in self.schema.discriminators:
                sub_builder = self.get_sub_builder(schema=disc)
                self._flatten_discriminators = self._flatten_discriminators or sub_builder._need_flatten()
            for disc in self.schema.discriminators:
                sub_builder = self.get_sub_builder(schema=disc)
                results = sub_builder.get_args()
                sub_args.extend(results)
                if results and not self._flatten_discriminators:
                    assert len(results) == 1
                    if disc.property not in discriminator_mapping:
                        discriminator_mapping[disc.property] = {}
                    discriminator_mapping[disc.property][disc.value] = results[0].var
        if self.schema.props:
            for prop in self.schema.props:
                if prop.name in discriminator_mapping:
                    # If discriminators are not flattened then prop value can be associate with discriminator arguments
                    assert hasattr(prop, 'enum')
                    for item in prop.enum.items:
                        if item.value in discriminator_mapping[prop.name]:
                            item.arg = discriminator_mapping[prop.name][item.value]
                    continue
                sub_builder = self.get_sub_builder(schema=prop)
                sub_args.extend(sub_builder.get_args())
        if not sub_args:
            return None
        return sub_args

    def get_sub_item(self):
        if hasattr(self.schema, "item") and self.schema.item:
            sub_builder = self.get_sub_builder(schema=self.schema.item)
            return sub_builder._build_arg_base()
        else:
            return None

    def get_additional_props(self):
        if hasattr(self.schema, "additional_props") and self.schema.additional_props:
            sub_builder = self.get_sub_builder(schema=self.schema.additional_props)
            return sub_builder._build_arg_base()
        else:
            return None

    def get_required(self):
        if not self._is_update_action and isinstance(self.schema, CMDSchema):
            return self.schema.required
        return False

    def get_default(self):
        if hasattr(self.schema, 'default') and self.schema.default:
            default = CMDArgDefault.build_default(self, self.schema.default)
            return default
        return None

    def get_blank(self):
        if isinstance(self.schema, CMDBooleanArgBase):
            blk = CMDArgBlank()
            blk.value = True
            return blk
        return None

    def get_hide(self):
        if getattr(self.schema, 'name', None) == 'id' and not self.get_required() and self._parent and \
                isinstance(self.schema, CMDResourceIdSchema):
            if self._arg_var.split('.', maxsplit=1)[-1] == 'id':
                # hide top level 'id' property when it has 'name' property,
                for prop in self._parent.schema.props:
                    if prop.name == 'name':
                        return True
        return False

    def get_var(self):
        return self._arg_var

    @staticmethod
    def _build_option_name(name):
        name = name.replace('_', '-')
        name = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name).lower()
        return '-'.join([p for p in name.split('-') if p])

    def get_options(self):
        if isinstance(self.schema, CMDObjectSchemaDiscriminator):
            opt_name = self._build_option_name(self.schema.value)
        elif isinstance(self.schema, CMDSchema):
            opt_name = self._build_option_name(self.schema.name.replace('$', ''))  # some schema name may contain $
        else:
            raise NotImplementedError()
        return [opt_name, ]

    def get_singular_options(self):
        if not isinstance(self.schema, CMDArraySchema):
            raise NotImplementedError()
        opt_name = self._build_option_name(self.schema.name.replace('$', ''))  # some schema name may contain $
        singular_opt_name = self._inflect_engine.singular_noun(opt_name) or opt_name
        if singular_opt_name != opt_name:
            return [singular_opt_name, ]
        return None

    def _build_help(self):
        if hasattr(self.schema, 'description') and self.schema.description:
            h = CMDArgumentHelp()
            h.short = self.schema.description
            return h
        return None

    def get_help(self):
        h = self._build_help()
        return h

    def get_fmt(self):
        if isinstance(self.schema, CMDObjectSchemaDiscriminator):
            return None
        assert hasattr(self.schema, 'fmt')
        if self.schema.fmt:
            assert isinstance(self.schema.fmt, CMDFormat)
            return self.schema.fmt.build_arg_fmt(self)
        return None

    def get_enum(self):
        assert hasattr(self.schema, 'enum')
        if self.schema.enum:
            enum = CMDArgEnum.build_enum(self, self.schema.enum)
            return enum
        return None

    def get_enum_item(self, schema_item):
        assert isinstance(schema_item, CMDSchemaEnumItem)
        item = CMDArgEnumItem.build_enum_item(self, schema_item)
        return item

    def get_cls(self):
        if isinstance(self.schema, CMDObjectSchemaDiscriminator):
            return None
        assert hasattr(self.schema, 'cls')
        return self.schema.cls

    def get_type(self):
        return self.schema._get_type()
