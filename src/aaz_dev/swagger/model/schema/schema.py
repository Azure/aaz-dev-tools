import logging

from schematics.models import Model
from schematics.types import ListType, BaseType, DictType, ModelType, BooleanType, FloatType, IntType, StringType, \
    PolyModelType

from command.model.configuration import CMDSchemaDefault, \
    CMDStringSchema, CMDResourceIdSchema, CMDResourceIdFormat, \
    CMDResourceLocationSchema, \
    CMDObjectSchemaBase, CMDObjectSchemaDiscriminator, CMDObjectSchemaAdditionalProperties, \
    CMDArraySchemaBase, CMDObjectSchema, CMDIdentityObjectSchema, CMDIdentityObjectSchemaBase, CMDClsSchemaBase
from command.model.configuration import CMDSchemaEnum, CMDSchemaEnumItem, CMDSchema, CMDSchemaBase
from swagger.utils import exceptions
from .external_documentation import ExternalDocumentation
from .fields import DataTypeFormatEnum, RegularExpressionField, XmsClientNameField, XmsExternalField, \
    XmsDiscriminatorValueField, XmsClientFlattenField, XmsMutabilityField, XmsClientDefaultField, XNullableField, \
    XmsAzureResourceField, MutabilityEnum, XmsArmIdDetailsField
from .fields import XmsSecretField, XAccessibilityField, XAzSearchDeprecatedField, XSfClientLibField, \
    XApimCodeNillableField, XCommentField, XAbstractField, XADLNameField, XCadlNameField, XTypespecNameField
from .reference import ReferenceField, Linkable
from .x_ms_enum import XmsEnumField
from .xml import XML

logger = logging.getLogger('backend')


def schema_and_reference_schema_claim_function(_, data):
    if isinstance(data, dict):
        if ReferenceSchema._claim_polymorphic(data=data):
            return ReferenceSchema
        else:
            return Schema
    else:
        return None


def _additional_properties_claim_function(_, data):
    if isinstance(data, bool):
        return bool
    elif isinstance(data, dict):
        return schema_and_reference_schema_claim_function(_, data)
    else:
        return None


def _items_claim_function(_, data):
    if isinstance(data, dict):
        return schema_and_reference_schema_claim_function(_, data)
    elif isinstance(data, list):
        if data and ReferenceSchema._claim_polymorphic(data=data[0]):
            return ListType(ModelType(ReferenceSchema))
        else:
            return ListType(ModelType(Schema))
    else:
        return None


class ReferenceSchema(Model, Linkable):
    ref = ReferenceField(required=True)
    description = StringType()
    title = StringType()
    read_only = BooleanType(
        serialized_name="readOnly",
        deserialize_from="readOnly"
    )  # Relevant only for Schema "properties" definitions. Declares the property as "read only". This means that it MAY be sent as part of a response but MUST NOT be sent as part of the request. Properties marked as readOnly being true SHOULD NOT be in the required list of the defined schema. Default value is false.
    type = StringType(
        choices=["array", "boolean", "integer", "number", "object", "string"],
        # https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04#section-3.5
    )   #

    x_ms_client_name = XmsClientNameField()  # TODO: used for deserialize name

    x_ms_client_flatten = XmsClientFlattenField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_instance = None
        self.x_ms_azure_resource = False

    def get_disc_parent(self):
        return self.ref_instance.get_disc_parent()

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        self.ref_instance, instance_traces = swagger_loader.load_ref(self.ref, *self.traces, 'ref')
        if isinstance(self.ref_instance, Linkable):
            self.ref_instance.link(swagger_loader, *instance_traces)
        if self.ref_instance.x_ms_azure_resource:
            self.x_ms_azure_resource = True

    def to_cmd(self, builder, support_cls_schema=False, **kwargs):
        model = builder.register_cls_definition(self, support_cls_schema=support_cls_schema, **kwargs)
        if isinstance(model, CMDSchema):
            builder.setup_description(model, self)
            if self.x_ms_client_flatten:
                model.client_flatten = True
        return model

    @classmethod
    def _claim_polymorphic(cls, data):
        return isinstance(data, dict) and "$ref" in data and len(data) <= 7 and \
               set(data.keys()).issubset({"$ref", "description", "title", "readOnly", "type", "x-ms-client-name", "x-ms-client-flatten"})


class Schema(Model, Linkable):
    """
    The Schema Object allows the definition of input and output data types. These types can be objects, but also primitives and arrays. This object is based on the JSON Schema Specification Draft 4 and uses a predefined subset of it. On top of this subset, there are extensions provided by this specification to allow for more complete documentation.
    Further information about the properties can be found in JSON Schema Core and JSON Schema Validation. Unless stated otherwise, the property definitions follow the JSON Schema specification as referenced here.
    """

    ref = ReferenceField()
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
    pattern = RegularExpressionField()

    # Validation keywords for arrays
    items = PolyModelType(
        [
            ModelType("Schema"),
            ModelType(ReferenceSchema),
            ListType(ModelType("Schema")),
            ListType(ModelType(ReferenceSchema))
        ],
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
        PolyModelType(
            [
                ModelType("Schema"),
                ModelType(ReferenceSchema)
            ],
            claim_function=schema_and_reference_schema_claim_function,
        ),
    )
    additional_properties = PolyModelType(
        [bool, ModelType("Schema"), ModelType(ReferenceSchema)],
        claim_function=_additional_properties_claim_function,
        serialized_name="additionalProperties",
        deserialize_from="additionalProperties"
    )
    discriminator = StringType()  # Adds support for polymorphism. The discriminator is the schema property name that is used to differentiate between other schema that inherit this schema. The property name used MUST be defined at this schema and it MUST be in the required property list. When used, the value MUST be the name of this schema or any schema that inherits it.

    # Validation keywords for any instance type
    enum = ListType(BaseType())
    x_ms_enum = XmsEnumField()
    type = StringType(
        choices=["array", "boolean", "integer", "number", "object", "string"],
        # https://datatracker.ietf.org/doc/html/draft-zyp-json-schema-04#section-3.5
    )
    all_of = ListType(
        PolyModelType(
            [ModelType("Schema"), ModelType(ReferenceSchema)],
            claim_function=schema_and_reference_schema_claim_function,
        ),
        serialized_name="allOf",
        deserialize_from="allOf"
    )

    read_only = BooleanType(
        serialized_name="readOnly",
        deserialize_from="readOnly"
    )  # Relevant only for Schema "properties" definitions. Declares the property as "read only". This means that it MAY be sent as part of a response but MUST NOT be sent as part of the request. Properties marked as readOnly being true SHOULD NOT be in the required list of the defined schema. Default value is false.
    xml = ModelType(XML)  # TODO: # This MAY be used only on properties schemas. It has no effect on root schemas. Adds Additional metadata to describe the XML representation format of this property.
    external_docs = ModelType(
        ExternalDocumentation,
        serialized_name="externalDocs",
        deserialize_from="externalDocs"
    )  # TODO: # Additional external documentation for this schema.
    example = BaseType()  # TODO: # A free-form property to include an example of an instance for this schema.

    x_ms_client_name = XmsClientNameField()  # TODO: used for deserialized name
    x_ms_external = XmsExternalField()  # TODO:
    x_ms_discriminator_value = XmsDiscriminatorValueField()
    x_ms_client_flatten = XmsClientFlattenField()
    x_ms_mutability = XmsMutabilityField()
    x_ms_client_default = XmsClientDefaultField()
    x_ms_arm_id_details = XmsArmIdDetailsField()  # TODO: Add support for it, can be used for resource id template

    x_ms_azure_resource = XmsAzureResourceField()

    x_ms_secret = XmsSecretField()

    x_nullable = XNullableField()  # when true, specifies that null is a valid value for the associated schema

    x_ms_identifiers = ListType(StringType(), serialized_name="x-ms-identifiers", deserialize_from="x-ms-identifiers")

    # specific properties, will not support
    _x_accessibility = XAccessibilityField()  # only used in ContainerRegistry Data plane
    _x_az_search_deprecated = XAzSearchDeprecatedField()  # only used in Search Data Plane
    _x_sf_clientlib = XSfClientLibField()  # only used in ServiceFabric Data Plane and ServiceFabricManagedClusters Mgmt Plane
    _x_apim_code_nillable = XApimCodeNillableField()  # only used in ApiManagement Mgmt Plane
    _x_comment = XCommentField()  # Only used in IoTCenter Mgmt Plane
    _x_abstract = XAbstractField()  # Only used in Logic Mgmt Plane and Web Mgmt Plane
    _x_adl_name = XADLNameField()  # Only used in FluidRelay Mgmt Plane
    _x_enum_Names = ListType(BaseType(), serialized_name="x-enumNames", deserialize_from="x-enumNames")  # Only used in Marketplane Catalog Data Plane
    _x_enum_flags = BooleanType(serialized_name="x-enumFlags", deserialize_from="x-enumFlags")  # Only used in Marketplane Catalog Data Plane
    _x_dictionary_key = ModelType(ReferenceSchema, serialized_name="x-dictionaryKey", deserialize_from="x-dictionaryKey")  # Only used in Marketplane Catalog Data Plane

    _x_cadl_name = XCadlNameField()  # Cadl field name
    _x_typespec_name = XTypespecNameField()  # Typespec field name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_instance = None
        self.disc_parent = None
        self.disc_children = {}

        self.resource_id_templates = set()  # valid when there's only one template

    def get_disc_parent(self):
        assert self.is_linked()
        if self.disc_parent is not None:
            return self.disc_parent
        elif self.discriminator is not None:
            if not self.properties or self.discriminator not in self.properties:
                raise exceptions.InvalidSwaggerValueError(
                    msg="Discriminator property isn't in properties",
                    key=self.traces,
                    value=self.discriminator
                )
            return self
        elif self.ref_instance is not None:
            return self.ref_instance.get_disc_parent()
        return None

    def link(self, swagger_loader, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces)

        if self.ref is not None:
            self.ref_instance, instance_traces = swagger_loader.load_ref(self.ref, *self.traces, 'ref')
            if isinstance(self.ref_instance, Linkable):
                self.ref_instance.link(swagger_loader, *instance_traces)
            if self.ref_instance.x_ms_azure_resource:
                self.x_ms_azure_resource = True

        if self.items is not None:
            if isinstance(self.items, list):
                for idx, item in enumerate(self.items):
                    item.link(swagger_loader, *self.traces, 'items', idx)
            else:
                self.items.link(swagger_loader, *self.traces, 'items')

        if self.properties is not None:
            for key, prop in self.properties.items():
                prop.link(swagger_loader, *self.traces, 'properties', key)

        if self.additional_properties is not None and isinstance(self.additional_properties, (Schema, ReferenceSchema)):
            self.additional_properties.link(swagger_loader, *self.traces, 'additionalProperties')

        if self.all_of is not None:
            for idx, item in enumerate(self.all_of):
                item.link(swagger_loader, *self.traces, 'allOf', idx)
                if item.x_ms_azure_resource:
                    self.x_ms_azure_resource = True

        self._link_disc()
        if self.type and self.type != "object" and self.all_of:
            if len(self.all_of) > 1:
                print(f"\tMultiAllOf for {self.type}: {traces}")
            else:
                print(f"\tAllOf for {self.type}: {traces}")

    def _link_disc(self):
        if self.all_of is None:
            return
        for item in self.all_of:
            disc_parent = item.get_disc_parent()
            if disc_parent is not None:
                if self.disc_parent is not None:
                    raise exceptions.InvalidSwaggerValueError(
                        msg="Multiple discriminator parents exists.",
                        key=self.traces, value=None
                    )
                self.disc_parent = disc_parent

                if self.x_ms_discriminator_value is not None:
                    disc_value = self.x_ms_discriminator_value
                elif len(self.traces) > 2 and self.traces[-2] == 'definitions':
                    disc_value = self.traces[-1]  # use the definition name as discriminator value
                else:
                    # Discriminator value is empty. Its not a discriminator
                    logger.warning(f"Discriminator value is empty. : {self.traces}")
                    continue
                if disc_value in self.disc_parent.disc_children:
                    raise exceptions.InvalidSwaggerValueError(
                        msg=f"Duplicated discriminator children for same value",
                        key=self.traces, value=disc_value
                    )
                self.disc_parent.disc_children[disc_value] = self

    def to_cmd(self, builder, **kwargs):
        if self.ref_instance is not None:
            model = builder(self.ref_instance, support_cls_schema=True)
        else:
            model = builder.build_schema(self)

        if isinstance(model, CMDArraySchemaBase):
            if self.all_of is not None:
                # inherit from allOf
                if len(self.all_of) > 1:
                    raise exceptions.InvalidSwaggerValueError(
                        msg=f"Multiple allOf is not supported for `{model.type}` type schema",
                        key=self.traces, value=None
                    )
                model = builder(self.all_of[0], support_cls_schema=True)

            if self.items:
                assert isinstance(self.items, (Schema, ReferenceSchema))
                v = builder(self.items, in_base=True, support_cls_schema=True)
                assert isinstance(v, CMDSchemaBase)
                model.item = v

                # freeze because array item is frozen
                if not model.frozen and model.item.frozen:
                    model.frozen = True

            if self.x_ms_identifiers:
                model.identifiers = []
                for identifier in self.x_ms_identifiers:
                    model.identifiers.append(identifier)

        elif isinstance(model, CMDObjectSchemaBase):
            # props
            prop_dict = {}
            if model.props is not None:
                # inherit from $ref
                for prop in model.props:
                    prop_dict[prop.name] = prop

            if self.all_of:
                # inherit from allOf
                for item in self.all_of:
                    disc_parent = item.get_disc_parent()
                    if disc_parent is not None and builder.find_traces(item.ref_instance.traces):
                        # discriminator parent already in trace, break reference loop
                        continue
                    v = builder(item, in_base=True, support_cls_schema=False)
                    assert isinstance(v, CMDObjectSchemaBase)
                    if v.fmt:
                        model.fmt = v.fmt

                    if v.props:
                        for p in v.props:
                            prop_dict[p.name] = p

                    if disc_parent is not None and not builder.find_traces(disc_parent.traces):
                        # directly use child definition instead of polymorphism.
                        # So the value for discriminator property is const.
                        is_children = False
                        disc_prop = disc_parent.discriminator
                        for disc_value, disc_child in disc_parent.disc_children.items():
                            if disc_child == self:
                                prop_dict[disc_prop].const = True
                                prop_dict[disc_prop].default = CMDSchemaDefault()
                                prop_dict[disc_prop].default.value = disc_value
                                is_children = True
                                break
                        if not is_children and len(self.all_of) == 1 and \
                                model.props is None and model.additional_props is None:
                            # inherit from allOf as reference only
                            model.discriminators = v.discriminators

                    if v.additional_props:
                        model.additional_props = v.additional_props

            if self.properties:
                for name, p in self.properties.items():
                    assert isinstance(p, (Schema, ReferenceSchema))
                    v = builder(p, in_base=False, support_cls_schema=True)
                    if v is None:
                        # ignore by mutability
                        continue
                    assert isinstance(v, CMDSchema)
                    v.name = name
                    prop_dict[name] = v

            if self.required:
                for name in self.required:
                    if name in prop_dict:
                        # because required property will not be included in a cls definition,
                        # so it's fine to update it in parent level when prop_dict[name] is a cls definition.
                        prop_dict[name].required = True
                        if MutabilityEnum.Create == builder.mutability:
                            # for create operation
                            # when a property is required, it's frozen status must be consisted with the defined schema.
                            # This can help to for empty object schema.
                            prop_dict[name].frozen = builder.frozen

            # discriminators
            if self.disc_children:
                discriminators = []
                assert self.discriminator is not None
                disc_prop = self.discriminator
                for disc_value, disc_child in self.disc_children.items():
                    if builder.find_traces(disc_child.traces):
                        # discriminator child already in trace, break reference loop
                        continue
                    disc = CMDObjectSchemaDiscriminator()
                    disc.property = disc_prop
                    disc.value = disc_value

                    if disc_prop not in prop_dict:
                        raise exceptions.InvalidSwaggerValueError(
                            msg="Discriminator Property don't exist",
                            key=self.traces,
                            value=[disc_prop, builder.mutability]
                        )
                    if not hasattr(prop_dict[disc_prop], "enum"):
                        raise exceptions.InvalidSwaggerValueError(
                            msg="Invalid Discriminator Property type",
                            key=self.traces,
                            value=[disc_prop, prop_dict[disc_prop].type]
                        )

                    # make sure discriminator value is an enum item of discriminator property
                    if prop_dict[disc_prop].enum is None:
                        prop_dict[disc_prop].enum = CMDSchemaEnum()
                        prop_dict[disc_prop].enum.items = []
                    exist_disc_value = False
                    for enum_item in prop_dict[disc_prop].enum.items:
                        if enum_item.value == disc_value:
                            exist_disc_value = True
                    if not exist_disc_value:
                        enum_item = CMDSchemaEnumItem()
                        enum_item.value = disc_value
                        prop_dict[disc_prop].enum.items.append(enum_item)

                    v = builder(disc_child, in_base=True, support_cls_schema=False)
                    assert isinstance(v, CMDObjectSchemaBase)
                    if v.frozen and prop_dict[disc_prop].frozen:
                        disc.frozen = True
                    if v.props:
                        disc.props = [prop for prop in v.props if prop.name not in prop_dict]
                    if v.discriminators:
                        disc.discriminators = v.discriminators

                    discriminators.append(disc)
                if discriminators:
                    model.discriminators = discriminators

            # convert special properties when self is an azure resource
            if self.x_ms_azure_resource and prop_dict:
                if 'id' in prop_dict and self.resource_id_templates and not prop_dict['id'].frozen:
                    id_prop = prop_dict['id']
                    if not isinstance(id_prop, CMDResourceIdSchema):
                        try:
                            assert isinstance(id_prop, CMDStringSchema)
                        except:
                            raise
                        raw_data = id_prop.to_native()
                        prop_dict['id'] = id_prop = CMDResourceIdSchema(raw_data=raw_data)
                    if len(self.resource_id_templates) == 1:
                        id_prop.fmt = CMDResourceIdFormat()
                        id_prop.fmt.template = [*self.resource_id_templates][0]
                    else:
                        err = exceptions.InvalidSwaggerValueError(
                            msg="Multi resource id templates error",
                            key=self.traces,
                            value=self.resource_id_templates
                        )
                        logger.warning(err)
                if 'location' in prop_dict and not prop_dict['location'].frozen:
                    location_prop = prop_dict['location']
                    if not isinstance(location_prop, CMDResourceLocationSchema):
                        assert isinstance(location_prop, CMDStringSchema)
                        raw_data = location_prop.to_native()
                        prop_dict['location'] = CMDResourceLocationSchema(raw_data=raw_data)

            if prop_dict:
                if "userAssignedIdentities" in prop_dict and "type" in prop_dict:
                    if isinstance(model, CMDObjectSchema):
                        # Transfer to IdentityObjectSchema
                        model = CMDIdentityObjectSchema(model.to_native())
                    elif isinstance(model, CMDObjectSchemaBase):
                        # Transfer to IdentityObjectSchemaBase
                        model = CMDIdentityObjectSchemaBase(model.to_native())
                    else:
                        raise NotImplementedError()
                model.props = []
                for prop in prop_dict.values():
                    model.props.append(prop)

            # additional properties
            if self.additional_properties:
                if isinstance(self.additional_properties, (Schema, ReferenceSchema)):
                    v = builder(self.additional_properties, in_base=True, support_cls_schema=True)
                    if v is not None:
                        assert isinstance(v, CMDSchemaBase)
                        model.additional_props = CMDObjectSchemaAdditionalProperties()
                        model.additional_props.item = v
                        # item is required, it's frozen status must be consisted with the defined schema.
                        # This can help to for empty object.
                        model.additional_props.item.frozen = builder.frozen
                elif isinstance(self.additional_properties, bool) and self.additional_properties is True:
                    # Free-Form Objects
                    # additionalProperties: true
                    model.additional_props = CMDObjectSchemaAdditionalProperties()
                    model.additional_props.any_type = True

            if model.additional_props:
                if builder.read_only:
                    model.additional_props.read_only = builder.read_only
                if builder.frozen:
                    model.additional_props.frozen = builder.frozen

            if self.x_ms_client_flatten and isinstance(model, CMDObjectSchema):
                # client flatten can only be supported for CMDObjectSchema install of CMDObjectSchemaBase.
                # Because CMDObjectSchemaBase will not link with argument
                model.client_flatten = True

            # when all additional_props and props and discriminators of model is frozen then this model is frozen
            if not model.frozen and (model.additional_props or model.props or model.discriminators):  # an empty object is not included
                need_frozen = True
                if model.additional_props:
                    if not model.additional_props.frozen:
                        need_frozen = False
                if model.props:
                    for prop in model.props:
                        if not prop.frozen:
                            need_frozen = False
                            break
                if model.discriminators:
                    for disc in model.discriminators:
                        if not disc.frozen:
                            need_frozen = False
                            break
                # Note: model will always frozen when an unempty object without any props, additional_props or discriminators,
                # If this property is required by parent schema, it will be updated in parent.
                model.frozen = need_frozen

        else:
            if self.all_of is not None:
                # inherit from allOf
                if len(self.all_of) > 1:
                    raise exceptions.InvalidSwaggerValueError(
                        msg=f"Multiple allOf is not supported for `{model.type}` type schema",
                        key=self.traces, value=None
                    )
                model = builder(self.all_of[0], support_cls_schema=True)

        builder.setup_fmt(model, self)
        builder.setup_enum(model, self)
        builder.setup_default(model, self)
        builder.setup_nullable(model, self)

        if isinstance(model, CMDSchema):
            builder.setup_description(model, self)
            builder.setup_secret(model, self)

        return model
