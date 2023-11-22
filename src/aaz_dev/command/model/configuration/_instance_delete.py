# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType

from ._content import CMDRequestJson
from ._fields import CMDVariantField


class CMDInstanceDeleteAction(Model):
    POLYMORPHIC_KEY = None

    # properties as tags
    ref = CMDVariantField(required=True, deserialize_from=["ref", "instance"])

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDInstanceDeleteAction):
            return hasattr(data, cls.POLYMORPHIC_KEY)
        return False

    def generate_args(self, ref_args, var_prefix=None):
        raise NotImplementedError()

    def reformat(self, **kwargs):
        raise NotImplementedError()

    def register_cls(self, **kwargs):
        return NotImplementedError()


# json instance delete
class CMDJsonInstanceDeleteAction(CMDInstanceDeleteAction):
    POLYMORPHIC_KEY = "json"

    # # properties as nodes
    json = ModelType(CMDRequestJson, required=True)

    def generate_args(self, ref_args, var_prefix=None):
        return self.json.generate_args(ref_args, var_prefix=var_prefix)

    def reformat(self, **kwargs):
        self.json.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.json.register_cls(**kwargs)
