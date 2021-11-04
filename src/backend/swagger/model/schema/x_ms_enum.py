from schematics.models import Model
from schematics.types import StringType, BooleanType, BaseType, ModelType, ListType


class XmsEnumValue(Model):
    """
    When set, this will override the values specified with enum, while also enabling further customization. We recommend still specifying enum as a fallback for consumers that don't understand x-ms-enum. Each item in x-ms-enum corresponds to an enum item.
    """

    value = BaseType(required=True)  # Property value is mandatory and corresponds to the value one would also have specified using enum.
    description = StringType()  # Property value is mandatory and corresponds to the value one would also have specified using enum
    name = StringType()  # allows overriding the name of the enum value that would usually be derived from the value.


class XmsEnum(Model):
    """
    Enum definitions in OpenAPI indicate that only a particular set of values may be used for a property or parameter. When the property is represented on the wire as a string, it would be a natural choice to represent the property type in C# and Java as an enum. However, not all enumeration values should necessarily be represented as strongly typed enums - there are additional considerations, such as how often expected values might change, since adding a new value to a strongly typed enum is a breaking change requiring an updated API version. Additionally, there is some metadata that is required to create a useful enum, such as a descriptive name, which is not represented in vanilla OpenAPI. For this reason, enums are not automatically turned into strongly typed enum types - instead they are rendered in the documentation comments for the property or parameter to indicate allowed values. To indicate that an enum will rarely change and that C#/Java enum semantics are desired, use the x-ms-enum extension. Note that depending on the code generation language the behavior of this extension may differ.
    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-enum
    """

    name = StringType(required=True)  # Specifies the name for the Enum.
    model_as_string = BooleanType(
        default=False,
        serialized_name="modelAsString",
        deserialize_from="modelAsString"
    )  # When set to true the enum will be modeled as a string. No validation will happen. When set to false, it will be modeled as an enum if that language supports enums. Validation will happen, irrespective of support of enums in that language.
    values = ListType(ModelType(XmsEnumValue))

    model_as_extensible = BooleanType(
        serialized_name="modelAsExtensible",
        deserialize_from="modelAsExtensible"
    )   # TODO: don't know its usage


class XmsEnumField(ModelType):

    def __init__(self, **kwargs):
        super(XmsEnumField, self).__init__(
            XmsEnum,
            serialized_name="x-ms-enum",
            deserialize_from="x-ms-enum",
            **kwargs
        )
