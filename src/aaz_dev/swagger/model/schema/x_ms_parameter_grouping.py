from schematics.models import Model
from schematics.types import StringType, ModelType


class XmsParameterGrouping(Model):
    """
    By default operation parameters are generated in the client as method arguments. This behavior can sometimes be undesirable when the number of parameters is high. x-ms-parameter-grouping extension is used to group multiple primitive parameters into a composite type to improve the API.
    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-parameter-grouping
    """

    name = StringType()  # When set, specifies the name for the composite type.
    postfix = StringType()  # Alternative to name parameter. If specified the name of the composite type will be generated as follows {MethodGroup}{Method}{Postfix}


class XmsParameterGroupingField(ModelType):

    def __init__(self, **kwargs):
        super(XmsParameterGroupingField, self).__init__(
            XmsParameterGrouping,
            serialized_name="x-ms-parameter-grouping",
            deserialize_from="x-ms-parameter-grouping",
            **kwargs
        )
