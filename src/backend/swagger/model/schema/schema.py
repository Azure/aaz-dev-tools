from schematics.models import Model
from schematics.types import ListType, BaseType, DictType, ModelType, BooleanType, FloatType, IntType, StringType, PolyModelType
from .reference import ReferenceField, Linkable
from .fields import DataTypeFormatEnum, RegularExpressionField, XmsClientNameField, XmsExternalField, XmsDiscriminatorValueField, XmsClientFlattenField, XmsMutabilityField, XmsClientDefaultField, XNullableField, XmsAzureResourceField
from .xml import XML
from .external_documentation import ExternalDocumentation
from .x_ms_enum import XmsEnumField
from .fields import XmsSecretField, XAccessibilityField, XAzSearchDeprecatedField, XSfClientLibField, XApimCodeNillableField, XCommentField, XAbstractField, XADLNameField, MutabilityEnum
from swagger.utils import exceptions

from command.model.configuration import CMDIntegerFormat, CMDStringFormat, CMDFloatFormat, CMDArrayFormat, CMDObjectFormat, CMDSchemaEnum, CMDSchemaEnumItem, CMDSchema, CMDSchemaBase

from command.model.configuration import CMDSchemaDefault,\
    CMDStringSchema, CMDStringSchemaBase, \
    CMDByteSchema, CMDByteSchemaBase, \
    CMDBinarySchema, CMDBinarySchemaBase, \
    CMDDateSchema, CMDDateSchemaBase, \
    CMDDateTimeSchema, CMDDateTimeSchemaBase, \
    CMDPasswordSchema, CMDPasswordSchemaBase, \
    CMDDurationSchema, CMDDurationSchemaBase, \
    CMDUuidSchema, CMDUuidSchemaBase, \
    CMDResourceIdSchema, CMDResourceIdFormat, \
    CMDResourceLocationSchema, \
    CMDIntegerSchema, CMDIntegerSchemaBase, \
    CMDInteger32Schema, CMDInteger32SchemaBase, \
    CMDInteger64Schema, CMDInteger64SchemaBase, \
    CMDBooleanSchema, CMDBooleanSchemaBase, \
    CMDFloatSchema, CMDFloatSchemaBase, \
    CMDFloat32Schema, CMDFloat32SchemaBase, \
    CMDFloat64Schema, CMDFloat64SchemaBase, \
    CMDObjectSchema, CMDObjectSchemaBase, CMDObjectSchemaDiscriminator, CMDObjectSchemaAdditionalProperties, \
    CMDArraySchema, CMDArraySchemaBase, \
    CMDClsSchema, CMDClsSchemaBase

import logging

logger = logging.getLogger('backend')


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
    x_ms_enum = XmsEnumField()
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
    xml = ModelType(XML)  # TODO: # This MAY be used only on properties schemas. It has no effect on root schemas. Adds Additional metadata to describe the XML representation format of this property.
    external_docs = ModelType(
        ExternalDocumentation,
        serialized_name="externalDocs",
        deserialize_from="externalDocs"
    )  # TODO: # Additional external documentation for this schema.
    example = BaseType()  # TODO: # A free-form property to include an example of an instance for this schema.

    x_ms_client_name = XmsClientNameField()  # TODO:
    x_ms_external = XmsExternalField()  # TODO:
    x_ms_discriminator_value = XmsDiscriminatorValueField()
    x_ms_client_flatten = XmsClientFlattenField()
    x_ms_mutability = XmsMutabilityField()
    x_ms_client_default = XmsClientDefaultField()

    x_ms_azure_resource = XmsAzureResourceField()

    x_ms_secret = XmsSecretField()  # TODO:

    x_nullable = XNullableField()  # TODO: # when true, specifies that null is a valid value for the associated schema

    # specific properties, will not support
    _x_accessibility = XAccessibilityField()   # only used in ContainerRegistry Data plane
    _x_az_search_deprecated = XAzSearchDeprecatedField()  # only used in Search Data Plane
    _x_sf_clientlib = XSfClientLibField()  # only used in ServiceFabric Data Plane and ServiceFabricManagedClusters Mgmt Plane
    _x_apim_code_nillable = XApimCodeNillableField()  # only used in ApiManagement Mgmt Plane
    _x_comment = XCommentField()  # Only used in IoTCenter Mgmt Plane
    _x_abstract = XAbstractField()  # Only used in Logic Mgmt Plane and Web Mgmt Plane
    _x_adl_name = XADLNameField()  # Only used in FluidRelay Mgmt Plane

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

        if self.additional_properties is not None and isinstance(self.additional_properties, Schema):
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
                    disc_value = self.traces[-1]   # use the definition name as discriminator value
                else:
                    raise exceptions.InvalidSwaggerValueError(
                        msg="Discriminator value is empty.",
                        key=self.traces, value=None
                    )
                if disc_value in self.disc_parent.disc_children:
                    raise exceptions.InvalidSwaggerValueError(
                        msg=f"Duplicated discriminator children for same value",
                        key=self.traces, value=disc_value
                    )
                self.disc_parent.disc_children[disc_value] = self

    def _build_model(self, in_base, read_only, frozen):
        if self.type == "string":
            if self.format is None:
                if in_base:
                    model = CMDStringSchemaBase()
                else:
                    model = CMDStringSchema()
            elif self.format == "byte":
                if in_base:
                    model = CMDByteSchemaBase()
                else:
                    model = CMDByteSchema()
            elif self.format == "binary":
                if in_base:
                    model = CMDBinarySchemaBase()
                else:
                    model = CMDBinarySchema()
            elif self.format == "date":
                if in_base:
                    model = CMDDateSchemaBase()
                else:
                    model = CMDDateSchema()
            elif self.format == "date-time":
                if in_base:
                    model = CMDDateTimeSchemaBase()
                else:
                    model = CMDDateTimeSchema()
            elif self.format == "password":
                if in_base:
                    model = CMDPasswordSchemaBase()
                else:
                    model = CMDPasswordSchema()
            elif self.format == "duration":
                if in_base:
                    model = CMDDurationSchemaBase()
                else:
                    model = CMDDurationSchema()
            elif self.format == "uuid":
                if in_base:
                    model = CMDUuidSchemaBase()
                else:
                    model = CMDUuidSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=self.traces, value=[self.type, self.format])
        elif self.type == "integer":
            if self.format is None:
                if in_base:
                    model = CMDIntegerSchemaBase()
                else:
                    model = CMDIntegerSchema()
            elif self.format == "int32":
                if in_base:
                    model = CMDInteger32SchemaBase()
                else:
                    model = CMDInteger32Schema()
            elif self.format == "int64":
                if in_base:
                    model = CMDInteger64SchemaBase()
                else:
                    model = CMDInteger64Schema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=self.traces, value=[self.type, self.format])
        elif self.type == "boolean":
            if self.format is None:
                if in_base:
                    model = CMDBooleanSchemaBase()
                else:
                    model = CMDBooleanSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=self.traces, value=[self.type, self.format])
        elif self.type == "number":
            if self.format is None:
                if in_base:
                    model = CMDFloatSchemaBase()
                else:
                    model = CMDFloatSchema()
            elif self.format == "float":
                if in_base:
                    model = CMDFloat32SchemaBase()
                else:
                    model = CMDFloat32Schema()
            elif self.format == "double":
                if in_base:
                    model = CMDFloat64SchemaBase()
                else:
                    model = CMDFloat64Schema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=self.traces, value=[self.type, self.format])
        elif self.type == "array":
            if self.format is None:
                if in_base:
                    model = CMDArraySchemaBase()
                else:
                    model = CMDArraySchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=self.traces, value=[self.type, self.format])
        elif self.type == "object" or self.properties or self.additional_properties:
            if self.format is None:
                if in_base:
                    model = CMDObjectSchemaBase()
                else:
                    model = CMDObjectSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=self.traces, value=[self.type, self.format])
        elif self.all_of is not None:
            model = self.all_of[0]._build_model(in_base=in_base, read_only=read_only, frozen=frozen)
        elif self.ref_instance is not None:
            model = self.ref_instance._build_model(in_base=in_base, read_only=read_only, frozen=frozen)
        else:
            raise exceptions.InvalidSwaggerValueError(
                f"type is not supported", key=self.traces, value=[self.type])
        model.read_only = read_only
        model.frozen = frozen
        return model

    def to_cmd_schema(self, traces_route, mutability, read_only=False, frozen=False, ref_link=None, in_base=False):
        # verify model will be read only or not
        read_only = read_only or self.read_only
        # verify model will be frozen (not used or not)
        if not frozen:
            if read_only:
                if mutability != MutabilityEnum.Read:
                    frozen = True  # frozen because of mutability
            elif self.x_ms_mutability:
                if mutability not in self.x_ms_mutability:
                    frozen = True  # frozen because of mutability

        if self.traces in traces_route:
            assert isinstance(ref_link, str), f"Ref Link needed: {[*traces_route, self.traces]}"
            schema_cls = f"@{ref_link.split('/')[-1]}"
            if in_base:
                model = CMDClsSchemaBase()
                model._type = schema_cls
            else:
                model = CMDClsSchema()
                model._type = schema_cls
            setattr(self, "_looped", True)
            if not hasattr(self, "_schema_cls"):
                setattr(self, "_schema_cls", schema_cls)
            else:
                assert self._schema_cls == schema_cls
            return model

        if self.ref_instance is not None:
            model = self.ref_instance.to_cmd_schema(
                traces_route=[*traces_route, self.traces],
                mutability=mutability,
                read_only=read_only,
                frozen=frozen,
                ref_link=self.ref
            )
        else:
            model = self._build_model(in_base=in_base, read_only=read_only, frozen=frozen)

        if isinstance(model, CMDStringSchemaBase):
            if self.all_of is not None:
                raise exceptions.InvalidSwaggerValueError(
                    msg=f"allOf is not supported for `string` type schema",
                    key=self.traces, value=None
                )
            model.fmt = self.build_cmd_string_format() or model.fmt  # use inherent format when None
            model.enum = self.build_enum() or model.enum    # use inherent enum when None
        elif isinstance(model, CMDIntegerSchemaBase):
            if self.all_of is not None:
                raise exceptions.InvalidSwaggerValueError(
                    msg=f"allOf is not supported for `integer` type schema",
                    key=self.traces, value=None
                )
            model.fmt = self.build_cmd_integer_format() or model.fmt
            model.enum = self.build_enum() or model.enum
        elif isinstance(model, CMDBooleanSchemaBase):
            if self.all_of is not None:
                raise exceptions.InvalidSwaggerValueError(
                    msg=f"allOf is not supported for `boolean` type schema",
                    key=[ref_link]
                )
        elif isinstance(model, CMDFloatSchemaBase):
            if self.all_of is not None:
                raise exceptions.InvalidSwaggerValueError(
                    msg=f"allOf is not supported for `number` type schema",
                    key=self.traces, value=None
                )
            model.fmt = self.build_cmd_float_format() or model.fmt
            model.enum = self.build_enum() or model.enum
        elif isinstance(model, CMDArraySchemaBase):
            if self.all_of is not None:
                raise exceptions.InvalidSwaggerValueError(
                    msg=f"allOf is not supported for `array` type schema",
                    key=self.traces, value=None
                )
            model.fmt = self.build_cmd_array_format() or model.fmt
            if self.items:
                assert isinstance(self.items, Schema)
                v = self.items.to_cmd_schema(
                    traces_route=[*traces_route, self.traces],
                    mutability=mutability,
                    read_only=read_only,
                    frozen=frozen,
                    in_base=True,
                )
                assert isinstance(v, CMDSchemaBase)
                model.item = v

                # freeze because array item is frozen
                if not model.frozen and model.item.frozen:
                    model.frozen = True
        elif isinstance(model, CMDObjectSchemaBase):
            # props
            prop_dict = {}
            if model.props is not None:
                # inherent from $ref
                for prop in model.props:
                    prop_dict[prop.name] = prop

            if self.all_of:
                # inherent from allOf
                for item in self.all_of:
                    disc_parent = item.get_disc_parent()
                    if disc_parent is not None and item.ref_instance.traces in traces_route:
                        # discriminator parent already in trace, break reference loop
                        continue
                    v = item.to_cmd_schema(
                        traces_route=[*traces_route, self.traces],
                        mutability=mutability,
                        read_only=read_only,
                        frozen=frozen,
                        in_base=True
                    )
                    if isinstance(v, CMDClsSchemaBase):
                        raise exceptions.InvalidSwaggerValueError(
                            msg="AllOf not support to reference loop",
                            key=self.traces,
                            value=v.type
                        )
                    assert isinstance(v, CMDObjectSchemaBase)
                    if v.fmt:
                        model.fmt = v.fmt

                    if v.props:
                        for p in v.props:
                            prop_dict[p.name] = p

                    if disc_parent is not None and disc_parent.traces not in traces_route:
                        # directly use child definition instead of polymorphism.
                        # So the value for discriminator property is const.
                        disc_prop = disc_parent.discriminator
                        for disc_value, disc_child in disc_parent.disc_children.items():
                            if disc_child == self:
                                prop_dict[disc_prop].const = True
                                prop_dict[disc_prop].default = CMDSchemaDefault()
                                prop_dict[disc_prop].default.value = disc_value
                                break

                    if v.additional_props:
                        model.additional_props = v.additional_props

            if self.properties:
                for name, p in self.properties.items():
                    assert isinstance(p, Schema)
                    v = p.to_cmd_schema(
                        traces_route=[*traces_route, self.traces],
                        mutability=mutability,
                        read_only=read_only,
                        frozen=frozen
                    )
                    if v is None:
                        # ignore by mutability
                        continue
                    assert isinstance(v, CMDSchema)
                    v.name = name
                    prop_dict[name] = v

            # TODO: move required as list
            if self.required:
                for name in self.required:
                    if name in prop_dict:
                        prop_dict[name].required = True

            # discriminators
            if self.disc_children:
                discriminators = []
                assert self.discriminator is not None
                disc_prop = self.discriminator
                for disc_value, disc_child in self.disc_children.items():
                    if disc_child.traces in traces_route:
                        # discriminator child already in trace, break reference loop
                        continue
                    disc = CMDObjectSchemaDiscriminator()
                    disc.prop = disc_prop
                    disc.value = disc_value

                    if disc_prop not in prop_dict:
                        raise exceptions.InvalidSwaggerValueError(
                            msg="Discriminator Property don't exist",
                            key=self.traces,
                            value=[disc_prop, mutability]
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

                    v = disc_child.to_cmd_schema(
                        traces_route=[*traces_route, self.traces],
                        mutability=mutability,
                        read_only=read_only,
                        frozen=frozen,
                        in_base=True
                    )
                    assert isinstance(v, CMDObjectSchemaBase)
                    if v.frozen:
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
                if 'id' in prop_dict and self.resource_id_templates:
                    id_prop = prop_dict['id']
                    if not isinstance(id_prop, CMDResourceIdSchema):
                        assert isinstance(id_prop, CMDStringSchema)
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
                if 'location' in prop_dict:
                    location_prop = prop_dict['location']
                    if not isinstance(location_prop, CMDResourceLocationSchema):
                        assert isinstance(location_prop, CMDStringSchema)
                        raw_data = location_prop.to_native()
                        prop_dict['location'] = CMDResourceLocationSchema(raw_data=raw_data)

            if prop_dict:
                model.props = []
                for prop in prop_dict.values():
                    model.props.append(prop)

            # fmt
            model.fmt = self.build_cmd_object_format() or model.fmt

            # additional properties
            if self.additional_properties:
                if isinstance(self.additional_properties, Schema):
                    v = self.additional_properties.to_cmd_schema(
                        traces_route=[*traces_route, self.traces],
                        mutability=mutability,
                        read_only=read_only,
                        frozen=frozen,
                        in_base=True,
                    )
                    if v is not None:
                        assert isinstance(v, CMDSchemaBase)
                        model.additional_props = CMDObjectSchemaAdditionalProperties()
                        model.additional_props.item = v
                elif self.additional_properties is True:
                    model.additional_props = CMDObjectSchemaAdditionalProperties()
            elif not model.props and not model.discriminators:
                # to handle object schema without any properties
                model.additional_props = CMDObjectSchemaAdditionalProperties()

            if model.additional_props:
                if read_only:
                    model.additional_props.read_only = read_only
                if frozen:
                    model.additional_props.frozen = frozen

            if self.x_ms_client_flatten and isinstance(model, CMDObjectSchema):
                # client flatten can only be supported for CMDObjectSchema install of CMDObjectSchemaBase.
                # Because CMDObjectSchemaBase will not link with argument
                model.client_flatten = True

            # when all additional_props and props and discriminators of model is frozen then this model is frozen
            if not model.frozen:
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
                model.frozen = need_frozen

        if getattr(self, "_looped", False):
            assert isinstance(model, (CMDObjectSchemaBase, CMDArraySchemaBase))
            model.cls = self._schema_cls
            setattr(self, "_looped", False)

        if self.x_ms_client_default is not None:
            model.default = CMDSchemaDefault()
            model.default.value = self.x_ms_client_default

        elif self.default is not None:
            model.default = CMDSchemaDefault()
            model.default.value = self.default

        if self.description and isinstance(model, CMDSchema):
            model.description = self.description

        return model

    def build_cmd_string_format(self):
        fmt_assigned = False

        fmt = CMDStringFormat()

        if self.pattern is not None:
            fmt.pattern = self.pattern
            fmt_assigned = True
        if self.max_length is not None:
            fmt.max_length = self.max_length
            fmt_assigned = True
        if self.min_length is not None:
            fmt.min_length = self.min_length
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_cmd_integer_format(self):
        fmt_assigned = False
        fmt = CMDIntegerFormat()

        if self.maximum is not None:
            fmt.maximum = int(self.maximum)
            if self.exclusive_maximum and fmt.maximum == self.maximum:
                fmt.maximum -= 1
            fmt_assigned = True

        if self.minimum is not None:
            fmt.minimum = int(self.minimum)
            if self.exclusive_minimum and fmt.minimum == self.minimum:
                fmt.minimum += 1
            fmt_assigned = True

        if self.multiple_of is not None:
            fmt.multiple_of = self.multiple_of
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_cmd_float_format(self):
        fmt_assigned = False
        fmt = CMDFloatFormat()

        if self.maximum is not None:
            fmt.maximum = self.maximum
            if self.exclusive_maximum:
                fmt.exclusive_maximum = True
            fmt_assigned = True

        if self.minimum is not None:
            fmt.minimum = int(self.minimum)
            if self.exclusive_minimum:
                fmt.exclusive_minimum = True
            fmt_assigned = True

        if self.multiple_of is not None:
            fmt.multiple_of = self.multiple_of
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_cmd_array_format(self):
        fmt_assigned = False
        fmt = CMDArrayFormat()

        if self.unique_items:
            fmt.unique = True
            fmt_assigned = True

        if self.max_length is not None:
            fmt.max_length = self.max_length
            fmt_assigned = True

        if self.min_length is not None:
            fmt.min_length = self.min_length
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_cmd_object_format(self):
        fmt_assigned = False
        fmt = CMDObjectFormat()

        if self.max_properties is not None:
            fmt.max_properties = self.max_properties
            fmt_assigned = True
        if self.min_properties is not None:
            fmt.min_properties = self.min_properties
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    def build_enum(self):
        if not self.enum and not (self.x_ms_enum and self.x_ms_enum.values):
            return None
        enum = CMDSchemaEnum()
        enum.items = []
        if self.x_ms_enum and self.x_ms_enum.values:
            for v in self.x_ms_enum.values:
                item = CMDSchemaEnumItem()
                item.value = v.value
                if v.name:
                    # TODO: the name should be used as display name for argument
                    pass
                enum.items.append(item)
        elif self.enum:
            for v in self.enum:
                item = CMDSchemaEnumItem()
                item.value = v
                enum.items.append(item)
        return enum
