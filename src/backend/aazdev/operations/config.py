# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
from command.model.configuration import CMDResource, CMDConfiguration
from swagger.controller.command_generator import CommandGenerator

from .xml import XMLSerializer


def generate_config(swagger_path, config_path, module_name, resource_id, api_version):
    generator = CommandGenerator(module_name="(MgmtPlane)/" + module_name, swagger_path=swagger_path)
    cmd_resource = CMDResource({"id": resource_id, "version": api_version})
    resources = generator.load_resources([cmd_resource])
    command_group = generator.create_draft_command_group(resources[resource_id])

    model = CMDConfiguration({"resources": [cmd_resource], "command_group": command_group})
    with open(config_path, "wb") as fp:
        fp.write(XMLSerializer(model).to_xml())
    return "Done."
