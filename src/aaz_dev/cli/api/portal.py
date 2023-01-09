
from flask import Blueprint
import click, logging
from utils.config import Config
from cli.controller.portal_cli_generator import PortalCliGenerator

logging.basicConfig(level="INFO")

bp = Blueprint('portal', __name__, url_prefix='/CLI/Portal')

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
    required=True, multiple=True,
    help="Name of the module to generate seperated."
)
def generate_module_command_portal(module):
    from cli.controller.az_module_manager import AzMainManager, AzExtensionManager
    from command.controller.specs_manager import AAZSpecsManager
    az_main_manager = AzMainManager()
    az_ext_manager = AzExtensionManager()
    aaz_spec_manager = AAZSpecsManager()
    root = aaz_spec_manager.find_command_group()
    if not root:
        return "Command group spec root not exist"
    portal_cli_generator = PortalCliGenerator()
    for mod in module:
        if az_main_manager.has_module(mod):
            cli_module = az_main_manager.load_module(mod)
            registered_cmds = az_main_manager.find_module_cmd_registered(cli_module['profiles']['latest'])
            logging.info("Input module: {0} in cli".format(mod))
        elif az_ext_manager.has_module(mod):
            cli_module = az_ext_manager.load_module(mod)
            registered_cmds = az_ext_manager.find_module_cmd_registered(cli_module['profiles']['latest'])
            logging.info("Input module: {0} in cli extension".format(mod))
        else:
            raise ValueError("Invalid input module: {0}, please check".format(mod))
        cmd_portal_list = portal_cli_generator.generate_cmds_portal_info(aaz_spec_manager, registered_cmds)
        portal_cli_generator.generate_cmds_portal_file(cmd_portal_list)
    logging.info("done")
