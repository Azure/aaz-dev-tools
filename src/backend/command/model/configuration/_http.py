# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from schematics.models import Model
from schematics.types import StringType, ModelType, ListType, URLType
from ._fields import CMDVariantField


class CMDHttpAction(Model):
    # properties as tags
    path = URLType(required=True)

    # properties as nodes
    request = ModelType()
