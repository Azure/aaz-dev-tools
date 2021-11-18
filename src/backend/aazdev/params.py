# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from knack.arguments import ArgumentsContext


def load_arguments(self, _):
    with ArgumentsContext(self, "") as c:
        c.argument("swagger_path", options_list=["--swagger"], type=str, help="Path to an existing swagger path.")
        c.argument("configuration_path", option_list=["--config"], type=str, help="Path to an existing configuration path.")
        c.argument("module_name", options_list=["--name"], type=str, help="Name of the module to generate.")
        c.argument("resource_id", options_list=["--id"], type=str, help="ID of the resource to generate.")
        c.argument("api_version", options_list=["--version"], type=str, help="Version of the configuration to generate.")
