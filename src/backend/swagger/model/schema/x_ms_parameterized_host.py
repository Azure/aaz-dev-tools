from schematics.models import Model
from schematics.types import StringType, ModelType, BooleanType, ListType
from .parameter import ParameterField, ParameterBase
from .reference import Linkable, Reference


class XmsParameterizedHost(Model, Linkable):
    """
    When used, replaces the standard OpenAPI "host" attribute with a host that contains variables to be replaced as part of method execution or client construction, very similar to how path parameters work.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-parameterized-host
    """

    host_template = StringType(
        required=True,
        serialized_name="hostTemplate",
        deserialize_from="hostTemplate"
    )  # Specifies the parameterized template for the host.
    use_scheme_prefix = BooleanType(
        default=True,
        serialized_name="useSchemePrefix",
        deserialize_from="useSchemePrefix"
    )  # Specifies whether to prepend the default scheme a.k.a protocol to the base uri of client.
    position_in_operation = StringType(
        default="first",
        choices=("first", "last"),
        serialized_name="positionInOperation",
        deserialize_from="positionInOperation"
    )  # Specifies whether the list of parameters will appear in the beginning or in the end, in the method signature for every operation. The order within the parameters provided in the below mentioned array will be preserved. Either the array of parameters will be prepended or appended, based on the value provided over here. Valid values are "first", "last". Every method/operation in any programming language has parameters categorized into two buckets "required" and "optional". It is natural for optional parameters to appear in the end in a method signature. This aspect will be preserved, while prepending(first) or appending(last) hostTemplate parameters.
    parameters = ListType(ParameterField(support_reference=True))  # The list of parameters that are used within the hostTemplate. This can include both reference parameters as well as explicit parameters. Note that "in" is required and must be set to "path". The reference parameters will be treated as global parameters and will end up as property of the client.

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        if self.parameters is not None:
            for idx, param in enumerate(self.parameters):
                if isinstance(param, Linkable):
                    param.link(swagger_loader, *self.traces, 'parameters', idx)

            # replace parameter reference by parameter instance
            for idx in range(len(self.parameters)):
                param = self.parameters[idx]
                while isinstance(param, Reference):
                    param = param.ref_instance
                assert isinstance(param, ParameterBase)
                self.parameters[idx] = param


class XmsParameterizedHostField(ModelType):

    def __init__(self, **kwargs):
        super(XmsParameterizedHostField, self).__init__(
            XmsParameterizedHost,
            serialized_name="x-ms-parameterized-host",
            deserialize_from="x-ms-parameterized-host",
            **kwargs
        )
