# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType, BooleanType
from ._fields import CMDVariantField
from ._schema import CMDJson


class CMDInstanceUpdateAction(Model):
    POLYMORPHIC_KEY = None

    # properties as tags
    instance = CMDVariantField(required=True)
    client_flatten = BooleanType(default=False)  # to control instance in client_flatten mode or not

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY is not None and cls.POLYMORPHIC_KEY in data
        return False


# json instance update
class CMDJsonInstanceUpdateAction(CMDInstanceUpdateAction):
    POLYMORPHIC_KEY = "json"

    # properties as nodes
    json = ModelType(CMDJson)


# generic instance update
class CMDGenericInstanceUpdateMethod(Model):

    # properties as tags
    add = CMDVariantField()
    set = CMDVariantField()
    remove = CMDVariantField()
    force_string = CMDVariantField()


class CMDGenericInstanceUpdateAction(CMDInstanceUpdateAction):
    POLYMORPHIC_KEY = "generic"

    # properties as nodes
    generic = ModelType(CMDGenericInstanceUpdateMethod)
