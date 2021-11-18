# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from knack.commands import CommandGroup


def load_command_table(self, _):
    def operation_group(name):
        return f"aazdev.operations.{name}#{{}}"

    with CommandGroup(self, "configuration", operation_group("configuration")) as g:
        g.command("generate", "generate_configuration")

    with CommandGroup(self, "code", operation_group("code")) as g:
        g.command("generate", "generate_code")
