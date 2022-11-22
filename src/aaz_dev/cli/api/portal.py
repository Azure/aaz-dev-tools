
from flask import Blueprint
import click
from utils.config import Config
from cli.controller.portal_cli_generator import PortalCliGenerator

bp = Blueprint('portal', __name__, url_prefix='/AAZ/Portal')

# commands
@bp.cli.command("generate", short_help="Generate command portal json file.")
@click.option(
    "--aaz-path", '-a',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.AAZ_PATH,
    required=not Config.AAZ_PATH,
    callback=Config.validate_and_setup_aaz_path,
    expose_value=False,
    help="The local path of aaz repo."
)
@click.option(
    "--cli-path", '-c',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.CLI_PATH,
    required=not Config.CLI_PATH,
    callback=Config.validate_and_setup_cli_path,
    expose_value=False,
    help="The local path of azure-cli repo. Official repo is https://github.com/Azure/azure-cli"
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=Config.CLI_EXTENSION_PATH,
    required=not Config.CLI_EXTENSION_PATH,
    callback=Config.validate_and_setup_cli_extension_path,
    expose_value=False,
    help="The local path of azure-cli-extension repo. Official repo is https://github.com/Azure/azure-cli-extensions"
)
@click.option(
    "--module", '-m',
    required=True,
    help="Name of the module to generate."
)
def generate_module_command_portal(module):
    from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
    from command.controller.specs_manager import AAZSpecsManager
    az_main_manager = AzMainManager()
    az_ext_manager = AzExtensionManager()
    if az_main_manager.has_module(module):
        cli_module = az_main_manager.load_module(module)
        print("Input module: {0} in cli".format(module))
    elif az_ext_manager.has_module(module):
        cli_module = az_ext_manager.load_module(module)
        print("Input module: {0} in cli extension".format(module))
    else:
        raise ValueError("Invalid input module: {0}, please check".format(module))
    aaz_spec_manager = AAZSpecsManager()
    root = aaz_spec_manager.find_command_group()
    if not root:
        return "Command group not exist"
    cmd_nodes_list = aaz_spec_manager.get_module_command_tree(module)
    portal_cli_generator = PortalCliGenerator()
    cmd_portal_list = []
    for node_path in cmd_nodes_list:
        # node_path = ['aaz', 'change-analysis', 'list']
        cmd_module = node_path[1]
        if cmd_module != module:
            continue
        node_names = node_path[1:-1]
        leaf_name = node_path[-1]
        leaf = aaz_spec_manager.find_command(*node_names, leaf_name)
        if not leaf or not leaf.versions:
            print("Command group: " + " ".join(leaf.names) + " not exist")
            continue
        if not leaf.versions:
            print("Command group: " + " ".join(leaf.names) + " version not exist")
            continue
        registered_version = az_main_manager.find_cmd_registered_version(cli_module['profiles']['latest'],
                                                                         *node_path[1:])
        if not registered_version:
            registered_version = az_ext_manager.find_cmd_registered_version(cli_module['profiles']['latest'],
                                                                            *node_path[1:])
        if not registered_version:
            print("Cannot find {0} registered version".format(" ".join(node_path[1:])))
            continue
        target_version = None
        for v in (leaf.versions or []):
            if v.name == registered_version:
                target_version = v
                break
        if not target_version:
            print("Command: " + " ".join(leaf.names) + " version not exist")
            continue
        cfg_reader = aaz_spec_manager.load_resource_cfg_reader_by_command_with_version(leaf, version=target_version)
        cmd_cfg = cfg_reader.find_command(*leaf.names)
        cmd_portal_info = portal_cli_generator.generate_command_portal_raw(cmd_cfg, leaf, target_version)
        if cmd_portal_info:
            cmd_portal_list.append(cmd_portal_info)

    portal_cli_generator.generate_cmds_portal(cmd_portal_list)
    print("done")
