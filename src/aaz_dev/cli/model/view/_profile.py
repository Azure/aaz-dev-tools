# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from cli.model.common._fields import CLIProfileNameField

from schematics.models import Model
from schematics.types import ModelType, DictType

from ._command_group import CLIViewCommandGroup


class CLIViewProfile(Model):
    name = CLIProfileNameField(required=True)
    command_groups = DictType(
        field=ModelType(CLIViewCommandGroup),
        serialized_name="commandGroups",
        deserialize_from="commandGroups"
    )

    class Options:
        serialize_when_none = False

    @property
    def profile_folder_name(self):
        profile_folder_name = self.name.lower().replace('-', '_')
        if profile_folder_name != "latest":
            # for rest profiles such as 2019-03-01-hybrid, the folder name starts with digit,
            # it's not a valid python package name.
            profile_folder_name = "profile_" + profile_folder_name
        return profile_folder_name
