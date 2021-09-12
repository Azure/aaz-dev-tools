from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, BooleanType, BaseType, PolyModelType, FloatType, IntType
from ._help import CMDArgumentHelp
from ._fields import CMDStageField, CMDVariantField, CMDTypeField, CMDRegularExpressionField
from ._enum import CMDEnum


class CMDArgDefault(Model):
    """ The argument value if an argument is not used """

    # properties as nodes
    value = BaseType(required=True)  # json value format string, support null


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
    value = BaseType(required=True)  # json value format string, support null


class CMDArgBase(Model):
    TYPE_VALUE = None

    # base types: "array", "boolean", "integer", "float", "object", "string",
    # predefined types: "@File", "@ResourceID", "@ResourceGroup", "@Subscription", "@Json"
    type_ = CMDTypeField(required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        return False


class CMDArg(CMDArgBase):

    # properties as tags
    var = CMDVariantField(required=True)
    options = ListType(StringType(), min_size=1, required=True)    # argument option names
    required = BooleanType(default=False)
    stage = CMDStageField()

    hide = BooleanType(default=False)

    # properties as nodes
    help_ = ModelType(CMDArgumentHelp)

    default = ModelType(CMDArgDefault)
    blank = ModelType(CMDArgBlank)

    @classmethod
    def _claim_polymorphic(cls, data):
        if super(CMDArg, cls)._claim_polymorphic(data):
            # distinguish with CMDArgBase and CMDArg
            return 'var' in data
        return False


# string
class CMDStringArgFormat(Model):
    pattern = CMDRegularExpressionField()
    max_length = IntType(min_value=0)
    min_length = IntType(min_value=0)


class CMDStringArgBase(CMDArgBase):
    TYPE_VALUE = "string"

    format_ = ModelType(
        CMDStringArgFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    enum = ModelType(CMDEnum)


class CMDStringArg(CMDArg, CMDStringArgBase):
    pass


# integer
class CMDIntegerArgFormat(Model):
    multiple_of = IntType(min_value=0)
    maximum = IntType()
    minimum = IntType()


class CMDIntegerArgBase(CMDArgBase):
    TYPE_VALUE = "integer"

    format_ = ModelType(
        CMDIntegerArgFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    enum = ModelType(CMDEnum)


class CMDIntegerArg(CMDArg, CMDIntegerArgBase):
    pass


# boolean
class CMDBooleanArgBase(CMDArgBase):
    TYPE_VALUE = "boolean"


class CMDBooleanArg(CMDArg, CMDBooleanArgBase):
    pass


# float
class CMDFloatArgFormat(Model):
    multiple_of = FloatType(min_value=0)
    maximum = FloatType()
    exclusive_maximum = BooleanType()
    minimum = FloatType()
    exclusive_minimum = BooleanType()


class CMDFloatArgBase(CMDArgBase):
    TYPE_VALUE = "float"

    format_ = ModelType(
        CMDFloatArgFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    enum = ModelType(CMDEnum)


class CMDFloatArg(CMDArg, CMDFloatArgBase):
    pass


# object
class CMDObjectArgFormat(Model):
    max_properties = IntType(min_value=0)
    min_properties = IntType(min_value=0)


class CMDObjectArgBase(CMDArgBase):
    TYPE_VALUE = "object"

    format_ = ModelType(
        CMDObjectArgFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True))


class CMDObjectArg(CMDArg, CMDObjectArgBase):
    pass


# array
class CMDArrayArgFormat(Model):
    unique = BooleanType(default=False)
    max_length = IntType(min_value=0)
    min_length = IntType(min_value=0)


class CMDArrayArgBase(CMDArgBase):
    TYPE_VALUE = "array"

    format_ = ModelType(
        CMDArrayArgFormat,
        serialized_name='format',
        deserialize_from='format'
    )
    item = PolyModelType(CMDArgBase, allow_subclasses=True)


class CMDArrayArg(CMDArg, CMDArrayArgBase):
    pass
