# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType

from ._fields import CMDVariantField, CMDBooleanField
from ._content import CMDJson
from ._arg import CMDClsArg


class CMDInstanceUpdateAction(Model):
    POLYMORPHIC_KEY = None

    # properties as tags
    instance = CMDVariantField(required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDInstanceUpdateAction):
            return hasattr(data, cls.POLYMORPHIC_KEY)
        return False

    def generate_args(self):
        raise NotImplementedError()


# json instance update
class CMDJsonInstanceUpdateAction(CMDInstanceUpdateAction):
    POLYMORPHIC_KEY = "json"

    # properties as nodes
    json = ModelType(CMDJson, required=True)

    def generate_args(self):
        return self.json.generate_args()


# generic instance update
class CMDGenericInstanceUpdateMethod(Model):
    # properties as tags
    add = CMDVariantField()
    set = CMDVariantField()
    remove = CMDVariantField()
    force_string = CMDVariantField(
        serialized_name='forceString',
        deserialize_from='forceString'
    )

    def generate_args(self):
        self.add = "$GenericUpdate.add"
        self.set = "$GenericUpdate.set"
        self.remove = "$GenericUpdate.remove"
        self.force_string = "$GenericUpdate.forceString"

        args = [
            CMDClsArg({
                'var': self.add,
                'type': "@GenericUpdateAdd"
            }),
            CMDClsArg({
                'var': self.set,
                'type': "@GenericUpdateSet"
            }),
            CMDClsArg({
                'var': self.remove,
                'type': "@GenericUpdateRemove"
            }),
            CMDClsArg({
                'var': self.force_string,
                'type': "@GenericUpdateForceString"
            })
        ]
        for arg in args:
            arg.group = "Generic Update"
        return args


class CMDGenericInstanceUpdateAction(CMDInstanceUpdateAction):
    POLYMORPHIC_KEY = "generic"

    # properties as tags
    client_flatten = CMDBooleanField(
        serialized_name='clientFlatten',
        deserialize_from='clientFlatten'
    )  # to control instance in client_flatten mode or not

    # properties as nodes
    generic = ModelType(CMDGenericInstanceUpdateMethod)

    def generate_args(self):
        return self.generic.generate_args()
