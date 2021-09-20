from schematics.models import Model
from schematics.types import ListType, BaseType, DictType, ModelType, BooleanType, FloatType, IntType, StringType, PolyModelType
from .reference import ReferenceType, Linkable
from .types import DataTypeFormatEnum, RegularExpressionType, XmsClientNameType, XmsExternal, XmsDiscriminatorValue, XmsClientFlatten, XmsMutabilityType, XmsClientDefaultType, XNullableType, XmsAzureResourceType
from .xml import XML
from .external_documentation import ExternalDocumentation
from .x_ms_enum import XmsEnumType
from .types import XmsSecretType, XAccessibilityType, XAzSearchDeprecatedType, XSfClientLibType, XApimCodeNillableType, XCommentType, XAbstractType, XClientNameType
from swagger.utils.exceptions import InvalidSwaggerValueError


def _additional_properties_claim_function(_, data):
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
    multiple_of = FloatType(
        min_value=0,
        serialized_name="multipleOf",
        deserialize_from="multipleOf"
    )
    maximum = FloatType()
    exclusive_maximum = BooleanType(
        serialized_name="exclusiveMaximum",
        deserialize_from="exclusiveMaximum",
    )
    minimum = FloatType()
    exclusive_minimum = BooleanType(
        serialized_name="exclusiveMinimum",
        deserialize_from="exclusiveMinimum"
    )

    # Validation keywords for strings
    max_length = IntType(
        min_value=0,
        serialized_name="maxLength",
        deserialize_from="maxLength"
    )
    min_length = IntType(
        min_value=0,
        serialized_name="minLength",
        deserialize_from="minLength"
    )
    pattern = RegularExpressionType()

    # Validation keywords for arrays
    items = PolyModelType(
        [ModelType("Schema"), ListType(ModelType("Schema"))],
        claim_function=_items_claim_function,
    )
    max_items = IntType(
        min_value=0,
        serialized_name="maxItems",
        deserialize_from="maxItems"
    )
    min_items = IntType(
        min_value=0,
        serialized_name="minItems",
        deserialize_from="minItems"
    )
    unique_items = BooleanType(
        serialized_name="uniqueItems",
        deserialize_from="uniqueItems"
    )

    # Validation keywords for objects
    max_properties = IntType(
        min_value=0,
        serialized_name="maxProperties",
        deserialize_from="maxProperties"
    )
    min_properties = IntType(
        min_value=0,
        serialized_name="minProperties",
        deserialize_from="minProperties"
    )
    required = ListType(StringType(), min_size=1)
    properties = DictType(
        ModelType("Schema"),
    )
    additional_properties = PolyModelType(
        [bool, ModelType("Schema")],
        claim_function=_additional_properties_claim_function,
        serialized_name="additionalProperties",
        deserialize_from="additionalProperties"
    )
    discriminator = StringType()  # Adds support for polymorphism. The discriminator is the schema property name that is used to differentiate between other schema that inherit this schema. The property name used MUST be defined at this schema and it MUST be in the required property list. When used, the value MUST be the name of this schema or any schema that inherits it.

    # Validation keywords for any instance type
    enum = ListType(BaseType())
    x_ms_enum = XmsEnumType()
    type = StringType(
        choices=["array", "boolean", "integer", "number", "object", "string"],  # https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04#section-3.5
    )
    all_of = ListType(
        ModelType("Schema"),
        serialized_name="allOf",
        deserialize_from="allOf"
    )

    read_only = BooleanType(
        serialized_name="readOnly",
        deserialize_from="readOnly"
    )  # Relevant only for Schema "properties" definitions. Declares the property as "read only". This means that it MAY be sent as part of a response but MUST NOT be sent as part of the request. Properties marked as readOnly being true SHOULD NOT be in the required list of the defined schema. Default value is false.
    xml = ModelType(XML)  # This MAY be used only on properties schemas. It has no effect on root schemas. Adds Additional metadata to describe the XML representation format of this property.
    external_docs = ModelType(
        ExternalDocumentation,
        serialized_name="externalDocs",
        deserialize_from="externalDocs"
    )  # Additional external documentation for this schema.
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

        if self.additional_properties is not None and isinstance(self.additional_properties, Schema):
            self.additional_properties.link(swagger_loader, *self.traces, 'additionalProperties')

        if self.all_of is not None:
            for idx, item in enumerate(self.all_of):
                item.link(swagger_loader, *self.traces, 'allOf', idx)

        self._link_disc()

    def _link_disc(self):
        if self.all_of is None:
            return
        for item in self.all_of:
            if item.disc_instance is not None:
                if self.disc_parent is not None:
                    raise InvalidSwaggerValueError(
                        msg="Multiple discriminator parents exists.",
                        key=self.traces, value=None
                    )
                self.disc_parent = item.disc_instance

                if self.x_ms_discriminator_value is not None:
                    disc_value = self.x_ms_discriminator_value
                elif len(self.traces) > 2 and self.traces[-2] == 'definitions':
                    disc_value = self.traces[-1]   # use the definition name as discriminator value
                else:
                    raise InvalidSwaggerValueError(
                        msg="DiscriminatorValue is empty.",
                        key=self.traces, value=None
                    )
                if disc_value in self.disc_parent.disc_children:
                    raise InvalidSwaggerValueError(
                        msg=f"Duplicated discriminator children for same value",
                        key=self.traces, value=disc_value
                    )
                self.disc_parent.disc_children[disc_value] = self

    @property
    def disc_instance(self):
        assert self.is_linked()
        if self.discriminator is not None:
            return self
        elif self.ref_instance is not None:
            return self.ref_instance.disc_instance
        return None

