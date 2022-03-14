# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType

from ._content import CMDRequestJson
from ._fields import CMDVariantField


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

    def reformat(self, **kwargs):
        raise NotImplementedError()


# json instance update
class CMDJsonInstanceUpdateAction(CMDInstanceUpdateAction):
    POLYMORPHIC_KEY = "json"

    # properties as nodes
    json = ModelType(CMDRequestJson, required=True)

    def generate_args(self):
        return self.json.generate_args(is_update_action=True)

    def reformat(self, **kwargs):
        self.json.reformat(**kwargs)
