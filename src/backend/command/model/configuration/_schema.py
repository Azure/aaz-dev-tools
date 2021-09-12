# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import ModelType, BooleanType
from ._fields import CMDTypeField, CMDVariantField, StringType, CMDSchemaField


class CMDSchemaBase(Model):
    # properties as tags
    TYPE_VALUE = None

    # base types: "array", "boolean", "integer", "float", "object", "string",
    type_ = CMDTypeField(required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        return False


class CMDSchema(CMDSchemaBase):

    name = StringType()
    arg = CMDVariantField()
    schema = CMDSchemaField()

