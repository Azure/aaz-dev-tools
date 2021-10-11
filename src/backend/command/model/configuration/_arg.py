from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, PolyModelType
from schematics.types.serializable import serializable

from ._fields import CMDStageField, CMDVariantField, CMDPrimitiveField, CMDBooleanField
from ._format import CMDStringFormat, CMDIntegerFormat, CMDFloatFormat, CMDObjectFormat, CMDArrayFormat
from ._help import CMDArgumentHelp
import copy


class CMDArgEnumItem(Model):
    # properties as tags
    name = StringType(required=True)
    hide = CMDBooleanField()

    # properties as nodes
    value = CMDPrimitiveField(required=True)

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
    # special types: "@File", "@ResourceID", "@ResourceGroup", "@Subscription", "@Json"

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


class CMDArg(CMDArgBase):
    # properties as tags
    var = CMDVariantField(required=True)
    options = ListType(StringType(), min_size=1, required=True)  # argument option names
    required = CMDBooleanField()
    stage = CMDStageField()

    hide = CMDBooleanField()
    group = StringType(serialize_when_none=False)   # argument group name
    id_part = StringType(
        serialized_name='idPart',
        deserialize_from='idPart',
        serialize_when_none=False
    )   # for Resource Id argument

    # properties as nodes
    help = ModelType(CMDArgumentHelp, serialize_when_none=False)
    default = ModelType(CMDArgDefault, serialize_when_none=False)  # default value is used when argument isn't in command
    blank = ModelType(CMDArgBlank, serialize_when_none=False)  # blank value is used when argument don't have any value

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDArg, cls)._claim_polymorphic(data):
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
        return arg

    # @staticmethod
    # def _dash_case_option(option):
    #
    #     pass
    #
    # @staticmethod
    # def _camel_case_option(option):
    #     pass

    # def switch_options_format(self, in_dash):
    #     if not self.options:
    #         return
    #     if in_dash:
    #         self.options = [self._dash_case_option(op) for op in self.options]
    #     else:
    #         self.options = [self._camel_case_option(op) for op in self.options]


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


class CMDClsArg(CMDArg, CMDClsArgBase):
    pass


# string
class CMDStringArgBase(CMDArgBase):
    TYPE_VALUE = "string"

    fmt = ModelType(
        CMDStringFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDArgEnum, serialize_when_none=False)

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDStringArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDStringArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg


class CMDStringArg(CMDArg, CMDStringArgBase):
    pass


# byte: base64 encoded characters
class CMDByteArgBase(CMDStringArgBase):
    TYPE_VALUE = "byte"


class CMDByteArg(CMDStringArg, CMDByteArgBase):
    pass


# binary: any sequence of octets
class CMDBinaryArgBase(CMDStringArgBase):
    TYPE_VALUE = "binary"


class CMDBinaryArg(CMDStringArg, CMDBinaryArgBase):
    pass


# duration
class CMDDurationArgBase(CMDStringArgBase):
    TYPE_VALUE = "duration"


class CMDDurationArg(CMDStringArg, CMDDurationArgBase):
    pass


# date: As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateArgBase(CMDStringArgBase):
    TYPE_VALUE = "date"


class CMDDateArg(CMDStringArg, CMDDateArgBase):
    pass


# date-time: As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateTimeArgBase(CMDStringArgBase):
    TYPE_VALUE = "date-time"


class CMDDateTimeArg(CMDStringArg, CMDDateTimeArgBase):
    pass


# uuid
class CMDUuidArgBase(CMDStringArgBase):
    TYPE_VALUE = "uuid"


class CMDUuidArg(CMDStringArg, CMDUuidArgBase):
    pass


# password
class CMDPasswordArgBase(CMDStringArgBase):
    TYPE_VALUE = "password"


class CMDPasswordArg(CMDStringArg, CMDPasswordArgBase):
    pass


# integer
class CMDIntegerArgBase(CMDArgBase):
    TYPE_VALUE = "integer"

    fmt = ModelType(
        CMDIntegerFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDArgEnum, serialize_when_none=False)

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDIntegerArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDIntegerArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg


class CMDIntegerArg(CMDArg, CMDIntegerArgBase):
    pass


# integer32
class CMDInteger32ArgBase(CMDIntegerArgBase):
    TYPE_VALUE = "integer32"


class CMDInteger32Arg(CMDIntegerArg, CMDInteger32ArgBase):
    pass


# integer64
class CMDInteger64ArgBase(CMDIntegerArgBase):
    TYPE_VALUE = "integer64"


class CMDInteger64Arg(CMDIntegerArg, CMDInteger64ArgBase):
    pass


# boolean
class CMDBooleanArgBase(CMDArgBase):
    TYPE_VALUE = "boolean"


class CMDBooleanArg(CMDArg, CMDBooleanArgBase):
    pass


# float
class CMDFloatArgBase(CMDArgBase):
    TYPE_VALUE = "float"

    fmt = ModelType(
        CMDFloatFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False,
    )
    enum = ModelType(CMDArgEnum, serialize_when_none=False)

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDFloatArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDFloatArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg


class CMDFloatArg(CMDArg, CMDFloatArgBase):
    pass


# float32
class CMDFloat32ArgBase(CMDFloatArgBase):
    TYPE_VALUE = "float32"


class CMDFloat32Arg(CMDFloatArg, CMDFloat32ArgBase):
    pass


# float64
class CMDFloat64ArgBase(CMDFloatArgBase):
    TYPE_VALUE = "float64"


class CMDFloat64Arg(CMDFloatArg, CMDFloat64ArgBase):
    pass


# object
class CMDObjectArgBase(CMDArgBase):
    TYPE_VALUE = "object"

    fmt = ModelType(
        CMDObjectFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True), serialize_when_none=False)

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDObjectArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDObjectArgBase)
        try:
            arg.fmt = builder.get_fmt()
        except Exception:
            raise
        arg.args = builder.get_sub_args()
        return arg


class CMDObjectArg(CMDArg, CMDObjectArgBase):
    pass


# array
class CMDArrayArgBase(CMDArgBase):
    TYPE_VALUE = "array"

    fmt = ModelType(
        CMDArrayFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    item = PolyModelType(CMDArgBase, allow_subclasses=True, required=True)

    def _get_type(self):
        return f"{self.TYPE_VALUE}<{self.item.type}>"

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDArrayArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDArrayArgBase)
        arg.fmt = builder.get_fmt()
        arg.item = builder.get_sub_item()
        return arg


class CMDArrayArg(CMDArg, CMDArrayArgBase):
    pass
