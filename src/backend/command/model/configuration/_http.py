# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, PolyModelType, IntType

from ._fields import CMDVariantField, CMDBooleanField, CMDURLPathField, CMDDescriptionField
from ._http_request_body import CMDHttpRequestBody
from ._http_response_body import CMDHttpResponseBody
from ._schema import CMDSchemaField
from ._arg_builder import CMDArgBuilder
from ._arg import CMDResourceGroupNameArg, CMDSubscriptionIdArg, CMDResourceLocationArg
from ._utils import CMDDiffLevelEnum
from msrestazure.tools import parse_resource_id, is_valid_resource_id


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


class CMDHttpRequestPath(CMDHttpRequestArgs):

    def generate_args(self, path):
        if is_valid_resource_id(path):
            id_parts = parse_resource_id(path)
        else:
            id_parts = {}
        resource_name = id_parts.pop("resource_name", None)
        if resource_name and not path.endswith(resource_name):
            resource_name = None
        args = []
        if self.params:
            var_prefix = '$Path'
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
                    builder = CMDArgBuilder.new_builder(schema=param, var_prefix=var_prefix)
                    result = builder.get_args()
                    assert len(result) == 1
                    arg = result[0]

                    if resource_name == placeholder:
                        arg.options = list({*arg.options, "name", "n"})

                arg.required = True
                arg.id_part = id_part
                args.append(arg)

        return args


class CMDHttpRequestQuery(CMDHttpRequestArgs):

    def generate_args(self):
        args = []
        for param in self.params:
            builder = CMDArgBuilder.new_builder(schema=param, var_prefix='$Query')
            args.extend(builder.get_args())
        return args


class CMDHttpRequestHeader(CMDHttpRequestArgs):
    # properties as tags
    client_request_id = StringType(
        serialized_name="clientRequestId",
        deserialize_from="clientRequestId",
    )  # specifies the header parameter to be used instead of `x-ms-client-request-id`

    def generate_args(self):
        args = []
        for param in self.params:
            builder = CMDArgBuilder.new_builder(schema=param, var_prefix='$Header')
            args.extend(builder.get_args())
        return args


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

    def generate_args(self, path):
        args = []
        if self.path:
            args.extend(self.path.generate_args(path))
        if self.query:
            args.extend(self.query.generate_args())
        if self.header:
            args.extend(self.header.generate_args())
        if self.body:
            args.extend(self.body.generate_args())
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
    description = CMDDescriptionField(required=True)

    # properties as nodes
    header = ModelType(CMDHttpResponseHeader)
    body = PolyModelType(CMDHttpResponseBody, allow_subclasses=True)

    class Options:
        serialize_when_none = False

    def diff(self, old, level):
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (self.status_codes is not None) != (old.status_codes is not None):
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


class CMDHttpAction(Model):
    # properties as tags
    path = CMDURLPathField(required=True)

    # properties as nodes
    request = ModelType(CMDHttpRequest)
    responses = ListType(ModelType(CMDHttpResponse))

    def generate_args(self):
        return self.request.generate_args(path=self.path)

    def reformat(self, **kwargs):
        if self.request:
            self.request.reformat(**kwargs)
        if self.responses:
            for response in self.responses:
                if response.is_error:
                    continue
                response.reformat(**kwargs)
