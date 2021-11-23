import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from command.model.configuration import CMDResource
from swagger.controller.command_generator import CommandGenerator





def generate_config(swagger_path, module_name, resource_id, api_version):
    generator = CommandGenerator(module_name="(MgmtPlane)/" + module_name, swagger_path=swagger_path)
    cmd_resource = CMDResource({"id": resource_id, "version": api_version})
    resources = generator.load_resources([cmd_resource])
    command_group = generator.create_draft_command_group(resources[resource_id])

    config = command_group.to_primitive()
    print(command_group)
    # print(json.dumps(config))


def generate_config_network_vnet():

    module_name = 'network'
    resource_id = '/subscriptions/{}/resourcegroups/{}/providers/microsoft.network/virtualnetworks/{}'
    api_version = "2021-05-01"

    generate_config(swagger_path=swagger_path, module_name=module_name, resource_id=resource_id, api_version=api_version)



