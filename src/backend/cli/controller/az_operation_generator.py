from command.model.configuration import CMDHttpOperation, CMDHttpRequestJsonBody, CMDArraySchema, \
    CMDInstanceUpdateOperation, CMDRequestJson, CMDHttpResponseJsonBody, CMDObjectSchema, CMDSchema, \
    CMDStringSchemaBase, CMDIntegerSchemaBase, CMDFloatSchemaBase, CMDBooleanSchemaBase, CMDObjectSchemaBase, \
    CMDArraySchemaBase, CMDClsSchemaBase, CMDJsonInstanceUpdateAction
from utils import exceptions
from utils.case import to_snack_case
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


class AzHttpOperationGenerator(AzOperationGenerator):

    def __init__(self, name, cmd_ctx, operation, request_cls_map, response_cls_map):
        super().__init__(name, cmd_ctx, operation)
        assert isinstance(self._operation, CMDHttpOperation)
        self._request_cls_map = request_cls_map
        self._response_cls_map = response_cls_map

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
                    continue
                self.success_responses.append(AzHttpResponseGenerator(self._cmd_ctx, response, self._response_cls_map))
            else:
                if not isinstance(response.body, CMDHttpResponseJsonBody):
                    raise NotImplementedError()
                schema = response.body.json.schema
                if not isinstance(schema, CMDClsSchemaBase):
                    raise NotImplementedError()
                name = schema.type[1:]
                if not error_format:
                    error_format = name
                if error_format != name:
                    raise exceptions.InvalidAPIUsage(f"Multiple error formats in one operation: {name}, {error_format}")
        if not AAZErrorFormatEnum.validate(error_format):
            raise exceptions.InvalidAPIUsage(f"Invalid error format: {error_format}")

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
                self.content = AzHttpRequestContentGenerator(self._cmd_ctx, body, self._request_cls_map)
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
        path = self._operation.http.request.path
        if not path:
            return None
        parameters = []
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
        return parameters

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


class AzJsonUpdateOperationGenerator(AzOperationGenerator):

    UPDATER_NAME = "_update_instance"

    VALUE_NAME = "_instance_value"

    BUILDER_NAME = "_builder"

    def __init__(self, name, cmd_ctx, operation, update_cls_map):
        super().__init__(name, cmd_ctx, operation)
        assert isinstance(self._operation, CMDInstanceUpdateOperation)
        assert isinstance(self._operation.instance_update, CMDJsonInstanceUpdateAction)
        self._update_cls_map = update_cls_map
        self.variant_key = self._cmd_ctx.get_variant(self._operation.instance_update.instance)
        self._json = self._operation.instance_update.json

        assert self._json.ref is None

        self.arg_key = "self.ctx.args"
        assert isinstance(self._json.schema, CMDSchema)
        if self._json.schema.arg:
            self.arg_key, hide = self._cmd_ctx.get_argument(self._json.schema.arg)
            assert not hide
        self.typ, _, self.cls_builder_name = render_schema(
            self._json.schema, self._update_cls_map, name=self._json.schema.name)

        self._update_over_schema(self._json.schema)

    def _update_over_schema(self, s):
        if getattr(s, 'cls', None):
            assert s.cls not in self._update_cls_map
            self._update_cls_map[s.cls] = AzRequestClsGenerator(self._cmd_ctx, s.cls, self._update_cls_map, s)

        if isinstance(s, CMDObjectSchemaBase):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.additional_props and s.additional_props.item:
                self._update_over_schema(s.additional_props.item)
        elif isinstance(s, CMDArraySchemaBase):
            if s.item:
                self._update_over_schema(s.item)

    def iter_scopes(self):
        if not self._json.schema or not isinstance(self._json.schema, (CMDObjectSchema, CMDArraySchema)):
            return

        for scopes in _iter_request_scopes_by_schema_base(self._json.schema, self.BUILDER_NAME, None, self._update_cls_map, self.arg_key, self._cmd_ctx):
            yield scopes


class AzGenericUpdateOperationGenerator(AzOperationGenerator):

    def __init__(self, cmd_ctx, variant_key):
        super().__init__("InstanceUpdateByGeneric", cmd_ctx, None)
        self.variant_key = variant_key
        self.arg_key = "self.ctx.args"

    @property
    def when(self):
        return None


class AzHttpRequestContentGenerator:
    VALUE_NAME = "_content_value"
    BUILDER_NAME = "_builder"

    def __init__(self, cmd_ctx, body, request_cls_map):
        self._cmd_ctx = cmd_ctx
        self._request_cls_map = request_cls_map
        assert isinstance(body.json, CMDRequestJson)
        self._json = body.json
        self.ref = self._cmd_ctx.get_variant(self._json.ref) if self._json.ref else None
        self.arg_key = "self.ctx.args"
        if self.ref is None:
            assert isinstance(self._json.schema, CMDSchema)
            if self._json.schema.arg:
                self.arg_key, hide = self._cmd_ctx.get_argument(self._json.schema.arg)
                assert not hide
            self.typ, _, self.cls_builder_name = render_schema(
                self._json.schema, self._request_cls_map, name=self._json.schema.name)

            self._update_over_schema(self._json.schema)

    def _update_over_schema(self, s):
        if getattr(s, 'cls', None):
            assert s.cls not in self._request_cls_map
            self._request_cls_map[s.cls] = AzRequestClsGenerator(self._cmd_ctx, s.cls, self._request_cls_map, s)

        if isinstance(s, CMDObjectSchemaBase):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.additional_props and s.additional_props.item:
                self._update_over_schema(s.additional_props.item)
        elif isinstance(s, CMDArraySchemaBase):
            if s.item:
                self._update_over_schema(s.item)

    def iter_scopes(self):
        if not self._json.schema or not isinstance(self._json.schema, (CMDObjectSchema, CMDArraySchema)):
            return

        for scopes in _iter_request_scopes_by_schema_base(self._json.schema, self.BUILDER_NAME, None, self._request_cls_map, self.arg_key, self._cmd_ctx):
            yield scopes


class AzRequestClsGenerator:
    BUILDER_NAME = "_builder"

    def __init__(self, cmd_ctx, name, request_cls_map, schema):
        self._cmd_ctx = cmd_ctx
        self.schema = schema
        self.name = name
        self.builder_name = parse_cls_builder_name(name)
        self._request_cls_map = request_cls_map

    def iter_scopes(self):
        arg_key = f"@{self.name}"
        for scopes in _iter_request_scopes_by_schema_base(self.schema, self.BUILDER_NAME, None, self._request_cls_map, arg_key ,self._cmd_ctx):
            yield scopes


class AzHttpResponseGenerator:

    @staticmethod
    def _generate_callback_name(status_codes):
        return "on_" + "_".join(str(code) for code in status_codes)

    def __init__(self, cmd_ctx, response, response_cls_map):
        self._cmd_ctx = cmd_ctx
        self._response = response
        self._response_cls_map = response_cls_map

        self.status_codes = response.status_codes
        self.callback_name = self._generate_callback_name(response.status_codes)

        self.variant_name = None
        if response.body is not None and isinstance(response.body, CMDHttpResponseJsonBody) and \
                response.body.json is not None and response.body.json.var is not None:
            variant = response.body.json.var
            self.variant_name = self._cmd_ctx.get_variant(variant, name_only=True)
            self.schema = AzHttpResponseSchemaGenerator(
                self._cmd_ctx, response.body.json.schema, self._response_cls_map, response.status_codes
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

    def __init__(self, cmd_ctx, schema, response_cls_map, status_codes):
        self._cmd_ctx = cmd_ctx
        self._response_cls_map = response_cls_map
        self._schema = schema
        self.name = self._generate_schema_name(status_codes)
        self.builder_name = self._generate_schema_builder_name(status_codes)

        self.typ, self.typ_kwargs, self.cls_builder_name = render_schema_base(self._schema, self._response_cls_map)

        self._update_over_schema(self._schema)

    def _update_over_schema(self, s):
        if getattr(s, 'cls', None):
            assert s.cls not in self._response_cls_map
            self._response_cls_map[s.cls] = AzResponseClsGenerator(self._cmd_ctx, s.cls, self._response_cls_map, s)

        if isinstance(s, CMDObjectSchemaBase):
            if s.props:
                for prop in s.props:
                    self._update_over_schema(prop)
            if s.additional_props and s.additional_props.item:
                self._update_over_schema(s.additional_props.item)
        elif isinstance(s, CMDArraySchemaBase):
            if s.item:
                self._update_over_schema(s.item)

    def iter_scopes(self):
        if not self.cls_builder_name and isinstance(self._schema, (CMDObjectSchemaBase, CMDArraySchemaBase)):
            for scopes in _iter_response_scopes_by_schema_base(self._schema, self.name, f"cls.{self.name}", self._response_cls_map):
                yield scopes


class AzResponseClsGenerator:

    @staticmethod
    def _generate_schema_name(name):
        return "_schema_" + to_snack_case(name)

    def __init__(self, cmd_ctx, name, response_cls_map, schema):
        self._cmd_ctx = cmd_ctx
        self.schema = schema
        self.name = name
        self._response_cls_map = response_cls_map
        self.schema_name = self._generate_schema_name(name)
        self.builder_name = parse_cls_builder_name(name)

        self.typ, self.typ_kwargs, _ = render_schema_base(self.schema, self._response_cls_map)

        self.props = []
        if isinstance(schema, CMDObjectSchemaBase):
            if schema.props and schema.additional_props:
                raise NotImplementedError()
            if schema.props:
                for s in schema.props:
                    s_name = to_snack_case(s.name)
                    self.props.append(s_name)
            elif schema.additional_props:
                self.props.append("Element")
        elif isinstance(schema, CMDArraySchemaBase):
            self.props.append("Element")

        self.props = sorted(self.props)

    def iter_scopes(self):
        for scopes in _iter_response_scopes_by_schema_base(self.schema, to_snack_case(self.name), self.schema_name, self._response_cls_map):
            yield scopes


def _iter_request_scopes_by_schema_base(schema, name, scope_define, cls_map, arg_key, cmd_ctx):
    rendered_schemas = []
    search_schemas = {}

    if isinstance(schema, CMDObjectSchemaBase):
        if schema.props and schema.additional_props:
            # not support for both props and additional props
            raise NotImplementedError()
        # TODO: support discriminator
        if schema.props:
            for s in schema.props:
                s_name = s.name
                s_typ, s_typ_kwargs, cls_builder_name = render_schema(s, cls_map, s_name)
                if s.arg:
                    s_arg_key, hide = cmd_ctx.get_argument(s.arg)
                    if hide:
                        continue
                else:
                    s_arg_key = arg_key

                r_key = s_arg_key.replace(arg_key, '')
                if not r_key:
                    r_key = '.' if s.required else None

                rendered_schemas.append((s_name, s_typ, r_key, s_typ_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    search_schemas[s_name] = (s, s_arg_key)
        elif schema.additional_props:
            assert schema.additional_props.item is not None
            s = schema.additional_props.item
            s_name = '{}'
            s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, cls_map)
            s_arg_key = arg_key + '{}'
            if not isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                r_key = '.'
            else:
                r_key = None

            rendered_schemas.append((s_name, s_typ, r_key, s_typ_kwargs, cls_builder_name))
            if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                search_schemas[s_name] = (s, s_arg_key)
    elif isinstance(schema, CMDArraySchemaBase):
        assert schema.item is not None
        s = schema.item
        s_name = "[]"
        s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, cls_map)
        s_arg_key = arg_key + '[]'

        if not isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
            r_key = '.'
        else:
            r_key = None

        rendered_schemas.append((s_name, s_typ, r_key, s_typ_kwargs, cls_builder_name))
        if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
            search_schemas[s_name] = (s, s_arg_key)
    else:
        raise NotImplementedError()

    if rendered_schemas:
        yield name, scope_define, rendered_schemas

    scope_define = scope_define or ""
    for s_name, (s, s_arg_key) in search_schemas.items():
        if s_name == '[]':
            s_scope_define = scope_define + "[]"
            s_name = '_elements'
        elif s_name == '{}':
            s_scope_define = scope_define + "{}"
            s_name = '_elements'
        else:
            s_scope_define = f"{scope_define}.{s_name}"
        for scopes in _iter_request_scopes_by_schema_base(s, to_snack_case(s_name), s_scope_define, cls_map, s_arg_key, cmd_ctx):
            yield scopes


def _iter_response_scopes_by_schema_base(schema, name, scope_define, response_cls_map):
    rendered_schemas = []
    search_schemas = {}
    if isinstance(schema, CMDObjectSchemaBase):
        if schema.props and schema.additional_props:
            # not support to parse schema with both props and additional_props
            raise NotImplementedError()
        # TODO: support discriminator
        if schema.props:
            for s in schema.props:
                s_name = to_snack_case(s.name)
                s_typ, s_typ_kwargs, cls_builder_name = render_schema(s, response_cls_map, s_name)
                rendered_schemas.append((s_name, s_typ, s_typ_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    search_schemas[s_name] = s
        elif schema.additional_props:
            # AAZDictType
            if schema.additional_props.item is not None:
                s = schema.additional_props.item
                s_name = "Element"
                s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, response_cls_map)
                rendered_schemas.append((s_name, s_typ, s_typ_kwargs, cls_builder_name))
                if not cls_builder_name and isinstance(s, (CMDObjectSchemaBase, CMDArraySchemaBase)):
                    search_schemas[s_name] = s
            else:
                # TODO: handler additional props with no item schema
                pass
    elif isinstance(schema, CMDArraySchemaBase):
        # AAZListType
        assert schema.item is not None
        s = schema.item
        s_name = "Element"
        s_typ, s_typ_kwargs, cls_builder_name = render_schema_base(s, response_cls_map)
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
        for scopes in _iter_response_scopes_by_schema_base(s, s_name, s_scope_define, response_cls_map):
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
        # TODO: handle schema.discriminators
        if schema.props:
            schema_type = "AAZObjectType"
            if schema.additional_props:
                raise NotImplementedError()
        elif schema.additional_props:
            schema_type = "AAZDictType"
        else:
            raise NotImplementedError()
    elif isinstance(schema, CMDArraySchemaBase):
        schema_type = "AAZListType"
    else:
        raise NotImplementedError()

    if flags:
        schema_kwargs['flags'] = flags

    return schema_type, schema_kwargs, cls_builder_name


def parse_cls_builder_name(cls_name):
    return f"_build_schema_{to_snack_case(cls_name)}"
