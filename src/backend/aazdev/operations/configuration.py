# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import json

from command.model.configuration import CMDResource
from swagger.controller.command_generator import CommandGenerator


def generate_configuration(swagger_path, configuration_path,
                           module_name, resource_id, api_version):
    generator = CommandGenerator(module_name="(MgmtPlane)/" + module_name)
    cmd_resource = CMDResource({"id": resource_id, "version": api_version})
    resources = generator.load_resources([cmd_resource])
    command_group = generator.create_draft_command_group(resources[resource_id])
    return json.dumps(command_group.to_primitive())
