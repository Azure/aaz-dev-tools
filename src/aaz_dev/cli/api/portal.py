
from flask import Blueprint
import click, logging
from utils.config import Config
from cli.controller.portal_cli_generator import PortalCliGenerator

logging.basicConfig(level="INFO")

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
            registered_cmds = az_main_manager.find_module_cmd_registered(cli_module['profiles']['latest'])
            logging.info("Input module: {0} in cli extension".format(mod))
        else:
            raise ValueError("Invalid input module: {0}, please check".format(mod))
        cmd_portal_list = []
        for cmd_name_version in registered_cmds:
            # cmd_name_version = ['monitor', 'diagnostic-setting', 'list', '2021-05-01-preview']
            node_names = cmd_name_version[:-2]
            leaf_name = cmd_name_version[-2]
            registered_version = cmd_name_version[-1]
            leaf = aaz_spec_manager.find_command(*node_names, leaf_name)
            if not leaf or not leaf.versions:
                logging.warning("Command group: " + " ".join(node_names) + " not exist")
                continue
            if not leaf.versions:
                logging.warning("Command group: " + " ".join(node_names) + " version not exist")
                continue
            target_version = None
            for v in (leaf.versions or []):
                if v.name == registered_version:
                    target_version = v
                    break
            if not target_version:
                logging.warning("Command: " + " ".join(node_names) + " version not exist")
                continue
            logging.info("Generating portal config of [ az {0} ] with registered version {1}".format(" ".join(cmd_name_version[:-1]),
                                                                                              registered_version))
            cfg_reader = aaz_spec_manager.load_resource_cfg_reader_by_command_with_version(leaf, version=target_version)
            cmd_cfg = cfg_reader.find_command(*leaf.names)
            cmd_portal_info = portal_cli_generator.generate_command_portal_raw(cmd_cfg, leaf, target_version)
            if cmd_portal_info:
                cmd_portal_list.append(cmd_portal_info)
        portal_cli_generator.generate_cmds_portal(cmd_portal_list)
    logging.info("done")
