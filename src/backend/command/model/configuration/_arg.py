from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, PolyModelType
from schematics.types.serializable import serializable

from ._fields import CMDStageField, CMDVariantField, CMDPrimitiveField, CMDBooleanField, CMDClassField
from ._format import CMDStringFormat, CMDIntegerFormat, CMDFloatFormat, CMDObjectFormat, CMDArrayFormat, \
    CMDResourceIdFormat
from ._help import CMDArgumentHelp
import copy


class CMDArgEnumItem(Model):
    # properties as tags
    name = StringType(required=True)
    hide = CMDBooleanField()

    # properties as nodes
    value = CMDPrimitiveField(required=True)

    class Options:
        serialize_when_none = False

    @classmethod
    def build_enum_item(cls, builder, schema_item):
        item = cls()
        item.value = copy.deepcopy(schema_item.value)
        item.name = str(item.value)
        return item


class CMDArgEnum(Model):
    # properties as tags

    # properties as nodes
    items = ListType(ModelType(CMDArgEnumItem), min_size=1)

    @classmethod
    def build_enum(cls, builder, schema_enum):
        enum = cls()
        enum.items = []
        for schema_item in schema_enum.items:
            item = builder.get_enum_item(schema_item)
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


class CMDArgBase(Model):
    TYPE_VALUE = None

    # base types: "array", "boolean", "integer", "float", "object", "string",
    # special types: "ResourceId", "ResourceGroupName", "SubscriptionId", "ResourceLocation", "File"

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
        return cls()

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
    blank = ModelType(CMDArgBlank)  # blank value is used when argument don't have any value

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

        arg.required = builder.get_required()
        arg.default = builder.get_default()
        arg.blank = builder.get_blank()

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
        # TODO: if cls referenced to a list argument, then support get_singular_options
        # arg.singular_options = builder.get_singular_options()
        return arg


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


class CMDStringArg(CMDStringArgBase, CMDArg):
    pass


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


# uuid
class CMDUuidArgBase(CMDStringArgBase):
    TYPE_VALUE = "uuid"


class CMDUuidArg(CMDUuidArgBase, CMDStringArg):
    pass


# password
class CMDPasswordArgBase(CMDStringArgBase):
    TYPE_VALUE = "password"


class CMDPasswordArg(CMDPasswordArgBase, CMDStringArg):
    pass


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


class CMDResourceIdArg(CMDResourceIdArgBase, CMDStringArg):
    pass


# resourceLocation
class CMDResourceLocationArgBase(CMDStringArgBase):
    TYPE_VALUE = "ResourceLocation"


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


class CMDIntegerArg(CMDIntegerArgBase, CMDArg):
    pass


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


class CMDBooleanArg(CMDBooleanArgBase, CMDArg):
    pass


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


class CMDFloatArg(CMDFloatArgBase, CMDArg):
    pass


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

    class Options:
        serialize_when_none = False

    @classmethod
    def build_arg_base(cls, builder):
        arg = cls()
        arg.item = builder.get_sub_item()
        return arg

    def reformat(self, **kwargs):
        if self.item:
            self.item.reformat(**kwargs)


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

    # cls definition will not include properties in CMDArg only
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
        arg.cls = builder.get_cls()
        return arg

    def _reformat_base(self, **kwargs):
        super()._reformat_base(**kwargs)
        if self.args:
            for arg in self.args:
                arg.reformat(**kwargs)
            self.args = sorted(self.args, key=lambda a: a.var)
        if self.additional_props:
            self.additional_props.reformat(**kwargs)


class CMDObjectArg(CMDObjectArgBase, CMDArg):

    @classmethod
    def build_arg(cls, builder):
        arg = super().build_arg(builder)
        assert isinstance(arg, CMDObjectArg)
        return arg


# array
class CMDArrayArgBase(CMDArgBase):
    TYPE_VALUE = "array"

    fmt = ModelType(
        CMDArrayFormat,
        serialized_name='format',
        deserialize_from='format',
    )

    item = CMDArgBaseField(required=True)

    # cls definition will not include properties in CMDArg only
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
        self.item.reformat(**kwargs)


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
