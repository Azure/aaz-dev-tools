# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from cli.model.common._fields import CLICommandNameField, CLIVersionField, CLIModifiedField
from schematics.models import Model
from schematics.types import ListType, BooleanType


class CLIViewCommand(Model):
    names = ListType(field=CLICommandNameField(), min_size=1, required=True)  # full name of a command
    registered = BooleanType()  # register in command table or not

    version = CLIVersionField()  # the version of wait command is not required.
    modified = CLIModifiedField()

    class Options:
        serialize_when_none = False
