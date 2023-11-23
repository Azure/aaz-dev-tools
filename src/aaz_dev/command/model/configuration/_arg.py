from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, PolyModelType
from schematics.types.serializable import serializable

from ._fields import CMDStageField, CMDVariantField, CMDPrimitiveField, CMDBooleanField, CMDClassField
from ._format import CMDStringFormat, CMDIntegerFormat, CMDFloatFormat, CMDObjectFormat, CMDArrayFormat, \
    CMDResourceIdFormat
from ._help import CMDArgumentHelp
from utils import exceptions

import copy


class CMDArgEnumItem(Model):
    # properties as tags
    name = StringType(required=True)
    hide = CMDBooleanField()

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null

    class Options:
        serialize_when_none = False

    @classmethod
    def build_enum_item(cls, schema_item, ref_enum_item):
        item = cls()
        item.value = copy.deepcopy(schema_item.value)
        item.hide = ref_enum_item.hide if ref_enum_item else None
        item.name = ref_enum_item.name if ref_enum_item else str(item.value)
        return item


class CMDArgEnum(Model):
    # properties as tags

    # properties as nodes
    items = ListType(ModelType(CMDArgEnumItem), min_size=1)

    @classmethod
    def build_enum(cls, schema_enum, ref_enum):
        enum = cls()
        enum.items = []
        for schema_item in schema_enum.items:
            ref_enum_item = None
            if ref_enum:
                for enum_item in ref_enum.items:
                    if enum_item.value == schema_item.value:
                        ref_enum_item = enum_item
                        break
            item = CMDArgEnumItem.build_enum_item(schema_item, ref_enum_item)
            enum.items.append(item)
        return enum

    def reformat(self, **kwargs):
        self.items = sorted(self.items, key=lambda it: it.name)


class CMDArgDefault(Model):
    """ The argument value if an argument is not used """

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null

    @classmethod
    def build_default(cls, builder, schema_default):
        default = cls()
        default.value = copy.deepcopy(schema_default.value)
        return default


class CMDArgBlank(Model):
    """ The argument value if an argument is assigned empty

    use cases:

    boolean type:
        If it is blank, it will be assigned true.

    int, float type:
        If it is not required, then it will be assigned null, which means to remove this property in request.

    string type:
        It should be distinguish with empty string.
        If it is not required, then it will be assigned null, which means to remove this property in request.

    object type:
        If it is required, then it will be assigned an empty dict
        If it is not required, then it will be assigned null, which means to remove this property in request.
    """

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null


class CMDArgPromptInput(Model):
    """ Support the prompt input for """

    # The prompt string, if given, is printed to standard output without a trailing newline before reading input.
    msg = StringType(required=True)


class CMDPasswordArgPromptInput(CMDArgPromptInput):

    # Ask the user to re-enter the same value to confirm. It's supported for CMDPasswordArg only.
    confirm = CMDBooleanField()


class CMDArgBase(Model):
    TYPE_VALUE = None

    # base types: "array", "boolean", "integer", "float", "object", "string",
    # special types: "ResourceId", "ResourceGroupName", "SubscriptionId", "ResourceLocation", "File"

    nullable = CMDBooleanField()  # whether can pass null value or not.

    blank = ModelType(CMDArgBlank)  # blank value is used when argument don't have any value

    class Options:
        serialize_when_none = False

    @serializable
    def type(self):
        return self._get_type()

    def _get_type(self):
        assert self.TYPE_VALUE is not None
        return self.TYPE_VALUE

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.TYPE_VALUE is None:
            return False

        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        elif isinstance(data, CMDArgBase):
            return data.TYPE_VALUE == cls.TYPE_VALUE
        return False

    @classmethod
    def build_arg_base(cls, builder):
        arg_base = cls()
        arg_base.nullable = builder.get_nullable()
        arg_base.blank = builder.get_blank()
        return arg_base

    def _reformat_base(self, **kwargs):
        pass

    def reformat(self, **kwargs):
        self._reformat_base(**kwargs)


class CMDArgBaseField(PolyModelType):

    def __init__(self, **kwargs):
        super(CMDArgBaseField, self).__init__(
            model_spec=CMDArgBase,
            allow_subclasses=True,
            serialize_when_none=False,
            **kwargs
        )

    def find_model(self, data):
        if self.claim_function:
            kls = self.claim_function(self, data)
            if not kls:
                raise Exception("Input for polymorphic field did not match any model")
            return kls

        fallback = None
        matching_classes = set()
        for kls in self._get_candidates():
            if issubclass(kls, CMDArg):
                continue

            try:
                kls_claim = kls._claim_polymorphic
            except AttributeError:
                if not fallback:
                    fallback = kls
            else:
                if kls_claim(data):
                    matching_classes.add(kls)

        if not matching_classes and fallback:
            return fallback
        elif len(matching_classes) != 1:
            raise Exception("Got ambiguous input for polymorphic field")

        return matching_classes.pop()


class CMDArg(CMDArgBase):
    # properties as tags
    var = CMDVariantField(required=True)
    options = ListType(StringType(), min_size=1, required=True)  # argument option names, the name is in dash case "aa-bb-cc"
    required = CMDBooleanField()
    stage = CMDStageField()

    hide = CMDBooleanField()
    group = StringType()   # argument group name
    id_part = StringType(
        serialized_name='idPart',
        deserialize_from='idPart',
    )   # for Resource Id argument

    # properties as nodes
    help = ModelType(CMDArgumentHelp)
    default = ModelType(CMDArgDefault)  # default value is used when argument isn't in command
    configuration_key = StringType(
        serialized_name='configurationKey',
        deserialize_from='configurationKey',
    )  # the key to retrieve the default value from cli configuration
    prompt = ModelType(CMDArgPromptInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_schema = None

    @classmethod
    def _claim_polymorphic(cls, data):
        if super()._claim_polymorphic(data):
            if isinstance(data, dict):
                # distinguish with CMDArgBase and CMDArg
                return 'var' in data
            else:
                return isinstance(data, CMDArg)
        return False

    @classmethod
    def build_arg(cls, builder):
        arg = cls.build_arg_base(builder)
        assert isinstance(arg, CMDArg)
        arg.var = builder.get_var()
        arg.options = builder.get_options()
        arg.help = builder.get_help()
        arg.group = builder.get_group()

        arg.required = builder.get_required()
        arg.default = builder.get_default()
        arg.configuration_key = builder.get_configuration_key()
        arg.prompt = builder.get_prompt()
        arg.hide = builder.get_hide()
        return arg

    def _reformat(self, **kwargs):
        self.options = sorted(self.options, key=lambda op: (len(op), op))

    def reformat(self, **kwargs):
        self._reformat_base(**kwargs)
        self._reformat(**kwargs)


#cls
class CMDClsArgBase(CMDArgBase):
    _type = StringType(
        deserialize_from='type',
        serialized_name='type',
        required=True
    )

    def _get_type(self):
        return self._type

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implement = None

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None and type_value.startswith("@"):
                return True
        elif isinstance(data, CMDClsArgBase):
            return True
        return False

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        arg._type = builder.get_type()
        return arg

    def get_unwrapped(self, **kwargs):
        if self.implement is None:
            return None
        assert isinstance(self.implement, CMDArgBase)
        if isinstance(self.implement, CMDObjectArgBase):
            cls = CMDObjectArg if isinstance(self, CMDClsArg) else CMDObjectArgBase
        elif isinstance(self.implement, CMDArrayArgBase):
            cls = CMDArrayArg if isinstance(self, CMDClsArg) else CMDArrayArgBase
        else:
            raise NotImplementedError()
        data = {k: v for k, v in self.implement.to_native().items() if k in cls._schema.valid_input_keys}
        data.update(kwargs)
        unwrapped = cls(data)
        return unwrapped


class CMDClsArg(CMDClsArgBase, CMDArg):
    singular_options = ListType(
        StringType(),
        serialized_name='singularOptions',
        deserialize_from='singularOptions',
    )  # for list use only

    @classmethod
    def build_arg(cls, builder):
        arg = super().build_arg(builder)
        assert isinstance(arg, CMDClsArg)
        arg.singular_options = builder.get_singular_options()
        return arg

    def _reformat(self, **kwargs):
        super()._reformat(**kwargs)
        if self.singular_options:
            self.singular_options = sorted(self.singular_options, key=lambda op: (len(op), op))

    def get_unwrapped(self, **kwargs):
        uninherent = {
            "var": self.var,
            "options": [*self.options],
            "required": self.required,
            "stage": self.stage,
            "hide": self.hide,
            "group": self.group,
            "id_part": self.id_part,
            "help": self.help.to_native() if self.help else None,
            "default": self.default.to_native() if self.default else None,
        }
        uninherent.update(kwargs)
        return super().get_unwrapped(**uninherent)


# string
class CMDStringArgBase(CMDArgBase):
    TYPE_VALUE = "string"

    fmt = ModelType(
        CMDStringFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDArgEnum)

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDStringArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.enum:
            self.enum.reformat(**kwargs)
        if self.blank:
            if not isinstance(self.blank.value, str) and not (self.nullable and self.blank.value is None):
                raise exceptions.VerificationError(
                    f"Invalid blank value", details=f"'{self.blank.value}' is not a valid string arg value")


class CMDStringArg(CMDStringArgBase, CMDArg):

    def _reformat(self, **kwargs):
        super()._reformat(**kwargs)
        if self.default:
            if not isinstance(self.default.value, str) and not (self.nullable and self.default.value is None):
                raise exceptions.VerificationError(
                    f"Invalid default value", details=f"'{self.default.value}' is not a valid string arg value")


# byte: base64 encoded characters
class CMDByteArgBase(CMDStringArgBase):
    TYPE_VALUE = "byte"


class CMDByteArg(CMDByteArgBase, CMDStringArg):
    pass


# binary: any sequence of octets
class CMDBinaryArgBase(CMDStringArgBase):
    TYPE_VALUE = "binary"


class CMDBinaryArg(CMDBinaryArgBase, CMDStringArg):
    pass


# duration
class CMDDurationArgBase(CMDStringArgBase):
    TYPE_VALUE = "duration"


class CMDDurationArg(CMDDurationArgBase, CMDStringArg):
    pass


# date: As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateArgBase(CMDStringArgBase):
    TYPE_VALUE = "date"


class CMDDateArg(CMDDateArgBase, CMDStringArg):
    pass


# date-time: As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateTimeArgBase(CMDStringArgBase):
    TYPE_VALUE = "dateTime"


class CMDDateTimeArg(CMDDateTimeArgBase, CMDStringArg):
    pass


class CMDTimeArgBase(CMDStringArgBase):
    TYPE_VALUE = "time"


class CMDTimeArg(CMDTimeArgBase, CMDStringArg):
    pass


# uuid
class CMDUuidArgBase(CMDStringArgBase):
    TYPE_VALUE = "uuid"


class CMDUuidArg(CMDUuidArgBase, CMDStringArg):
    pass


# password
class CMDPasswordArgBase(CMDStringArgBase):
    TYPE_VALUE = "password"


class CMDPasswordArg(CMDPasswordArgBase, CMDStringArg):

    prompt = ModelType(CMDPasswordArgPromptInput)


# subscription
class CMDSubscriptionIdArgBase(CMDStringArgBase):
    TYPE_VALUE = "SubscriptionId"


class CMDSubscriptionIdArg(CMDSubscriptionIdArgBase, CMDStringArg):
    pass


# resourceGroupName
class CMDResourceGroupNameArgBase(CMDStringArgBase):
    TYPE_VALUE = "ResourceGroupName"


class CMDResourceGroupNameArg(CMDResourceGroupNameArgBase, CMDStringArg):
    pass


# resourceId
class CMDResourceIdArgBase(CMDStringArgBase):
    TYPE_VALUE = "ResourceId"

    fmt = ModelType(
        CMDResourceIdFormat,
        serialized_name='format',
        deserialize_from='format'
    )

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDResourceIdArgBase)
        arg.fmt = builder.get_fmt()
        return arg


class CMDResourceIdArg(CMDResourceIdArgBase, CMDStringArg):
    pass


# resourceLocation
class CMDResourceLocationArgBase(CMDStringArgBase):
    TYPE_VALUE = "ResourceLocation"

    no_rg_default = CMDBooleanField()  # the default value will not be the location of resource group

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDResourceLocationArgBase)
        arg.no_rg_default = builder.get_resource_location_no_rg_default()
        return arg


class CMDResourceLocationArg(CMDResourceLocationArgBase, CMDStringArg):

    @classmethod
    def build_arg(cls, builder):
        arg = super().build_arg(builder)
        if arg.options == ['location']:
            # add 'l' alias for location arg
            arg.options.append('l')
        return arg


# integer
class CMDIntegerArgBase(CMDArgBase):
    TYPE_VALUE = "integer"

    fmt = ModelType(
        CMDIntegerFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDArgEnum)

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDIntegerArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.enum:
            self.enum.reformat(**kwargs)
        if self.blank:
            if not isinstance(self.blank.value, int) and not (self.nullable and self.blank.value is None):
                raise exceptions.VerificationError(
                    f"Invalid blank value", details=f"'{self.blank.value}' is not a valid int arg value")


class CMDIntegerArg(CMDIntegerArgBase, CMDArg):

    def _reformat(self, **kwargs):
        super()._reformat(**kwargs)
        if self.default:
            if not isinstance(self.default.value, int) and not (self.nullable and self.default.value is None):
                raise exceptions.VerificationError(
                    f"Invalid default value", details=f"'{self.default.value}' is not a valid int arg value")


# integer32
class CMDInteger32ArgBase(CMDIntegerArgBase):
    TYPE_VALUE = "integer32"


class CMDInteger32Arg(CMDInteger32ArgBase, CMDIntegerArg):
    pass


# integer64
class CMDInteger64ArgBase(CMDIntegerArgBase):
    TYPE_VALUE = "integer64"


class CMDInteger64Arg(CMDInteger64ArgBase, CMDIntegerArg):
    pass


# boolean
class CMDBooleanArgBase(CMDArgBase):
    TYPE_VALUE = "boolean"

    reverse = CMDBooleanField()

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDBooleanArgBase)
        arg.reverse = builder.get_reverse_boolean()
        return arg


class CMDBooleanArg(CMDBooleanArgBase, CMDArg):

    def _reformat(self, **kwargs):
        super()._reformat(**kwargs)
        if self.default:
            if not isinstance(self.default.value, bool) and not (self.nullable and self.default.value is None):
                raise exceptions.VerificationError(
                    f"Invalid default value", details=f"'{self.default.value}' is not a valid boolean arg value")


# float
class CMDFloatArgBase(CMDArgBase):
    TYPE_VALUE = "float"

    fmt = ModelType(
        CMDFloatFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDArgEnum)

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDFloatArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.enum:
            self.enum.reformat(**kwargs)
        if self.blank:
            if not isinstance(self.blank.value, float) and not (self.nullable and self.blank.value is None):
                if isinstance(self.blank.value, int):
                    # frontend will pass an int value when it doesn't have decimal part
                    self.blank.value = float(self.blank.value)
                else:
                    raise exceptions.VerificationError(
                        f"Invalid blank value", details=f"'{self.blank.value}' is not a valid float arg value")


class CMDFloatArg(CMDFloatArgBase, CMDArg):

    def _reformat(self, **kwargs):
        super()._reformat(**kwargs)
        if self.default:
            if not isinstance(self.default.value, float) and not (self.nullable and self.default.value is None):
                if isinstance(self.default.value, int):
                    # frontend will pass an int value when it doesn't have decimal part
                    self.default.value = float(self.default.value)
                else:
                    raise exceptions.VerificationError(
                        f"Invalid default value", details=f"'{self.default.value}' is not a valid float arg value")


# float32
class CMDFloat32ArgBase(CMDFloatArgBase):
    TYPE_VALUE = "float32"


class CMDFloat32Arg(CMDFloat32ArgBase, CMDFloatArg):
    pass


# float64
class CMDFloat64ArgBase(CMDFloatArgBase):
    TYPE_VALUE = "float64"


class CMDFloat64Arg(CMDFloat64ArgBase, CMDFloatArg):
    pass


# object
class CMDObjectArgAdditionalProperties(Model):
    # properties as nodes
    item = CMDArgBaseField()
    any_type = CMDBooleanField(
        serialized_name="anyType",
        deserialize_from="anyType",
    )  # when item is not defined and support any type for additional properties

    class Options:
        serialize_when_none = False

    @classmethod
    def build_arg_base(cls, builder):
        arg = cls()
        arg.item = builder.get_sub_item()
        arg.any_type = builder.get_any_type()
        return arg

    def reformat(self, **kwargs):
        if self.item:
            if self.any_type:
                raise exceptions.VerificationError(
                    "InvalidAdditionalPropertiesDefinition",
                    details="Additional property defined 'item' and 'any_type'."
                )
            try:
                self.item.reformat(**kwargs)
            except exceptions.VerificationError as err:
                err.payload['details'] = {
                    "type": "AdditionalProperties",
                    "details": err.payload['details']
                }
                raise err


class CMDObjectArgBase(CMDArgBase):
    TYPE_VALUE = "object"

    fmt = ModelType(
        CMDObjectFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True))
    additional_props = ModelType(
        CMDObjectArgAdditionalProperties,
        serialized_name="additionalProps",
        deserialize_from="additionalProps",
    )

    # cls definition will not include properties in CMDArg only, such as following properties:
    # var
    # options
    # required
    # stage
    # hide
    # group
    # id_part
    # help
    # default
    cls = CMDClassField()

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDObjectArgBase)
        try:
            arg.fmt = builder.get_fmt()
        except Exception:
            raise
        arg.args = builder.get_sub_args()
        arg.additional_props = builder.get_additional_props()
        if not arg.args and not arg.additional_props:
            # when object arg don't have args or additional_props, set its blank value as empty dict
            arg.blank = CMDArgBlank()
            arg.blank.value = {}
        arg.cls = builder.get_cls()
        return arg

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.args:
            used_options = set()
            for arg in self.args:
                try:
                    arg.reformat(**kwargs)
                except exceptions.VerificationError as err:
                    err.payload['details'] = {
                        "type": "Argument",
                        "options": arg.options,
                        "var": arg.var,
                        "details": err.payload['details']
                    }
                    raise err
                for option in arg.options:
                    if option in used_options:
                        raise exceptions.VerificationError(
                            message=f"Argument option '{option}' duplicated.",
                            details={
                                "type": "Argument",
                                "options": arg.options,
                                "var": arg.var,
                            }
                        )
                    used_options.add(option)
            self.args = sorted(self.args, key=lambda a: a.var)
        if self.additional_props:
            self.additional_props.reformat(**kwargs)

        if self.blank:
            if not isinstance(self.blank.value, dict) and not (self.nullable and self.blank.value is None):
                raise exceptions.VerificationError(
                    f"Invalid blank value", details=f"'{self.blank.value}' is not a valid object arg value")


class CMDObjectArg(CMDObjectArgBase, CMDArg):

    @classmethod
    def build_arg(cls, builder):
        arg = super().build_arg(builder)
        assert isinstance(arg, CMDObjectArg)
        return arg

    def _reformat(self, **kwargs):
        super()._reformat(**kwargs)
        if self.default:
            if not isinstance(self.default.value, dict) and not (self.nullable and self.default.value is None):
                raise exceptions.VerificationError(
                    f"Invalid default value", details=f"'{self.default.value}' is not a valid object arg value")


# array
class CMDArrayArgBase(CMDArgBase):
    TYPE_VALUE = "array"

    fmt = ModelType(
        CMDArrayFormat,
        serialized_name='format',
        deserialize_from='format',
    )

    item = CMDArgBaseField(required=True)

    # cls definition will not include properties in CMDArg only, such as following properties:
    # var
    # options
    # required
    # stage
    # hide
    # group
    # id_part
    # help
    # default
    cls = CMDClassField()

    def _get_type(self):
        return f"{self.TYPE_VALUE}<{self.item.type}>"

    @classmethod
    def build_arg_base(cls, builder):
        arg = super().build_arg_base(builder)
        assert isinstance(arg, CMDArrayArgBase)
        arg.fmt = builder.get_fmt()
        arg.item = builder.get_sub_item()
        arg.cls = builder.get_cls()
        return arg

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.item is None:
            raise exceptions.VerificationError(
                "Invalid array type",
                details="Array item is not defined "
            )
        try:
            self.item.reformat(**kwargs)
        except exceptions.VerificationError as err:
            err.payload['details'] = {
                "type": "ArrayItem",
                "details": err.payload['details']
            }
            raise err

        if self.blank:
            if not isinstance(self.blank.value, list) and not (self.nullable and self.blank.value is None):
                raise exceptions.VerificationError(
                    f"Invalid blank value", details=f"'{self.blank.value}' is not a valid array arg value")


class CMDArrayArg(CMDArrayArgBase, CMDArg):

    singular_options = ListType(
        StringType(),
        serialized_name='singularOptions',
        deserialize_from='singularOptions',
    )  # options to pass element instead of full list

    @classmethod
    def build_arg(cls, builder):
        arg = super().build_arg(builder)
        assert isinstance(arg, CMDArrayArg)
        arg.singular_options = builder.get_singular_options()
        return arg

    def _reformat(self, **kwargs):
        super()._reformat(**kwargs)
        if self.singular_options:
            self.singular_options = sorted(self.singular_options, key=lambda op: (len(op), op))
        if self.default:
            if not isinstance(self.default.value, list) and not (self.nullable and self.default.value is None):
                raise exceptions.VerificationError(
                    f"Invalid default value", details=f"'{self.default.value}' is not a valid array arg value")
