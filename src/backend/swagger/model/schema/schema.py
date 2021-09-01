from schematics.models import Model
from schematics.types import ListType, BaseType, DictType, ModelType, BooleanType, FloatType, IntType, StringType, PolyModelType
from .reference import ReferenceType, Linkable
from .types import DataTypeFormatEnum, RegularExpressionType, XmsClientNameType, XmsExternal, XmsDiscriminatorValue, XmsClientFlatten, XmsMutabilityType, XmsClientDefaultType, XNullableType, XmsAzureResourceType
from .xml import XML
from .external_documentation import ExternalDocumentation
from .x_ms_enum import XmsEnumType
from .types import XmsSecretType, XAccessibilityType, XAzSearchDeprecatedType, XSfClientLibType, XApimCodeNillableType, XCommentType, XAbstractType, XClientNameType


def _additionalProperties_claim_function(_, data):
    if isinstance(data, bool):
        return bool
    elif isinstance(data, dict):
        return Schema
    else:
        return None


def _items_claim_function(_, data):
    if isinstance(data, dict):
        return Schema
    elif isinstance(data, list):
        return ListType(ModelType(Schema))
    else:
        return None


class Schema(Model, Linkable):
    """
    The Schema Object allows the definition of input and output data types. These types can be objects, but also primitives and arrays. This object is based on the JSON Schema Specification Draft 4 and uses a predefined subset of it. On top of this subset, there are extensions provided by this specification to allow for more complete documentation.
    Further information about the properties can be found in JSON Schema Core and JSON Schema Validation. Unless stated otherwise, the property definitions follow the JSON Schema specification as referenced here.
    """

    ref = ReferenceType()
    format = DataTypeFormatEnum()
    title = StringType()
    description = StringType()
    default = BaseType()

    # Validation keywords for numeric instances (number and integer)
    multipleOf = FloatType(min_value=0)
    maximum = FloatType()
    exclusiveMaximum = BooleanType()
    minimum = FloatType()
    exclusiveMinimum = BooleanType()

    # Validation keywords for strings
    maxLength = IntType(min_value=0)
    minLength = IntType(min_value=0)
    pattern = RegularExpressionType()

    # Validation keywords for arrays
    items = PolyModelType(
        [ModelType("Schema"), ListType(ModelType("Schema"))],
        claim_function=_items_claim_function,
    )
    maxItems = IntType(min_value=0)
    minItems = IntType(min_value=0)
    uniqueItems = BooleanType()

    # Validation keywords for objects
    maxProperties = IntType(min_value=0)
    minProperties = IntType(min_value=0)
    required = ListType(StringType(), min_size=1)
    properties = DictType(
        ModelType("Schema"),
    )
    additionalProperties = PolyModelType(
        [bool, ModelType("Schema")],
        claim_function=_additionalProperties_claim_function,
    )
    discriminator = StringType()  # Adds support for polymorphism. The discriminator is the schema property name that is used to differentiate between other schema that inherit this schema. The property name used MUST be defined at this schema and it MUST be in the required property list. When used, the value MUST be the name of this schema or any schema that inherits it.

    # Validation keywords for any instance type
    enum = ListType(BaseType())
    x_ms_enum = XmsEnumType()
    type = StringType(
        choices=["array", "boolean", "integer", "number", "null", "object", "string"],  # https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04#section-3.5
    )
    allOf = ListType(
        ModelType("Schema"),
    )

    readOnly = BooleanType()  # Relevant only for Schema "properties" definitions. Declares the property as "read only". This means that it MAY be sent as part of a response but MUST NOT be sent as part of the request. Properties marked as readOnly being true SHOULD NOT be in the required list of the defined schema. Default value is false.
    xml = ModelType(XML)  # This MAY be used only on properties schemas. It has no effect on root schemas. Adds Additional metadata to describe the XML representation format of this property.
    externalDocs = ModelType(ExternalDocumentation)  # Additional external documentation for this schema.
    example = BaseType()  # A free-form property to include an example of an instance for this schema.

    x_ms_client_name = XmsClientNameType()
    x_ms_external = XmsExternal()
    x_ms_discriminator_value = XmsDiscriminatorValue()
    x_ms_client_flatten = XmsClientFlatten()
    x_ms_mutability = XmsMutabilityType()
    x_ms_client_default = XmsClientDefaultType()

    x_ms_azure_resource = XmsAzureResourceType() # indicates that the Definition Schema Object is a resource as defined by the Resource Manager API

    x_ms_secret = XmsSecretType()

    x_nullable = XNullableType()  # when true, specifies that null is a valid value for the associated schema

    # specific properties
    _x_accessibility = XAccessibilityType()   # only used in ContainerRegistry Data plane
    _x_az_search_deprecated = XAzSearchDeprecatedType()  # only used in Search Data Plane
    _x_sf_clientlib = XSfClientLibType()  # only used in ServiceFabric Data Plane and ServiceFabricManagedClusters Mgmt Plane
    _x_apim_code_nillable = XApimCodeNillableType()  # only used in ApiManagement Mgmt Plane
    _x_comment = XCommentType()  # Only used in IoTCenter Mgmt Plane
    _x_abstract = XAbstractType()  # Only used in Logic Mgmt Plane and Web Mgmt Plane

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_instance = None
        self.disc_parent = None
        self.disc_children = {}

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        if self.ref is not None:
            self.ref_instance, instance_traces = swagger_loader.load_ref(self.ref, *self.traces, 'ref')
            if isinstance(self.ref_instance, Linkable):
                self.ref_instance.link(swagger_loader, *instance_traces)

        if self.items is not None:
            if isinstance(self.items, list):
                for idx, item in enumerate(self.items):
                    item.link(swagger_loader, *self.traces, 'items', idx)
            else:
                self.items.link(swagger_loader, *self.traces, 'items')

        if self.properties is not None:
            for key, prop in self.properties.items():
                prop.link(swagger_loader, *self.traces, 'properties', key)

        if self.additionalProperties is not None and isinstance(self.additionalProperties, Schema):
            self.additionalProperties.link(swagger_loader, *self.traces, 'additionalProperties')

        if self.allOf is not None:
            for idx, item in enumerate(self.allOf):
                item.link(swagger_loader, *self.traces, 'allOf', idx)

        self._link_disc()

    def _link_disc(self):
        if self.allOf is None:
            return
        for item in self.allOf:
            if item.disc_instance is not None:
                if self.disc_parent is not None:
                    raise ValueError("Multiple discriminator parents exists.")
                self.disc_parent = item.disc_instance

                if self.x_ms_discriminator_value is not None:
                    disc_value = self.x_ms_discriminator_value
                elif len(self.traces) > 2 and self.traces[-2] == 'definitions':
                    disc_value = self.traces[-1]   # use the definition name as discriminator value
                else:
                    raise ValueError("DiscriminatorValue is empty.")
                if disc_value in self.disc_parent.disc_children:
                    raise ValueError(f"Duplicated discriminator children for value '{disc_value}'")
                self.disc_parent.disc_children[disc_value] = self

    @property
    def disc_instance(self):
        assert self.is_linked()
        if self.discriminator is not None:
            return self
        elif self.ref_instance is not None:
            return self.ref_instance.disc_instance
        return None

