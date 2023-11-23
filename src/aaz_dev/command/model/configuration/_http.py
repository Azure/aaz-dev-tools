# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, PolyModelType, IntType

from ._fields import CMDVariantField, CMDBooleanField, CMDURLPathField, CMDDescriptionField
from ._http_request_body import CMDHttpRequestBody
from ._http_response_body import CMDHttpResponseBody
from ._schema import CMDSchemaField, _diff_props
from ._arg_builder import CMDArgBuilder
from ._arg import CMDResourceGroupNameArg, CMDSubscriptionIdArg, CMDResourceLocationArg
from ._utils import CMDDiffLevelEnum
from msrestazure.tools import parse_resource_id, resource_id
from ._utils import CMDArgBuildPrefix


class CMDHttpRequestArgs(Model):
    # properties as nodes
    params = ListType(CMDSchemaField())
    consts = ListType(CMDSchemaField())

    class Options:
        serialize_when_none = False

    def reformat(self, **kwargs):
        if self.params:
            for param in self.params:
                param.reformat(**kwargs)
            self.params = sorted(self.params, key=lambda s: s.name)
        if self.consts:
            for const in self.consts:
                const.reformat(**kwargs)
            self.consts = sorted(self.consts, key=lambda c: c.name)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}

        params_diff = _diff_props(self.params, old.params, level)
        if params_diff:
            diff["params"] = params_diff
        consts_diff = _diff_props(self.consts, old.consts, level)
        if consts_diff:
            diff["consts"] = consts_diff
        return diff


class CMDHttpRequestPath(CMDHttpRequestArgs):

    def generate_args(self, path, ref_args, has_subresource, var_prefix=None):
        try:
            id_parts = parse_resource_id(path)
            resource_id(**id_parts)
        except KeyError:
            # not a valid resource id
            id_parts = {}
        resource_name = id_parts.pop("resource_name", None)
        if resource_name and (not path.endswith(resource_name) or has_subresource):
            resource_name = None
        args = []
        if self.params:
            if var_prefix:
                if not var_prefix.endswith("$"):
                    var_prefix += '.'
                var_prefix += CMDArgBuildPrefix.Path[1:]  # PATH
            else:
                var_prefix = CMDArgBuildPrefix.Path
            for param in self.params:
                id_part = None
                placeholder = '{' + param.name + '}'
                for part, name in id_parts.items():
                    if name == placeholder:
                        id_part = part
                        break

                if id_part == 'subscription' or param.name == 'subscriptionId':
                    arg = CMDSubscriptionIdArg({
                        'var': f'{var_prefix}.subscriptionId',
                        'options': ['subscription'],
                    })
                    param.arg = arg.var
                    arg.ref_schema = param
                elif id_part == 'resource_group' or param.name == 'resourceGroupName':
                    arg = CMDResourceGroupNameArg({
                        'var': f'{var_prefix}.resourceGroupName',
                        'options': ['resource-group', 'g'],
                    })
                    param.arg = arg.var
                    arg.ref_schema = param
                elif param.name == 'location':
                    arg = CMDResourceLocationArg({
                        'var': f'{var_prefix}.location',
                        'options': ['location', 'l'],
                    })
                    param.arg = arg.var
                    arg.ref_schema = param
                else:
                    builder = CMDArgBuilder.new_builder(
                        schema=param, var_prefix=var_prefix, ref_args=ref_args
                    )
                    result = builder.get_args()
                    assert len(result) == 1
                    arg = result[0]

                    if resource_name == placeholder and not builder._ref_arg:
                        arg.options = list({*arg.options, "name", "n"})

                arg.required = True
                arg.id_part = id_part  # id_part should not be generated for create command or commands for subresource
                args.append(arg)

        return args


class CMDHttpRequestQuery(CMDHttpRequestArgs):

    def generate_args(self, ref_args, var_prefix=None):
        args = []
        if self.params:
            if var_prefix:
                if not var_prefix.endswith("$"):
                    var_prefix += '.'
                var_prefix += CMDArgBuildPrefix.Query[1:]  # Query
            else:
                var_prefix = CMDArgBuildPrefix.Query
            for param in self.params:
                builder = CMDArgBuilder.new_builder(
                    schema=param, var_prefix=var_prefix, ref_args=ref_args
                )
                args.extend(builder.get_args())
        return args


class CMDHttpRequestHeader(CMDHttpRequestArgs):
    # properties as tags
    client_request_id = StringType(
        serialized_name="clientRequestId",
        deserialize_from="clientRequestId",
    )  # specifies the header parameter to be used instead of `x-ms-client-request-id`

    def generate_args(self, ref_args, var_prefix=None):
        args = []
        if var_prefix:
            if not var_prefix.endswith("$"):
                var_prefix += '.'
            var_prefix += CMDArgBuildPrefix.Header[1:]  # Header
        else:
            var_prefix = CMDArgBuildPrefix.Header
        for param in self.params:
            builder = CMDArgBuilder.new_builder(
                schema=param, var_prefix=var_prefix, ref_args=ref_args
            )
            args.extend(builder.get_args())
        return args

    def diff(self, old, level):
        diff = super().diff(old, level)
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.client_request_id != old.client_request_id:
                diff["client_request_id"] = f"{old.client_request_id} != {self.client_request_id}"
        return diff


class CMDHttpRequest(Model):
    # properties as tags
    method = StringType(choices=("get", "put", "post", "delete", "options", "head", "patch",), required=True)

    # properties as nodes
    path = ModelType(CMDHttpRequestPath)
    query = ModelType(CMDHttpRequestQuery)
    header = ModelType(CMDHttpRequestHeader)
    body = PolyModelType(CMDHttpRequestBody, allow_subclasses=True)

    class Options:
        serialize_when_none = False

    def generate_args(self, path, ref_args, has_subresource, var_prefix=None):
        args = []
        if self.path:
            args.extend(self.path.generate_args(path, ref_args, has_subresource, var_prefix=var_prefix))
        if self.query:
            args.extend(self.query.generate_args(ref_args, var_prefix=var_prefix))
        if self.header:
            args.extend(self.header.generate_args(ref_args, var_prefix=var_prefix))
        if self.body:
            args.extend(self.body.generate_args(ref_args, var_prefix=var_prefix))
        return args

    def reformat(self, **kwargs):
        if self.path:
            self.path.reformat(**kwargs)
        if self.query:
            self.query.reformat(**kwargs)
        if self.header:
            self.header.reformat(**kwargs)
        if self.body:
            self.body.reformat(**kwargs)

    def register_cls(self, **kwargs):
        if self.body:
            self.body.register_cls(**kwargs)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.method != old.method:
                diff["method"] = f"{old.method} != {self.method}"
            if (not self.path) != (not old.path):
                diff["path"] = "Miss path" if old.path else "New path"
            elif self.path:
                path_diff = self.path.diff(old.path, level)
                if path_diff:
                    diff["path"] = path_diff
            if (not self.query) != (not old.query):
                diff["query"] = "Miss query" if old.query else "New query"
            elif self.query:
                query_diff = self.query.diff(old.query, level)
                if query_diff:
                    diff["query"] = query_diff
            if (not self.header) != (not old.header):
                diff["header"] = "Miss header" if old.header else "New header"
            elif self.header:
                header_diff = self.header.diff(old.header, level)
                if header_diff:
                    diff["header"] = header_diff
            if (not self.body) != (not old.body):
                diff["body"] = "Miss request body" if old.body else "New request body"
            elif self.body:
                body_diff = self.body.diff(old.body, level)
                if body_diff:
                    diff["body"] = body_diff
        return diff


class CMDHttpResponseHeaderItem(Model):
    # properties as tags
    name = StringType(required=True)
    var = CMDVariantField()

    class Options:
        serialize_when_none = False

    def diff(self, old, level):
        diff = {}

        if level >= CMDDiffLevelEnum.Structure:
            if old.var and not self.var:
                diff["var"] = "Miss variant"
            if self.var and not old.var:
                diff["var"] = "New variant"

        if level >= CMDDiffLevelEnum.Associate:
            if self.var != old.var:
                diff["var"] = f"{old.var} != {self.var}"
        return diff


class CMDHttpResponseHeader(Model):
    # properties as nodes
    items = ListType(ModelType(CMDHttpResponseHeaderItem))

    class Options:
        serialize_when_none = False

    def diff(self, old, level):
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            items_dict = {item.name: item for item in self.items}
            for old_item in old.items:
                if old_item.name not in items_dict:
                    diff[old_item.name] = "Miss header item"
                else:
                    item = items_dict.pop(old_item.name)
                    item_diff = item.diff(old_item, level)
                    if item_diff:
                        diff[old_item.name] = item_diff

        if level >= CMDDiffLevelEnum.Structure:
            old_items_dict = {item.name: item for item in old.items}
            for item in self.items:
                if item.name not in old_items_dict:
                    diff[item.name] = "New header item"
                else:
                    old_items_dict.pop(item.name)
            for old_item in old_items_dict.values():
                diff[old_item.name] = "Miss header item"
        return diff

    def reformat(self, **kwargs):
        if self.items:
            self.items = sorted(self.items, key=lambda h: h.name)


class CMDHttpResponse(Model):
    # properties as tags
    status_codes = ListType(
        IntType(),
        serialized_name='statusCode',
        deserialize_from='statusCode',
    )  # if status_codes is None, then it's the default response.
    is_error = CMDBooleanField(
        serialized_name='isError',
        deserialize_from='isError'
    )
    description = CMDDescriptionField()

    # properties as nodes
    header = ModelType(CMDHttpResponseHeader)
    body = PolyModelType(CMDHttpResponseBody, allow_subclasses=True)

    class Options:
        serialize_when_none = False

    def diff(self, old, level):
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (not self.status_codes) != (not old.status_codes):
                diff["status_codes"] = f"{old.status_codes} != {self.status_codes}"
            elif self.status_codes and set(self.status_codes) != set(old.status_codes):
                diff["status_codes"] = f"{old.status_codes} != {self.status_codes}"

            if (not self.is_error) != (not old.is_error):
                diff["is_error"] = f"{old.is_error} != {self.is_error}"

            if old.header is not None:
                if self.header is None:
                    diff["header"] = "Miss header"
                else:
                    header_diff = self.header.diff(old.header, level)
                    if header_diff:
                        diff["header"] = header_diff

            if old.body is not None:
                if self.body is None:
                    diff["body"] = "Miss response body"
                else:
                    body_diff = self.body.diff(old.body, level)
                    if body_diff:
                        diff["body"] = body_diff

        if level >= CMDDiffLevelEnum.Structure:
            if self.header is not None and old.header is None:
                diff["header"] = "New header"
            if self.body is not None and old.body is None:
                diff["body"] = "New response body"

        if level >= CMDDiffLevelEnum.All:
            if self.description != old.description:
                diff["description"] = f"'{old.description}' != '{self.description}'"

        return diff

    def reformat(self, **kwargs):
        if self.header:
            self.header.reformat(**kwargs)
        if self.body:
            self.body.reformat(**kwargs)

    def register_cls(self, **kwargs):
        if self.body:
            self.body.register_cls(**kwargs)


class CMDHttpAction(Model):
    # properties as tags
    path = CMDURLPathField(required=True)

    # properties as nodes
    request = ModelType(CMDHttpRequest)
    responses = ListType(ModelType(CMDHttpResponse))

    def generate_args(self, ref_args, has_subresource, var_prefix=None):
        return self.request.generate_args(
            path=self.path, ref_args=ref_args, has_subresource=has_subresource, var_prefix=var_prefix)

    def reformat(self, **kwargs):
        if self.request:
            self.request.reformat(**kwargs)
        if self.responses:
            for response in self.responses:
                if response.is_error:
                    continue
                response.reformat(**kwargs)

    def register_cls(self, **kwargs):
        if self.request:
            self.request.register_cls(**kwargs)
        if self.responses:
            for response in self.responses:
                if response.is_error:
                    continue
                response.register_cls(**kwargs)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.path != old.path:
                diff["path"] = f"{old.path} != {self.path}"
            if (not self.request) != (not old.request):
                diff["request"] = "Miss request" if old.request else "New request"
            elif self.request:
                request_diff = self.request.diff(old.request, level)
                if request_diff:
                    diff["request"] = request_diff

        responses_diff = _diff_responses(self.responses or [], old.responses or [], level)
        if responses_diff:
            diff["responses"] = responses_diff

        return diff


def _diff_responses(responses, old_responses, level):
    diff = {}

    def _build_key(_r):
        _codes = ','.join([str(code) for code in _r.status_codes]) if _r.status_codes else ''
        _error = 'error' if _r.is_error else ''
        return '|'.join([_codes, _error])

    if level >= CMDDiffLevelEnum.BreakingChange:
        responses_dict = {_build_key(resp): resp for resp in responses}
        for old_resp in old_responses:
            old_resp_key = _build_key(old_resp)
            if old_resp_key not in responses_dict:
                diff[old_resp_key] = "Miss response"
            else:
                resp = responses_dict.pop(old_resp_key)
                resp_diff = resp.diff(old_resp, level)
                if resp_diff:
                    diff[old_resp_key] = resp_diff

        for resp in responses_dict.values():
            resp_key = _build_key(resp)
            diff[resp_key] = "New response"

    return diff
