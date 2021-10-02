# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, PolyModelType, IntType

from ._fields import CMDVariantField, CMDBooleanField, CMDURLPathField
from ._http_body import CMDHttpBody
from ._http_param import CMDHttpParam


class CMDHttpRequestArgs(Model):
    # properties as nodes
    params = ListType(PolyModelType(CMDHttpParam, allow_subclasses=True))
    consts = ListType(PolyModelType(CMDHttpParam, allow_subclasses=True))

    class Options:
        serialize_when_none = True


class CMDHttpRequestPath(CMDHttpRequestArgs):
    pass


class CMDHttpRequestQuery(CMDHttpRequestArgs):
    pass


class CMDHttpRequestHeader(CMDHttpRequestArgs):
    # properties as tags
    client_request_id = StringType(
        serialized_name="clientRequestId",
        deserialize_from="clientRequestId",
    )    # specifies the header parameter to be used instead of `x-ms-client-request-id`


class CMDHttpRequest(Model):
    # properties as tags
    method = StringType(choices=("get", "put", "post", "delete", "options", "head", "patch",), required=True)

    # properties as nodes
    path = ModelType(CMDHttpRequestPath)
    query = ModelType(CMDHttpRequestQuery)
    header = ModelType(CMDHttpRequestHeader)
    body = PolyModelType(CMDHttpBody, allow_subclasses=True)

    class Options:
        serialize_when_none = True


class CMDHttpResponseHeaderItem(Model):
    # properties as tags
    name = StringType(required=True)
    var = CMDVariantField()

    class Options:
        serialize_when_none = True


class CMDHttpResponseHeader(Model):
    # properties as nodes
    items = ListType(ModelType(CMDHttpResponseHeaderItem))

    class Options:
        serialize_when_none = True


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
    description = StringType(required=True)

    # properties as nodes
    header = ModelType(CMDHttpResponseHeader)
    body = PolyModelType(CMDHttpBody, allow_subclasses=True)

    class Options:
        serialize_when_none = True


class CMDHttpAction(Model):
    # properties as tags
    path = CMDURLPathField(required=True)

    # properties as nodes
    request = ModelType(CMDHttpRequest)
    responses = ListType(ModelType(CMDHttpResponse))
