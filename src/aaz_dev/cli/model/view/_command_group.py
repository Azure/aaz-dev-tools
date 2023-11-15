# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from cli.model.common._fields import CLICommandNameField
from schematics.models import Model
from schematics.types import ModelType, ListType, DictType

from ._command import CLIViewCommand


class CLIViewCommandGroup(Model):
    names = ListType(field=CLICommandNameField(), min_size=1, required=True)  # full name of a command group

    command_groups = DictType(
        field=ModelType("CLIViewCommandGroup"),
        serialized_name="commandGroups",
        deserialize_from="commandGroups"
    )
    commands = DictType(
        field=ModelType(CLIViewCommand)
    )
    wait_command = ModelType(
        CLIViewCommand,
        serialized_name="waitCommand",
        deserialize_from="waitCommand"
    )

    class Options:
        serialize_when_none = False
