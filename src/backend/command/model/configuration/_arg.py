from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, PolyModelType, FloatType, IntType
from schematics.types.serializable import serializable
from ._help import CMDArgumentHelp
from ._fields import CMDStageField, CMDVariantField, CMDRegularExpressionField, CMDPrimitiveField, CMDBooleanField


class CMDArgEnumItem(Model):
    # properties as tags
    name = StringType(required=True)
    hide = CMDBooleanField()

    # properties as nodes
    value = CMDPrimitiveField(required=True)


class CMDArgEnum(Model):
    # properties as tags

    # properties as nodes
    items = ListType(ModelType(CMDArgEnumItem), min_size=1)


class CMDArgDefault(Model):
    """ The argument value if an argument is not used """

    # properties as nodes
    value = CMDPrimitiveField()  # json value format string, support null


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


class CMDArg(CMDArgBase):

    # properties as tags
    var = CMDVariantField(required=True)
    options = ListType(StringType(), min_size=1, required=True)    # argument option names
    required = CMDBooleanField()
    stage = CMDStageField()

    hide = CMDBooleanField()

    # properties as nodes
    help = ModelType(CMDArgumentHelp, serialize_when_none=False)
    default = ModelType(CMDArgDefault, serialize_when_none=False)
    blank = ModelType(CMDArgBlank, serialize_when_none=False)

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDArg, cls)._claim_polymorphic(data):
            if isinstance(data, dict):
                # distinguish with CMDArgBase and CMDArg
                return 'var' in data
            else:
                return isinstance(data, CMDArg)
        return False


# string
class CMDStringArgFormat(Model):
    pattern = CMDRegularExpressionField()
    max_length = IntType(
        serialized_name="maxLength",
        deserialize_from="maxLength",
        min_value=0
    )
    min_length = IntType(
        serialized_name="minLength",
        deserialize_from="minLength",
        min_value=0
    )

    class Options:
        serialize_when_none = False


class CMDStringArgBase(CMDArgBase):
    TYPE_VALUE = "string"

    fmt = ModelType(
        CMDStringArgFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDArgEnum, serialize_when_none = False)


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
class CMDIntegerArgFormat(Model):
    multiple_of = IntType(
        min_value=0,
        serialized_name='multipleOf',
        deserialize_from='multipleOf'
    )
    maximum = IntType()
    minimum = IntType()

    class Options:
        serialize_when_none = False


class CMDIntegerArgBase(CMDArgBase):
    TYPE_VALUE = "integer"

    fmt = ModelType(
        CMDIntegerArgFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    enum = ModelType(CMDArgEnum, serialize_when_none=False)


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
class CMDFloatArgFormat(Model):
    multiple_of = FloatType(
        min_value=0,
        serialized_name='multipleOf',
        deserialize_from='multipleOf'
    )
    maximum = FloatType()
    exclusive_maximum = CMDBooleanField(
        serialized_name='exclusiveMaximum',
        deserialize_from='exclusiveMaximum'
    )
    minimum = FloatType()
    exclusive_minimum = CMDBooleanField(
        serialized_name='exclusiveMinimum',
        deserialize_from='exclusiveMinimum'
    )

    class Options:
        serialize_when_none = False


class CMDFloatArgBase(CMDArgBase):
    TYPE_VALUE = "float"

    fmt = ModelType(
        CMDFloatArgFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False,
    )
    enum = ModelType(CMDArgEnum, serialize_when_none=False)


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
class CMDObjectArgFormat(Model):
    max_properties = IntType(
        min_value=0,
        serialized_name='maxProperties',
        deserialize_from='maxProperties'
    )
    min_properties = IntType(
        min_value=0,
        serialized_name='minProperties',
        deserialize_from='minProperties'
    )

    class Options:
        serialize_when_none = False


class CMDObjectArgBase(CMDArgBase):
    TYPE_VALUE = "object"

    fmt = ModelType(
        CMDObjectArgFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True), serialize_when_none=False)


class CMDObjectArg(CMDArg, CMDObjectArgBase):
    pass


# array
class CMDArrayArgFormat(Model):
    unique = CMDBooleanField()
    max_length = IntType(
        min_value=0,
        serialized_name='maxLength',
        deserialize_from='maxLength'
    )
    min_length = IntType(
        min_value=0,
        serialized_name='minLength',
        deserialize_from='minLength'
    )

    class Options:
        serialize_when_none = False


class CMDArrayArgBase(CMDArgBase):
    TYPE_VALUE = "array"

    fmt = ModelType(
        CMDArrayArgFormat,
        serialized_name='format',
        deserialize_from='format',
        serialize_when_none=False
    )
    item = PolyModelType(CMDArgBase, allow_subclasses=True, required=True)

    def _get_type(self):
        return f"{self.TYPE_VALUE}<{self.item.type}>"


class CMDArrayArg(CMDArg, CMDArrayArgBase):
    pass
