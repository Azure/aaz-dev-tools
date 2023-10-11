from schematics.types import StringType, DictType, ListType, BooleanType, BaseType


class DataTypeFormatEnum(StringType):
    VALID_TYPE_FORMATS = (
        "int32", "int64",
        "float", "double",
        "byte", "binary", "date", "date-time", "time", "password",
        # additional formats
        "duration", "uuid",
        "file", "uri",
        "arm-id",
    )

    def __init__(self, **kwargs):
        super().__init__(choices=self.VALID_TYPE_FORMATS, **kwargs)


class MimeField(StringType):
    pass


class RegularExpressionField(StringType):
    # This string SHOULD be a valid regular expression
    pass


class SecurityRequirementField(DictType):
    """
    Lists the required security schemes to execute this operation. The object can have multiple security schemes declared in it which are all required (that is, there is a logical AND between the schemes).

    The type of value could be string or list
    """

    def __init__(self, **kwargs):
        super().__init__(
            field=ListType(StringType()), **kwargs)


class ScopesField(DictType):
    """Lists the available scopes for an OAuth2 security scheme."""

    def __init__(self, **kwargs):
        super().__init__(field=StringType(), **kwargs)


class XmsCodeGenerationSettingsField(BaseType):
    """
    x-ms-code-generation-settings extension on info element enables passing code generation settings via the OpenAPI definition.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-code-generation-settings
    """
    def __init__(self, **kwargs):
        super().__init__(
            default=False,
            serialized_name="x-ms-code-generation-settings",
            deserialize_from="x-ms-code-generation-settings",
            **kwargs
        )


class XcadlGeneratedField(BaseType):

    def __init__(self, **kwargs):
        super().__init__(
            default=False,
            serialized_name="x-cadl-generated",
            deserialize_from="x-cadl-generated",
            **kwargs
        )


class XTypespecGeneratedField(BaseType):

    def __init__(self, **kwargs):
        super().__init__(
            default=False,
            serialized_name="x-typespec-generated",
            deserialize_from="x-typespec-generated",
            **kwargs
        )


class XmsSkipURLEncodingField(BooleanType):
    """
    skips URL encoding for path and query parameters.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-skip-url-encoding
    """

    def __init__(self, **kwargs):
        super().__init__(
            default=False,
            serialized_name="x-ms-skip-url-encoding",
            deserialize_from="x-ms-skip-url-encoding",
            **kwargs
        )


class XmsParameterLocationField(StringType):
    """
    By default Autorest processes global parameters as properties on the client. For example subscriptionId and apiVersion which are defined in the global parameters section end up being properties of the client. It would be natural to define resourceGroupName once in the global parameters section and then reference it everywhere, rather than repeating the same definition inline everywhere. One may not want resourceGroupName as a property on the client, just because it is defined in the global parameters section. This extension helps you achieve that. You can add this extension with value "method" "x-ms-parameter-location": "method" and resourceGroupName will not be a client property.

    This extension can only be applied on global parameters. If this is applied on any parameter in an operation then it will be ignored.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-parameter-location
    """

    def __init__(self, **kwargs):
        super().__init__(
            choices=("client", "method"),
            serialized_name="x-ms-parameter-location",
            deserialize_from="x-ms-parameter-location",
            **kwargs
        )


class XmsClientNameField(StringType):
    """
    In some situations, data passed by name, such as query parameters, entity headers, or elements of a JSON document body, are not suitable for use in client-side code. For example, a header like 'x-ms-version' would turn out like xMsVersion, or x_ms_version, or XMsVersion, depending on the preferences of a particular code generator. It may be better to allow a code generator to use 'version' as the name of the parameter in client code.

    By using the 'x-ms-client-name' extension, a name can be defined for use specifically in code generation, separately from the name on the wire. It can be used for query parameters and header parameters, as well as properties of schemas.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-client-name
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name="x-ms-client-name",
            deserialize_from="x-ms-client-name",
            **kwargs
        )


class XmsExternalField(BooleanType):
    """
    To allow generated clients to share models via shared libraries an x-ms-external extension was introduced. When a Schema Object contains this extensions it's definition will be excluded from generated library. Note that in strongly typed languages the code will not compile unless the assembly containing the type is referenced with the project/library.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-external
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name="x-ms-external",
            deserialize_from="x-ms-external",
            **kwargs
        )


class XmsDiscriminatorValueField(StringType):
    """
    Swagger 2.0 specification requires that when used, the value of discriminator field MUST match the name of the schema or any schema that inherits it. To overcome this limitation x-ms-discriminator-value extension was introduced.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-discriminator-value
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name="x-ms-discriminator-value",
            deserialize_from="x-ms-discriminator-value",
            **kwargs
        )


class XmsClientFlattenField(BooleanType):
    """
    This extension allows to flatten deeply nested payloads into a more user friendly object.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-client-flatten
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name="x-ms-client-flatten",
            deserialize_from="x-ms-client-flatten",
            **kwargs
        )


class MutabilityEnum:

    Create = "create"
    Read = "read"
    Update = "update"


class XmsMutabilityField(ListType):
    """
    This extension offers insight to Autorest on how to generate code (mutability of the property of the model classes being generated). It doesn't alter the modeling of the actual payload that is sent on the wire.

    It is an array of strings with three possible values. The array cannot have repeatable values. Valid values are: "create", "read", "update".
    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-mutability
    """

    VALID_VALUES = (
        MutabilityEnum.Create,  # Indicates that the value of the property can be set while creating/initializing/constructing the object
        MutabilityEnum.Read,   # Indicates that the value of the property can be read
        MutabilityEnum.Update,  # Indicates that value of the property can be updated anytime(even after the object is created)
    )

    def __init__(self, **kwargs):
        super().__init__(
            field=StringType(choices=self.VALID_VALUES),
            serialized_name='x-ms-mutability',
            deserialize_from='x-ms-mutability',
            **kwargs
        )


class XmsExamplesField(DictType):
    """
    Describes the format for specifying examples for request and response of an operation in an OpenAPI definition. It is a dictionary of different variations of the examples for a given operation.

    https://github.com/Azure/azure-rest-api-specs/blob/master/documentation/x-ms-examples.md
    """

    def __init__(self, **kwargs):
        super().__init__(
            field=BaseType(),
            serialized_name='x-ms-examples',
            deserialize_from='x-ms-examples',
            **kwargs
        )


class XmsErrorResponseField(BooleanType):
    """
    Indicates whether the response status code should be treated as an error response or not.

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-error-response
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-error-response',
            deserialize_from='x-ms-error-response',
            **kwargs
        )


class XmsTextField(BooleanType):
    """
    Swagger spec doesn't allow dev to model this XML structure: <title language="text">the title</title> This is well known issue: https://github.com/OAI/OpenAPI-Specification/issues/630

    This extension is defined to help for this scenario.

    Note: The extension is not tight to this particular scenario (you could model any text node that way), but we recommend to follow as much as possible the Swagger specification, and to use it only in case of attributes/text.

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-text
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-text',
            deserialize_from='x-ms-text',
            **kwargs
        )


class XmsClientDefaultField(BaseType):
    """
    Set the default value for a property or a parameter.

    With this extension, you can set a default value for a property or parameter that is independent of how the property / parameter's schema is handling a default. This is different than the default value you can specify

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-client-default

    Schema: string, integer, long, float, double, boolean
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-client-default',
            deserialize_from='x-ms-client-default',
            **kwargs
        )


class XmsArmIdDetailsField(BaseType):
    """

    http://azure.github.io/autorest/extensions/#x-ms-arm-id-details
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-arm-id-details',
            deserialize_from='x-ms-arm-id-details',
            **kwargs
        )


class XmsAzureResourceField(BooleanType):
    """
    Resource types as defined by the Resource Manager API are tagged by using a x-ms-azure-resource extension.

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-azure-resource
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-azure-resource',
            deserialize_from='x-ms-azure-resource',
            **kwargs
        )


class XmsRequestIdField(StringType):
    """
    When set, allows to overwrite the x-ms-request-id response header (default is x-ms-request-id).

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-request-id
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-request-id',
            deserialize_from='x-ms-request-id',
            **kwargs
        )


class XmsClientRequestIdField(BooleanType):
    """
    When set, specifies the header parameter to be used instead of x-ms-client-request-id (default is x-ms-client-request-id).

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-client-request-id
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-client-request-id',
            deserialize_from='x-ms-client-request-id',
            **kwargs
        )


class XmsApiVersionField(BooleanType):
    """"""

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-api-version',
            deserialize_from='x-ms-api-version',
            **kwargs
        )


class XmsSkipUrlEncodingField(BooleanType):
    """"""

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-skip-url-encoding',
            deserialize_from='x-ms-skip-url-encoding',
            **kwargs
        )


class XmsSecretField(BooleanType):

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-secret',
            deserialize_from='x-ms-secret',
            **kwargs
        )


class XNullableField(BooleanType):
    """
    Set "x-nullable": true on a schema to indicate that a null is a legal value. By default, a null value should be disallowed when forming a request and rejected during payload deserialization.

    For arrays, sending/receiving a null array entry is not supported and should result in an error.

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-nullable
    """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-nullable',
            deserialize_from='x-nullable',
            **kwargs
        )


class XCadlNameField(StringType):
    """ https://github.com/microsoft/cadl """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-cadl-name',
            deserialize_from='x-cadl-name',
            **kwargs
        )


class XTypespecNameField(StringType):

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-typespec-name',
            deserialize_from='x-typespec-name',
            **kwargs
        )


class XmsHeaderCollectionPrefix(StringType):
    """ only used in Storage Data plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-ms-header-collection-prefix',
            deserialize_from='x-ms-header-collection-prefix',
            **kwargs
        )


class XAccessibilityField(StringType):
    """ only used in ContainerRegistry Data plane """

    def __init__(self, **kwargs):
        super().__init__(
            choices=("internal", "public"),
            serialized_name='x-accessibility',
            deserialize_from='x-accessibility',
            **kwargs
        )


class XRequiredField(BooleanType):
    """ only used in ContainerRegistry Data plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-required',
            deserialize_from='x-required',
            **kwargs
        )


class XPublishField(BooleanType):
    """ only used in Maps Data Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-publish',
            deserialize_from='x-publish',
            **kwargs
        )


class XAzSearchDeprecatedField(BooleanType):
    """ only used in Search Data Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-az-search-deprecated',
            deserialize_from='x-az-search-deprecated',
            **kwargs
        )


class XSfCodeGenField(BaseType):
    """ only used in ServiceFabricMesh Mgmt Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-sf-codegen',
            deserialize_from='x-sf-codegen',
            **kwargs
        )


class XSfClientLibField(BaseType):
    """ only used in ServiceFabric Data Plane and ServiceFabricManagedClusters Mgmt Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-sf-clientlib',
            deserialize_from='x-sf-clientlib',
            **kwargs
        )


class XApimCodeNillableField(BooleanType):
    """ only used in ApiManagement Mgmt Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-apim-code-nillable',
            deserialize_from='x-apim-code-nillable',
            **kwargs
        )


class XCommentField(StringType):
    """ Only used in IoTCenter Mgmt Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-comment',
            deserialize_from='x-comment',
            **kwargs
        )


class XOriginalNameField(StringType):
    """ Only used in Marketplane Catalog Data Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-originalName',
            deserialize_from='x-originalName',
            **kwargs
        )


class XAbstractField(BooleanType):
    """ Only used in Logic Mgmt Plane and Web Mgmt Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-abstract',
            deserialize_from='x-abstract',
            **kwargs
        )


class XClientNameField(StringType):
    """ Only used in Maps Data Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-client-name',
            deserialize_from='x-client-name',
            **kwargs
        )


class XNewPatternField(StringType):
    """ Only used in FrontDoor Mgmt Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-new-pattern',
            deserialize_from='x-new-pattern',
            **kwargs
        )


class XPreviousPatternField(StringType):
    """ Only used in FrontDoor Mgmt Plane """

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-previous-pattern',
            deserialize_from='x-previous-pattern',
            **kwargs
        )


class XADLNameField(StringType):
    """ Only used in Plane"""

    def __init__(self, **kwargs):
        super().__init__(
            serialized_name='x-adl-name',
            deserialize_from='x-adl-name',
            **kwargs
        )
