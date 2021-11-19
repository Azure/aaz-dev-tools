# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from knack.arguments import ArgumentsContext
from swagger.utils.tools import swagger_resource_path_to_resource_id
from argcomplete.completers import FilesCompleter


def file_type(path):
    import os
    return os.path.expanduser(path)


def resource_id_type(resource):
    return swagger_resource_path_to_resource_id(resource)


def load_arguments(self, _):
    with ArgumentsContext(self, "") as c:
        c.argument("swagger_path", options_list=["--swagger"], type=file_type, completer=FilesCompleter(), help="Path to an existing swagger path.")
        c.argument("config_path", option_list=["--config"], type=file_type, completer=FilesCompleter(), help="Path to an existing configuration path.")
        c.argument("module_name", options_list=["--module"], type=str, help="Name of the module to generate.")
        c.argument("resource_id", options_list=["--resource"], type=resource_id_type, help="Path or ID of the resource to generate.")
        c.argument("api_version", options_list=["--version"], type=str, help="Version of the configuration to generate.")
