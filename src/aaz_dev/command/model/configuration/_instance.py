# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from schematics.models import Model
from schematics.types import StringType, ListType, ModelType
from schematics.types.serializable import serializable

from ._fields import CMDVariantField, CMDBooleanField


class CMDInstanceIdentifier(Model):

    key = StringType(required=True, min_length=1)
    arg = CMDVariantField(required=True)


class CMDInstance(Model):

    ref = CMDVariantField(required=True)
    identifiers = ListType(ModelType(CMDInstanceIdentifier))
