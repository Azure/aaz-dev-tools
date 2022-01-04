# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, PolyModelType, IntType

from ._fields import CMDVariantField, CMDBooleanField, CMDURLPathField, CMDDescriptionField
from ._http_body import CMDHttpBody
from ._schema import CMDSchemaField
from ._arg_builder import CMDArgBuilder
from ._arg import CMDClsArg
from msrestazure.tools import parse_resource_id, is_valid_resource_id


class CMDHttpRequestArgs(Model):
    # properties as nodes
    params = ListType(CMDSchemaField())
    consts = ListType(CMDSchemaField())

    class Options:
        serialize_when_none = False


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
                if id_part == 'subscription':
                    arg = CMDClsArg({
                        'var': f'{var_prefix}.subscription',
                        'type': '@Subscription',
                        'options': ['subscription'],
                    })
                    param.arg = arg.var
                    arg.ref_schema = param
                elif id_part == 'resource_group':
                    arg = CMDClsArg({
                        'var': f'{var_prefix}.resourceGroup',
                        'type': '@ResourceGroup',
                        'options': ['resource-group', 'g'],
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
    )    # specifies the header parameter to be used instead of `x-ms-client-request-id`

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
    body = PolyModelType(CMDHttpBody, allow_subclasses=True)

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


class CMDHttpResponseHeaderItem(Model):
    # properties as tags
    name = StringType(required=True)
    var = CMDVariantField()

    class Options:
        serialize_when_none = False


class CMDHttpResponseHeader(Model):
    # properties as nodes
    items = ListType(ModelType(CMDHttpResponseHeaderItem))

    class Options:
        serialize_when_none = False


class CMDHttpResponse(Model):
    # properties as tags
    status_codes = ListType(
        IntType(),
        serialized_name='statusCode',
        deserialize_from='statusCode',
    )   # if status_codes is None, then it's the default response.
    is_error = CMDBooleanField(
        serialized_name='isError',
        deserialize_from='isError'
    )
    description = CMDDescriptionField(required=True)

    # properties as nodes
    header = ModelType(CMDHttpResponseHeader)
    body = PolyModelType(CMDHttpBody, allow_subclasses=True)

    class Options:
        serialize_when_none = False


class CMDHttpAction(Model):
    # properties as tags
    path = CMDURLPathField(required=True)

    # properties as nodes
    request = ModelType(CMDHttpRequest)
    responses = ListType(ModelType(CMDHttpResponse))

    def generate_args(self):
        return self.request.generate_args(path=self.path)
