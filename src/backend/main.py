# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import sys

from knack import (
    CLI,
    CLICommandsLoader,
)


class AazDevCommandsLoader(CLICommandsLoader):
    def load_command_table(self, args):
        from aazdev.commands import load_command_table
        load_command_table(self, args)
        return super().load_command_table(args)

    def load_arguments(self, command):
        from aazdev.params import load_arguments
        load_arguments(self, command)
        super().load_arguments(command)


def main():
    try:
        aazdev = CLI(cli_name="aazdev",
                     commands_loader_cls=AazDevCommandsLoader)
        exit_code = aazdev.invoke(sys.argv[1:])
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
