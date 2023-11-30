from command.model.configuration import (
    CMDHttpOperation, CMDHttpRequestJsonBody, CMDArraySchema, CMDInstanceUpdateOperation, CMDRequestJson,
    CMDHttpResponseJsonBody, CMDObjectSchema, CMDSchema, CMDStringSchemaBase, CMDIntegerSchemaBase, CMDFloatSchemaBase,
    CMDBooleanSchemaBase, CMDObjectSchemaBase, CMDArraySchemaBase, CMDClsSchemaBase, CMDJsonInstanceUpdateAction,
    CMDObjectSchemaDiscriminator, CMDSchemaEnum, CMDJsonInstanceCreateAction, CMDJsonInstanceDeleteAction,
    CMDInstanceCreateOperation, CMDInstanceDeleteOperation, CMDClientEndpointsByTemplate)
from utils import exceptions
from utils.case import to_snake_case
from utils.error_format import AAZErrorFormatEnum


class AzOperationGenerator:

    def __init__(self, name, cmd_ctx, operation):
        self.name = name
        self._cmd_ctx = cmd_ctx
        self._operation = operation
        self.is_long_running = False

    @property
    def when(self):
        return self._operation.when


class AzLifeCycleCallbackGenerator(AzOperationGenerator):

    def __init__(self, name):
        super().__init__(name, None, None)

    @property
    def when(self):
        return None


class AzLifeCycleInstanceUpdateCallbackGenerator(AzLifeCycleCallbackGenerator):

    def __init__(self, name, variant_key, is_selector_variant):
        super().__init__(name)
        self.variant_key = variant_key
        self.is_selector_variant = is_selector_variant


class AzHttpOperationGenerator(AzOperationGenerator):

    def __init__(self, name, cmd_ctx, operation, client_endpoints):
        super().__init__(name, cmd_ctx, operation)
        assert isinstance(self._operation, CMDHttpOperation)

        self._client_endpoints = client_endpoints

        if self._operation.long_running is not None:
            self.is_long_running = True
            self.lro_options = {
                'final-state-via': self._operation.long_running.final_state_via
            }

        self.success_responses = []
        self.success_202_response = None

        error_format = None
        for response in self._operation.http.responses:
            if not response.is_error:
                if self.is_long_running and response.status_codes == [202]:
                    # ignore 202 response for long running operation.
                    # Long running operation should use 200 or 201 schema to deserialize the final response.
                    continue
                self.success_responses.append(AzHttpResponseGenerator(self._cmd_ctx, response))
            else:
                if not isinstance(response.body, CMDHttpResponseJsonBody):
                    if not response.body:
                        raise exceptions.InvalidAPIUsage(
                            f"Invalid `Error` response schema in operation `{self._operation.operation_id}`: "
                            f"Missing `schema` property in response "
                            f"`{response.status_codes or 'default'}`."
                        )
                    else:
                        raise exceptions.InvalidAPIUsage(
                            f"Invalid `Error` response schema in operation `{self._operation.operation_id}`: "
                            f"Only support json schema, current is '{type(response.body)}' in response "
                            f"`{response.status_codes or 'default'}`"
                        )
                schema = response.body.json.schema
                if not isinstance(schema, CMDClsSchemaBase):
                    raise NotImplementedError()
                name = schema.type[1:]
                if not error_format:
                    error_format = name
                if error_format != name:
                    raise exceptions.InvalidAPIUsage(
                        f"Invalid `Error` response schema in operation `{self._operation.operation_id}`: "
                        f"Multiple schema formats are founded: {name}, {error_format}"
                    )
        if not error_format:
            raise exceptions.InvalidAPIUsage(
                f"Missing `Error` response schema in operation `{self._operation.operation_id}`: "
                f"Please define the `default` response in swagger for error."
            )
        elif not AAZErrorFormatEnum.validate(error_format):
            raise exceptions.InvalidAPIUsage(
                f"Invalid `Error` response schema in operation `{self._operation.operation_id}`: "
                f"Invalid error format `{error_format}`. Support `ODataV4Format` and `MgmtErrorFormat` only"
            )

        if self.is_long_running:
            callback_name = None
            for response in self.success_responses:
                if 200 in response.status_codes or 201 in response.status_codes:
                    callback_name = response.callback_name
                    break
            self.success_202_response = AzHttp202ResponseGenerator(self._cmd_ctx, callback_name)
        self.error_format = error_format

        # specify content
        self.content = None
        self.form_content = None
        self.stream_content = None
        if self._operation.http.request.body:
            body = self._operation.http.request.body
            if isinstance(body, CMDHttpRequestJsonBody):
                self.content = AzHttpRequestContentGenerator(self._cmd_ctx, body)
            else:
                raise NotImplementedError()

    @property
    def url(self):
        return self._operation.http.path

    @property
    def method(self):
        return self._operation.http.request.method.upper()

    @property
    def url_parameters(self):
        parameters = []
        # add params in client endpoints
        if isinstance(self._client_endpoints, CMDClientEndpointsByTemplate) and self._client_endpoints.params:
            for param in self._client_endpoints.params:
                kwargs = {}
                if param.skip_url_encoding:
                    kwargs['skip_quote'] = True
                if param.required:
                    kwargs['required'] = param.required
                arg_key, hide = self._cmd_ctx.get_argument(param.arg)
                if not hide:
                    parameters.append([
                        param.name,
                        arg_key,
                        False,
                        kwargs
                    ])
        # add params in client path
        path = self._operation.http.request.path
        if not path:
            return parameters or None
        if path.params:
            for param in path.params:
                kwargs = {}
                if param.skip_url_encoding:
                    kwargs['skip_quote'] = True
                if param.required:
                    kwargs['required'] = param.required
                arg_key, hide = self._cmd_ctx.get_argument(param.arg)
                if not hide:
                    parameters.append([
                        param.name,
                        arg_key,
                        False,
                        kwargs
                    ])
        if path.consts:
            for param in path.consts:
                assert param.const
                kwargs = {}
                if param.skip_url_encoding:
                    kwargs['skip_quote'] = True
                if param.required:
                    kwargs['required'] = param.required
                parameters.append([
                    param.name,
                    param.default.value,
                    True,
                    kwargs
                ])

        return parameters or None

    @property
    def query_parameters(self):
        query = self._operation.http.request.query
        if not query:
            return None
        parameters = []
        if query.params:
            for param in query.params:
                kwargs = {}
                if param.skip_url_encoding:
                    kwargs['skip_quote'] = True
                if param.required:
                    kwargs['required'] = param.required
                arg_key, hide = self._cmd_ctx.get_argument(param.arg)
                if not hide:
                    parameters.append([
                        param.name,
                        arg_key,
                        False,
                        kwargs
                    ])
        if query.consts:
            for param in query.consts:
                assert param.const
                kwargs = {}
                if param.skip_url_encoding:
                    kwargs['skip_quote'] = True
                if param.required:
                    kwargs['required'] = param.required
                parameters.append([
                    param.name,
                    param.default.value,
                    True,
                    kwargs
                ])
        return parameters

    @property
    def header_parameters(self):
        header = self._operation.http.request.header
        parameters = []
        if header:
            if header.params:
                for param in header.params:
                    kwargs = {}
                    if param.required:
                        kwargs['required'] = param.required
                    arg_key, hide = self._cmd_ctx.get_argument(param.arg)
                    if not hide:
                        parameters.append([
                            param.name,
                            arg_key,
                            False,
                            kwargs
                        ])
            if header.consts:
                for param in header.consts:
                    assert param.const
                    kwargs = {}
                    if param.required:
                        kwargs['required'] = param.required
                    parameters.append([
                        param.name,
                        param.default.value,
                        True,
                        kwargs
                    ])
        if self.content:
            body = self._operation.http.request.body
            if isinstance(body, CMDHttpRequestJsonBody):
                parameters.append([
                    "Content-Type",
                    "application/json",
                    True,
                    {}
                ])
        if self.success_responses:
            for response in self.success_responses:
                if response._response.body is not None and isinstance(response._response.body, CMDHttpResponseJsonBody):
                    parameters.append([
                        "Accept",
                        "application/json",
                        True,
                        {}
                    ])
                    break
        return parameters


class AzInstanceOperationGenerator(AzOperationGenerator):

    def __init__(self, name, cmd_ctx, operation, arg_key, variant_key, is_selector_variant):
        super().__init__(name, cmd_ctx, operation)
        self.arg_key = arg_key
        self.variant_key = variant_key
        self.is_selector_variant = is_selector_variant


class AzJsonCreateOperationGenerator(AzInstanceOperationGenerator):

    HANDLER_NAME = "_create_instance"

    VALUE_NAME = "_instance_value"

    BUILDER_NAME = "_builder"

    def __init__(self, name, cmd_ctx, operation):
        variant_key, is_selector_variant = cmd_ctx.get_variant(operation.instance_create.ref)

        super().__init__(name, cmd_ctx, operation,
                         arg_key="self.ctx.args",
                         variant_key=variant_key,
                         is_selector_variant=is_selector_variant)

        assert isinstance(self._operation, CMDInstanceCreateOperation)
        assert isinstance(self._operation.instance_create, CMDJsonInstanceCreateAction)
        self._json = self._operation.instance_create.json

        assert self._json.ref is None
        assert isinstance(self._json.schema, CMDSchema)
        if self._json.schema.arg:
            self.arg_key, hide = self._cmd_ctx.get_argument(self._json.schema.arg)
            assert not hide

        self.typ, _, self.cls_builder_name = render_schema(
            self._json.schema, self._cmd_ctx.update_clses, name=self._json.schema.name)

        self._update_over_schema(self._json.schema)

    def _update_over_schema(self, s):
        if getattr(s, 'cls', None):
            self._cmd_ctx.set_update_cls(s)

        if isinstance(s, CMDObjectSchemaBase):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.additional_props and s.additional_props.item:
                self._update_over_schema(s.additional_props.item)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)
        elif isinstance(s, CMDArraySchemaBase):
            if s.item:
                self._update_over_schema(s.item)
        elif isinstance(s, CMDObjectSchemaDiscriminator):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)

    def iter_scopes(self):
        if not self._json.schema or not isinstance(self._json.schema, (CMDObjectSchema, CMDArraySchema)):
            return

        for scopes in _iter_request_scopes_by_schema_base(self._json.schema, self.BUILDER_NAME, None, self.arg_key, self._cmd_ctx):
            yield scopes


class AzJsonDeleteOperationGenerator(AzInstanceOperationGenerator):

    HANDLER_NAME = "_delete_instance"

    def __init__(self, name, cmd_ctx, operation):
        variant_key, is_selector_variant = cmd_ctx.get_variant(operation.instance_delete.ref)

        super().__init__(name, cmd_ctx, operation,
                         arg_key="self.ctx.args",
                         variant_key=variant_key,
                         is_selector_variant=is_selector_variant)
        assert isinstance(self._operation, CMDInstanceDeleteOperation)
        assert isinstance(self._operation.instance_delete, CMDJsonInstanceDeleteAction)
        self._json = self._operation.instance_delete.json

        assert self._json.ref is None
        assert self._json.schema is None


class AzInstanceUpdateOperationGenerator(AzInstanceOperationGenerator):
    pass


class AzJsonUpdateOperationGenerator(AzInstanceUpdateOperationGenerator):

    HANDLER_NAME = "_update_instance"

    VALUE_NAME = "_instance_value"

    BUILDER_NAME = "_builder"

    def __init__(self, name, cmd_ctx, operation):
        variant_key, is_selector_variant = cmd_ctx.get_variant(operation.instance_update.ref)
        super().__init__(name, cmd_ctx, operation,
                         arg_key="self.ctx.args",
                         variant_key=variant_key,
                         is_selector_variant=is_selector_variant)
        assert isinstance(self._operation, CMDInstanceUpdateOperation)
        assert isinstance(self._operation.instance_update, CMDJsonInstanceUpdateAction)
        self._json = self._operation.instance_update.json

        assert self._json.ref is None
        assert isinstance(self._json.schema, CMDSchema)
        if self._json.schema.arg:
            self.arg_key, hide = self._cmd_ctx.get_argument(self._json.schema.arg)
            assert not hide
        self.typ, _, self.cls_builder_name = render_schema(
            self._json.schema, self._cmd_ctx.update_clses, name=self._json.schema.name)

        self._update_over_schema(self._json.schema)

    def _update_over_schema(self, s):
        if getattr(s, 'cls', None):
            self._cmd_ctx.set_update_cls(s)

        if isinstance(s, CMDObjectSchemaBase):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.additional_props and s.additional_props.item:
                self._update_over_schema(s.additional_props.item)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)
        elif isinstance(s, CMDArraySchemaBase):
            if s.item:
                self._update_over_schema(s.item)
        elif isinstance(s, CMDObjectSchemaDiscriminator):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)

    def iter_scopes(self):
        if not self._json.schema or not isinstance(self._json.schema, (CMDObjectSchema, CMDArraySchema)):
            return

        for scopes in _iter_request_scopes_by_schema_base(self._json.schema, self.BUILDER_NAME, None, self.arg_key, self._cmd_ctx):
            yield scopes


class AzGenericUpdateOperationGenerator(AzInstanceUpdateOperationGenerator):

    def __init__(self, cmd_ctx, variant_key, is_selector_variant):
        super().__init__("InstanceUpdateByGeneric", cmd_ctx, None,
                         arg_key="self.ctx.generic_update_args",
                         variant_key=variant_key,
                         is_selector_variant=is_selector_variant)

    @property
    def when(self):
        return None


class AzHttpRequestContentGenerator:
    VALUE_NAME = "_content_value"
    BUILDER_NAME = "_builder"

    def __init__(self, cmd_ctx, body):
        self._cmd_ctx = cmd_ctx
        assert isinstance(body.json, CMDRequestJson)
        self._json = body.json
        self.ref = None
        if self._json.ref:
            self.ref, is_selector = self._cmd_ctx.get_variant(self._json.ref)
            assert not is_selector
        self.arg_key = "self.ctx.args"
        if self.ref is None:
            assert isinstance(self._json.schema, CMDSchema)
            if self._json.schema.arg:
                self.arg_key, hide = self._cmd_ctx.get_argument(self._json.schema.arg)
                assert not hide
            self.typ, self.typ_kwargs, self.cls_builder_name = render_schema(
                self._json.schema, self._cmd_ctx.update_clses, name=self._json.schema.name)

            self._update_over_schema(self._json.schema)

    def _update_over_schema(self, s):
        if getattr(s, 'cls', None):
            self._cmd_ctx.set_update_cls(s)

        if isinstance(s, CMDObjectSchemaBase):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.additional_props and s.additional_props.item:
                self._update_over_schema(s.additional_props.item)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)
        elif isinstance(s, CMDArraySchemaBase):
            if s.item:
                self._update_over_schema(s.item)
        elif isinstance(s, CMDObjectSchemaDiscriminator):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)

    def iter_scopes(self):
        if not self._json.schema or not isinstance(self._json.schema, (CMDObjectSchema, CMDArraySchema)):
            return

        for scopes in _iter_request_scopes_by_schema_base(self._json.schema, self.BUILDER_NAME, None, self.arg_key, self._cmd_ctx):
            yield scopes


class AzRequestClsGenerator:
    BUILDER_NAME = "_builder"

    def __init__(self, cmd_ctx, name, schema):
        self._cmd_ctx = cmd_ctx
        self.schema = schema
        self.name = name
        self.builder_name = parse_cls_builder_name(name)

    def iter_scopes(self):
        arg_key = f"@{self.name}"
        for scopes in _iter_request_scopes_by_schema_base(self.schema, self.BUILDER_NAME, None, arg_key, self._cmd_ctx):
            yield scopes


class AzHttpResponseGenerator:

    @staticmethod
    def _generate_callback_name(status_codes):
        return "on_" + "_".join(str(code) for code in status_codes)

    def __init__(self, cmd_ctx, response):
        self._cmd_ctx = cmd_ctx
        self._response = response

        self.status_codes = response.status_codes
        self.callback_name = self._generate_callback_name(response.status_codes)

        self.variant_name = None
        if response.body is not None and isinstance(response.body, CMDHttpResponseJsonBody) and \
                response.body.json is not None and response.body.json.var is not None:
            variant = response.body.json.var
            self.variant_name = self._cmd_ctx.get_variant(variant, name_only=True)
            self.schema = AzHttpResponseSchemaGenerator(
                self._cmd_ctx, response.body.json.schema, response.status_codes
            )


class AzHttp202ResponseGenerator:

    def __init__(self, cmd_ctx, callback_name):
        self._cmd_ctx = cmd_ctx
        self.status_codes = [202]
        self.callback_name = callback_name


class AzHttpResponseSchemaGenerator:

    @staticmethod
    def _generate_schema_name(status_codes):
        return "_schema_on_" + "_".join(str(code) for code in status_codes)

    @staticmethod
    def _generate_schema_builder_name(status_codes):
        return "_build_schema_on_" + "_".join(str(code) for code in status_codes)

    def __init__(self, cmd_ctx, schema, status_codes):
        self._cmd_ctx = cmd_ctx
        self._schema = schema
        self.name = self._generate_schema_name(status_codes)
        self.builder_name = self._generate_schema_builder_name(status_codes)

        self.typ, self.typ_kwargs, self.cls_builder_name = render_schema_base(self._schema, self._cmd_ctx.response_clses)

        self._update_over_schema(self._schema)

    def _update_over_schema(self, s):
        if getattr(s, 'cls', None):
            self._cmd_ctx.set_response_cls(s)

        if isinstance(s, CMDObjectSchemaBase):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.additional_props and s.additional_props.item:
                self._update_over_schema(s.additional_props.item)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)
        elif isinstance(s, CMDArraySchemaBase):
            if s.item:
                self._update_over_schema(s.item)
        elif isinstance(s, CMDObjectSchemaDiscriminator):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.discriminators:
                for disc in s.discriminators:
                    self._update_over_schema(disc)

    def iter_scopes(self):
        if not self.cls_builder_name and isinstance(self._schema, (CMDObjectSchemaBase, CMDArraySchemaBase)):
            for scopes in _iter_response_scopes_by_schema_base(self._schema, self.name, f"cls.{self.name}", self._cmd_ctx):
                yield scopes


class AzResponseClsGenerator:

    @staticmethod
    def _generate_schema_name(name):
        return "_schema_" + to_snake_case(name)

    def __init__(self, cmd_ctx, name, schema):
        self._cmd_ctx = cmd_ctx
        self.schema = schema
        self.name = name
        self.schema_name = self._generate_schema_name(name)
        self.builder_name = parse_cls_builder_name(name)

        self.typ, self.typ_kwargs, _ = render_schema_base(self.schema, self._cmd_ctx.response_clses)

        self.props = []
        self.discriminators = []
        if isinstance(schema, CMDObjectSchemaBase):
            if schema.props and schema.additional_props:
                raise NotImplementedError()
            if schema.discriminators:
                for disc in schema.discriminators:
                    disc_key = to_snake_case(disc.property)
                    disc_value = disc.value
                    self.discriminators.append((disc_key, disc_value))
            if schema.props:
                for s in schema.props:
                    s_name = to_snake_case(s.name)
                    self.props.append(s_name)
            elif schema.additional_props:
                if schema.additional_props.item is not None:
                    self.props.append("Element")
                else:
                    assert schema.additional_props.any_type is True
            else:
                raise NotImplementedError()
        elif isinstance(schema, CMDArraySchemaBase):
            self.props.append("Element")

        self.props = sorted(self.props)

    def iter_scopes(self):
        for scopes in _iter_response_scopes_by_schema_base(self.schema, to_snake_case(self.name), self.schema_name, self._cmd_ctx):
            yield scopes


def _iter_request_scopes_by_schema_base(schema, name, scope_define, arg_key, cmd_ctx):
    rendered_schemas = []
    search_schemas = {}
    discriminators = []
    if isinstance(schema, CMDObjectSchemaBase):
        if schema.props and schema.additional_props:
            # not support for both props and additional props
            raise NotImplementedError()

        if schema.discriminators:
            discriminators.extend(schema.discriminators)

        if schema.props:
            for s in schema.props:
                s_name = s.name
                s_typ, s_typ_kwargs, cls_builder_name = render_schema(s, cmd_ctx.update_clses, s_name)
                if s.arg:
                    # current schema linked with argument
                    s_arg_key, hide = cmd_ctx.get_argument(s.arg)
                    if hide:
                        continue
                else:
                    # current schema not linked with argument, then use current arg_key
                    s_arg_key = arg_key

                # handle enum item attached with argument
                has_enum_argument = False
                if hasattr(s, "enum") and isinstance(s.enum, CMDSchemaEnum):
                    for item in s.enum.items:
                        if item.arg:
                            # enum item linked with argument
                            item_arg_key, hide = cmd_ctx.get_argument(item.arg)
                            if hide:
                                continue
                            has_enum_argument = True
                            r_key = item_arg_key.replace(arg_key, '')
                            if not r_key:
                                r_key = '.'  # which means if the arg exist, fill it
                            is_const = True
                            const_value = item.value
                            rendered_schemas.append(
                                (s_name, s_typ, is_const, const_value, r_key, s_typ_kwargs, cls_builder_name)
                            )

                if not has_enum_argument:
                    r_key = s_arg_key.replace(arg_key, '')
                    if not r_key:
                        r_key = '.' if s.required else None  # which means if the parent exist, fill it

                    is_const = False
                    const_value = None
                    if s.const:
                        is_const = True
                        const_value = s.default.value

                    rendered_schemas.append(
                        (s_name, s_typ, is_const, const_value, r_key, s_typ_kwargs, cls_builder_name)
                    )
                    if not cls_builder_name and not is_const \
                            and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                        search_schemas[s_name] = (s, s_arg_key)

        elif schema.additional_props:
            if schema.additional_props.any_type is True:
                s_name = '{}'
                r_key = '.'  # if element exist, always fill it

                is_const = False
                const_value = None
                rendered_schemas.append(
                    (s_name, None, is_const, const_value, r_key, None, None)
                )
            else:
                assert schema.additional_props.item is not None
                s = schema.additional_props.item
                s_name = '{}'
                s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, cmd_ctx.update_clses)
                s_arg_key = arg_key + '{}'
                r_key = '.'  # if element exist, always fill it

                is_const = False
                const_value = None
                rendered_schemas.append(
                    (s_name, s_typ, is_const, const_value, r_key, s_typ_kwargs, cls_builder_name)
                )
                if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    search_schemas[s_name] = (s, s_arg_key)

    elif isinstance(schema, CMDObjectSchemaDiscriminator):
        if schema.discriminators:
            discriminators.extend(schema.discriminators)

        if schema.props:
            for s in schema.props:
                s_name = s.name
                s_typ, s_typ_kwargs, cls_builder_name = render_schema(s, cmd_ctx.update_clses, s_name)
                if s.arg:
                    # current schema linked with argument
                    s_arg_key, hide = cmd_ctx.get_argument(s.arg)
                    if hide:
                        continue
                else:
                    # current schema not linked with argument, then use current arg_key
                    s_arg_key = arg_key

                # handle enum item attached with argument
                has_enum_argument = False
                if hasattr(s, "enum") and isinstance(s.enum, CMDSchemaEnum):
                    for item in s.enum.items:
                        if item.arg:
                            # enum item linked with argument
                            item_arg_key, hide = cmd_ctx.get_argument(item.arg)
                            if hide:
                                continue
                            has_enum_argument = True
                            r_key = item_arg_key.replace(arg_key, '')
                            if not r_key:
                                r_key = '.'
                            is_const = True
                            const_value = item.value
                            rendered_schemas.append(
                                (s_name, s_typ, is_const, const_value, r_key, s_typ_kwargs, cls_builder_name)
                            )

                if not has_enum_argument:
                    r_key = s_arg_key.replace(arg_key, '')
                    if not r_key:
                        r_key = '.' if s.required else None

                    is_const = False
                    const_value = None
                    if s.const:
                        is_const = True
                        const_value = s.default.value

                    rendered_schemas.append(
                        (s_name, s_typ, is_const, const_value, r_key, s_typ_kwargs, cls_builder_name)
                    )
                    if not cls_builder_name and not is_const \
                            and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                        # step into object and array schemas
                        search_schemas[s_name] = (s, s_arg_key)

    elif isinstance(schema, CMDArraySchemaBase):
        assert schema.item is not None  # make sure array schema defined its element schema
        s = schema.item
        s_name = '[]'
        s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, cmd_ctx.update_clses)
        s_arg_key = arg_key + '[]'
        r_key = '.'  # if element exist, always fill it

        is_const = False
        const_value = None
        rendered_schemas.append(
            (s_name, s_typ, is_const, const_value, r_key, s_typ_kwargs, cls_builder_name)
        )
        if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
            search_schemas[s_name] = (s, s_arg_key)

    else:
        raise NotImplementedError()

    if rendered_schemas or discriminators:
        disc_defines = [(disc.property, disc.value) for disc in discriminators]
        yield name, scope_define, rendered_schemas, disc_defines

    scope_define = scope_define or ""
    for s_name, (s, s_arg_key) in search_schemas.items():
        if s_name == '[]':
            s_scope_define = scope_define + '[]'
            s_name = '_elements'
        elif s_name == '{}':
            s_scope_define = scope_define + '{}'
            s_name = '_elements'
        else:
            s_scope_define = f"{scope_define}.{s_name}"
        for scopes in _iter_request_scopes_by_schema_base(s, to_snake_case(s_name), s_scope_define, s_arg_key, cmd_ctx):
            yield scopes

    for disc in discriminators:
        key_name = disc.property
        key_value = disc.value
        disc_name = f"disc_{to_snake_case(disc.get_safe_value())}"

        disc_scope_define = scope_define + "{" + key_name + ":" + key_value + "}"
        disc_arg_key = arg_key
        for scopes in _iter_request_scopes_by_schema_base(disc, disc_name, disc_scope_define, disc_arg_key, cmd_ctx):
            yield scopes


def _iter_response_scopes_by_schema_base(schema, name, scope_define, cmd_ctx):
    rendered_schemas = []
    search_schemas = {}
    discriminators = []
    if isinstance(schema, CMDObjectSchemaBase):
        if schema.props and schema.additional_props:
            # not support to parse schema with both props and additional_props
            raise NotImplementedError()

        if schema.discriminators:
            discriminators.extend(schema.discriminators)

        if schema.props:
            for s in schema.props:
                s_name = to_snake_case(s.name)
                s_typ, s_typ_kwargs, cls_builder_name = render_schema(s, cmd_ctx.response_clses, s_name)
                rendered_schemas.append((s_name, s_typ, s_typ_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    search_schemas[s_name] = s
        elif schema.additional_props:
            if schema.additional_props.item is not None:
                # AAZDictType
                s = schema.additional_props.item
                s_name = "Element"
                s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, cmd_ctx.response_clses)
                rendered_schemas.append((s_name, s_typ, s_typ_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    search_schemas[s_name] = s
            else:
                assert schema.additional_props.any_type is True
        else:
            # allow empty object
            pass

    elif isinstance(schema, CMDObjectSchemaDiscriminator):
        if schema.discriminators:
            discriminators.extend(schema.discriminators)

        if schema.props:
            for s in schema.props:
                s_name = to_snake_case(s.name)
                s_typ, s_typ_kwargs, cls_builder_name = render_schema(s, cmd_ctx.response_clses, s_name)
                rendered_schemas.append((s_name, s_typ, s_typ_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    search_schemas[s_name] = s
        else:
            # allow empty object
            pass

    elif isinstance(schema, CMDArraySchemaBase):
        # AAZListType
        assert schema.item is not None
        s = schema.item
        s_name = "Element"
        s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, cmd_ctx.response_clses)
        rendered_schemas.append((s_name, s_typ, s_typ_kwargs, cls_builder_name))
        if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
            search_schemas[s_name] = s

    else:
        raise NotImplementedError()

    if rendered_schemas:
        yield name, scope_define, rendered_schemas

    for s_name, s in search_schemas.items():
        s_scope_define = f"{scope_define}.{s_name}"
        if s_name == "Element":
            s_name = '_element'
        for scopes in _iter_response_scopes_by_schema_base(s, s_name, s_scope_define, cmd_ctx):
            yield scopes

    for disc in discriminators:
        key_name = to_snake_case(disc.property)
        key_value = disc.value
        disc_name = f"disc_{to_snake_case(disc.get_safe_value())}"

        disc_scope_define = f'{scope_define}.discriminate_by("{key_name}", "{key_value}")'
        for scopes in _iter_response_scopes_by_schema_base(disc, disc_name, disc_scope_define, cmd_ctx):
            yield scopes


def render_schema(schema, cls_map, name):
    schema_kwargs = {}
    if name != schema.name:
        schema_kwargs['serialized_name'] = schema.name

    flags = {}

    if schema.required:
        flags['required'] = True
    if schema.skip_url_encoding:
        flags['skip_quote'] = True
    if getattr(schema, 'client_flatten', False):
        flags['client_flatten'] = True
    if getattr(schema, 'secret', False):
        flags['secret'] = True
        if 'required' in flags:
            # when a property is `secret` then remove the required flag for that property.
            # because a secret property will not be returned in response and for `get+put` update command, it's allowed
            # without that property in payload.
            del flags['required']

    if flags:
        schema_kwargs['flags'] = flags

    schema_type, schema_kwargs, cls_builder_name = render_schema_base(schema, cls_map, schema_kwargs)

    return schema_type, schema_kwargs, cls_builder_name


def render_schema_base(schema, cls_map, schema_kwargs=None):
    if isinstance(schema, CMDClsSchemaBase):
        cls_name = schema.type[1:]
        schema = cls_map[cls_name].schema
    else:
        cls_name = getattr(schema, 'cls', None)
    cls_builder_name = parse_cls_builder_name(cls_name) if cls_name else None

    if schema_kwargs is None:
        schema_kwargs = {}

    if schema.nullable:
        schema_kwargs['nullable'] = True

    flags = schema_kwargs.get('flags', {})

    if schema.read_only:
        flags['read_only'] = True

    if isinstance(schema, CMDStringSchemaBase):
        schema_type = "AAZStrType"
    elif isinstance(schema, CMDIntegerSchemaBase):
        schema_type = "AAZIntType"
    elif isinstance(schema, CMDBooleanSchemaBase):
        schema_type = "AAZBoolType"
    elif isinstance(schema, CMDFloatSchemaBase):
        schema_type = "AAZFloatType"
    elif isinstance(schema, CMDObjectSchemaBase):
        if schema.props or schema.discriminators:
            schema_type = "AAZObjectType"
            if schema.additional_props:
                raise NotImplementedError()
        elif schema.additional_props:
            if schema.additional_props.any_type is True:
                schema_type = "AAZFreeFormDictType"
            else:
                assert schema.additional_props.item is not None
                schema_type = "AAZDictType"
        else:
            # empty object
            schema_type = "AAZObjectType"
    elif isinstance(schema, CMDArraySchemaBase):
        schema_type = "AAZListType"
    else:
        raise NotImplementedError()

    if flags:
        schema_kwargs['flags'] = flags

    return schema_type, schema_kwargs, cls_builder_name


def parse_cls_builder_name(cls_name):
    return f"_build_schema_{to_snake_case(cls_name)}"
