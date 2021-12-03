# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

from schematics.types import ListType, ModelType

from .xml import XMLModel
from command.model.configuration import CMDResource, CMDCommandGroup
from swagger.controller.command_generator import CommandGenerator


class CodeGen(XMLModel):
    resource = ListType(ModelType(CMDResource), min_size=1)
    commandGroup = ModelType(CMDCommandGroup)


def generate_config(swagger_path, config_path, module_name, resource_id, api_version):
    generator = CommandGenerator(module_name="(MgmtPlane)/" + module_name, swagger_path=swagger_path)
    cmd_resource = CMDResource({"id": resource_id, "version": api_version})
    resources = generator.load_resources([cmd_resource])
    command_group = generator.create_draft_command_group(resources[resource_id])

    model = CodeGen({"resource": [cmd_resource], "commandGroup": command_group})
    with open(config_path, "w") as fp:
        fp.write(model.to_xml())
    return "Done."
