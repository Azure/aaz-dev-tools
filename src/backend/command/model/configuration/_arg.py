from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, PolyModelType
from schematics.types.serializable import serializable

from ._fields import CMDStageField, CMDVariantField, CMDPrimitiveField, CMDBooleanField, CMDClassField
from ._format import CMDStringFormat, CMDIntegerFormat, CMDFloatFormat, CMDObjectFormat, CMDArrayFormat
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
        _attributes = {"name", "hide"}

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

    class Options:
        _attributes = set()

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

    class Options:
        _attributes = set()

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

    class Options:
        _attributes = set()


class CMDArgBase(Model):
    TYPE_VALUE = None

    # base types: "array", "boolean", "integer", "float", "object", "string",
    # special types: "@File", "@ResourceID", "@ResourceGroup", "@Subscription", "@Json"

    class Options:
        serialize_when_none = False
        _attributes = {"type"}

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

    class Options:
        _attributes = CMDArgBase.Options._attributes | {"var", "options", "required", "stage", "hide", "group", "id_part"}

    def __init__(self, *args, **kwargs):
        super(CMDArg, self).__init__(*args, **kwargs)
        self.ref_schema = None

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

        arg.hide = builder.get_hide()
        return arg


# cls
class CMDClsArgBase(CMDArgBase):
    _type = StringType(
        deserialize_from='type',
        serialized_name='type',
        required=True
    )

    class Options:
        _attributes = CMDArgBase.Options._attributes | {"_type"}

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
        arg = super(CMDClsArgBase, cls).build_arg_base(builder)
        arg._type = builder.get_type()
        return arg


class CMDClsArg(CMDArg, CMDClsArgBase):
    class Options:
        _attributes = CMDArg.Options._attributes | CMDClsArgBase.Options._attributes


# string
class CMDStringArgBase(CMDArgBase):
    TYPE_VALUE = "string"

    fmt = ModelType(
        CMDStringFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDArgEnum)

    class Options:
        _attributes = CMDArgBase.Options._attributes | {"fmt"}

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDStringArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDStringArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg


class CMDStringArg(CMDArg, CMDStringArgBase):
    class Options:
        _attributes = CMDArg.Options._attributes | CMDStringArgBase.Options._attributes


# byte: base64 encoded characters
class CMDByteArgBase(CMDStringArgBase):
    TYPE_VALUE = "byte"

    class Options:
        _attributes = CMDStringArgBase.Options._attributes


class CMDByteArg(CMDStringArg, CMDByteArgBase):
    class Options:
        _attributes = CMDStringArg.Options._attributes | CMDByteArgBase.Options._attributes


# binary: any sequence of octets
class CMDBinaryArgBase(CMDStringArgBase):
    TYPE_VALUE = "binary"

    class Options:
        _attributes = CMDStringArgBase.Options._attributes


class CMDBinaryArg(CMDStringArg, CMDBinaryArgBase):
    class Options:
        _attributes = CMDStringArg.Options._attributes | CMDBinaryArgBase.Options._attributes


# duration
class CMDDurationArgBase(CMDStringArgBase):
    TYPE_VALUE = "duration"

    class Options:
        _attributes = CMDStringArgBase.Options._attributes


class CMDDurationArg(CMDStringArg, CMDDurationArgBase):
    class Options:
        _attributes = CMDStringArg.Options._attributes | CMDDurationArgBase.Options._attributes


# date: As defined by full-date - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateArgBase(CMDStringArgBase):
    TYPE_VALUE = "date"

    class Options:
        _attributes = CMDStringArgBase.Options._attributes


class CMDDateArg(CMDStringArg, CMDDateArgBase):
    class Options:
        _attributes = CMDStringArg.Options._attributes | CMDDateArgBase.Options._attributes


# date-time: As defined by date-time - https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#anchor14
class CMDDateTimeArgBase(CMDStringArgBase):
    TYPE_VALUE = "date-time"

    class Options:
        _attributes = CMDStringArgBase.Options._attributes


class CMDDateTimeArg(CMDStringArg, CMDDateTimeArgBase):
    class Options:
        _attributes = CMDStringArg.Options._attributes | CMDDateTimeArgBase.Options._attributes


# uuid
class CMDUuidArgBase(CMDStringArgBase):
    TYPE_VALUE = "uuid"

    class Options:
        _attributes = CMDStringArgBase.Options._attributes


class CMDUuidArg(CMDStringArg, CMDUuidArgBase):
    class Options:
        _attributes = CMDStringArg.Options._attributes | CMDUuidArgBase.Options._attributes


# password
class CMDPasswordArgBase(CMDStringArgBase):
    TYPE_VALUE = "password"

    class Options:
        _attributes = CMDStringArgBase.Options._attributes


class CMDPasswordArg(CMDStringArg, CMDPasswordArgBase):
    class Options:
        _attributes = CMDStringArg.Options._attributes | CMDPasswordArgBase.Options._attributes


# integer
class CMDIntegerArgBase(CMDArgBase):
    TYPE_VALUE = "integer"

    fmt = ModelType(
        CMDIntegerFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDArgEnum)

    class Options:
        _attributes = CMDArgBase.Options._attributes

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDIntegerArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDIntegerArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg


class CMDIntegerArg(CMDArg, CMDIntegerArgBase):
    class Options:
        _attributes = CMDArg.Options._attributes | CMDIntegerArgBase.Options._attributes


# integer32
class CMDInteger32ArgBase(CMDIntegerArgBase):
    TYPE_VALUE = "integer32"

    class Options:
        _attributes = CMDIntegerArgBase.Options._attributes


class CMDInteger32Arg(CMDIntegerArg, CMDInteger32ArgBase):
    class Options:
        _attributes = CMDIntegerArg.Options._attributes | CMDInteger32ArgBase.Options._attributes


# integer64
class CMDInteger64ArgBase(CMDIntegerArgBase):
    TYPE_VALUE = "integer64"

    class Options:
        _attributes = CMDIntegerArgBase.Options._attributes


class CMDInteger64Arg(CMDIntegerArg, CMDInteger64ArgBase):
    class Options:
        _attributes = CMDIntegerArg.Options._attributes | CMDInteger64ArgBase.Options._attributes


# boolean
class CMDBooleanArgBase(CMDArgBase):
    TYPE_VALUE = "boolean"

    class Options:
        _attributes = CMDArgBase.Options._attributes


class CMDBooleanArg(CMDArg, CMDBooleanArgBase):
    class Options:
        _attributes = CMDArg.Options._attributes | CMDBooleanArgBase.Options._attributes


# float
class CMDFloatArgBase(CMDArgBase):
    TYPE_VALUE = "float"

    fmt = ModelType(
        CMDFloatFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    enum = ModelType(CMDArgEnum)

    class Options:
        _attributes = CMDArgEnum.Options._attributes

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDFloatArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDFloatArgBase)
        arg.fmt = builder.get_fmt()
        arg.enum = builder.get_enum()
        return arg


class CMDFloatArg(CMDArg, CMDFloatArgBase):
    class Options:
        _attributes = CMDArg.Options._attributes | CMDFloatArgBase.Options._attributes


# float32
class CMDFloat32ArgBase(CMDFloatArgBase):
    TYPE_VALUE = "float32"

    class Options:
        _attributes = CMDFloatArgBase.Options._attributes


class CMDFloat32Arg(CMDFloatArg, CMDFloat32ArgBase):
    class Options:
        _attributes = CMDFloatArg.Options._attributes | CMDFloat32ArgBase.Options._attributes


# float64
class CMDFloat64ArgBase(CMDFloatArgBase):
    TYPE_VALUE = "float64"

    class Options:
        _attributes = CMDFloatArgBase.Options._attributes


class CMDFloat64Arg(CMDFloatArg, CMDFloat64ArgBase):
    _attributes = CMDFloatArg.Options._attributes | CMDFloat64ArgBase.Options._attributes


# object

class CMDObjectArgAdditionalProperties(Model):
    # properties as nodes
    item = PolyModelType(CMDArgBase, allow_subclasses=True)

    class Options:
        serialize_when_none = False
        _attributes = set()

    @classmethod
    def build_arg_base(cls, builder):
        arg = cls()
        arg.item = builder.get_sub_item()
        return arg


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

    class Options:
        _attributes = CMDArgBase.Options._attributes

    @classmethod
    def build_arg_base(cls, builder):
        arg = super(CMDObjectArgBase, cls).build_arg_base(builder)
        assert isinstance(arg, CMDObjectArgBase)
        try:
            arg.fmt = builder.get_fmt()
        except Exception:
            raise
        arg.args = builder.get_sub_args()
        arg.additional_props = builder.get_additional_props()
        return arg


class CMDObjectArg(CMDArg, CMDObjectArgBase):

    cls = CMDClassField()  # define a class which can be used by loop

    class Options:
        _attributes = CMDArg.Options._attributes | CMDObjectArgBase.Options._attributes

    @classmethod
    def build_arg(cls, builder):
        arg = super(CMDObjectArg, cls).build_arg(builder)
        assert isinstance(arg, CMDObjectArg)
        arg.cls = builder.get_cls()
        return arg


# array
class CMDArrayArgBase(CMDArgBase):
    TYPE_VALUE = "array"

    fmt = ModelType(
        CMDArrayFormat,
        serialized_name='format',
        deserialize_from='format',
    )
    item = PolyModelType(CMDArgBase, allow_subclasses=True, required=True)

    class Options:
        _attributes = CMDArgBase.Options._attributes

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

    cls = CMDClassField()  # define a class which can be used by loop

    class Options:
        _attributes = CMDArg.Options._attributes | CMDArrayArgBase.Options._attributes

    @classmethod
    def build_arg(cls, builder):
        arg = super(CMDArrayArg, cls).build_arg(builder)
        assert isinstance(arg, CMDArrayArg)
        arg.cls = builder.get_cls()
        return arg
