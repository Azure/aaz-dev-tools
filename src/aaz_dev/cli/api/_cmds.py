import click
import logging
from flask import Blueprint
import sys

from utils.config import Config

logger = logging.getLogger('backend')

bp = Blueprint('cli-cmds', __name__, url_prefix='/CLI/CMDs', cli_group="cli")
bp.cli.short_help = "Manage aaz commands in azure-cli and azure-cli-extensions."


@bp.cli.command("regenerate", short_help="Regenerate aaz commands from command models in azure-cli/azure-cli-extensions")
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
    callback=Config.validate_and_setup_cli_path,
    help="The local path of azure-cli repo. Only required when generate code to azure-cli repo."
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_extension_path,
    help="The local path of azure-cli-extension repo. Only required when generate code to azure-cli-extension repo."
)
@click.option(
    "--extension-or-module-name", '--name',
    required=True,
    help="Name of the module in azure-cli or the extension in azure-cli-extensions"
)
def regenerate_code(extension_or_module_name, cli_path=None, cli_extension_path=None):
    from utils.config import Config
    from utils.exceptions import InvalidAPIUsage
    from cli.controller.az_module_manager import AzExtensionManager, AzMainManager
    if not cli_path and not cli_extension_path:
        logger.error("Please provide `--cli-path` or `--cli-extension-path`")
        sys.exit(1)
    if cli_path and cli_extension_path:
        logger.error("Please don't provide `--cli-path` and `--cli-extension-path`")
        sys.exit(1)

    try:
        if cli_path is not None:
            assert Config.CLI_PATH is not None
            manager = AzMainManager()
        else:
            assert cli_extension_path is not None
            assert Config.CLI_EXTENSION_PATH is not None
            manager = AzExtensionManager()

        if not manager.has_module(extension_or_module_name):
            # module = manager.create_new_mod(extension_or_module_name)
            raise ValueError(f"Cannot find module or extension `{extension_or_module_name}`")
        logger.info(f"Load module `{extension_or_module_name}`")
        module = manager.load_module(extension_or_module_name)
        logger.info(f"Regenerate module `{extension_or_module_name}`")
        manager.update_module(extension_or_module_name, module.profiles)
    except InvalidAPIUsage as err:
        logger.error(err)
        sys.exit(1)
    except ValueError as err:
        logger.error(err)
        sys.exit(1)


@bp.cli.command("generate-by-swagger-tag", short_help="Generate aaz commands from command models in azure-cli/azure-cli-extensions selected by swagger tags.")
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
    callback=Config.validate_and_setup_cli_path,
    help="The local path of azure-cli repo. Only required when generate code to azure-cli repo."
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_extension_path,
    help="The local path of azure-cli-extension repo. Only required when generate code to azure-cli-extension repo."
)
@click.option(
    "--extension-or-module-name", '--name',
    required=True,
    help="Name of the module in azure-cli or the extension in azure-cli-extensions"
)
@click.option(
    "--swagger-module-path", "--sm",
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_MODULE_PATH,
    required=not Config.SWAGGER_MODULE_PATH,
    callback=Config.validate_and_setup_swagger_module_path,
    expose_value=False,
    help="The local path of swagger module."
)
@click.option(
    "--resource-provider", "--rp",
    default=Config.DEFAULT_RESOURCE_PROVIDER,
    required=not Config.DEFAULT_RESOURCE_PROVIDER,
    callback=Config.validate_and_setup_default_resource_provider,
    expose_value=False,
    help="The resource provider name."
)
@click.option(
    "--swagger-tag", "--tag",
    required=True,
    help="Swagger tag with input files."
)
@click.option(
    "--profile",
    required=True,
    type=click.Choice(Config.CLI_PROFILES),
    default=Config.CLI_DEFAULT_PROFILE,
)
def generate_by_swagger_tag(profile, swagger_tag, extension_or_module_name, cli_path=None, cli_extension_path=None):
    from utils.config import Config
    from utils.exceptions import InvalidAPIUsage
    from cli.controller.az_module_manager import AzExtensionManager, AzMainManager
    from swagger.controller.specs_manager import SwaggerSpecsManager
    from command.controller.specs_manager import AAZSpecsManager
    if not Config.DEFAULT_SWAGGER_MODULE:
        Config.DEFAULT_SWAGGER_MODULE = "__MODULE__"

    try:
        swagger_specs = SwaggerSpecsManager()
        aaz_specs = AAZSpecsManager()
        module_manager = swagger_specs.get_module_manager(Config.DEFAULT_PLANE, Config.DEFAULT_SWAGGER_MODULE)
        rp = module_manager.get_openapi_resource_provider(Config.DEFAULT_RESOURCE_PROVIDER)

        resource_map = rp.get_resource_map_by_tag(swagger_tag)
        if not resource_map:
            raise InvalidAPIUsage(f"Tag `{swagger_tag}` is not exist")

        commands_map = {}
        for resource_id, version_map in resource_map.items():
            v_list = [v for v in version_map]
            if len(v_list) > 1:
                raise InvalidAPIUsage(f"Tag `{swagger_tag}` contains multiple api versions of one resource", payload={
                    "Resource": resource_id,
                    "versions": v_list,
                })

            v = v_list[0]
            # TODO: handle plane here
            cfg_reader = aaz_specs.load_resource_cfg_reader(Config.DEFAULT_PLANE, resource_id, v)
            if not cfg_reader:
                logger.error(f"Command models not exist in aaz for resource: {resource_id} version: {v}")
                continue
            for cmd_names, command in cfg_reader.iter_commands():
                key = tuple(cmd_names)
                if key in commands_map and commands_map[key] != command.version:
                    raise ValueError(f"Multi version contained for command: {''.join(cmd_names)} versions: {commands_map[key]}, {command.version}")
                commands_map[key] = command.version

        profile = _build_profile(profile, commands_map)

        if cli_path is not None:
            assert Config.CLI_PATH is not None
            manager = AzMainManager()
        else:
            assert cli_extension_path is not None
            assert Config.CLI_EXTENSION_PATH is not None
            manager = AzExtensionManager()

        if not manager.has_module(extension_or_module_name):
            logger.info(f"Create cli module `{extension_or_module_name}`")
            manager.create_new_mod(extension_or_module_name)

        logger.info(f"Load cli module `{extension_or_module_name}`")
        module = manager.load_module(extension_or_module_name)

        module.profiles[profile.name] = profile
        logger.info(f"Regenerate module `{extension_or_module_name}`")
        manager.update_module(extension_or_module_name, module.profiles)

    except InvalidAPIUsage as err:
        logger.error(err)
        sys.exit(1)
    except ValueError as err:
        logger.error(err)
        sys.exit(1)


def _build_profile(profile_name, commands_map):
    from cli.model.view import CLIViewProfile, CLIViewCommand, CLIViewCommandGroup
    profile = CLIViewProfile({
        "name": profile_name,
        "commandGroups": {},
    })
    command_group_map = {tuple(): profile}
    for cmd_names, version in commands_map.items():
        group_names = cmd_names[:-1]
        if group_names not in command_group_map:
            group = CLIViewCommandGroup({
                "names": list(group_names),
                "commandGroups": {},
                "commands": {}
            })
        else:
            group = command_group_map[group_names]
        group.commands[cmd_names[-1]] = CLIViewCommand({
            "names": list(cmd_names),
            "version": version,
            "registered": True
        })

        while group_names not in command_group_map:
            command_group_map[group_names] = group
            parent_group_names = group_names[:-1]
            if parent_group_names not in command_group_map:
                parent_group = CLIViewCommandGroup({
                    "names": list(parent_group_names),
                    "commandGroups": {},
                    "commands": {}
                })
            else:
                parent_group = command_group_map[parent_group_names]
            parent_group.command_groups[group_names[-1]] = group

            group = parent_group
            group_names = parent_group_names

    return profile


@bp.cli.command("generate-powershell", short_help="Generate powershell code based on selected azure cli module.")
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
    callback=Config.validate_and_setup_cli_path,
    help="The local path of azure-cli repo. Only required when generate code to azure-cli repo."
)
@click.option(
    "--cli-extension-path", '-e',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    callback=Config.validate_and_setup_cli_extension_path,
    help="The local path of azure-cli-extension repo. Only required when generate code to azure-cli-extension repo."
)
@click.option(
    "--extension-or-module-name", '--name',
    required=True,
    help="Name of the module in azure-cli or the extension in azure-cli-extensions"
)
@click.option(
    "--swagger-module-path", "--sm",
    type=click.Path(file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    default=Config.SWAGGER_MODULE_PATH,
    required=not Config.SWAGGER_MODULE_PATH,
    callback=Config.validate_and_setup_swagger_module_path,
    expose_value=False,
    help="The local path of swagger module."
)
@click.option(
    "--resource-provider", "--rp",
    default=Config.DEFAULT_RESOURCE_PROVIDER,
    required=not Config.DEFAULT_RESOURCE_PROVIDER,
    callback=Config.validate_and_setup_default_resource_provider,
    expose_value=False,
    help="The resource provider name."
)
def generate_powershell(extension_or_module_name, cli_path=None, cli_extension_path=None):
    pass
