# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from schematics.models import Model
from schematics.types import ModelType, DictType, StringType

from ._profile import CLIViewProfile


class CLIModule(Model):
    name = StringType(required=True)
    folder = StringType()
    profiles = DictType(
        field=ModelType(CLIViewProfile),
    )

    class Options:
        serialize_when_none = False
