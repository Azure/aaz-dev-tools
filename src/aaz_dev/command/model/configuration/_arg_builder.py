import re

import inflect
from utils.case import to_camel_case

from ._arg import CMDArg, CMDArgBase, CMDArgumentHelp, CMDArgEnum, CMDArgDefault, CMDBooleanArgBase, \
    CMDArgBlank, CMDObjectArgAdditionalProperties, CMDResourceLocationArgBase, CMDClsArgBase, CMDPasswordArgPromptInput
from ._format import CMDFormat
from ._schema import CMDObjectSchema, CMDSchema, CMDSchemaBase, CMDObjectSchemaBase, CMDObjectSchemaDiscriminator, \
    CMDArraySchemaBase, CMDObjectSchemaAdditionalProperties, CMDResourceIdSchema, CMDBooleanSchemaBase, \
    CMDResourceLocationSchemaBase, CMDPasswordSchema


class CMDArgBuilder:
    _inflect_engine = inflect.engine()

    @classmethod
    def new_builder(cls, schema, parent=None, var_prefix=None, ref_args=None, ref_arg=None, is_update_action=False):
        if var_prefix is None:
            if parent is None or parent._arg_var is None:
                arg_var = "$"
            else:
                arg_var = parent._arg_var
        else:
            arg_var = var_prefix

        if parent is None or parent._arg_var is None:
            if isinstance(schema, CMDSchema):
                if not arg_var.endswith("$") and not schema.name.startswith('[') and not schema.name.startswith('{'):
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
                        arg_var += schema.get_safe_value()
                    elif isinstance(schema, CMDSchema):
                        arg_var += f'{schema.name}'.replace('$', '')  # some schema name may contain $
                    else:
                        raise NotImplementedError()
            else:
                raise NotImplementedError()
            cls_name = getattr(parent.schema, 'cls', None)
            if cls_name is not None:
                arg_var = arg_var.replace(parent._arg_var, f"@{cls_name}")

        if ref_arg:
            assert ref_args is None

        flatten = None
        sub_ref_args = []
        if not ref_arg and ref_args:
            for arg in ref_args:
                if arg.var == arg_var:
                    ref_arg = arg
                    flatten = False
                    break
                elif arg.var.startswith(f"{arg_var}."):
                    flatten = True  # this argument already flattened
                    sub_ref_args.append(arg)
        sub_ref_args = sub_ref_args or None
        return cls(schema=schema, arg_var=arg_var, ref_arg=ref_arg, sub_ref_args=sub_ref_args, parent=parent, is_update_action=is_update_action, flatten=flatten)

    def __init__(self, schema, arg_var, ref_arg, sub_ref_args, parent=None, is_update_action=False, flatten=None):
        self.schema = schema
        self._parent = parent
        self._arg_var = arg_var
        self._ref_arg = ref_arg
        self._sub_ref_args = sub_ref_args
        self._flatten = flatten
        self._flatten_discriminators = False  # flatten it's discriminators or not
        self._is_update_action = is_update_action

    def get_sub_builder(self, schema, ref_args=None, ref_arg=None):
        return self.new_builder(
            schema=schema, parent=self, ref_args=ref_args, ref_arg=ref_arg, is_update_action=self._is_update_action)

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
            if self.get_cls():
                # not support to flatten object which is a cls.
                return False
            if self._flatten is not None:
                return self._flatten
            if self.schema.client_flatten:
                return True
            if self.schema.name == "properties" and self.schema.props:
                # flatten 'properties' property by default if it has props
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
                        if sub_arg.group is None:
                            sub_arg.group = to_camel_case(self.schema.name)
                        if not arg.required:
                            sub_arg.required = False
            return arg.args or []
        elif isinstance(self.schema, CMDSchema):
            self.schema.arg = arg.var
            arg.ref_schema = self.schema

        return [arg, ]

    def get_sub_args(self):
        assert isinstance(self.schema, (CMDObjectSchemaBase, CMDObjectSchemaDiscriminator))
        sub_args = []
        discriminator_mapping = {}
        if self._ref_arg:
            if isinstance(self._ref_arg, CMDClsArgBase):
                # use the linked instance
                unwrapped_ref_arg = self._ref_arg.get_unwrapped()
                assert unwrapped_ref_arg is not None
                sub_ref_args = unwrapped_ref_arg.args
            else:
                sub_ref_args = self._ref_arg.args
        else:
            sub_ref_args = self._sub_ref_args

        if self.schema.discriminators:
            # update self._flatten_discriminators, if any discriminator need flatten, then all discriminator needs to flatten
            for disc in self.schema.discriminators:
                sub_builder = self.get_sub_builder(schema=disc, ref_args=sub_ref_args)
                self._flatten_discriminators = self._flatten_discriminators or sub_builder._need_flatten()
            for disc in self.schema.discriminators:
                sub_builder = self.get_sub_builder(schema=disc, ref_args=sub_ref_args)
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
                sub_builder = self.get_sub_builder(schema=prop, ref_args=sub_ref_args)
                sub_args.extend(sub_builder.get_args())

        if not sub_args:
            return None
        return sub_args

    def get_sub_item(self):
        if hasattr(self.schema, "item") and self.schema.item:
            sub_ref_arg = self._ref_arg.item if self._ref_arg else None
            sub_builder = self.get_sub_builder(schema=self.schema.item, ref_arg=sub_ref_arg)
            return sub_builder._build_arg_base()
        else:
            return None

    def get_any_type(self):
        if hasattr(self.schema, "any_type") and self.schema.any_type and self.get_sub_item() is None:
            return True
        else:
            return False

    def get_additional_props(self):
        if hasattr(self.schema, "additional_props") and self.schema.additional_props:
            sub_ref_arg = self._ref_arg.additional_props if self._ref_arg else None
            sub_builder = self.get_sub_builder(schema=self.schema.additional_props, ref_arg=sub_ref_arg)
            return sub_builder._build_arg_base()
        else:
            return None

    def get_required(self):
        if not self._is_update_action and isinstance(self.schema, CMDSchema):
            return self.schema.required
        return False

    def get_nullable(self):
        if isinstance(self.schema, CMDSchemaBase) and self.schema.nullable:
            return True

        if isinstance(self.schema, CMDSchema):
            # when updated and schema is not required then nullable is true.
            # This can help update command to remove properties
            if not self.schema.required and self._is_update_action:
                return True

        elif isinstance(self.schema, CMDSchemaBase):
            # when updated and the element is nullable
            # This can help update command to remove elements.
            if self._is_update_action:
                return True

        return False

    def get_default(self):
        if self._ref_arg:
            # ref_arg already has default value return it
            if self._ref_arg.default:
                return CMDArgDefault(raw_data=self._ref_arg.default.to_native())
        if self._is_update_action:
            # ignore default for update actions
            return None
        if hasattr(self.schema, 'default') and self.schema.default:
            return CMDArgDefault.build_default(self, self.schema.default)
        return None

    def get_configuration_key(self):
        if self._ref_arg:
            return self._ref_arg.configuration_key
        return None

    def get_prompt(self):
        if self._ref_arg:
            # ref_arg already has prompt return it
            if hasattr(self._ref_arg, "prompt") and self._ref_arg.prompt:
                return self._ref_arg.prompt.__class__(raw_data=self._ref_arg.prompt.to_native())
        if isinstance(self.schema, CMDPasswordSchema):
            return CMDPasswordArgPromptInput(raw_data={"msg": "Password:"})
        return None

    def get_blank(self):
        if self.get_prompt() is not None:
            # disable blank when get prompt is available
            return None

        if self._ref_arg:
            if self._ref_arg.blank:
                return CMDArgBlank(raw_data=self._ref_arg.blank.to_native())
            return None  # ignore the logic from schema

        if isinstance(self.schema, CMDBooleanArgBase):
            blk = CMDArgBlank()
            blk.value = True
            return blk
        return None

    def get_hide(self):
        if self._ref_arg:
            return self._ref_arg.hide  # ignore the logic from schema

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
        if self._ref_arg:
            return [*self._ref_arg.options]

        if isinstance(self.schema, CMDObjectSchemaDiscriminator):
            opt_name = self._build_option_name(self.schema.get_safe_value())
        elif isinstance(self.schema, CMDSchema):
            name = self.schema.name.replace('$', '')
            if name == "[Index]" or name == "{Key}":
                assert self._arg_var.endswith(name)
                prefix = self._arg_var[:-len(name)].split('.')[-1]
                prefix = self._inflect_engine.singular_noun(prefix)
                if name == "[Index]":
                    name = f'{prefix}-index'
                elif name == "{Key}":
                    name = f'{prefix}-key'
            elif name.startswith('[].') or name.startswith('{}.'):
                assert self._arg_var.endswith(name)
                prefix = self._arg_var[:-len(name)].split('.')[-1]
                prefix = self._inflect_engine.singular_noun(prefix)
                name = prefix + name[2:]
            name = name.replace('.', '-')
            opt_name = self._build_option_name(name)  # some schema name may contain $
        else:
            raise NotImplementedError()
        return [opt_name, ]

    def get_singular_options(self):
        if self._ref_arg:
            singular_options = getattr(self._ref_arg, 'singular_options', None)
            if singular_options:
                return [*singular_options]

        # Disable singular options by default
        # if isinstance(self.schema, CMDArraySchema):
        #     opt_name = self._build_option_name(self.schema.name.replace('$', ''))  # some schema name may contain $
        #     singular_opt_name = self._inflect_engine.singular_noun(opt_name) or opt_name
        #     if singular_opt_name != opt_name:
        #         return [singular_opt_name, ]
        return None

    def get_help(self):
        if self._ref_arg:
            if self._ref_arg.help:
                return CMDArgumentHelp(raw_data=self._ref_arg.help.to_native())

        if hasattr(self.schema, 'description') and self.schema.description:
            h = CMDArgumentHelp()
            h.short = self.schema.description.replace('\n', ' ')
            return h
        return None

    def get_group(self):
        if self._ref_arg:
            return self._ref_arg.group
        return None

    def get_fmt(self):
        if isinstance(self.schema, CMDObjectSchemaDiscriminator):
            return None
        assert hasattr(self.schema, 'fmt')
        if self.schema.fmt:
            assert isinstance(self.schema.fmt, CMDFormat)
            ref_fmt = getattr(self._ref_arg, 'fmt', None) if self._ref_arg else None
            return self.schema.fmt.build_arg_fmt(self, ref_fmt=ref_fmt)
        return None

    def get_enum(self):
        assert hasattr(self.schema, 'enum')
        if self.schema.enum:
            ref_enum = self._ref_arg.enum if self._ref_arg else None
            enum = CMDArgEnum.build_enum(self.schema.enum, ref_enum=ref_enum)
            return enum
        return None

    def get_cls(self):
        if isinstance(self.schema, CMDObjectSchemaDiscriminator):
            return None
        assert hasattr(self.schema, 'cls')
        return self.schema.cls

    def get_type(self):
        return self.schema._get_type()

    def get_reverse_boolean(self):
        assert isinstance(self.schema, CMDBooleanSchemaBase)
        if self._ref_arg and isinstance(self._ref_arg, CMDBooleanArgBase):
            return self._ref_arg.reverse
        return False

    def get_resource_location_no_rg_default(self):
        assert isinstance(self.schema, CMDResourceLocationSchemaBase)
        if self._ref_arg and isinstance(self._ref_arg, CMDResourceLocationArgBase):
            return self._ref_arg.no_rg_default
        return False
