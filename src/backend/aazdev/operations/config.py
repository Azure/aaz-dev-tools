# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import json

from command.model.configuration import CMDResource
from swagger.controller.command_generator import CommandGenerator
from swagger.utils.tools import swagger_path_to_resource_id


def generate_config(swagger_path, config_path, module_name, resource_id, api_version):
    generator = CommandGenerator(module_name="(MgmtPlane)/" + module_name)
    resource_id = swagger_path_to_resource_id(resource_id)
    cmd_resource = CMDResource({"id": resource_id, "version": api_version})
    resources = generator.load_resources([cmd_resource])
    command_group = generator.create_draft_command_group(resources[resource_id])
    return json.dumps(command_group.to_primitive())
