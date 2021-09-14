# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, URLType, PolyModelType, IntType, BooleanType
from ._fields import CMDVariantField
from ._http_body import CMDHttpBody


class CMDHttpParam(Model):
    name = StringType(required=True)
    arg = CMDVariantField(required=True)


class CMDHttpConst(Model):
    name = StringType(required=True)
    value = StringType(required=True)


class CMDHttpRequestArgs(Model):

    # properties as nodes
    params = ListType(ModelType(CMDHttpParam))
    consts = ListType(ModelType(CMDHttpConst))


class CMDHttpRequest(Model):
    # properties as tags
    method = StringType(choices=("get", "put", "post", "delete", "options", "head", "patch", ), required=True)

    # properties as nodes
    path = ModelType(CMDHttpRequestArgs)
    query = ModelType(CMDHttpRequestArgs)
    header = ModelType(CMDHttpRequestArgs)
    body = PolyModelType(CMDHttpBody, allow_subclasses=True)


class CMDHttpResponseHeaderItem(Model):
    # properties as tags
    name = StringType(required=True)
    var = CMDVariantField()


class CMDHttpResponseHeader(Model):
    # properties as nodes
    items = ListType(ModelType(CMDHttpResponseHeaderItem))


class CMDHttpResponse(Model):
    # properties as tags
    status_code = ListType(IntType())
    is_error = BooleanType(default=False)

    # properties as nodes
    header = ModelType(CMDHttpResponseHeader)
    body = PolyModelType(CMDHttpBody, allow_subclasses=True)


class CMDHttpAction(Model):
    # properties as tags
    path = URLType(required=True)

    # properties as nodes
    request = ModelType(CMDHttpRequest)
    responses = ListType(ModelType(CMDHttpResponse))
