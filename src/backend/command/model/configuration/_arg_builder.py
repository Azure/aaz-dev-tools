

from ._schema import CMDObjectSchema, CMDSchema, CMDSchemaBase, CMDObjectSchemaBase, CMDObjectSchemaDiscriminator, CMDArraySchemaBase, CMDSchemaEnumItem
from ._arg import CMDArg, CMDArgBase, CMDArgumentHelp, CMDArgEnum, CMDArgEnumItem, CMDArgDefault, CMDBooleanArgBase, CMDArgBlank
from ._format import CMDFormat
import re


class CMDArgBuilder:

    @classmethod
    def new_builder(cls, schema, parent=None, var_prefix=None):
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
                arg_var += f'{schema.name}'
            else:
                raise NotImplementedError()
        else:
            assert isinstance(parent, CMDArgBuilder)
            if isinstance(parent.schema, CMDArraySchemaBase):
                arg_var += '[]'
            elif isinstance(parent.schema, (CMDObjectSchemaBase, CMDObjectSchemaDiscriminator)):
                if not arg_var.endswith("$"):
                    arg_var += '.'
                if isinstance(schema, CMDObjectSchemaDiscriminator):
                    arg_var += f'{schema.value}'
                elif isinstance(schema, CMDSchema):
                    arg_var += f'{schema.name}'
                else:
                    raise NotImplementedError()
            else:
                raise NotImplementedError()

        return cls(schema=schema, arg_var=arg_var, parent=parent)

    def __init__(self, schema, arg_var, parent=None):
        self.schema = schema
        self._parent = parent
        self._arg_var = arg_var
        self._flatten_discriminators = False

    def get_sub_builder(self, schema):
        return self.new_builder(schema=schema, parent=self)

    def _build_arg_base(self):
        arg_cls = self.schema.ARG_TYPE
        assert issubclass(arg_cls, CMDArgBase)
        return arg_cls.build_arg_base(self)

    def _build_arg(self):
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
        if isinstance(self.schema, CMDSchemaBase) and self.schema.read_only:
            return []
        arg = self._build_arg()
        if self._need_flatten():
            if isinstance(self.schema, CMDSchema):
                self.schema.arg = None
                # for sub_arg in arg.args:
                #     sub_arg.group = self.schema.name
            return arg.args or []
        elif isinstance(self.schema, CMDSchema):
            self.schema.arg = arg.var
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
                if not self._flatten_discriminators:
                    assert len(results) == 1
                    if disc.prop not in discriminator_mapping:
                        discriminator_mapping[disc.prop] = {}
                    discriminator_mapping[disc.prop][disc.value] = results[0].var
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
        assert isinstance(self.schema, CMDArraySchemaBase)
        sub_builder = self.get_sub_builder(schema=self.schema.item)
        return sub_builder._build_arg_base()

    def get_required(self):
        if isinstance(self.schema, CMDSchemaBase):
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
            opt_name = self._build_option_name(self.schema.name)
        else:
            raise NotImplementedError()
        return [opt_name, ]

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