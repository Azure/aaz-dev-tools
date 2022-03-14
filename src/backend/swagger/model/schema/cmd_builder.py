from command.model.configuration import CMDIntegerFormat, CMDStringFormat, CMDFloatFormat, CMDArrayFormat, \
    CMDObjectFormat, CMDSchemaEnum, CMDSchemaEnumItem

from command.model.configuration import CMDSchemaDefault, \
    CMDStringSchema, CMDStringSchemaBase, \
    CMDByteSchema, CMDByteSchemaBase, \
    CMDBinarySchema, CMDBinarySchemaBase, \
    CMDDateSchema, CMDDateSchemaBase, \
    CMDDateTimeSchema, CMDDateTimeSchemaBase, \
    CMDPasswordSchema, CMDPasswordSchemaBase, \
    CMDDurationSchema, CMDDurationSchemaBase, \
    CMDUuidSchema, CMDUuidSchemaBase, \
    CMDIntegerSchema, CMDIntegerSchemaBase, \
    CMDInteger32Schema, CMDInteger32SchemaBase, \
    CMDInteger64Schema, CMDInteger64SchemaBase, \
    CMDBooleanSchema, CMDBooleanSchemaBase, \
    CMDFloatSchema, CMDFloatSchemaBase, \
    CMDFloat32Schema, CMDFloat32SchemaBase, \
    CMDFloat64Schema, CMDFloat64SchemaBase, \
    CMDObjectSchema, CMDObjectSchemaBase, CMDArraySchema, CMDArraySchemaBase, CMDClsSchema, CMDClsSchemaBase

from swagger.utils import exceptions
from .fields import MutabilityEnum
from .schema import ReferenceSchema


class CMDBuilder:

    def __init__(self, path, method=None, mutability=None, in_base=False, read_only=False, frozen=False, parent_ids=None, cls_definitions=None):
        self.path = path
        self.method = method
        self.mutability = mutability
        self.in_base = in_base
        self.read_only = read_only
        self.frozen = frozen
        self.id = None    # used to find loop
        self.parent_ids = parent_ids or []
        self.cls_definitions = {} if cls_definitions is None else cls_definitions

    def __call__(self, schema, **kwargs):
        sub_builder = CMDBuilder(
            path=kwargs.pop('path', self.path),
            method=kwargs.pop('method', self.method),
            mutability=kwargs.pop('mutability', self.mutability),
            in_base=kwargs.pop('in_base', self.in_base),
            read_only=kwargs.pop('read_only', self.read_only),
            frozen=kwargs.pop('frozen', self.frozen),
            parent_ids=[*self.parent_ids, self.id],
            cls_definitions=kwargs.pop('cls_definitions', self.cls_definitions),
        )
        if getattr(schema, 'read_only', None):
            sub_builder.read_only = True
        if not sub_builder.frozen:
            if sub_builder.read_only:
                if self.mutability != MutabilityEnum.Read:
                    sub_builder.frozen = True
            elif getattr(schema, 'x_ms_mutability', None):
                if self.mutability not in schema.x_ms_mutability:
                    sub_builder.frozen = True
        if hasattr(schema, 'traces'):
            sub_builder.id = (schema.traces, sub_builder.mutability, sub_builder.read_only, sub_builder.frozen)
            if sub_builder.id in sub_builder.parent_ids:
                if len(schema.traces) == 3:
                    # make sure the trace is reference definition, the trace should be [file_path, 'definitions', name]
                    raise exceptions.InvalidSwaggerValueError(
                            msg="Find invalid reference loop",
                            key=sub_builder.id,
                            value=sub_builder.parent_ids.index(sub_builder.id),
                        )
        return schema.to_cmd(sub_builder, **kwargs)

    def find_traces(self, traces):
        assert traces is not None
        for parent_id in self.parent_ids:
            if parent_id is None:
                continue
            parent_traces, mutability, read_only, frozen = parent_id
            if parent_traces == traces:
                return True
        return False

    def build_schema(self, schema):
        schema_type = getattr(schema, 'type', None)
        if schema_type == "string":
            if schema.format is None:
                if self.in_base:
                    model = CMDStringSchemaBase()
                else:
                    model = CMDStringSchema()
            elif schema.format == "byte":
                if self.in_base:
                    model = CMDByteSchemaBase()
                else:
                    model = CMDByteSchema()
            elif schema.format == "binary":
                if self.in_base:
                    model = CMDBinarySchemaBase()
                else:
                    model = CMDBinarySchema()
            elif schema.format == "date":
                if self.in_base:
                    model = CMDDateSchemaBase()
                else:
                    model = CMDDateSchema()
            elif schema.format == "date-time":
                if self.in_base:
                    model = CMDDateTimeSchemaBase()
                else:
                    model = CMDDateTimeSchema()
            elif schema.format == "password":
                if self.in_base:
                    model = CMDPasswordSchemaBase()
                else:
                    model = CMDPasswordSchema()
            elif schema.format == "duration":
                if self.in_base:
                    model = CMDDurationSchemaBase()
                else:
                    model = CMDDurationSchema()
            elif schema.format == "uuid":
                if self.in_base:
                    model = CMDUuidSchemaBase()
                else:
                    model = CMDUuidSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=getattr(schema, "traces", None), value=[schema_type, schema.format])
        elif schema_type == "integer":
            if schema.format is None:
                if self.in_base:
                    model = CMDIntegerSchemaBase()
                else:
                    model = CMDIntegerSchema()
            elif schema.format == "int32":
                if self.in_base:
                    model = CMDInteger32SchemaBase()
                else:
                    model = CMDInteger32Schema()
            elif schema.format == "int64":
                if self.in_base:
                    model = CMDInteger64SchemaBase()
                else:
                    model = CMDInteger64Schema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=getattr(schema, "traces", None), value=[schema_type, schema.format])
        elif schema_type == "boolean":
            if schema.format is None:
                if self.in_base:
                    model = CMDBooleanSchemaBase()
                else:
                    model = CMDBooleanSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=getattr(schema, "traces", None), value=[schema_type, schema.format])
        elif schema_type == "number":
            if schema.format is None:
                if self.in_base:
                    model = CMDFloatSchemaBase()
                else:
                    model = CMDFloatSchema()
            elif schema.format == "float":
                if self.in_base:
                    model = CMDFloat32SchemaBase()
                else:
                    model = CMDFloat32Schema()
            elif schema.format == "double":
                if self.in_base:
                    model = CMDFloat64SchemaBase()
                else:
                    model = CMDFloat64Schema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=getattr(schema, "traces", None), value=[schema_type, schema.format])
        elif schema_type == "array":
            if schema.format is None:
                if self.in_base:
                    model = CMDArraySchemaBase()
                else:
                    model = CMDArraySchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=getattr(schema, "traces", None), value=[schema_type, schema.format])
        elif schema_type == "object" or getattr(schema, "properties", None) or getattr(schema, "additional_properties",
                                                                                       None):
            if schema.format is None:
                if self.in_base:
                    model = CMDObjectSchemaBase()
                else:
                    model = CMDObjectSchema()
            else:
                raise exceptions.InvalidSwaggerValueError(
                    f"format is not supported", key=getattr(schema, "traces", None), value=[schema_type, schema.format])
        # for swagger schema only
        elif getattr(schema, "all_of", None) is not None:
            model = self.build_schema(schema.all_of[0])
        elif getattr(schema, "ref_instance", None) is not None:
            model = self.build_schema(schema.ref_instance)
        else:
            raise exceptions.InvalidSwaggerValueError(
                f"type is not supported", key=getattr(schema, "traces", None), value=[schema_type])

        model.read_only = self.read_only
        model.frozen = self.frozen
        return model

    def _get_cls_definition_name(self, schema):
        assert isinstance(schema, ReferenceSchema)
        schema_cls_name = f"{schema.ref.split('/')[-1]}_{self.mutability}"
        if self.mutability != MutabilityEnum.Read:
            if self.read_only:
                schema_cls_name += "_read"
        if self.frozen:
            schema_cls_name += "_frozen"
        return schema_cls_name

    def register_cls_definition(self, schema, support_cls_schema, **kwargs):
        name = self._get_cls_definition_name(schema)
        if self.frozen:
            if support_cls_schema:
                if self.in_base:
                    model = CMDClsSchemaBase()
                else:
                    model = CMDClsSchema()
                model.read_only = self.read_only
                model.frozen = self.frozen
                model._type = f"@{name}"
            else:
                model = self(schema.ref_instance, **kwargs)
            return model

        if name not in self.cls_definitions:
            if support_cls_schema:
                self.cls_definitions[name] = {"count": 1}   # register in cls_definitions first in case of loop reference below
                model = self(schema.ref_instance, **kwargs)
                if isinstance(model, (CMDObjectSchemaBase, CMDArraySchemaBase)):

                    # Important: only support object and array schema to defined as cls
                    self.cls_definitions[name]['model'] = model  # when self.cls_definitions[name]['count'] > 1, the loop reference exist
                else:
                    del self.cls_definitions[name]
            else:
                model = self(schema.ref_instance, **kwargs)
        else:
            if support_cls_schema:
                self.cls_definitions[name]['count'] += 1
                if self.in_base:
                    model = CMDClsSchemaBase()
                else:
                    model = CMDClsSchema()
                model.read_only = self.read_only
                if 'model' in self.cls_definitions[name]:
                    model.frozen = self.frozen or self.cls_definitions[name]['model'].frozen  # need to combine with the model frozen, especially for _create model with all ready_only properties
                else:
                    model.frozen = self.frozen
                model._type = f"@{name}"
            else:
                if 'model' not in self.cls_definitions[name]:
                    raise exceptions.InvalidSwaggerValueError(
                        msg="Find invalid reference loop",
                        key=schema.traces,
                        value=name
                    )
                model = self(schema.ref_instance, **kwargs)
        return model

    def get_cls_definition_model(self, model):
        assert isinstance(model, CMDClsSchemaBase)
        name = model.type[1:]
        return self.cls_definitions[name]['model']

    @staticmethod
    def setup_enum(model, schema):
        if not schema.enum and not (getattr(schema, 'x_ms_enum', None) and schema.x_ms_enum.values):
            return
        enum = CMDSchemaEnum()
        enum.items = []
        if schema.x_ms_enum and schema.x_ms_enum.values:
            for v in schema.x_ms_enum.values:
                item = CMDSchemaEnumItem()
                item.value = v.value
                if v.name:
                    # TODO: the name should be used as display name for argument
                    pass
                enum.items.append(item)
        elif schema.enum:
            for v in schema.enum:
                item = CMDSchemaEnumItem()
                item.value = v
                enum.items.append(item)

        model.enum = enum

    def setup_fmt(self, model, schema):
        if not hasattr(model, 'fmt'):
            return
        fmt = None
        if isinstance(model, CMDStringSchemaBase):
            fmt = self.build_cmd_string_format(schema)
        elif isinstance(model, CMDIntegerSchemaBase):
            fmt = self.build_cmd_integer_format(schema)
        elif isinstance(model, CMDBooleanSchemaBase):
            # TODO:
            pass
        elif isinstance(model, CMDFloatSchemaBase):
            fmt = self.build_cmd_float_format(schema)
        elif isinstance(model, CMDArraySchemaBase):
            fmt = self.build_cmd_array_format(schema)
        elif isinstance(model, CMDObjectSchemaBase):
            fmt = self.build_cmd_object_format(schema)

        model.fmt = fmt or model.fmt

    @staticmethod
    def setup_default(model, schema):
        if getattr(schema, 'x_ms_client_default', None) is not None:
            model.default = CMDSchemaDefault()
            model.default.value = schema.x_ms_client_default
        elif schema.default is not None:
            model.default = CMDSchemaDefault()
            model.default.value = schema.default

    @staticmethod
    def setup_description(model, schema):
        if schema.description:
            model.description = schema.description

    @staticmethod
    def build_cmd_string_format(schema):
        fmt_assigned = False
        fmt = CMDStringFormat()

        if schema.pattern is not None:
            fmt.pattern = schema.pattern
            fmt_assigned = True
        if schema.max_length is not None:
            fmt.max_length = schema.max_length
            fmt_assigned = True
        if schema.min_length is not None:
            fmt.min_length = schema.min_length
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    @staticmethod
    def build_cmd_integer_format(schema):
        fmt_assigned = False
        fmt = CMDIntegerFormat()

        if schema.maximum is not None:
            fmt.maximum = int(schema.maximum)
            if schema.exclusive_maximum and fmt.maximum == schema.maximum:
                fmt.maximum -= 1
            fmt_assigned = True

        if schema.minimum is not None:
            fmt.minimum = int(schema.minimum)
            if schema.exclusive_minimum and fmt.minimum == schema.minimum:
                fmt.minimum += 1
            fmt_assigned = True

        if schema.multiple_of is not None:
            fmt.multiple_of = schema.multiple_of
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    @staticmethod
    def build_cmd_float_format(schema):
        fmt_assigned = False
        fmt = CMDFloatFormat()

        if schema.maximum is not None:
            fmt.maximum = schema.maximum
            if schema.exclusive_maximum:
                fmt.exclusive_maximum = True
            fmt_assigned = True

        if schema.minimum is not None:
            fmt.minimum = int(schema.minimum)
            if schema.exclusive_minimum:
                fmt.exclusive_minimum = True
            fmt_assigned = True

        if schema.multiple_of is not None:
            fmt.multiple_of = schema.multiple_of
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    @staticmethod
    def build_cmd_array_format(schema):
        fmt_assigned = False
        fmt = CMDArrayFormat()

        if schema.unique_items:
            fmt.unique = True
            fmt_assigned = True

        if schema.max_length is not None:
            fmt.max_length = schema.max_length
            fmt_assigned = True

        if schema.min_length is not None:
            fmt.min_length = schema.min_length
            fmt_assigned = True

        if getattr(schema, "collection_format", None) is not None and schema.collection_format != 'csv':
            fmt.str_format = schema.collection_format
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    @staticmethod
    def build_cmd_object_format(schema):
        fmt_assigned = False
        fmt = CMDObjectFormat()

        if schema.max_properties is not None:
            fmt.max_properties = schema.max_properties
            fmt_assigned = True
        if schema.min_properties is not None:
            fmt.min_properties = schema.min_properties
            fmt_assigned = True

        if not fmt_assigned:
            return None
        return fmt

    @staticmethod
    def classify_responses(schema):
        success_responses = []
        success_202_response = None
        success_204_response = None
        redirect_responses = []
        error_responses = []

        if 'default' in schema.responses:
            resp = schema.responses['default']
            error_responses.append((None, resp))

        for code, resp in schema.responses.items():
            if code == "default":
                continue
            status_code = int(code)
            if status_code < 300:
                if status_code == 202:
                    success_202_response = ({status_code}, resp)
                elif status_code == 204:
                    success_204_response = ({status_code}, resp)
                else:
                    # success
                    find_match = False
                    for status_codes, p_resp in success_responses:
                        if p_resp.schema == resp.schema:
                            status_codes.add(status_code)
                            find_match = True
                            break
                    if not find_match:
                        success_responses.append(({status_code}, resp))
            elif status_code < 400:
                # redirect
                find_match = False
                for status_codes, p_resp in redirect_responses:
                    if p_resp.schema == resp.schema:
                        status_codes.add(status_code)
                        find_match = True
                        break
                if not find_match:
                    redirect_responses.append(({status_code}, resp))
            else:
                # error
                find_match = False
                for status_codes, p_resp in error_responses:
                    if p_resp.schema == resp.schema:
                        if status_codes is not None:  # ignore to add into default response
                            status_codes.add(status_code)
                        find_match = True
                if not find_match:
                    error_responses.append(({status_code}, resp))

        if len(success_responses) >= 2:
            raise exceptions.InvalidSwaggerValueError(
                msg="Multi Schema for success responses",
                key=[schema.traces],
                value=[status_codes for status_codes, _ in success_responses]
            )
        if len(redirect_responses) >= 2:
            raise exceptions.InvalidSwaggerValueError(
                msg="Multi Schema for redirect responses",
                key=[schema.traces],
                value=[status_codes for status_codes, _ in redirect_responses]
            )
        if len(error_responses) >= 3:
            raise exceptions.InvalidSwaggerValueError(
                msg="Multi Schema for error responses",
                key=[schema.traces],
                value=[status_codes for status_codes, _ in error_responses]
            )

        if success_202_response is not None:
            # append 202 Long Running response at the end of success response
            success_responses.append(success_202_response)
        if success_204_response is not None:
            # append 204 No Content response at the end of success response
            success_responses.append(success_204_response)

        # # default response
        # if 'default' not in error_responses and len(error_responses) == 1:
        #     p_resp, p_model = [*error_responses.values()][0]
        #     if p_model.body is not None:
        #         # use the current error response as default
        #         p_model.status_codes = None
        #         error_responses = {
        #             "default": (p_resp, p_model)
        #         }
        # if 'default' not in error_responses:
        #     raise exceptions.InvalidSwaggerValueError(
        #         msg="Miss default response",
        #         key=self.traces,
        #         value=[path, method]
        #     )

        return success_responses, redirect_responses, error_responses

    def apply_cls_definitions(self):
        for name, definition in self.cls_definitions.items():
            if definition['count'] > 1:
                definition['model'].cls = name
